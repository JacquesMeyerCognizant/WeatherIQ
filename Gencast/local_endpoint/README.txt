# SageMaker Jupyter Notebook and Docker Deployment Guide

## Local Environment Setup

To create or renew the local environment using `environment.yml`:

conda env remove -n gencast        # Remove existing environment (if needed)
conda env create -f environment.yml
source ~/.bashrc                   # Reload shell (if needed)
conda activate gencast

Make the environment visible in Jupyter Notebook:

pip install ipykernel
python -m ipykernel install --user --name=gencast --display-name "Python (gencast3)"

## Handling EFS Memory Issues in SageMaker

Check available storage:

df -h

Identify large directories:

du -h --max-depth=1 /home/ec2-user/SageMaker | sort -hr | head -n 20

Clear trash:

rm -rf /home/ec2-user/SageMaker/.Trash-1000/*

## Docker Workflow

### Connect to AWS ECR

aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.eu-west-2.amazonaws.com

### Build and Run Docker Container localy 

docker build -t gencast-container .
docker run -p 8080:8080 gencast-container

### Test the Endpoint localy

In a new terminal:

curl -X POST http://localhost:8080/invocations \
     -H "Content-Type: application/json" \
     -d '{"currentDate": "2019-01-01", "targetDate": "2019-01-02"}'

### Access and Copy Output

docker ps
docker exec -it <container_id> /bin/bash
cd /opt/ml/output
ls -lh
exit
docker cp <container_id>:/opt/ml/output/predictions.nc ./predictions.nc

### Clean Up Docker Resources

docker system prune -a --volumes
docker images
docker rmi -f <image_id>


