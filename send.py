# THIS ALLOWS YOU TO UPLOAD A VIDEO TO THE SERVER

import requests  
headers = {"Authorization": "sk-7130445a9530ae258bfa501db075fee8"}  # API key  

# Video file details  
data = {  
    "file": ("1-GameFollow.mp4", open("/Users/kareemamin/hallpass/oix-lab-hackathon/11April25Hack/1-GameFollow.mp4", "rb"), "video/mp4")  
}  

# Optional callback URL for task status notifications  
params = {"callBackUri": "https://webhook.site/4a85d7b9-a993-4bf5-bb0e-318bbb7b9b16"}  

response = requests.post(  
    "https://mavi-backend.openinterx.com/api/serve/video/upload",  
    files=data,  
    params=params,  
    headers=headers  
    
)  

print(response.json())