# Background Removal

Extract subjects from images with transparent backgrounds.

## Tools

### remove.bg (API)

```bash
curl -X POST "https://api.remove.bg/v1.0/removebg" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -F "image_file=@photo.jpg" \
  -F "size=auto" \
  -o "result.png"
```

```python
import requests

response = requests.post(
    "https://api.remove.bg/v1.0/removebg",
    files={"image_file": open("photo.jpg", "rb")},
    data={"size": "auto"},
    headers={"X-Api-Key": "YOUR_API_KEY"}
)
with open("result.png", "wb") as f:
    f.write(response.content)
```

**Pricing:** ~$0.20/image (50 free/month)

### ClipDrop (Stability AI)

```python
import requests

response = requests.post(
    "https://clipdrop-api.co/remove-background/v1",
    files={"image_file": open("photo.jpg", "rb")},
    headers={"x-api-key": "YOUR_API_KEY"}
)
```

**Features:** Background removal, cleanup, relighting

### Photoroom API

```python
response = requests.post(
    "https://sdk.photoroom.com/v1/segment",
    files={"image_file": open("photo.jpg", "rb")},
    headers={"x-api-key": "YOUR_API_KEY"}
)
```

### Local (rembg)

```bash
pip install rembg

# CLI
rembg i input.jpg output.png

# Python
from rembg import remove
from PIL import Image

output = remove(Image.open("input.jpg"))
output.save("output.png")
```

**Models:**
- `u2net` — General purpose (default)
- `u2net_human_seg` — Optimized for people
- `silueta` — Faster, smaller

## Batch Processing

```python
from rembg import remove
from pathlib import Path

for img_path in Path("input/").glob("*.jpg"):
    result = remove(Image.open(img_path))
    result.save(f"output/{img_path.stem}.png")
```

## Edge Refinement

Raw removal often has rough edges:

1. **Feather edges** — Gaussian blur on alpha channel
2. **Matting models** — Use dedicated matting for hair/fur
3. **Manual cleanup** — Touch up in photo editor

## Use Cases

- Product photography
- Profile pictures
- Compositing
- E-commerce listings
- Marketing materials

## Quality Tips

- **Good lighting** — clear subject separation helps
- **High contrast** — distinct foreground/background
- **Clean backgrounds** — simpler = better results
- **Check hair/fur** — often needs manual refinement
