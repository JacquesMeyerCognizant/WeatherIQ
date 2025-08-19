
FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=TRUE

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
COPY model/inference.py .
COPY model/loading_API_data.py .
COPY model/resources.py .
COPY model/stats ./stats
COPY model/GenCast_1p0deg_2019.npz /app/

# Run the script
CMD ["python", "inference.py"]


