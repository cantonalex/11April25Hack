import os
import subprocess
import json

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

print(f"Found all required videos: {', '.join(video_files)}")

# Choose a common start time for all videos (in seconds)
# Let's take 10 seconds into each video as the starting point
start_time = 10
duration = 20  # 20 seconds for each video
segment_duration = duration / 4  # Each video gets 5 seconds in the final cut

# Create temp directory for processed clips
if not os.path.exists("temp"):
    os.makedirs("temp")

# Process each video to extract the same 20-second segment
processed_clips = []
for i, video in enumerate(video_files):
    output_file = f"temp/clip_{i+1}.mp4"
    processed_clips.append(output_file)
    
    # Build ffmpeg command to extract the 20-second clip
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", video,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        output_file
    ]
    
    print(f"Extracting 20-second clip from {video}...")
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
        print(f"  Successfully created {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"  Error processing {video}: {e}")
        print(f"  ffmpeg error: {e.stderr}")
        exit(1)

# Extract audio from the first video for the entire sequence
audio_file = "temp/audio.mp3"
audio_cmd = [
    "ffmpeg",
    "-i", processed_clips[0],
    "-vn",
    "-acodec", "libmp3lame",
    "-q:a", "2",
    audio_file
]

print("\nExtracting audio from the first video...")
try:
    subprocess.run(audio_cmd, check=True, capture_output=True, text=True)
    print(f"  Successfully extracted audio to {audio_file}")
except subprocess.CalledProcessError as e:
    print(f"Error extracting audio: {e}")
    print(f"ffmpeg error: {e.stderr}")
    exit(1)

# Create a video sequence that cuts between clips
print("\nCreating sequential video with cuts between clips...")

# Create a text file listing segments to include
segments_file = "temp/segments.txt"
with open(segments_file, "w") as f:
    for i, clip in enumerate(processed_clips):
        # For each clip, we'll use a 5-second segment
        # Use the full path for the file reference
        f.write(f"file '{os.path.abspath(clip)}'\n")
        f.write(f"inpoint {i * segment_duration}\n")
        f.write(f"outpoint {(i + 1) * segment_duration}\n")

# Use ffmpeg to create the sequential video
sequence_cmd = [
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", segments_file,
    "-i", audio_file,
    "-map", "0:v",
    "-map", "1:a",
    "-c:v", "libx264",
    "-c:a", "aac",
    "-shortest",
    "sequential_cuts.mp4"
]

try:
    subprocess.run(sequence_cmd, check=True, capture_output=True, text=True)
    print("Successfully created sequential_cuts.mp4")
except subprocess.CalledProcessError as e:
    print(f"Error creating sequential video: {e}")
    print(f"ffmpeg error: {e.stderr}")
    exit(1)

# Create a JSON file with information about the sequence
sequence_info = {
    "original_videos": video_files,
    "sync_start_time": start_time,
    "total_duration": duration,
    "segment_duration": segment_duration,
    "processed_clips": processed_clips,
    "audio_source": video_files[0],
    "output_file": "sequential_cuts.mp4"
}

with open("sequence_info.json", "w") as f:
    json.dump(sequence_info, f, indent=2)

print("\nVideo sequence complete!")
print("- Individual 20-second clips saved in the 'temp' directory")
print("- Final sequential video with cuts: sequential_cuts.mp4")
print("- Audio taken from the first video")
print("- Sequence details saved in sequence_info.json")

# Cleanup temp files if desired
# import shutil
# shutil.rmtree("temp")
