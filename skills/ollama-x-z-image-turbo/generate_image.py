import base64
import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.getenv("OLLAMA_IMAGE_MODEL", "x/z-image-turbo:latest")

class ImageRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024
    steps: int = 20
    seed: int | None = None
    negative: str | None = None

@app.post("/generate-image/", response_class=Response)
async def generate_image(request: ImageRequest):
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": MODEL,
        "prompt": request.prompt,
        "stream": False,
        "options": {
            "width": request.width,
            "height": request.height,
            "steps": request.steps,
        },
    }
    if request.seed is not None:
        payload["options"]["seed"] = request.seed
    if request.negative:
        payload["options"]["negative"] = request.negative

    r = requests.post(url, json=payload, timeout=180)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=r.text)

    data = r.json()
    # Ollama image models return base64 in images[]
    if "images" in data and data["images"]:
        img_b64 = data["images"][0]
    elif "response" in data:
        img_b64 = data["response"]
    else:
        raise HTTPException(status_code=500, detail="No image data in response")

    try:
        img = base64.b64decode(img_b64)
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid image base64")

    return Response(content=img, media_type="image/png")
