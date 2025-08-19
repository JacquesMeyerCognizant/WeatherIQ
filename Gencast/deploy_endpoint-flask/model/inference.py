from flask import Flask, request, jsonify, Response, make_response
from resources import gencast_predict
from loading_API_data import get_input_data

import json
import xarray as xr
import numpy as np
import os
import uuid
import boto3
from graphcast import checkpoint
from graphcast import gencast

app = Flask(__name__)

# Dummy model object
model = {"name": "dummy_model"}

# 1. Load the model
def model_fn(model_path):
    print(">>> model_fn called")
    with open(model_path, "rb") as f:
        ckpt = checkpoint.load(f, gencast.CheckPoint)
    return ckpt

# 2. Dummy input processor
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
    output_dir = os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output")
    output_path = os.path.join(output_dir, "predictions.nc")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prediction.to_netcdf(output_path)

    # Upload to S3
    s3 = boto3.client("s3")
    bucket = "gencast-async"
    key = f"async-output/predictions-{uuid.uuid4()}.nc"
    s3.upload_file(output_path, bucket, key)
    print(f">>> Uploaded prediction to s3://{bucket}/{key}")


    
@app.route("/ping", methods=["GET"])
def ping():
    return "Healthy", 200


@app.route("/invocations", methods=["POST"])
def invoke():
    try:
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

        # Step 4: Run prediction
        prediction = predict_fn(processed_input, model)

        # Step 5: Format the output and store to S3
        output_fn(prediction, request.headers.get("Accept", "application/json"))

        # Proper async inference response
        response = make_response("", 204)
        response.headers["Content-Length"] = "0"
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

