import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from moviepy import VideoFileClip, concatenate_videoclips
import cartopy.crs as ccrs
import pandas as pd
import cartopy.feature as cf
import numpy as np
import json

class Video_map:
    def __init__(self,ds1, selected_windFarm ):
        self.ds1 = ds1
        self.selected_windFarm = selected_windFarm
        self.variable_info = {
            "2m_temperature": {
                "name_en": "Temperature",
                "meaning": "Near-surface air temperature"
            },
            "10m_wind_speed": {
                "name_en": "Wind",
                "meaning": "Zonal wind speed"
            },
            "total_precipitation_12hr": {
                "name_en": "Rain",
                "meaning": "Total precipitation in last 12hr"
            },
            "10m_power_performance": {
                "name_en": "Performance",
                "meaning": "Total precipitation in last 12hr"
            }
        }

    def preprocess_dataset(self, ds):
        ds = ds.assign_coords(lon=(((ds.lon + 180) % 360) - 180))
        ds = ds.sortby('lon')
        lon_range = (-13, 5)
        lat_range = (47, 62)
        ds1 = ds.sel(
            lon=ds.lon.where((ds.lon >= lon_range[0]) & (ds.lon <= lon_range[1]), drop=True),
            lat=ds.lat.where((ds.lat >= lat_range[0]) & (ds.lat <= lat_range[1]), drop=True)
        )
        return ds1

    def create_animation(self, variable, time_range, save_path, segment_duration):
        with open("./agent_json_data/windfarm.json", "r") as f:
            windfarm_location = json.load(f)
        # Find the windfarm by name
        selected_data = next((wf for wf in windfarm_location if wf["name"] == self.selected_windFarm), None)
        windfarm_name = selected_data["name"]
        location = selected_data["location"]
        
        data = self.ds1[variable]
        info = self.variable_info.get(variable, {})
        name_en = info.get("name_en", variable)
        meaning = info.get("meaning", "")
        value_range = info.get("range", "")
    
        # Mean over batch/sample if needed
        if "sample" in data.dims:
            data = data.mean(dim="sample")
        if "batch" in data.dims:
            data = data.isel(batch=0)
    
        # Determine units
        if variable == "2m_temperature":
            data_units = "°C"
        elif variable == "10m_wind_speed":
            data_units = "m/s"
        elif variable == "total_precipitation_12hr":
            data_units = "mm"
        elif variable == "10m_power_performance":
            data_units = "% \n Wind Farm Performance Rate"
        else:
            data_units = data.attrs.get("units", "")
    
        # Recenter longitude
        data = self.preprocess_dataset(data)
        data = data.sel(time=data['time'][data['datetime'].dt.hour.isin(time_range)])
    
        if len(data['time']) == 0:
            print(f"No data available for {variable} from {time_range[0]} to {time_range[-1]}. Skipping this segment.")
            return None
    
        projection = ccrs.LambertConformal(central_longitude=-2, central_latitude=54)
        fig, ax = plt.subplots(figsize=(10.8, 19.2), subplot_kw={'projection': ccrs.Mercator()})
    
        final_extent = [-11, 4, 49, 61]
        #ax.set_extent(final_extent, crs=ccrs.PlateCarree())
        ax.coastlines(resolution='50m', linewidth=0.5)
        ax.add_feature(cf.BORDERS.with_scale('50m'), linewidth=0.3)
        gl= ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=.6, color='gray', alpha=0.5, linestyle='-.')   
        gl.top_labels = False
        gl.bottom_labels = False
        gl.left_labels = False
        gl.right_labels = False
    
    
        if variable == "total_precipitation_12hr":
            colors = [(1, 1, 1, 1), (0, 0, 1, 1)]
            cmap = LinearSegmentedColormap.from_list("white_to_blue", colors, N=256)
        elif variable == "10m_wind_speed":
            colors = [(1, 1, 1, 1), (1, 0, 0)]  # Blue → Yellow → Red
            cmap = LinearSegmentedColormap.from_list("wind_gradient", colors, N=256)
        else:
            cmap = "coolwarm"
    
        vmin = np.percentile(data.values, 5)
        vmax = np.percentile(data.values, 95)
        
        first_frame = data.sel(time=data['time'][0]).values.squeeze()
        contourf = ax.contourf(
            data.lon,
            data.lat,
            first_frame,
            cmap=cmap,
            levels=5,
            vmin=vmin,
            vmax=vmax,
            transform=ccrs.PlateCarree()
        )
    
        # wind farm marker
        # Wind farm marker with wind info from dataset
        ax.plot(location['lon'], location['lat'], marker='o', color='black', markersize=8, transform=ccrs.PlateCarree())
        if variable != "10m_wind_speed" :
            ax.text(location['lon'] -0.4, location['lat']-1, windfarm_name, fontsize=25, transform=ccrs.PlateCarree())
        
        #colorbar
        cbar = plt.colorbar(contourf, ax=ax, orientation='horizontal', pad=0.05, fraction=0.05, aspect=80)
        cbar.set_label(f"{data_units}", fontsize=30)
        cbar.ax.tick_params(labelsize=20)
        title = ax.set_title("", fontsize=30)
        
        
        quiv_container = {"quiv": None}
        # Add wind arrows if the variable is wind component
        if variable == "10m_wind_speed":
            data_v = self.ds1["10m_v_component_of_wind"]
            data_u =  self.ds1["10m_u_component_of_wind"]
        
            data_v = data_v.sel(time=data['time'][data['datetime'].dt.hour.isin(time_range)])
            data_u = data_u.sel(time=data['time'][data['datetime'].dt.hour.isin(time_range)])
        
            first_frame_u = data_u.sel(time=data['time'][0]).values.squeeze()
            first_frame_v = data_v.sel(time=data_v['time'][0]).values.squeeze()
        
            quiv_container["quiv"] = ax.quiver(
                data.lon[::3], data.lat[::3],
                first_frame_u[::3, ::3],
                first_frame_v[::3, ::3],
                transform=ccrs.PlateCarree(), scale=400
            )
        contour_sets = {"contourf": None, "contour": None, "quiv": None}
        # Create a placeholder for dynamic wind label
        wind_label_text = None
        if variable == "10m_wind_speed":
            wind_label_text = ax.text(
                location['lon'] - 0.4, location['lat'] -2, "", fontsize=25, transform=ccrs.PlateCarree()
            )
    
        # Set title and date 
        ax.text(0.5, 1.05, name_en, transform=ax.transAxes,
                ha='center', va='bottom', fontsize=50, fontweight='bold')
        
        # Get nearest grid point once
        lon_idx = np.abs( self.ds1.lon - location['lon']).argmin().item()
        lat_idx = np.abs( self.ds1.lat - location['lat']).argmin().item()
    
        
        # Animate each datetime frame
        def animate(i):
            frame_data = data.sel(time=data['time'][i]).values.squeeze()
    
            #img.set_array(frame_data.ravel())
            # Remove previous contour sets
            if contour_sets["contourf"]:
                contour_sets["contourf"].remove()
            if contour_sets["contour"]:
                contour_sets["contour"].remove()
        
            # Create new contour sets
            contour_sets["contourf"] = ax.contourf(
                data.lon,
                data.lat,
                frame_data,
                cmap=cmap,
                levels=5,
                vmin=vmin,
                vmax=vmax,
                transform=ccrs.PlateCarree()
            )
    
            timestamp = pd.to_datetime(data['datetime'].values[i]).round('h')
            formatted_time = timestamp.strftime('%Y-%m-%d %H:%M')
                
            date_part, hour_part = formatted_time.split(" ")
            ax.set_title(f"{date_part} " + r"$\bf{" + hour_part + r"}$", fontsize=30) 
                
    
    
            # Update wind label dynamically
            if variable == "10m_wind_speed" and wind_label_text is not None:
                wind_speed =  self.ds1['10m_wind_speed'].sel(
                    time=data['time'].values[i],
                    lon= self.ds1.lon[lon_idx],
                    lat= self.ds1.lat[lat_idx],
                    method="nearest"
                ).values.item()
                
                wind_dir =  self.ds1['10m_wind_cardinal'].sel(
                    time=data['time'].values[i],
                    lon= self.ds1.lon[lon_idx],
                    lat= self.ds1.lat[lat_idx],
                    method="nearest"
                ).values.item()
    
                wind_label_text.set_text(f"{windfarm_name}\n{wind_speed:.1f} m/s \n{wind_dir}")
                wind_label_text.set_fontsize(25)  # Set the font size to 12 (or any other value)
    
    
                #print(f"it is time : {i} and wind is {wind_speed}")
            
                    
            # animate the arrows
            if variable == "10m_wind_speed" and quiv_container["quiv"] is not None:
                frame_data_u = data_u.sel(time=data['time'][i]).values.squeeze()
                frame_data_v = data_v.sel(time=data_v['time'][i]).values.squeeze()
                quiv_container["quiv"] = ax.quiver(
                    data.lon[::3], data.lat[::3],
                    frame_data_u[::3, ::3],
                    frame_data_v[::3, ::3],
                    transform=ccrs.PlateCarree(), scale=300, regrid_shape=20, alpha=0.3
                )
    
            # Return updated artists
            artists = [contour_sets["contourf"]]
            if variable == "10m_wind_speed":
                if quiv_container["quiv"] is not None:
                    artists.append(quiv_container["quiv"])
                if wind_label_text is not None:
                    artists.append(wind_label_text)
            return artists
    
    
        frame_count = len(data['time'])
        interval = ((segment_duration)* 1000) / (frame_count*3 ) # video duration
        print(segment_duration)
        
        anim = animation.FuncAnimation(
                fig, animate, frames=frame_count, interval=interval, blit=False
            )
            
        # Handle saving if requested
        if save_path:
            anim.save(save_path, writer='ffmpeg',dpi=100)
    
        # Display or return animation
        plt.close(fig)
        return save_path


    # Function to create video clips for different time segments and concatenate them
    def create_weather_video(self, variables, duration_config):
        time_segments = {
            "first_half": range(5, 13),
            "second_half": range(13, 23),
        }
       
        for segment_name, time_range in time_segments.items():
            clips = []
            print(f"\n📽️ Creating {segment_name} video...")
    
            # Get duration from JSON config
            segment_key = f"{segment_name}"
            segment_duration = duration_config.get(segment_key, {}).get("audio_duration_seconds", 20)
    
            for variable in variables:
                print(f"🎬 Generating animation for {variable} during {segment_name}...")
                save_name = f"./video/{variable}_{segment_name}.mp4"
                animation_path = self.create_animation(
                    variable, time_range,
                    save_path=save_name,
                    segment_duration=segment_duration
                )
                if animation_path:
                    clip = VideoFileClip(animation_path)
                    clips.append(clip)
    
            #debug
            for clip in clips:
                print(f"Clip size: {clip.size}")
    
    
            if clips:
                video_path = f"video/weather_{segment_name}.mp4"
                final_video = concatenate_videoclips(clips)
                final_video.write_videofile(video_path, codec='libx264')
                duration_config[segment_key]['video_path'] = video_path
                print(video_path)
            else:
                print(f"No valid clips for {segment_name}. Skipping video.")
    
        return duration_config


    def create_map_video(self):
        # Load the JSON file
        with open('./weather_text_to_audio.json', 'r') as f:
            json_data = json.load(f)
        
        # Run the video creation for the specified variables
        variables_to_plot = [
            #"2m_temperature",
            "total_precipitation_12hr",
            "10m_wind_speed",
            "10m_power_performance",
        ]
        self.ds1 = self.preprocess_dataset(self.ds1)
        
        json_data = self.create_weather_video(variables_to_plot, json_data)
        
        # Save updated JSON
        with open('./weather_text_to_audio.json', 'w') as f:
            json.dump(json_data, f, indent=4)
        
