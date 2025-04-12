# THIS ALLOWS YOU TO CHAT WITH THE VIDEO


import requests  

headers = {"Authorization": "sk-7130445a9530ae258bfa501db075fee8"}  # API key  

data = {  
    "videoNos": ["mavi_video_566058593833586688"],  # List of video IDs to chat about  
    "message": "what is the gender of person in this video?",  # User query or prompt  
    "history": [],  # Chat history (leave empty for new conversations)  
    "stream": False  # Set to True for streaming responses  
}  

response = requests.post(  
    "https://mavi-backend.openinterx.com/api/serve/video/chat",  
    headers=headers,  
    json=data  
)  

print(response.text)