# SageMaker Jupyter Notebook Gencast 0x25 demo

## 📦 Model & Data Availability

Due to GitHub's file size limitations, the following files are not included in this repository:

- GenCast 0x25 model file (GenCast 0x25p0deg <2019.npz)
- Input data (source-era5_date-2019-03-29_res-0.25_levels-13_steps-01.nc)

These files are available for download at: 

    ```bash 
    https://console.cloud.google.com/storage/browser/dm_graphcast/gencast?inv=1&invt=Ab558A&pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))
    ```

Once downloaded, please place them in the following directories:


| File Name            | Destination Folder   | Notes                         |
|----------------------|----------------------|-------------------------------|
| `GenCast 0x25p0deg <2019.npz`          | `demo_cloud_0x25/`             | GenCast 0x25 model file        |
| `source-era5_date-2019-03-29_res-0.25_levels-13_steps-01.nc`  | `demo_cloud_0x25/`   | Input and data for evaluation     |


⚠️ This section specifically supports the GenCast 0x25 model. Ensure that both the model and data files correspond to this version.