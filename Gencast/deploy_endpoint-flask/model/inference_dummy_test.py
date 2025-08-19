from flask import Flask, request, jsonify, Response, make_response
import json
import xarray as xr
import numpy as np
import os
import uuid
import boto3


app = Flask(__name__)

# Dummy model object
model = {"name": "dummy_model"}

#@app.before_first_request
def load_model():
    global model
    print(">>> Dummy model loaded.")

# 1. Dummy model loader
def model_fn(model_path):
    print(">>> model_fn called")
    return {"name": "dummy_model"}

# 2. Dummy input processor
def input_fn(input_data, content_type):
    print(">>> input_fn called")
    
    if content_type == "application/json":
        data = json.loads(input_data)
    elif content_type in ["application/octet-stream", "binary/octet-stream"]:
        # input_data is already decoded before being passed here
        data = json.loads(input_data)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")
    
    currentDate = data.get("currentDate", "unknown")
    targetDate = data.get("targetDate", "unknown")
    return {"currentDate": currentDate, "targetDate": targetDate}


# 3. Dummy prediction
def predict_fn(input_data, model):
    print(">>> predict_fn called")
    # Return a dummy xarray.Dataset
    dummy_data = xr.Dataset({
        "temperature": (("lat", "lon"), np.random.rand(2, 2)),
        "humidity": (("lat", "lon"), np.random.rand(2, 2))
    }, coords={"lat": [0, 1], "lon": [0, 1]})
    return dummy_data

# 4. Dummy output writer
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
        load_model()
        input_data = request.data
        if isinstance(input_data, bytes):
            input_data = input_data.decode("utf-8")

        model_input = input_fn(input_data, request.content_type)
        prediction = predict_fn(model_input, model)
        output_fn(prediction, request.headers.get("Accept", "application/json"))

        # Proper async inference response
        response = make_response("", 204)
        response.headers["Content-Length"] = "0"
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

