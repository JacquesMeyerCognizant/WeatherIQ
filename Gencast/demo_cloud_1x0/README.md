# 🌦️ GenCast Real-Time Weather Forecasting

Welcome to the repository for real-time weather prediction using Google DeepMind's GenCast model. 
This project explores data preparation, model execution, and evaluation workflows using ERA5 data 
in the WeatherBench 2 format.

## 📦 Model & Data Availability

Due to GitHub's file size limitations, the following files are not included in this repository:

- GenCast 1x0 model file (model.npz)
- Input data (source-era5_date-2019-03-29_res-1.0_levels-13_steps-01.nc)

These files are available for download at: 

    ```bash 
    https://console.cloud.google.com/storage/browser/dm_graphcast/gencast?inv=1&invt=Ab558A&pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))
    ```

Once downloaded, please place them in the following directories:


| File Name            | Destination Folder   | Notes                         |
|----------------------|----------------------|-------------------------------|
| `GenCast 1p0deg <2019.npz`          | `model/`             | GenCast 1x0 model file        |
| `source-era5_date-2019-03-29_res-1.0_levels-13_steps-01.nc`  | `evaluation_data/`   | Input and data for evaluation     |

⚠️ This section specifically supports the GenCast 1x0 model. Ensure that both the model and data files correspond to this version.

---

## 📓 Notebook Overview

This repository includes several notebooks, each serving a specific purpose in the GenCast workflow:

| Notebook                                  | Description                                                                 |
|------------------------------------------|-----------------------------------------------------------------------------|
| `o_2G_gencast_.ipynb`                     | Launches GenCast with two autoregressive steps to reduce the 12-hour gap.  |
| `o_data_source_comparison.ipynb`         | Compares three data sources: WeatherBench2, GCP ERA5, and Copernicus CDS.  |
| `o_evalutation_code.ipynb`               | Custom evaluation code to compare predictions against reference datasets.  |
| `o_gencast_demo_cloud_vm.ipynb`          | Official DeepMind demo for basic GenCast autoregression.                   |
| `o_real_time_prediction_1G_1x0_gencast.ipynb` | Personalized pipeline for real-time prediction and interpolation. Final code used in endpoints in notebook version     |

## Environment Setup Guide for `gencast`

This guide helps you set up and manage the `gencast` Conda environment for your project.

---

### 🔄 Recreate the Environment

To rebuild the environment from scratch:

    ```bash
    # Remove existing environment (optional)
    conda env remove -n gencast

    # Create environment from YAML file
    conda env create -f environment.yml

    # Reload shell configuration (if needed)
    source ~/.bashrc

    # Activate the environment
    conda activate gencast
    ```

### 🧠 Kernel Setup for Jupyter

To make the environment available in Jupyter:

    ```bash
    # Install IPython kernel
    pip install ipykernel

    # Register the kernel
    python -m ipykernel install --user --name=gencast --display-name "Python (gencast)"

    ```
### 💾 Check Disk Space on SageMaker

To check available storage on Sagemaker:

    ```bash
    df -h
    ```







