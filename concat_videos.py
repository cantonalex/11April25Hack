import os
import subprocess

# The four video files to use
video_files = [
    "1-GameFollow.mp4",
    "3-LeftHandheld.mp4",
    "4-TightHandheld.mp4",
    "5-Slash.mp4"
]

# Verify all videos exist
missing_videos = [v for v in video_files if not os.path.exists(v)]
if missing_videos:
    print(f"Error: The following required videos are missing: {', '.join(missing_videos)}")
    exit(1)

print(f"Using videos: {', '.join(video_files)}")

# Define segments to extract from each video (start_time, end_time in seconds)
# We'll take 5-second clips from different parts of each video
segments = [
    # Video 1: Three segments from beginning, middle, and end
    {"file": video_files[0], "start": 5, "end": 10},
    {"file": video_files[0], "start": 15, "end": 20},
    {"file": video_files[0], "start": 25, "end": 30},
    
    # Video 2: Two segments
    {"file": video_files[1], "start": 10, "end": 15},
    {"file": video_files[1], "start": 20, "end": 25},
    
    # Video 3: Two segments
    {"file": video_files[2], "start": 5, "end": 10},
    {"file": video_files[2], "start": 15, "end": 20},
    
    # Video 4: Three segments
    {"file": video_files[3], "start": 10, "end": 15},
    {"file": video_files[3], "start": 20, "end": 25},
    {"file": video_files[3], "start": 30, "end": 35},
]

print("Segments to concatenate:")
for i, segment in enumerate(segments, 1):
    print(f"  {i}. File: {segment['file']}, Start: {segment['start']}, End: {segment['end']}")

# Create a temporary file list for ffmpeg
temp_file = "concat_list.txt"
with open(temp_file, "w") as f:
    for segment in segments:
        file_path = segment['file']
        start_time = segment['start']
        end_time = segment['end']
        
        # Write the file entry for ffmpeg concat
        f.write(f"file '{file_path}'\n")
        f.write(f"inpoint {start_time}\n")
        f.write(f"outpoint {end_time}\n")

# Build ffmpeg command
ffmpeg_cmd = [
    "ffmpeg", 
    "-f", "concat", 
    "-safe", "0", 
    "-i", temp_file,
    "-c", "copy",
    "highlight_reel.mp4"
]

# Run the ffmpeg command
print("\nConcatenating video segments...")
try:
    result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
    print("\nVideo concatenation complete. Output saved as 'highlight_reel.mp4'.")
except subprocess.CalledProcessError as e:
    print(f"\nError during video concatenation: {e}")
    print(f"ffmpeg error: {e.stderr}")

# Clean up temporary file
try:
    os.remove(temp_file)
except:
    pass