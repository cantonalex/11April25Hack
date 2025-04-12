# THIS ALLOWS YOU TO SEARCH FOR SPECIFIC FRAGMENTS WITHIN VIDEOS

import requests
import json

headers = {"Authorization": ""}  # API key  

data = {  
    "videoNos": ["mavi_video_566084575235805184"],  # List of specific video IDs (you need at least 1 video_no to do the search)  
    "searchValue": "when someone says out of bounds"  # The search query  
}  

response = requests.post(  
    "https://mavi-backend.openinterx.com/api/serve/video/searchVideoFragment",  
    headers=headers,  
    json=data  
)  

# Pretty print the JSON response
print(json.dumps(response.json(), indent=2))