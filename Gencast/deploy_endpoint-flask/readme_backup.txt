
# ----------------Sagemaker Jupiter Notebook ---------------------

## create the local environment using environment.yml
# to renew the environement if changes needed
conda env remove -n gencast  # (if needed)
conda env create -f environment.yml
source ~/.bashrc   # if needed
conda activate gencast

## make it visible on the notebook kernel selection
pip install ipykernel
python -m ipykernel install --user --name=gencast --display-name "Python (gencast3)"


## When error linked to memory usqge on the EFS with SagemakerAI 
# espace stockage dispo  
df -h 
# to see the biggest largest : 
du -h --max-depth=1 /home/ec2-user/SageMaker | sort -hr | head -n 20
# free up the trash : 
rm -rf /home/ec2-user/SageMaker/.Trash-1000/*

# -------------- docker ----------------------

#Connect To ECR with CLI AWS :
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.eu-west-2.amazonaws.com

# create the docker image with the Dockerfile and the requirements.txt, 
docker build -t gencast-container .

docker run -p 8080:8080 gencast-container

#In a new terminal do a request : 
curl -X POST http://localhost:8080/invocations \
     -H "Content-Type: application/json" \
     -d '{"currentDate": "2019-01-01", "targetDate": "2019-01-02"}'


#To check if the result was stored, run and copy Copy the CONTAINER ID (e.g., abc123456789). :
docker ps
docker exec -it <container_id> /bin/bash

#navigate to output
cd /opt/ml/output
ls -lh

#to copy the output :
exit
docker cp <container_id>:/opt/ml/output/predictions.nc ./predictions.nc


# This will remove: All stopped containers - All unused images - All build cache and volumes
docker system prune -a --volumes

#list local images 
docker images

# force delete specific image
docker rmi -f 50ab623dc926


#---------push docker ikage to ECR with the "push_to_ecr.sh" file -----------------

#explanation in the .sh file
chmod +x push_to_ecr.sh
./push_to_ecr.sh

# go check on AWS ECR if the image was well pushed, there could be IAM secrurity problems

# Tag your local image correctly
docker tag gencast-container 193871648423.dkr.ecr.eu-west-2.amazonaws.com/gencast-container:latest

# repush the local image to ECR
docker push 193871648423.dkr.ecr.eu-west-2.amazonaws.com/gencast-container:latest

#-------- deploy with the code in create_async-endpoint.ipynb---------------

#the code will Create SageMaker model, Create async endpoint config, Create async endpoint config
pip install boto3
pip install sagemaker

#Service Quotas > AWS services > Amazon SageMaker > ml.g5.12xlarge for endpoint usage
