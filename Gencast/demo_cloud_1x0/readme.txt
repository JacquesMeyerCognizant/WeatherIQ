🌦️ GenCast Real-Time Weather Forecasting
========================================

Welcome to the repository for real-time weather prediction using Google DeepMind's GenCast model. 
This project explores data preparation, model execution, and evaluation workflows using ERA5 data 
in the WeatherBench 2 format.


## Environment Setup Guide for `gencast`

This guide helps you set up and manage the `gencast` Conda environment for your project.

- Renewing the Environment (if needed)

If you need to recreate the environment from scratch:

    '''
    # Remove existing environment (optional)
    conda env remove -n gencast

    # Create environment from YAML file
    conda env create -f environment.yml

    # Reload shell configuration (if needed)
    source ~/.bashrc

    # Activate the environment
    conda activate gencast
    '''

- Kernel Setup for Jupyter

To make the environment available in Jupyter:
    '''
    # Install IPython kernel
    pip install ipykernel

    # Register the kernel
    python -m ipykernel install --user --name=gencast --display-name "Python (gencast)"
    ''' 
- Check Disk Space on Sagemaker

To check available storage on Sagemaker:
    '''
    df -h
    '''


📓 Notebook Overview
--------------------

This repository includes several notebooks, each serving a specific purpose in the GenCast workflow:

| Notebook                             | Description                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------|
| o_2G_gencast_.ipynb                 | Launches GenCast with two autoregressive steps to reduce the 12-hour gap.  |
| o_data_source_comparison.ipynb     | Compares three data sources: WeatherBench2, GCP ERA5, and Copernicus CDS.  |
| o_evalutation_code.ipynb           | Custom evaluation code to compare predictions against reference datasets.  |
| o_gencast_demo_cloud_vm.ipynb      | Official DeepMind demo for basic GenCast autoregression.                   |
| o_real_time_prediction_1G_1x0_gencast.ipynb | Personalized pipeline for real-time prediction and interpolation.     |


