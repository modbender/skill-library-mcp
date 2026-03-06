# Image Editing Tools

Provider setup and API reference.

## Cloud APIs

### OpenAI (DALL-E 2)

```python
from openai import OpenAI
client = OpenAI()  # OPENAI_API_KEY env var

# Edit/Inpaint
response = client.images.edit(
    model="dall-e-2",
    image=open("image.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="description",
    size="1024x1024"
)
```

**Pricing:** $0.020/image (1024x1024)

### Stability AI

```python
import requests

response = requests.post(
    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image",
    headers={"Authorization": f"Bearer {API_KEY}"},
    files={"init_image": open("image.png", "rb")},
    data={
        "text_prompts[0][text]": "description",
        "init_image_mode": "IMAGE_STRENGTH",
        "image_strength": 0.35
    }
)
```

### ClipDrop

```python
import requests

# Background removal
response = requests.post(
    "https://clipdrop-api.co/remove-background/v1",
    headers={"x-api-key": API_KEY},
    files={"image_file": open("photo.jpg", "rb")}
)

# Cleanup (remove objects)
response = requests.post(
    "https://clipdrop-api.co/cleanup/v1",
    headers={"x-api-key": API_KEY},
    files={
        "image_file": open("photo.jpg", "rb"),
        "mask_file": open("mask.png", "rb")
    }
)

# Relight
response = requests.post(
    "https://clipdrop-api.co/relight/v1",
    headers={"x-api-key": API_KEY},
    files={"image_file": open("photo.jpg", "rb")},
    data={"mode": "sunrise"}
)
```

### remove.bg

```python
response = requests.post(
    "https://api.remove.bg/v1.0/removebg",
    headers={"X-Api-Key": API_KEY},
    files={"image_file": open("photo.jpg", "rb")},
    data={"size": "auto"}
)
```

## Local Tools

### IOPaint

```bash
pip install iopaint
iopaint start --model lama --port 8080
```

Access web UI at http://localhost:8080

### rembg

```bash
pip install rembg[gpu]  # or rembg for CPU
rembg i input.jpg output.png
```

### Real-ESRGAN

```bash
pip install realesrgan
realesrgan-ncnn-vulkan -i input.jpg -o output.png
```

### GFPGAN

```bash
pip install gfpgan
python inference_gfpgan.py -i inputs/ -o results/
```

## Desktop Apps

| App | Features | Price |
|-----|----------|-------|
| Photoshop | Generative Fill, everything | $23/mo |
| Topaz Photo AI | Upscale, denoise, sharpen | $199 |
| Affinity Photo | Manual editing, AI plugins | $70 |
| GIMP + plugins | Free, extensible | Free |

## Comparison

| Task | Best Free | Best Paid |
|------|-----------|-----------|
| Inpainting | IOPaint | Photoshop |
| Background removal | rembg | remove.bg |
| Upscaling | Real-ESRGAN | Topaz |
| Face restoration | GFPGAN | — |
| All-in-one | ComfyUI | Photoshop |
