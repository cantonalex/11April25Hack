import json
import os
import subprocess

# Path to the JSON file created by search.py
json_file_path = "video_segments.json"

# Check if the JSON file exists
if not os.path.exists(json_file_path):
    print(f"Error: {json_file_path} not found. Please run search.py first.")
    exit(1)

# Load the editing instructions from the JSON file
try:
    with open(json_file_path, 'r') as f:
        editing_instructions = json.load(f)
    
    print(f"Loaded {len(editing_instructions)} video segments from {json_file_path}")
    print("Segments to concatenate:")
    for i, segment in enumerate(editing_instructions, 1):
        print(f"  {i}. File: {os.path.basename(segment['file'])}, Start: {segment['start']}, End: {segment['end']}")
except Exception as e:
    print(f"Error loading {json_file_path}: {e}")
    exit(1)

# Create a temporary file list for ffmpeg
temp_file = "concat_list.txt"
with open(temp_file, "w") as f:
    for segment in editing_instructions:
        # Adjust file path - check if we need to add the directory to reach bball-highlight.mp4
        file_path = segment['file']
        if not os.path.exists(file_path) and os.path.basename(file_path) == "bball-hightlight.mp4":
            file_path = os.path.join("11April25Hack", os.path.basename(file_path))
        
        # Create input clip with proper timing
        start_time = segment['start']
        end_time = segment['end']
        duration = end_time - start_time
        
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