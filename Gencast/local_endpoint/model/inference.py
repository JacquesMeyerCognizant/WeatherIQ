

from resources import gencast_predict
from loading_API_data import get_input_data

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

# JAX-related
import jax
import haiku as hk

# GraphCast modules
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

import os
import joblib
import json

# 1. Load the model
def model_fn(model_path):
    print(">>> model_fn called")
    with open(model_path, "rb") as f:
        ckpt = checkpoint.load(f, gencast.CheckPoint)
    return ckpt

 

# 2. Process the input
def input_fn(input_data, content_type):
    print(">>> input_fn called")
    if content_type == "application/json":
        data = json.loads(input_data)
        currentDate = data["currentDate"]
        targetDate = data["targetDate"]
        model_input_data = get_input_data(currentDate, targetDate)
        return model_input_data
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

# 3. Run prediction
def predict_fn(input_data, model):
    print(">>> predict_fn called")
    prediction = gencast_predict(input_data, model)
    return prediction


# 4. Format the output
def output_fn(prediction, accept):
    print(">>> output_fn called")
    # Ensure prediction is an xarray.Dataset
    if not isinstance(prediction, xr.Dataset):
        prediction = xr.Dataset(prediction)

    output_path = "/opt/ml/output/predictions.nc"
    prediction.to_netcdf(output_path)
    return None 

def main():
    # Simulate SageMaker environment
    MODEL_PATH = "./GenCast_1p0deg_2019.npz"  # Update this path if needed

    # Step 1: Load the model
    model = model_fn(MODEL_PATH)

    # Step 2: Create a sample input
    sample_input = {
        "currentDate": "2019-03-29",
        "targetDate": "2019-04-01"
    }
    input_data_json = json.dumps(sample_input)

    # Step 3: Process the input
    processed_input = input_fn(input_data_json, content_type="application/json")
    processed_input

    # Step 4: Run prediction
    prediction = predict_fn(processed_input, model)

    print(prediction)

    # Step 5: Format the output
    # output, content_type = output_fn(prediction, accept="application/json")

    # # Print the result
    # print("Prediction Output:")
    # print(output)

if __name__ == "__main__":
    main()








