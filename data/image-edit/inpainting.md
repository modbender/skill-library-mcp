# Inpainting

Replace or remove parts of an image using AI.

## How It Works

1. Provide source image
2. Create mask (white = area to change)
3. Optionally describe replacement content
4. AI fills masked area matching surrounding context

## Tools

### DALL-E 2 (OpenAI)

```python
from openai import OpenAI
client = OpenAI()

response = client.images.edit(
    model="dall-e-2",
    image=open("image.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunny beach with palm trees",
    size="1024x1024"
)
```

**Requirements:**
- Image must be square PNG
- Mask: transparent areas = edit zone
- Max 4MB per file

### Stable Diffusion Inpaint

```python
from diffusers import StableDiffusionInpaintPipeline
import torch

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
)
pipe.to("cuda")

result = pipe(
    prompt="A fluffy cat",
    image=init_image,
    mask_image=mask,
    num_inference_steps=30,
    guidance_scale=7.5
).images[0]
```

**Key parameters:**
- `strength` — How much to change (0.5-1.0)
- `guidance_scale` — Prompt adherence (5-15)

### IOPaint (Local, Free)

```bash
# Install
pip install iopaint

# Run web UI
iopaint start --model lama --port 8080
```

**Models:**
- `lama` — Fast, good for object removal
- `ldm` — Better quality, slower
- `sd` — Stable Diffusion backend

## Best Practices

- **Extend mask slightly** — cover edges of object to remove
- **Describe surroundings** — "grassy field" helps context
- **Multiple passes** — for large areas, edit in chunks
- **Clean up edges** — blend modes in photo editor

## Object Removal (No Prompt)

For pure removal without replacement:
- Use LaMa model (designed for removal)
- Leave prompt empty or minimal
- AI infers from surrounding context

## Common Issues

- **Visible seams** — feather mask edges
- **Wrong content** — be more specific in prompt
- **Repeating patterns** — edit in smaller sections
- **Color mismatch** — adjust levels after inpainting
