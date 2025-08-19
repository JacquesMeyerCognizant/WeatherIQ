import os
import cdsapi
import xarray as xr
import numpy as np
import zipfile
import glob

from datetime import datetime, timedelta

import xarray as xr
import numpy as np
import pandas as pd
import gcsfs

def extract_arco_era5_data(user_current_date: str, user_target_date: str):
    """
    Extracts ERA5 weather data from the ARCO public dataset on GCP for a given date range.
    Applies lag logic to ensure compatibility with ERA5T data availability and prepares
    the dataset for forecasting.

    Parameters:
    - user_current_date (str): The starting date for prediction (format: 'YYYY-MM-DD').
    - user_target_date (str): The target date to predict towards (format: 'YYYY-MM-DD').

    Returns:
    - ds_1deg (xr.Dataset): Downsampled dataset with selected variables and coordinates.
    - nb_of_steps_to_perform (int): Number of prediction steps required.
    """

    # Load the ARCO ERA5 dataset from GCP (Zarr format)
    ds = xr.open_zarr(
        'gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3',
        chunks=None,
        storage_options=dict(token='anon')
    )

    # Get the latest available time from dataset metadata
    latest_time_str = ds.attrs.get('valid_time_stop_era5t', ds.attrs.get('valid_time_stop'))
    latest_time = datetime.strptime(latest_time_str, "%Y-%m-%d")
    today = datetime.today()

    # Convert user input dates to datetime objects
    user_current_date_obj = datetime.strptime(user_current_date, '%Y-%m-%d')
    user_target_date_obj = datetime.strptime(user_target_date, '%Y-%m-%d')

    # Apply lag logic: if the current date is within the last 6 days, shift it back
    days_ago = (today - user_current_date_obj).days
    if 0 <= days_ago <= 6:
        lag = 6 - days_ago
        effective_current_date_obj = user_current_date_obj - timedelta(days=lag)
    else:
        effective_current_date_obj = user_current_date_obj

    # Calculate the number of days to predict
    days_prediction_length = (user_target_date_obj - effective_current_date_obj).days
    print(f"The number of days to predict to get to target date is {days_prediction_length} (+2 for 72hrs pred)")

    # Limit prediction range to 13 days to allow for 72-hour forecasts
    if days_prediction_length > 13:
        raise ValueError("Target date exceeds the 13-day prediction limit.")

    # Calculate the number of prediction steps (every 12 hours + extra for 72h forecast)
    nb_of_steps_to_perform = (days_prediction_length * 2) + 1 + 4

    # Generate time steps every 12 hours starting from effective current date
    requested_times = pd.date_range(start=effective_current_date_obj, periods=2, freq='12h')

    # Filter dataset to valid time range
    ds = ds.sel(time=slice(ds.attrs['valid_time_start'], latest_time_str))
    available_times = pd.to_datetime(ds.time.values)
    valid_times = [t for t in requested_times if t in available_times]

    # Rename latitude and longitude dimensions for consistency
    ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})

    # Select pressure levels relevant for forecasting
    levels = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]
    ds = ds.sel(level=levels)

    # Select relevant meteorological variables
    variables = [
        'land_sea_mask', 'geopotential_at_surface',
        '2m_temperature', 'sea_surface_temperature', 'mean_sea_level_pressure',
        '10m_v_component_of_wind', '10m_u_component_of_wind',
        'u_component_of_wind', 'specific_humidity', 'temperature',
        'vertical_velocity', 'v_component_of_wind', 'geopotential'
    ]
    ds = ds[variables]

    # Select only the valid time steps
    ds = ds.sel(time=valid_times)

    # Add a batch dimension for model compatibility
    ds = ds.expand_dims('batch')

    # Assign datetime and time coordinates
    datetime_coord = np.array(valid_times, dtype='datetime64[ns]').reshape(1, -1)
    time_coord = (pd.to_datetime(valid_times) - pd.to_datetime(valid_times[0])).to_numpy().astype('timedelta64[ns]')
    ds = ds.assign_coords({
        'time': time_coord,
        'datetime': (('batch', 'time'), datetime_coord)
    })

    # Compute the dataset (load into memory) and downsample to 1-degree resolution
    ds = ds.compute()
    ds_1deg = ds.isel(lat=slice(None, None, 4), lon=slice(None, None, 4))
    ds_1deg = ds_1deg.sortby('lat')

    return ds_1deg, nb_of_steps_to_perform



def drop_time_dimensions_for_static_variables(input_1):
    """
    Removes the 'datetime' dimension from static variables in the dataset
    to prepare them for merging with dynamic variables.
    
    Parameters:
    input_1 (xr.Dataset): The input dataset containing both static and dynamic variables.
    
    Returns:
    xr.Dataset: A dataset with static variables reduced and merged with dynamic variables.
    """
    
    # List of variables considered static (do not change over time)
    static_vars = ['land_sea_mask', 'geopotential_at_surface']
    
    # Reduce static variables by selecting the first batch and time slice,
    # then drop the 'datetime' dimension to make them truly static
    ds_static_reduced = xr.Dataset({
        var: input_1[var].isel(batch=0, time=0).squeeze().drop_vars('datetime')
        for var in static_vars
    })
    
    # Identify dynamic variables (all variables not in static_vars)
    dynamic_vars = [var for var in input_1.data_vars if var not in static_vars]
    ds_dynamic = input_1[dynamic_vars]
    
    # Merge static and dynamic datasets into a single dataset
    input_1 = xr.merge([ds_static_reduced, ds_dynamic])
    
    return input_1


def add_empty_total_precipitation_variable(input_1):
    """
    Adds an empty 'total_precipitation_12hr' variable to the dataset.
    This is required for structural consistency, even though the model
    does not use this variable and it is not present in the source data.

    Parameters:
    - input_1 (xr.Dataset): The input dataset to which the variable will be added.

    Returns:
    - xr.Dataset: The updated dataset with the new NaN-filled variable.
    """

    # Create a DataArray filled with NaNs, matching the shape of surface-level variables
    nan_precip = xr.DataArray(
        np.full(
            shape=(input_1.sizes['batch'], input_1.sizes['time'],
                   input_1.sizes['lat'], input_1.sizes['lon']),
            fill_value=np.nan
        ),
        dims=('batch', 'time', 'lat', 'lon'),
        coords={
            'batch': input_1.batch,
            'time': input_1.time,
            'lat': input_1.lat,
            'lon': input_1.lon
        },
        name='total_precipitation_12hr'
    )

    # Add the NaN-filled variable to the dataset
    input_1['total_precipitation_12hr'] = nan_precip
    return input_1

def create_target_data(input_1,nb_of_steps_to_perform):
    """
    Creates an empty target dataset, aligned with the model's expected output structure.
    The targets are filled with NaNs and span the forecast horizon defined by `nb_of_steps_to_perform`.

    Parameters:
    - input_1 (xr.Dataset): The input dataset used to infer shape and coordinate structure.

    Returns:
    - eval_targets_test (xr.Dataset): A dataset with NaN-filled forecast targets and proper time/datetime coordinates.
    """

    # Step size in nanoseconds (12 hours)
    step_ns = 43_200_000_000_000

    # Generate time offsets for each prediction step
    target_times = np.arange(step_ns, step_ns * (nb_of_steps_to_perform + 1), step_ns)
    target_time_coords = pd.to_timedelta(target_times, unit='ns')

    # Extract the last datetime from the input dataset
    last_datetime = np.array(input_1.coords["datetime"].values).flatten()[1]

    # Define the step size as a pandas Timedelta
    step = pd.to_timedelta(step_ns, unit='ns')

    # Generate datetime coordinates for each prediction step
    target_datetime_coords = pd.date_range(
        start=last_datetime + step,
        periods=nb_of_steps_to_perform,
        freq=step
    )

    # Use the last time step of input_1 as a template for shape and variables
    template = input_1.isel(time=-1).drop_vars("time")

    # Create a list of NaN-filled copies of the template, one for each target time
    eval_targets_test = xr.concat(
        [template.expand_dims(time=[t]) * np.nan for t in target_time_coords],
        dim="time"
    )

    # Assign the generated time and datetime coordinates
    eval_targets_test = eval_targets_test.assign_coords({
        "time": target_time_coords,
        "datetime": ("time", target_datetime_coords)
    })

    return eval_targets_test

def combine_input_and_target(eval_targets_test, input_1):
    """
    Combines the input dataset and the empty target dataset into a single dataset.
    Static variables are preserved, while dynamic variables are concatenated along the time dimension.

    Parameters:
    - eval_targets_test (xr.Dataset): The empty target dataset with future time steps.
    - input_1 (xr.Dataset): The input dataset with past time steps.

    Returns:
    - combined (xr.Dataset): A unified dataset containing both input and target data.
    """

    # Define static variables that do not change over time
    static_vars = ['land_sea_mask', 'geopotential_at_surface']

    # Remove static variables from both datasets before concatenation
    input_1_dynamic = input_1.drop_vars(static_vars)
    eval_targets_test_dynamic = eval_targets_test.drop_vars(static_vars)

    # Concatenate dynamic variables along the time axis
    combined_dynamic = xr.concat([input_1_dynamic, eval_targets_test_dynamic], dim='time')

    # Extract static variables from the input dataset (assumed identical across datasets)
    static_data = input_1[static_vars]

    # Merge static and dynamic variables into a single dataset
    combined = xr.merge([static_data, combined_dynamic])

    # Sort the dataset by latitude for consistency
    combined = combined.sortby('lat')

    return combined

def get_input_data(current_date, target_date ):

    # fetch data from the GCP Bucket for the selected dates
    input_1, nb_of_steps_to_perform = extract_arco_era5_data(current_date, target_date)

    # setting the last time value from the input as the starting time 0
    input_1 = input_1.assign_coords(time=input_1.time - input_1.time[-1])

    # drop time dimentions for static variables
    input_1 = drop_time_dimensions_for_static_variables(input_1)

    # the bucket data does not contain variable 'total_precipitation_12hr',
    # the model does not use this varaible as input, but the data structure still requires it, creating ane emtpy variables 
    input_1 = add_empty_total_precipitation_variable(input_1)

    # creating empty target dataset
    eval_targets_test = create_target_data(input_1, nb_of_steps_to_perform)

    # combining empty target dataset and input data to get the final replicated dataset to give to the model
    combined = combine_input_and_target(eval_targets_test, input_1)

    return combined





















