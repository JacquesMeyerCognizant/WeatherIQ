import xarray as xr
import numpy as np
import pandas as pd
import json
 
def data_cleaning (ds1) : 
    
    # Keep only the required variables
    required_vars = [
        '10m_u_component_of_wind',
        '10m_v_component_of_wind',
        '2m_temperature',
        'total_precipitation_12hr'
    ]
    ds1 = ds1[required_vars]
    
    # Convert 'total_precipitation_12hr' from meters to millimeters
    if 'total_precipitation_12hr' in ds1:
        ds1['total_precipitation_12hr'] = ds1['total_precipitation_12hr'] * 1000
        ds1['total_precipitation_12hr'].attrs['units'] = 'mm'
        ds1['total_precipitation_12hr'] = ds1['total_precipitation_12hr'].where(ds1['total_precipitation_12hr'] >= 0, 0)
    
    # Convert temperature from Kelvin to Celsius and round to nearest 0.5
    if '2m_temperature' in ds1:
        ds1['2m_temperature'] = ds1['2m_temperature'] - 273.15
        ds1['2m_temperature'] = np.round(ds1['2m_temperature'] * 2) / 2
        ds1['2m_temperature'].attrs['units'] = 'C'
    
    # Calculate wind speed and direction
    if '10m_u_component_of_wind' in ds1 and '10m_v_component_of_wind' in ds1:
        u = ds1['10m_u_component_of_wind']
        v = ds1['10m_v_component_of_wind']
        wind_speed = np.sqrt(u**2 + v**2)
        wind_direction = (np.arctan2(u, v) * 180 / np.pi) % 360
    
        ds1['10m_wind_speed'] = wind_speed
        ds1['10m_wind_speed'].attrs['units'] = 'm/s'
        ds1['10m_wind_speed'].attrs['description'] = 'Wind speed at 10 meters'
    
        ds1['10m_wind_direction'] = wind_direction
        ds1['10m_wind_direction'].attrs['units'] = 'degrees'
        ds1['10m_wind_direction'].attrs['description'] = 'Wind direction at 10 meters (0° = North, increasing clockwise)'
    
    # Add wind direction as cardinal directions
    if '10m_wind_direction' in ds1:
        angle = (ds1['10m_wind_direction'] + 180) % 360  # Convert TO direction to FROM direction
        directions = np.array(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
        idx = np.round(angle / 45).astype(int) % 8
        cardinal = xr.apply_ufunc(lambda i: directions[i], idx, vectorize=True, dask='allowed', output_dtypes=[str])
        ds1['10m_wind_cardinal'] = cardinal
        ds1['10m_wind_cardinal'].attrs['description'] = 'Cardinal wind direction (from) at 10 meters'
    
    # Load power curve data
    power_curve_df = pd.read_csv("code/power_curve_full_data.csv")
    power_curve_df.columns = power_curve_df.columns.str.strip()
    
    wind_speeds = power_curve_df["Wind Speed (m/s)"].values
    power_output = power_curve_df["Power Output (kW)"].values
    performance = power_curve_df["performance (%)"].values
    
    # Interpolate power output and performance based on wind speed
    interp_power_output = np.interp(ds1['10m_wind_speed'], wind_speeds, power_output)
    interp_performance = np.interp(ds1['10m_wind_speed'], wind_speeds, performance)
    
    # Add interpolated variables to dataset
    ds1['10m_power_output_kw'] = (ds1['10m_wind_speed'].dims, interp_power_output)
    ds1['10m_power_output_kw'].attrs['units'] = 'kW'
    
    ds1['10m_power_performance'] = (ds1['10m_wind_speed'].dims, interp_performance)
    ds1['10m_power_performance'].attrs['units'] = '%'
    ds1['10m_power_performance'] = ds1['10m_power_performance']*100
    return ds1


#create 4 subdatasets, one for eacgh day + one hourly interpolated fro day1
def daily_sub_dataset_creation(ds1):
    day2 = ds1.isel(time=slice(-5, -2))
    day3 = ds1.isel(time=slice(-3,None))
    ds1 = ds1.isel(time=slice(None, -4)) # only select the values for the target date (day1)
    day1 = ds1.isel(time=slice(-25, None)).isel(time=[0, 12, 24])
    return day1, day2, day3, ds1



def save_video_files_paths_in_json():

    with open('weather_text_to_audio.json', 'r') as f:
        json_data = json.load(f)
    
    # Update the existing dictionary
    json_data["3_days_prediction"]["video_path"] = "video/tab_video/videos/1920p30/3_days_prediction.mp4"
    json_data["3_days_energy_prediction"]["video_path"] = "images/power_output.png"
    json_data["intro"]["video_path"] = "video/intro_outro.mp4"
    json_data["outro"]["video_path"] = "video/intro_outro.mp4"
    
    # Save it back
    with open('weather_text_to_audio.json', 'w') as f:
        json.dump(json_data, f, indent=4)


