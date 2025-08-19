
# GenCast Research & Deployment

This repository contains research, demo code, and deployment scripts related to DeepMind's GenCast weather forecasting model. It includes tools to run the model locally and on AWS SageMaker.

🔗 Official GenCast GitHub Repository: google-deepmind/graphcast

---

## Repository Structure

This folder is organized into four main components:

### 1. demo_cloud_0x25 :
- Contains the official demo code provided by DeepMind to launch the GenCast 0x25 model.
- Useful for understanding the baseline functionality and setup of the model.
### 2. demo_cloud_1x0 : 
- Includes research and experimentation with the GenCast 1x0 model.
- Features notebooks covering:
    - Data input formatting
    - Performance evaluation
    - Functional demonstrations
### 3. deploy_endpoint_flask : 
- Contains the finalized model code in Python script format.
- Includes deployment scripts to host the model on an AWS SageMaker endpoint using Flask.
- Designed for scalable cloud deployment.
### 4. local_endpoint : 
- Contains the same finalized model code as above, adapted for local deployment.
- Includes scripts to launch the model in a containerized local endpoint environment.

---

## Additional Notes : 

Each subfolder includes its own README file with specific instructions on how to launch and use the respective components.