import json
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.ticker as mticker
import xarray as xr
import matplotlib.pyplot as plt

# Class to process wind farm data and generate JSON outputs
class DataJson:
    def __init__(self, ds1, day1, day2, day3, selected_windFarm):
        # Store datasets and selected wind farm
        self.ds1 = ds1
        self.selected_windFarm = selected_windFarm
        self.day1 = day1
        self.day2 = day2
        self.day3 = day3
        self.lat = None
        self.lon = None
        self.nb_turbines = None
        self.init_windfarm_data()  # Initialize wind farm metadata

    # Load wind farm metadata (lat, lon, turbine count) from JSON
    def init_windfarm_data(self):
        with open("agent_json_data/windfarm.json", "r") as f:
            windfarm_data = json.load(f)

        # Extract lat/lon for each wind farm
        windfarms = {
            wf["name"]: (wf["location"]["lat"], wf["location"]["lon"])
            for wf in windfarm_data
            if "location" in wf and "lat" in wf["location"] and "lon" in wf["location"]
        }

        # Set lat/lon for selected wind farm
        self.lat, self.lon = windfarms[self.selected_windFarm]
        if self.lon < 0:
            self.lon += 360  # Adjust for global coordinate system

        # Get number of turbines for selected wind farm
        self.nb_turbines = next(
            (entry["turbines"] for entry in windfarm_data if entry["name"] == self.selected_windFarm),
            None
        )

    # Generate all required JSON files
    def create_all_json_files(self):
        self.create_json_data_3_days_prediction_table()
        self.create_json_data_1_day_windfarm()
        self.create_energy_produced_vizuals()

    # ------------------------------- 3 days prediction ------------------------------------------------

    # Extract daily average weather and performance metrics
    def extract_daily_averages(self, ds):
        wind_speed = ds["10m_wind_speed"].sel(lat=self.lat, lon=self.lon, method="nearest")
        wind_direction_cardinal = ds["10m_wind_cardinal"].sel(lat=self.lat, lon=self.lon, method="nearest")
        power_performance = ds["10m_power_performance"].sel(lat=self.lat, lon=self.lon, method="nearest")
        temp = ds["2m_temperature"].sel(lat=self.lat, lon=self.lon, method="nearest")
        precip = ds["total_precipitation_12hr"].sel(lat=self.lat, lon=self.lon, method="nearest")

        # Aggregate and round values
        data = {}
        data["max_temperature_C"] = round(temp.max().item(), 2)
        data["min_temperature_C"] = round(temp.min().item(), 2)
        data["precip_24h_mm"] = round(precip.sum().item(), 2)
        data["wind_speed"] = round(wind_speed.mean().item(), 1)
        data["wind_direction_cardinal"] = str(wind_direction_cardinal.max().item())
        data["10m_power_performance"] = round(power_performance.mean().item(), 1)
        return data

    # Extract date and weekday from dataset
    def extract_date_and_weekday(self, ds):
        date_str = str(ds.datetime.values[1])
        date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
        weekday = date_obj.strftime("%A")
        return date_str[:10], weekday

    # Create JSON file with 3-day forecast summary
    def create_json_data_3_days_prediction_table(self):
        day1_avg = self.extract_daily_averages(self.day1)
        day2_avg = self.extract_daily_averages(self.day2)
        day3_avg = self.extract_daily_averages(self.day3)
        day1_date, day1_weekday = self.extract_date_and_weekday(self.day1)
        day2_date, day2_weekday = self.extract_date_and_weekday(self.day2)
        day3_date, day3_weekday = self.extract_date_and_weekday(self.day3)

        # Structure results by wind farm
        results = {
            self.selected_windFarm: {
                "day1": {"date": day1_date, "weekday": day1_weekday, "data": day1_avg},
                "day2": {"date": day2_date, "weekday": day2_weekday, "data": day2_avg},
                "day3": {"date": day3_date, "weekday": day3_weekday, "data": day3_avg}
            }
        }

        # Save to JSON file
        with open("agent_json_data/windfarm_weather_3_days.json", "w") as f:
            json.dump(results, f, indent=4)
        print("Weather data insights saved to windfarm_weather_3_days.json")

    # ------------------------- Windfarm over one day ------------------------------------------------------

    # Create JSON file with detailed insights for one day
    def create_json_data_1_day_windfarm(self):
        # Select last 24 hours and specific time steps
        last_day = self.ds1.isel(time=slice(-24, None)).isel(time=[8, 11, 16, 20, 23])

        # Override map for precipitation values
        precip_override_map = {0: 1, 2: 4, 3: 4}

        # Variables to extract
        variables = [
            "total_precipitation_12hr",
            "10m_wind_speed",
            "10m_wind_cardinal",
            "10m_power_performance"
        ]

        # Extract time values
        time_array = [str(t.values) for t in last_day.datetime]
        insights = {"time": time_array}
        windfarm_data_list = []

        # Loop through each selected time step
        for i, t in enumerate(last_day.time):
            entry = {"time": time_array[i]}
            for var in variables:
                if var in last_day:
                    # Handle precipitation override
                    if var == "total_precipitation_12hr" and i in precip_override_map:
                        source_index = precip_override_map[i]
                        source_time = last_day.time[source_index]
                        data = last_day[var].sel(lat=self.lat, lon=self.lon, time=source_time, method="nearest")
                    else:
                        data = last_day[var].sel(lat=self.lat, lon=self.lon, time=t, method="nearest")

                    # Convert to native Python type
                    if hasattr(data, 'item'):
                        item = data.item()
                        value = round(item, 1) if isinstance(item, (int, float, np.number)) else item
                    else:
                        value = str(data.values)

                    entry[var] = value

            windfarm_data_list.append(entry)

        # Add wind farm data to insights
        insights[self.selected_windFarm] = windfarm_data_list

        # Save to JSON file
        with open("agent_json_data/weather_data_insights_on_windfarm.json", "w") as f:
            json.dump(insights, f, indent=4)

        print("Insights saved to weather_data_insights_on_windfarm.json")

        #  --------------------------------- energy ouput -------------------------------------------------
    
    # Format large y-axis values for plots (e.g., 1000 -> 1k, 1,000,000 -> 1M)
    def y_axis_formatter(self, x, pos):
        if x >= 1_000_000:
            return f"{int(x / 1_000_000)}"
        elif x >= 1_000:
            return f"{int(x / 1_000)}"
        else:
            return str(int(x))

    # Combine three xarray datasets into one, removing duplicate timestamps
    def create_combined_data(self):
        # Concatenate datasets along the time dimension
        combined = xr.concat([self.day1, self.day2, self.day3], dim='time')
        # Ensure datetime is a coordinate
        combined = combined.assign_coords(datetime=("time", combined["datetime"].values))
        # Remove duplicate datetime entries
        _, index = np.unique(combined['datetime'].values, return_index=True)
        unique_combined = combined.isel(time=index)
        # Sort by datetime
        unique_combined = unique_combined.sortby('datetime')
        return unique_combined

    # Convert large numbers to human-readable format (e.g., 1500 -> 1.5k)
    def human_readable(self, value, x=0):
        if x == 0:
            if value >= 1_000_000:
                return f"{value / 1_000_000:.1f}M"
            elif value >= 1_000:
                return f"{value / 1_000:.1f}k"
            else:
                return f"{value:.1f}"
        else:
            if value >= 1_000_000:
                return f"{value / 1_000_000:.1f}"
            elif value >= 1_000:
                return f"{value / 1_000:.1f}"
            else:
                return f"{value:.1f}"

    # Generate a visualization of energy produced and save summary to JSON
    def create_energy_produced_vizuals(self):
        # Combine datasets and extract relevant data
        unique_combined = self.create_combined_data()
        datetime = unique_combined['datetime'].values
        power_output = np.squeeze(unique_combined['10m_power_output_kw'].sel(lat=self.lat, lon=self.lon, method='nearest').values)

        # Create DataFrame for easier manipulation
        df = pd.DataFrame({'datetime': pd.to_datetime(datetime), '10m_power_output_kw': power_output})
        df = df.sort_values('datetime').reset_index(drop=True)
        df['date'] = df['datetime'].dt.date

        grouped_rows = []
        dates = []
        average_points = []

        # Identify valid 3-point sequences for daily energy calculation
        for i in range(len(df) - 2):
            t0 = df.loc[i, 'datetime']
            t1 = df.loc[i + 1, 'datetime']
            t2 = df.loc[i + 2, 'datetime']

            if (t0.hour == 0 and t1.hour == 12 and t2.hour == 0 and t0.date() == t1.date() and t2.date() == t0.date() + pd.Timedelta(days=1)):
                energy_values = df.loc[i:i+2, '10m_power_output_kw'].values
                grouped_rows.append(energy_values)
                dates.append(t0.date())
                average_points.append((t1, np.mean(energy_values) * self.nb_turbines))

        # Calculate daily totals and averages
        daily_totals = [np.mean(row) * 24 for row in grouped_rows]
        daily_averages = [np.mean(row) for row in grouped_rows]
        total_energy = np.sum(daily_totals)
        overall_average = np.mean(daily_averages)

        # Create the plot
        fig = plt.figure(figsize=(10.8, 19.2), dpi=100)
        plot_bottom = 0.30
        plot_height = 0.5
        ax = fig.add_axes([0.1, plot_bottom, 0.85, plot_height])

        # Plot total power output
        ax.plot(df['datetime'], df['10m_power_output_kw'] * self.nb_turbines,
                label='Total Power Output', color='blue')
        ax.set_title(
            f"Total Power Prediction\n over "
            f"$\\bf{{{self.selected_windFarm}}}$\n",
            fontsize=50
        )
        ax.set_ylabel('Energy Output (kWh x1000)', fontsize=28)
        ax.grid(True)
        ax.tick_params(axis='x', labelsize=33)
        ax.tick_params(axis='y', labelsize=28)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(self.y_axis_formatter))
        plt.xticks(rotation=45)

        # Plot average points
        avg_times, avg_values = zip(*average_points)
        ax.scatter(avg_times, avg_values, color='red', s=100, label='Daily Average', zorder=5)

        # Annotate average values
        for x, y in average_points:
            ax.text(x + pd.Timedelta(hours=1), y + 1500, self.human_readable(y, 1), color='red', fontsize=30, ha='left')

        ax.legend(fontsize=22)
        ax.legend(loc='upper left', fontsize=24, bbox_to_anchor=(0.5, 0.85))

        # Remove x-axis labels
        ax.set_xticks([])
        ax.set_xlabel('')

        # Add vertical lines and labels for each day
        start_date = df['datetime'].iloc[0].normalize()
        for i in range(1, len(dates) + 1):
            day_start = start_date + pd.Timedelta(days=i)
            ax.axvline(day_start, color='gray', linestyle='--', linewidth=2)
            label_position = day_start - pd.Timedelta(hours=12)
            total_day_energy = daily_totals[i-1] * self.nb_turbines
            ax.text(label_position, ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.02,
                    f'Day {i}\n$\\mathbf{{{self.human_readable(total_day_energy)}}}$ kWh',
                    rotation=0, ha='center', va='top', fontsize=28, color='black')

        # Add turbine model info below the plot
        turbine_info = f"Turbine Model: SWT-3.6-107\n{self.nb_turbines} Turbines"
        fig.text(0.5, 0.16, turbine_info, ha='center', va='top', fontsize=30,
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

        # Save the plot
        plt.savefig("images/power_output.png", dpi=100)
        plt.close(fig)

        # Prepare data for JSON export
        data_to_export = {
            f"All Turbines in {self.selected_windFarm}": [
                {
                    "Day": f"Day {i+1}",
                    "Timestamp": str(average_points[i][0].date()),
                    "weekday": average_points[i][0].strftime("%A"),
                    "Average Energy Output (kWh)": self.human_readable(average_points[i][1]),
                    "Total Energy (kWh/all turbines)": self.human_readable(daily_totals[i] * self.nb_turbines)
                }
                for i in range(len(dates))
            ],
            "Turbine Count": self.nb_turbines
        }

        # Save summary to JSON file
        with open("agent_json_data/energy_output_summary.json", "w") as json_file:
            json.dump(data_to_export, json_file, indent=4)