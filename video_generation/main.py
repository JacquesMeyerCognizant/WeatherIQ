
from code.data_cleaning import data_cleaning, daily_sub_dataset_creation, save_video_files_paths_in_json
from code.video_concat import create_final_video

from code.data_json import DataJson
from code.agent_call import Agent_call
from code.video_map import Video_map
from code.video_tab import Video_tab

import xarray as xr

class Main:
    def __init__(self):
        self.ds1 = None
        self.selected_windFarm = "Race Bank"
        self.day1 = None
        self.day2 = None
        self.day3 = None

        self.import_data()
        self.ds1 = data_cleaning(self.ds1)
        self.day1, self.day2, self.day3, self.ds1 = daily_sub_dataset_creation(self.ds1)

        print("Main class initialized.")

    def import_data(self):
        file_path = "./target_3_date_prediction.nc"
        ds1 = xr.open_dataset(file_path, decode_times=False)
        ds1['time'].attrs.pop('dtype', None)
        self.ds1 = xr.decode_cf(ds1)
 
    def run(self):

        print("Running the main logic...")
        # Create subdatasets to give to the LLm agents
        data_json = DataJson(self.ds1, self.day1, self.day2, self.day3, self.selected_windFarm)   
        data_json.create_all_json_files()

        # Calling the LLM agents to create the video scripts
        agent_call = Agent_call()
        agent_call.generate_text()

        # Calling the LLM agents to create the audio reccording based on the scripts
        agent_call.create_audio_reccordings()

        # creating the map video over the UK
        video_map = Video_map(self.ds1, self.selected_windFarm)
        video_map.create_map_video()

        # creating the tab video over 3 days
        Video_tab().render()
        # Saving all the videos and audios paths into the global json to prepare concatenation
        save_video_files_paths_in_json()

        # concatenating all the videos with the matching audios
        create_final_video()


if __name__ == "__main__":
    app = Main()
    app.run()