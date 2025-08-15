# 🌦️ Weather Forecast Video Generation

This folder contains the code for generating weather forecast videos using the 72-hour GenCast prediction data. The output is a video that visualizes the predicted weather conditions and the generated power over an offshore windfarm for selected dates.

---

## 🚀 Features

- Visualizes 72-hour weather forecasts
- Displays predicted power generation for selected windfarms
- Generates a video output in `.mp4` format

---

## 🛠️ How to Use

### 1. Set Up the Environment

Install the required dependencies in your Python environment:

```bash
pip install -r requirements.txt
```

### 2. Input an Example Dataset

The Input is the prediction made by the Gencast WeatherIQ Endpoint also available on this repo.
The example input dataset is too large to be stored in the GitHub repository. You can download it from the following link:

```bash
https://drive.google.com/file/d/1FmnCpcOCR94-qA9PtdUt45U_-t2j3sEL/view?usp=sharing
```
Place the downloaded dataset in the same directory as main.py.

### 3. Select a Windfarm

You can choose the windfarm to visualize by modifying the selected_windFarm variable in main.py.

The list of available windfarms is stored in:

```bash
video_generation/agent_json_data/windfarm.json
```

### 4. Run the Script

Launch the script from the terminal:

```bash
python main.py
```

### 5. Output

The generated video will be saved as:

```bash
final_weather_video.mp4
```

in the same directory as main.py.

---

## 📁 Folder Structure

```bash
video_generation/
├── agent_json_data/
│   └── windfarm.json
├── main.py
├── requirements.txt
├── final_weather_video.mp4
├── target_3_date_prediction.nc
└── README.md
```

---

## 📬 Contact and more information 

Have a look a the technical slides for more information about the code and the user case.
For questions or contributions, feel free to open an issue or pull request.
