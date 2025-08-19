from manim import *
import json
import os

config.pixel_height = 1920
config.pixel_width = 1080
config.frame_rate = 30
config.media_width = "10%"
config.verbosity = "WARNING"
config.output_file = "3_days_prediction.mp4"
config.media_dir = "video/tab_video"

from manim import rgb_to_color

TRUE_RED = rgb_to_color((1.0, 0.0, 0.0))  # Pure red

def wind_speed_to_color(wind):
    wind = float(wind)
    if wind < 5 or wind > 25:
        return TRUE_RED
    norm = (wind - 5) / 20
    return interpolate_color(ORANGE, GREEN, norm)


class Video_tab(Scene):
    # creates the tab animation for the 3 days forecast with anim lib
    def construct(self):
        self.camera.background_color = WHITE

        with open("agent_json_data/windfarm_weather_3_days.json", "r") as f:
            raw_data = json.load(f)
            
        font="DejaVu Sans"
        cities = list(raw_data.keys())
        first_city = raw_data[cities[0]]
        days = ["day1", "day2", "day3"]
        headers = [" "] + cities

        table_data = []
        conditions = {}
        custom_cells = {}

        def get_condition(temp, precip):
            if precip > 5:
                return "rain"
            elif precip > 2:
                return "rain"
            elif precip > 0.005:
                return "sunny"
            else:
                return "sunny"

        for day_index, day in enumerate(days):
            row = []
            weekday = first_city[day]["weekday"] if day in first_city else f"Day {day_index+1}"
            row.append(weekday)

            for city_index, city in enumerate(cities):
                if day in raw_data[city]:
                    data = raw_data[city][day]["data"]
                    max_temp = data["max_temperature_C"]
                    min_temp = data["min_temperature_C"]
                    precip = data["precip_24h_mm"]
                    wind = data["wind_speed"]
                    wind_direction = data["wind_direction_cardinal"]
                    performance = data["10m_power_performance"]

                    condition = get_condition(max_temp, precip)
                    #row.append(f"{temp}°C\n\n{precip} mm\n\n{wind} m/s ({wind_direction})\n\nPerf:{performance}%")

                    # Add placeholder
                    row.append(" ")

                    # Store custom cell content
                    cell_content = VGroup(
                        Text(f"Perf: {performance}%", font=font, font_size=42, color=wind_speed_to_color(wind)),
                        Text(
                            f"{wind} m/s ({wind_direction})",
                            font=font,
                            font_size=35,
                            color=wind_speed_to_color(wind)
                        ),
                        Text(f"Temp: {max_temp}-{min_temp}°C  ", font=font, font_size=30, color=BLACK),
                        Text(f"Rain: {precip} mm", font=font, font_size=30, color=BLACK),
                        #Text(f"{wind} m/s ({wind_direction})", font="Monospace", font_size=42, color=BLUE),
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)

                    custom_cells[(len(table_data) + 1, city_index + 1)] = cell_content
                    conditions[(day_index + 1, city_index + 1)] = condition
                else:
                    row.append("N/A")

            table_data.append(row)

        table = Table(
            [headers] + table_data,
            include_outer_lines=True,
            element_to_mobject_config={
                "font": "DejaVu Sans",
                "font_size": 38,
                "color": BLACK
            },
            v_buff=3,
            h_buff=3,
            line_config={"color": BLACK, "stroke_width": 0.7}
        ).scale(0.90)

        title = Text("3-Day Weather Forecast", font=font, font_size=55, color=BLACK)
        title.next_to(table, UP, buff=2)

        # Load the image
        scale_image = ImageMobject("images/color_grade_table.png")
        scale_image.scale(1.7)  # Adjust scale as needed
        scale_image.next_to(table, DOWN, buff=0.5)

        # Animate both table and scale together
        self.play(Write(title), Create(table), FadeIn(scale_image))

        # Replace placeholders with custom cell content
        for (row_idx, col_idx), content in custom_cells.items():
            cell = table.get_cell((row_idx + 1, col_idx + 1))  # +1 for header row
            content.move_to(cell.get_center())
            self.add(content)

        self.wait()




