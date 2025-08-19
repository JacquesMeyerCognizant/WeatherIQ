# Standard libraries
import dataclasses
import datetime
import glob
import math
import os
import zipfile
from typing import Optional



# Numerical and array operations
import numpy as np
import xarray as xr
import xarray
from datatree import DataTree

xr.DataTree = DataTree  # Patch xarray to include DataTree

# JAX-related
import jax
import haiku as hk

# GraphCast modules
import datatree 
from graphcast import rollout
from graphcast import xarray_jax
from graphcast import normalization
from graphcast import checkpoint
from graphcast import data_utils
from graphcast import xarray_tree
from graphcast import gencast
from graphcast import denoiser
from graphcast import nan_cleaning

# CDS API
import cdsapi

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

def process_predictions(predictions_1: xr.Dataset, input_1: xr.Dataset) -> xr.Dataset:
    """
    Processes model predictions by averaging samples, assigning datetime coordinates,
    interpolating the target date to 1-hour intervals, and extending the forecast to 3 days.

    Parameters:
    - predictions_1 (xr.Dataset): The raw model predictions with a 'sample' dimension.
    - input_1 (xr.Dataset): The original input dataset used to derive datetime references.
    - output_path (str, optional): Path to save the final forecast as a NetCDF file.

    Returns:
    - combined (xr.Dataset): The final processed forecast dataset.
    """

    # Step 1: Average predictions across ensemble samples
    mean_predictions_1 = predictions_1.mean(dim="sample")

    # Step 2: Assign datetime coordinates to the forecast
    start_datetime = input_1["datetime"].values[0, 0] + np.timedelta64(12, 'h')
    new_times = mean_predictions_1.coords['time'].values
    datetime_values = [
        start_datetime + np.timedelta64(int(t / np.timedelta64(1, 'h')), 'h')
        for t in new_times
    ]
    mean_predictions_1 = mean_predictions_1.assign_coords(datetime=("time", datetime_values))

    # Step 3: Interpolate the target date to 1-hour intervals
    mean_predictions_target = mean_predictions_1.isel(time=slice(-7, -4))
    interpolate_predictions_1 = mean_predictions_target.resample(time='1H').interpolate('linear')

    # Recalculate datetime coordinates for interpolated predictions
    new_times = interpolate_predictions_1.coords['time'].values
    datetime_values = [
        start_datetime + np.timedelta64(int(t / np.timedelta64(1, 'h')), 'h')
        for t in new_times
    ]
    interpolate_predictions_1 = interpolate_predictions_1.assign_coords(datetime=("time", datetime_values))

    # Step 4: Extend forecast to 3 days
    last2days = mean_predictions_1.isel(time=slice(-4, None))
    combined = xr.concat([interpolate_predictions_1, last2days], dim='time')

    return combined

def gencast_predict(input_data, model):
    
    STATS_DIR = "./stats"
   

    # initialize the model
    
    ckpt = model 

    denoiser_architecture_config = ckpt.denoiser_architecture_config
    denoiser_architecture_config.sparse_transformer_config.attention_type = "triblockdiag_mha"
    denoiser_architecture_config.sparse_transformer_config.mask_type = "full"
    
    params = ckpt.params
    state = {}
    
    task_config = ckpt.task_config
    sampler_config = ckpt.sampler_config
    noise_config = ckpt.noise_config
    noise_encoder_config = ckpt.noise_encoder_config
    denoiser_architecture_config = ckpt.denoiser_architecture_config
    print("Model description:\n", ckpt.description, "\n")
    print("Model license:\n", ckpt.license, "\n")


    # @title Extract training and eval data

    eval_inputs, eval_targets, eval_forcings = data_utils.extract_inputs_targets_forcings(
        input_data, target_lead_times=slice("12h", f"{(input_data.dims['time']-2)*12}h"), # All but 2 input frames.
        **dataclasses.asdict(task_config))

    # @title Load normalization data

    with open(STATS_DIR +"/diffs_stddev_by_level.nc", "rb") as f:
      diffs_stddev_by_level = xarray.load_dataset(f).compute()
    with open(STATS_DIR +"/mean_by_level.nc", "rb") as f:
      mean_by_level = xarray.load_dataset(f).compute()
    with open(STATS_DIR +"/stddev_by_level.nc", "rb") as f:
      stddev_by_level = xarray.load_dataset(f).compute()
    with open(STATS_DIR +"/min_by_level.nc", "rb") as f:
      min_by_level = xarray.load_dataset(f).compute()


    # @title Build jitted functions, and possibly initialize random weights


    def construct_wrapped_gencast():
      """Constructs and wraps the GenCast Predictor."""
      predictor = gencast.GenCast(
          sampler_config=sampler_config,
          task_config=task_config,
          denoiser_architecture_config=denoiser_architecture_config,
          noise_config=noise_config,
          noise_encoder_config=noise_encoder_config,
      )
    
      predictor = normalization.InputsAndResiduals(
          predictor,
          diffs_stddev_by_level=diffs_stddev_by_level,
          mean_by_level=mean_by_level,
          stddev_by_level=stddev_by_level,
      )
    
      predictor = nan_cleaning.NaNCleaner(
          predictor=predictor,
          reintroduce_nans=True,
          fill_value=min_by_level,
          var_to_clean='sea_surface_temperature',
      )
    
      return predictor
    
    
    @hk.transform_with_state
    def run_forward(inputs, targets_template, forcings):
      predictor = construct_wrapped_gencast()
      return predictor(inputs, targets_template=targets_template, forcings=forcings)
    
    
    @hk.transform_with_state
    def loss_fn(inputs, targets, forcings):
      predictor = construct_wrapped_gencast()
      loss, diagnostics = predictor.loss(inputs, targets, forcings)
      return xarray_tree.map_structure(
          lambda x: xarray_jax.unwrap_data(x.mean(), require_jax=True),
          (loss, diagnostics),
      )
    
    
    def grads_fn(params, state, inputs, targets, forcings):
      def _aux(params, state, i, t, f):
        (loss, diagnostics), next_state = loss_fn.apply(
            params, state, jax.random.PRNGKey(0), i, t, f
        )
        return loss, (diagnostics, next_state)
    
      (loss, (diagnostics, next_state)), grads = jax.value_and_grad(
          _aux, has_aux=True
      )(params, state, inputs, targets, forcings)
      return loss, diagnostics, next_state, grads
    
    
    loss_fn_jitted = jax.jit(
        lambda rng, i, t, f: loss_fn.apply(params, state, rng, i, t, f)[0]
    )
    grads_fn_jitted = jax.jit(grads_fn)
    run_forward_jitted = jax.jit(
        lambda rng, i, t, f: run_forward.apply(params, state, rng, i, t, f)[0]
    )
    # We also produce a pmapped version for running in parallel.
    run_forward_pmap = xarray_jax.pmap(run_forward_jitted, dim="sample")


    # @title Autoregressive rollout (loop in python)

    def run_autoregression(eval_inputs, eval_targets, eval_forcings):
        print("Inputs:  ", eval_inputs.dims.mapping)
        print("Targets: ", eval_targets.dims.mapping)
        print("Forcings:", eval_forcings.dims.mapping)
    
        num_ensemble_members = 8 # @param ints
        rng = jax.random.PRNGKey(0)
        # We fold-in the ensemble member, this way the first N members should always
        # match across different runs which use take the same inputs
        # regardless of total ensemble size.
        rngs = np.stack(
            [jax.random.fold_in(rng, i) for i in range(num_ensemble_members)], axis=0)
    
        chunks = []
        for chunk in rollout.chunked_prediction_generator_multiple_runs(
            # Use pmapped version to parallelise across devices.
            predictor_fn=run_forward_pmap,
            rngs=rngs,
            inputs=eval_inputs,  # eval_inputs,
            targets_template=eval_targets * np.nan,
            forcings=eval_forcings,
            num_steps_per_chunk=1,
            num_samples=num_ensemble_members,
            pmap_devices=jax.local_devices()
            ):
            chunks.append(chunk)
        predictions = xarray.combine_by_coords(chunks)
        return predictions
    
    # Run autoregression with pred_input_1
    
    print("-------autoregression 1----------------")
    predictions_1 = run_autoregression(eval_inputs, eval_targets, eval_forcings)

    final_forecast = process_predictions(predictions_1, input_data)

    return final_forecast

