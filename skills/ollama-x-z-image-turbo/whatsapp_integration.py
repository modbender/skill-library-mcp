import requests
import json
from fastapi import FastAPI

app = FastAPI()

@app.post("/send-to-whatsapp/")
async def send_to_whatsapp(image_url: str, message: str, recipient: str):
    # Logique pour envoyer l'image à WhatsApp
    whatsapp_api_url = "https://api.whatsapp.com/send"
    payload = {
        "phone": recipient,
        "body": f"{message} \n Voici votre image : {image_url}"
    }

    response = requests.post(whatsapp_api_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
    return response.json()