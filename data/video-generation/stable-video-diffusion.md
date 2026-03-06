# Stable Video Diffusion (Local)

**Best for:** Privacy, no API costs, research/experimentation

## Requirements

- GPU: 12GB+ VRAM (RTX 3080/4080 or better)
- CUDA 11.8+
- Python 3.10+

## Setup

```bash
pip install diffusers transformers accelerate
```

## Quick Start

```python
import torch
from diffusers import StableVideoDiffusionPipeline
from PIL import Image

pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt",
    torch_dtype=torch.float16
)
pipe.to("cuda")

image = Image.open("input.png").resize((1024, 576))
frames = pipe(image, num_frames=25).frames[0]
```

## Models

- `stable-video-diffusion-img2vid` — 14 frames
- `stable-video-diffusion-img2vid-xt` — 25 frames

## Limitations

- Image-to-video only (no text-to-video)
- Fixed resolution: 1024x576
- No audio
