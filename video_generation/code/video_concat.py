import subprocess
import json

# adding slience to sound more natural between the segements
def add_silence(audio_path, output_path, duration=0.5):
    subprocess.run([
        'ffmpeg', '-y',
        '-i', audio_path,
        '-filter_complex', f"[0:a]apad=pad_dur={duration}[a]",
        '-map', '0:v?',  # optional video stream
        '-map', '[a]',
        '-c:a', 'aac',
        output_path
    ])


def create_final_video():
    # Load JSON data
    with open('weather_text_to_audio.json') as f:
        data = json.load(f)
    segments = []
    
    # Step 2: Replace audio in video segments
    for key in ['intro', 'first_half', 'second_half', '3_days_prediction','3_days_energy_prediction', 'outro']:
        video_path = data[key]['video_path']
        audio_path = data[key]['audio_path']
        output_audio = f'audio/{key}.mp3'
        output_video = f'video/concat_videos/temp_{key}.mp4'
        segments.append(output_video)
    
        # Check if the video_path is actually an image
        if video_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Get audio duration
            audio_info = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries',
                'format=duration', '-of',
                'default=noprint_wrappers=1:nokey=1', output_audio
            ], capture_output=True, text=True)
            audio_duration = float(audio_info.stdout.strip())
    
            print(f"📷 Detected image. Creating video from image for duration: {audio_duration:.2f}s")
    
            # Create a video from the image
            image_video_path = f'video/concat_videos/image_video_{key}.mp4'
            subprocess.run([
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', video_path,
                '-i', output_audio,
                '-c:v', 'libx264',
                '-t', str(audio_duration),
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1080:1920',
                '-c:a', 'aac',
                '-shortest',
                image_video_path
            ])
            video_path = image_video_path
    
        # Get video duration
        video_info = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of',
            'default=noprint_wrappers=1:nokey=1', video_path
        ], capture_output=True, text=True)
        video_duration = float(video_info.stdout.strip())
    
        # Get audio duration
        audio_info = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of',
            'default=noprint_wrappers=1:nokey=1', output_audio
        ], capture_output=True, text=True)
        audio_duration = float(audio_info.stdout.strip())
    
        if audio_duration > video_duration:
            print(f"🕒 Padding video to match audio duration: video={video_duration:.2f}s, audio={audio_duration:.2f}s")
            subprocess.run([
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', output_audio,
                '-filter_complex', f"[0:v]tpad=stop_mode=clone:stop_duration={audio_duration - video_duration + 0.25}[v]",
                '-map', '[v]',
                '-map', '1:a',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                output_video
            ])
        else:
            print(f"🔊 Replacing audio only: video={video_duration:.2f}s, audio={audio_duration:.2f}s")
            subprocess.run([
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', output_audio,
                '-c:v', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_video
            ])
            
    # Step 3: Convert each MP4 to TS format with re-encoding to ensure sync
    ts_segments = []
    for seg in segments:
        ts_output = seg.replace('.mp4', '.ts')
        ts_segments.append(ts_output)
        subprocess.run([
            'ffmpeg', '-y',
            '-i', seg,
            '-vf', 'fps=25,format=yuv420p',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'mpegts',
            ts_output
        ])
    
    # Step 4: Concatenate TS files and rewrap into MP4
    concat_str = '|'.join(ts_segments)
    subprocess.run([
        'ffmpeg', '-y',
        '-i', f"concat:{concat_str}",
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        'final_weather_video.mp4'
    ])
    
    print("✅ Final video created: final_weather_video.mp4")

