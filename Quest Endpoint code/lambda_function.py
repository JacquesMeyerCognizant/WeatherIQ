import os
import io
import boto3
import json
import csv
import logging

# It is good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Endpoint name from the Environment variable
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']


def lambda_handler(event, context):
  
   # Using sagemaker boto3 client.
   # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html
   sagemaker_runtime = boto3.client('sagemaker-runtime')
   
   # Reading the data payload from the test event
   data = json.loads(json.dumps(event))
   payload = data['data']
   
   # Sending the payload to the Sagemaker Endpoint using Invoke Endpoint API
   # Boto3 info: https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/sagemaker-runtime.html#SageMakerRuntime.Client.invoke_endpoint
   endpoint_response = sagemaker_runtime.invoke_endpoint(
                                             EndpointName=ENDPOINT_NAME,
                                             ContentType='text/csv',
                                             Body=payload
                                             )
   
   logger.info(endpoint_response)
   
   result = json.loads(endpoint_response['Body'].read().decode())
    
   return f"The estimated price is: {result}"
   
"""
You can use the code below to create a test event.
{
    "data": "5,0,0"
}
"""