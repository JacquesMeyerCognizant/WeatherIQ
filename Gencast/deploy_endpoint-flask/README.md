# SageMaker Jupyter Notebook and Docker Deployment Guide

## 📦 Model & Data Availability

Due to GitHub's file size limitations, the following files are not included in this repository:

- GenCast 1x0 model file (GenCast 1p0deg <2019.npz)

These files are available for download at: 

    ```bash 
    https://console.cloud.google.com/storage/browser/dm_graphcast/gencast?inv=1&invt=Ab558A&pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))
    ```

Once downloaded, please place them in the following directories:


| File Name            | Destination Folder   | Notes                         |
|----------------------|----------------------|-------------------------------|
| `GenCast 1p0deg <2019.npz`          | `model/`             | GenCast 1x0 model file        |


## Local Environment Setup

To create or renew the local environment using `environment.yml`:

    ```bash
    conda env remove -n gencast        # Remove existing environment (if needed)
    conda env create -f environment.yml
    source ~/.bashrc                   # Reload shell (if needed)
    conda activate gencast
    ```

Make the environment visible in Jupyter Notebook:

    ```bash
    pip install ipykernel
    python -m ipykernel install --user --name=gencast --display-name "Python (gencast3)"
    ```

## Handling EFS Memory Issues in SageMaker

Check available storage:

    ```bash
    df -h
    ```

Identify large directories:

    ```bash
    du -h --max-depth=1 /home/ec2-user/SageMaker | sort -hr | head -n 20
    ```

Clear trash:

    ```bash
    rm -rf /home/ec2-user/SageMaker/.Trash-1000/*
    ```

---

## Docker Workflow

### Connect to AWS ECR

    ```bash
    aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.eu-west-2.amazonaws.com
    ```

### Build  Docker Container

    ```bash
    docker build -t gencast-container .
    ```

### Clean Up Docker Resources

    ```bash
    docker system prune -a --volumes
    docker images
    docker rmi -f <image_id>
    ```

---

## Push Docker Image to ECR

Make the script executable and run it:

    ```bash
    chmod +x push_to_ecr.sh
    ./push_to_ecr.sh
    ```

Tag and push manually if needed:

    ```bash
    docker tag gencast-container 193871648423.dkr.ecr.eu-west-2.amazonaws.com/gencast-container:latest
    docker push 193871648423.dkr.ecr.eu-west-2.amazonaws.com/gencast-container:latest
    ```

---

## SageMaker Async Endpoint Deployment

Use `create_async-endpoint.ipynb` to:

- Create SageMaker model
- Create async endpoint configuration
- Deploy async endpoint

Install required packages:

    ```bash
    !pip install boto3
    !pip install sagemaker
    ```

Check service quotas for `ml.g5.12xlarge` usage under:
Service Quotas > AWS Services > Amazon SageMaker
