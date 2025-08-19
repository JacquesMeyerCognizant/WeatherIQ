#3)
FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu22.04

EXPOSE 8080

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=TRUE
ENV SAGEMAKER_PROGRAM=inference.py
ENV SAGEMAKER_SUBMIT_DIRECTORY=/opt/ml/code


# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev git curl wget build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set Python aliases
RUN ln -sf /usr/bin/python3 /usr/bin/python && ln -sf /usr/bin/pip3 /usr/bin/pip

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY model/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your code and model files
COPY model/inference.py /opt/ml/code/
COPY model/loading_API_data.py /opt/ml/code/
COPY model/resources.py /opt/ml/code/
COPY model/stats /opt/ml/code/stats
COPY model/GenCast_1p0deg_2019.npz /opt/ml/model/

# Run the script
ENTRYPOINT ["python", "/opt/ml/code/inference.py"]






#FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04
# FROM 763104351884.dkr.ecr.eu-west-2.amazonaws.com/pytorch-inference:2.0.0-gpu-py310-cu118-ubuntu20.04-sagemaker

# #FROM 763104351884.dkr.ecr.eu-west-2.amazonaws.com/sagemaker-inference-toolkit:1.13-gpu-py310-cu118

# ENV DEBIAN_FRONTEND=noninteractive
# ENV PYTHONUNBUFFERED=TRUE

# # Install Python and system dependencies
# RUN apt-get update && apt-get install -y \
#     python3 python3-pip python3-dev git curl wget build-essential ca-certificates && \
#     rm -rf /var/lib/apt/lists/*


# # Upgrade pip and install SageMaker inference toolkit
# RUN pip3 install --upgrade pip && \
#     pip3 install sagemaker-inference


# WORKDIR /opt/ml/code

# # Copy requirements and install dependencies
# COPY model/requirements.txt ./requirements.txt
# RUN pip3 install -r requirements.txt

# # Copy model code and data
# COPY model/inference.py /opt/ml/code/
# COPY model/loading_API_data.py /opt/ml/code/
# COPY model/resources.py /opt/ml/code/
# COPY model/stats /opt/ml/code/stats
# COPY model/GenCast_1p0deg_2019.npz /opt/ml/model/

# # Set SageMaker environment variables
# ENV SAGEMAKER_PROGRAM=inference.py
# ENV SAGEMAKER_SUBMIT_DIRECTORY=/opt/ml/code
# ENV MODEL_FILE=/opt/ml/model/GenCast_1p0deg_2019.npz

# # Use SageMaker model server
# ENTRYPOINT ["serve"]

#---------------------------


# FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# # Set environment variables
# ENV DEBIAN_FRONTEND=noninteractive
# ENV PYTHONUNBUFFERED=TRUE
# ENV PATH=/opt/conda/bin:$PATH

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     git curl wget build-essential ca-certificates nodejs npm && \
#     rm -rf /var/lib/apt/lists/*

# # Install `serve` globally using npm
# RUN npm install -g serve

# # Install Miniconda (Python 3.10)
# RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
#     bash miniconda.sh -b -p /opt/conda && \
#     rm miniconda.sh && \
#     conda install python=3.10 -y && \
#     conda clean -afy
# RUN pip install sagemaker-inference

# # Set working directory
# WORKDIR /opt/ml/code

# # Copy requirements and install dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip && \
#     pip install -r requirements.txt && \
#     pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# # Copy model code and data
# COPY model/inference.py /opt/ml/code/
# COPY model/loading_API_data.py /opt/ml/code/
# COPY model/resources.py /opt/ml/code/
# COPY model/stats /opt/ml/code/stats
# COPY model/GenCast_1p0deg_2019.npz /opt/ml/model/

# # Set SageMaker environment variables
# ENV SAGEMAKER_PROGRAM=inference.py
# ENV SAGEMAKER_SUBMIT_DIRECTORY=/opt/ml/code
# ENV MODEL_FILE=/opt/ml/model/GenCast_1p0deg_2019.npz

# # Define the entrypoint for SageMaker and expose port 8080 for serving the image
# EXPOSE 8080
# ENTRYPOINT ["serve", "-s", "/opt/ml/code", "-l", "8080"]

# RUN echo "✅ Custom CUDA 12 Docker image with Python 3.10 ready for SageMaker inference and static content serving"

# # -----------------------------------------------------


# # # # Image officielle SageMaker PyTorch avec GPU, Python 3.10, CUDA 11.8
# # FROM 763104351884.dkr.ecr.eu-west-2.amazonaws.com/pytorch-inference:2.0.0-gpu-py310-cu118-ubuntu20.04-sagemaker

# # # Répertoire de travail
# # WORKDIR /opt/ml/code

# # # Copie des dépendances
# # COPY requirements.txt .

# # # Installation des dépendances Python
# # RUN pip install --upgrade pip && \
# #     pip install -r requirements.txt

# # # Copie du code source
# # COPY model/inference.py /opt/ml/code/
# # COPY model/loading_API_data.py /opt/ml/code/
# # COPY model/resources.py /opt/ml/code/
# # COPY model/stats /opt/ml/code/stats
# # COPY model/GenCast_1p0deg_2019.npz /opt/ml/model/

# # # Définir le script d'inférence
# # ENV SAGEMAKER_MODEL_SERVER_TIMEOUT=3600
# # ENV SAGEMAKER_SUBMIT_DIRECTORY=/opt/ml/code
# # ENV SAGEMAKER_PROGRAM=model/inference.py
# # ENV MODEL_FILE=model/GenCast_1p0deg_2019.npz


# # # Le point d'entrée est déjà configuré dans l'image officielle avec `serve`


# # RUN echo "✅ Docker image ready for SageMaker inference"



