import os
import json
import boto3
from mutagen.mp3 import MP3
from pydub import AudioSegment
import time

# Define a class to handle agent calls and audio generation
class Agent_call:
    def __init__(self):
        # Initialize output text placeholders
        self.output_text_energy_prediction = None
        self.output_text_target_day = None
        self.output_text_3_days_forecast = None

    # Generic method to call a Bedrock agent with either JSON or plain text input
    def generic_agent_call(self, is_json, input_content, agent_id, agent_alias_id):
        start_time = time.time()  # Start timer for performance measurement

        if is_json:
            # Load JSON content from file
            with open(input_content, "r") as f:
                json_data = json.load(f)

            # Convert JSON to a formatted string for prompt injection
            json_string = json.dumps(json_data, indent=2)
            prompt = f"""Here is the data : {json_string}"""
        else:
            # Use plain text input directly
            prompt = f"""Here is the data : {input_content}"""

        # Initialize Bedrock Agent Runtime client
        client = boto3.client("bedrock-agent-runtime", region_name="eu-west-1")

        # Invoke the agent with the prompt
        response_stream = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId="session-001",
            inputText=prompt
        )

        # Read the streamed response and concatenate chunks
        output_text = ""
        for event in response_stream["completion"]:
            if "chunk" in event:
                chunk_text = event["chunk"]["bytes"].decode("utf-8")
                output_text += chunk_text

        # Print the full response
        print(output_text)

        end_time = time.time()  # End timer
        print(f"\n\n--------------------------Execution time: {end_time - start_time:.6f} seconds ----------------------------------------")

        return output_text

    # Save agent-generated text outputs to a JSON file
    def save_agent_text_outputs(self):
        # Hardcoded forecast text for the target day
        self.output_text_target_day = r"""{
          "intro": {
            "text": "Here is your Cognizant weather IQ forecast for April 1 2019 at the Race Bank windfarm. Expect a day with moderate winds and varying performance levels."
          },
          "first_half": {
            "text": "Starting with the morning, we see no rain expected before midday, with total precipitation remaining at 0.0 mm. Winds will be coming from the east at 5.7 m/s, shifting to the southeast at 5.6 m/s by midday. Turbine performance will start at 10.9% and slightly dip to 10.6% by midday."
          },
          "second_half": {
            "text": "Moving into the afternoon and evening, we anticipate a slight increase in precipitation, with 0.2 mm expected by 5 PM and continuing through midnight. Wind speeds will decrease to 5.0 m/s from the southeast, then shift from the south at 5.3 m/s by 9 PM, increasing to 6.1 m/s by midnight. Turbine performance will drop to 6.7% by 5 PM, improve to 9.0% by 9 PM, and significantly increase to 13.9% by midnight."
          },
          "outro": {
            "text": "Overall, it's a day of moderate winds with a notable shift in direction and varying turbine performance, influenced by the wind conditions. This was your Cognizant weather IQ forecast."
          }
        }"""

        # Parse the hardcoded JSON string
        data = json.loads(self.output_text_target_day)

        # Save the initial forecast to a file
        with open("weather_text_to_audio.json", "w") as f:
            json.dump(data, f, indent=4)

        # Load the saved file to append additional forecast data
        with open("weather_text_to_audio.json", "r") as f:
            json_data = json.load(f)

        # Add 3-day forecast and energy prediction to the JSON
        json_data["3_days_prediction"] = {
            "text": self.output_text_3_days_forecast
        }
        json_data["3_days_energy_prediction"] = {
            "text": self.output_text_energy_prediction
        }

        # Save the updated JSON back to file
        with open('weather_text_to_audio.json', 'w') as f:
            json.dump(json_data, f, indent=4)

    # Generate all required text outputs by calling the appropriate agents
    def generate_text(self):
        self.output_text_energy_prediction = self.generic_agent_call(
            is_json=1,
            input_content="agent_json_data/energy_output_summary.json",
            agent_id="YNSYYRS9LZ",
            agent_alias_id="8F0BKZSMIH"
        )
        self.output_text_target_day = self.generic_agent_call(
            is_json=1,
            input_content="agent_json_data/weather_data_insights_on_windfarm.json",
            agent_id="UMBA8NKSWE",
            agent_alias_id="YRK1YMNG7H"
        )
        self.output_text_target_day = self.generic_agent_call(
            is_json=0,
            input_content=self.output_text_target_day,
            agent_id="JDPCELIMJP",
            agent_alias_id="502WNOSKF9"
        )
        self.output_text_3_days_forecast = self.generic_agent_call(
            is_json=1,
            input_content="agent_json_data/windfarm_weather_3_days.json",
            agent_id="5PAXGQDXWQ",
            agent_alias_id="ZWFSPTUQOQ"
        )

    # Generate an audio file from text using Amazon Polly
    def generate_audio(self, polly, text, file_name, rate):
        ssml_text = f"""
        <speak>
          <prosody rate="{rate}">
            {text}
            <break time="500ms"/>
          </prosody>
        </speak>
        """
        response = polly.synthesize_speech(
            Text=ssml_text,
            TextType='ssml',
            OutputFormat='mp3',
            Engine='neural',
            VoiceId='Amy'
        )
        with open(file_name, 'wb') as f:
            f.write(response['AudioStream'].read())

    # Function to get the duration of an MP3 file
    def get_audio_duration(self, file_name):
        audio = MP3(file_name)
        return audio.info.length

    # Function to append 0.5 seconds of silence to an MP3 file
    def append_silence(self, file_name, silence_duration_ms=500):
        audio = AudioSegment.from_mp3(file_name)
        silence = AudioSegment.silent(duration=silence_duration_ms)
        combined = audio + silence
        combined.export(file_name, format="mp3")

    def create_audio_reccordings (self):
        # Load the JSON file
        with open('weather_text_to_audio.json', 'r') as f:
            data = json.load(f)
        # Ensure the audio directory exists
        os.makedirs('audio', exist_ok=True)

        # Initialize Polly client
        polly = boto3.client('polly', region_name='us-east-1')

        # Sections to process
        sections = ['intro', 'first_half', 'second_half', 'outro', '3_days_prediction','3_days_energy_prediction']

        # Generate audio and update JSON
        for section in sections:
            file_name = f"audio/{section}.mp3"
            print(f"Processing: {section}")
            self.generate_audio(polly, data[section]['text'], file_name, rate="fast")
            # append_silence(file_name)
            duration = self.get_audio_duration(file_name)

            # Update JSON with audio path and duration
            data[section]['audio_path'] = file_name
            data[section]['audio_duration_seconds'] = round(duration, 2)

        # Save updated JSON
        with open('weather_text_to_audio.json', 'w') as f:
            json.dump(data, f, indent=4)

        print("Audio files created with silence and JSON updated with durations.")