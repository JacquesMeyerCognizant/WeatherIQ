#!/bin/bash

# Set variables
REGION="eu-west-2"
ACCOUNT_ID="193871648423"
REPO_NAME="gencast-container" 
IMAGE_TAG="latest"
FULL_IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"

# Create the ECR repository (if it doesn't exist)
aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Creating ECR repository: $REPO_NAME"
  aws ecr create-repository --repository-name $REPO_NAME --region $REGION
else
  echo "ECR repository $REPO_NAME already exists."
fi

# Authenticate Docker to ECR
echo "Authenticating Docker to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Tag the image
echo "Tagging image as $FULL_IMAGE_URI"
docker tag gencast-image:latest $FULL_IMAGE_URI

# Push the image
echo "Pushing image to ECR..."
docker push $FULL_IMAGE_URI

echo "✅ Image pushed to: $FULL_IMAGE_URI"


#the script pushes the latest version of your local Docker image named gencast-image.

#  What is Amazon ECR?
# Amazon ECR (Elastic Container Registry) is a fully managed Docker container registry provided by AWS. It allows you to:

# Store, manage, and deploy Docker container images.
# Integrate directly with Amazon SageMaker, ECS, EKS, and other AWS services.
# Securely control access to your container images using IAM.
# Why You Need ECR for SageMaker
# When you build a custom Docker image (like your gencast-image), SageMaker needs to pull that image from somewhere. ECR is the AWS-native place to host it.

# So the flow looks like this:

# You build your Docker image locally (e.g., gencast-image).
# You push it to ECR (your private container registry on AWS).
# SageMaker pulls the image from ECR when deploying your model.
#  Analogy
# Think of ECR like a private GitHub for Docker images:

# You push your image to it.
# AWS services (like SageMaker) pull from it to run your code.

# to run the file: 
#chmod +x push_to_ecr.sh
#./push_to_ecr.sh
