# SageMaker Jupyter Notebook and Docker local Deployment Guide

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


⚠️ This section specifically supports the GenCast 1x0 model. Ensure that both the model and data files correspond to this version.

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

## Docker Workflow

### Connect to AWS ECR

     ```bash
     aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.eu-west-2.amazonaws.com
     ```

### Build and Run Docker Container localy 

     ```bash
     docker build -t gencast-container .
     docker run -p 8080:8080 gencast-container
     ```

### Test the Endpoint localy

In a new terminal:

     ```bash
     curl -X POST http://localhost:8080/invocations \
          -H "Content-Type: application/json" \
          -d '{"currentDate": "2019-01-01", "targetDate": "2019-01-02"}'
     ```

### Access and Copy Output

     ```bash
     docker ps
     docker exec -it <container_id> /bin/bash
     cd /opt/ml/output
     ls -lh
     exit
     docker cp <container_id>:/opt/ml/output/predictions.nc ./predictions.nc
     ```

### Clean Up Docker Resources

     ```bash
     docker system prune -a --volumes
     docker images
     docker rmi -f <image_id>
     ```


