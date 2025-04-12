# THIS ALLOWS YOU TO SEARCH FOR SPECIFIC FRAGMENTS WITHIN VIDEOS

import requests
import json
import os
import subprocess
from pathlib import Path

headers = {"Authorization": "sk-7130445a9530ae258bfa501db075fee8"}  # API key  

data = {  
    "videoNos": ["mavi_video_566084575235805184"],  # List of specific video IDs (you need at least 1 video_no to do the search)  
    "searchValue": "short clips of highlights"  # The search query  
}  

response = requests.post(  
    "https://mavi-backend.openinterx.com/api/serve/video/searchVideoFragment",  
    headers=headers,  
    json=data  
)  

# Get the response
result = response.json()

# Base directory path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Specific video paths
video_paths = [
    os.path.join(base_dir, "1-GameFollow.mp4"),
    os.path.join(base_dir, "3-LeftHandheld.mp4"),
    os.path.join(base_dir, "4-TightHandheld.mp4"),
    os.path.join(base_dir, "5-Slash.mp4")
]

# Format and save the top 4 segments for concat_videos.py
if result.get("code") == "0000" and "data" in result and "videos" in result["data"]:
    # Get top 4 video fragments only
    top_videos = result["data"]["videos"][:4]
    
    # Create temp directory for processed segments
    temp_dir = os.path.join(base_dir, "temp_montage")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Store the timestamps
    timestamps = []
    print("First 4 timestamps (start to end):")
    
    for i, video in enumerate(top_videos):
        # Convert timestamps from strings to floats
        start_time = float(video["fragmentStartTime"])
        end_time = float(video["fragmentEndTime"])
        
        # Limit to 10 seconds if longer
        if end_time - start_time > 10:
            end_time = start_time + 10
            
        timestamps.append((start_time, end_time))
        
        # Print the timestamps
        print(f"Segment {i+1}: {start_time:.2f}s to {end_time:.2f}s (duration: {end_time-start_time:.2f}s)")
    
    # Make sure we have at least one timestamp
    if not timestamps:
        print("No timestamps found. Exiting.")
        exit(1)
    
    # If we have fewer than 4 timestamps, duplicate the last one to fill
    while len(timestamps) < 4:
        timestamps.append(timestamps[-1])
    
    # For each timestamp, create a montage of all 4 videos
    montage_segments = []
    
    for ts_idx, (start_time, end_time) in enumerate(timestamps):
        print(f"\nProcessing timestamp segment {ts_idx+1}: {start_time:.2f}s to {end_time:.2f}s")
        
        # Extract the same segment from all 4 videos using this timestamp
        segment_files = []
        
        for vid_idx, video_path in enumerate(video_paths):
            output_segment = os.path.join(temp_dir, f"segment_{ts_idx}_{vid_idx}.mp4")
            segment_files.append(output_segment)
            
            # Use FFmpeg to extract the segment from each video with the same timestamp
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(start_time),
                "-to", str(end_time),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y",  # Overwrite output files
                output_segment
            ]
            
            video_name = os.path.basename(video_path)
            print(f"  Extracting from {video_name}: {start_time:.2f}s to {end_time:.2f}s")
            subprocess.run(cmd, check=True)
        
        # Create a 2x2 montage for this timestamp
        montage_output = os.path.join(temp_dir, f"montage_segment_{ts_idx}.mp4")
        montage_segments.append(montage_output)
        
        # FFmpeg command to create a 2x2 grid montage
        montage_cmd = [
            "ffmpeg",
            "-i", segment_files[0],
            "-i", segment_files[1],
            "-i", segment_files[2],
            "-i", segment_files[3],
            "-filter_complex",
            "[0:v]setpts=PTS-STARTPTS,scale=640:360[a];"
            "[1:v]setpts=PTS-STARTPTS,scale=640:360[b];"
            "[2:v]setpts=PTS-STARTPTS,scale=640:360[c];"
            "[3:v]setpts=PTS-STARTPTS,scale=640:360[d];"
            "[a][b]hstack=inputs=2[top];"
            "[c][d]hstack=inputs=2[bottom];"
            "[top][bottom]vstack=inputs=2[v]",
            "-map", "[v]",
            # Take audio from the first video only
            "-map", "0:a?",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-crf", "23",
            "-preset", "veryfast",
            "-y",
            montage_output
        ]
        
        print(f"  Creating 2x2 montage for segment {ts_idx+1}...")
        subprocess.run(montage_cmd, check=True)
        
        # Remove the individual segment files to save space
        for file in segment_files:
            if os.path.exists(file):
                os.remove(file)
    
    # Now concatenate all the montage segments if we have more than one
    final_output_path = os.path.join(base_dir, "montage_output.mp4")
    
    if len(montage_segments) == 1:
        # If there's only one segment, just rename it
        os.rename(montage_segments[0], final_output_path)
    else:
        # Create a file list for concatenation
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file, "w") as f:
            for segment in montage_segments:
                f.write(f"file '{segment}'\n")
        
        # Use FFmpeg to concatenate all montage segments
        concat_cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-y",
            final_output_path
        ]
        
        print(f"\nConcatenating {len(montage_segments)} montage segments...")
        subprocess.run(concat_cmd, check=True)
        
        # Clean up the montage segments
        for file in montage_segments:
            if os.path.exists(file):
                os.remove(file)
        os.remove(concat_file)
    
    print(f"\nFinal montage successfully created at: {final_output_path}")
    
    # Clean up the temp directory
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)
    
else:
    print("Error in API response:")
    print(json.dumps(result, indent=2))