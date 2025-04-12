# THIS ALLOWS YOU TO SEARCH FOR SPECIFIC FRAGMENTS WITHIN VIDEOS

import requests
import json
import os

headers = {"Authorization": "sk-7130445a9530ae258bfa501db075fee8"}  # API key  

data = {  
    "videoNos": ["mavi_video_566084575235805184"],  # List of specific video IDs (you need at least 1 video_no to do the search)  
    "searchValue": "get me 5 second clips of them shooting"  # The search query  
}  

response = requests.post(  
    "https://mavi-backend.openinterx.com/api/serve/video/searchVideoFragment",  
    headers=headers,  
    json=data  
)  

# Get the response
result = response.json()

# Format and save the top 4 segments for concat_videos.py
if result.get("code") == "0000" and "data" in result and "videos" in result["data"]:
    # Get top 4 video fragments only
    top_videos = result["data"]["videos"][:4]
    
    # Convert to format needed by concat_videos.py
    editing_instructions = []
    for video in top_videos:
        # Use the 1-GameFollow.mp4 file specifically
        video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "1-GameFollow.mp4"))
        
        # Convert timestamps from strings to floats
        start_time = float(video["fragmentStartTime"])
        end_time = float(video["fragmentEndTime"])
        
        editing_instructions.append({
            "file": video_path,
            "start": start_time,
            "end": end_time
        })
    
    # Save to a JSON file that concat_videos.py can use
    with open("../video_segments.json", "w") as f:
        json.dump(editing_instructions, f, indent=2)
    
    print(f"Saved top 4 video segments to video_segments.json using 1-GameFollow.mp4")
    # Pretty print the original response
    print("\nOriginal API response:")
    print(json.dumps(result, indent=2))
else:
    print("Error in API response:")
    print(json.dumps(result, indent=2))