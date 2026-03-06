# Outpainting

Extend an image beyond its original borders.

## How It Works

1. Place original image on larger canvas
2. Mask the empty areas (white = generate here)
3. Describe what should appear in extended areas
4. AI generates content matching style and context

## Tools

### DALL-E 2 (OpenAI)

```python
from openai import OpenAI
from PIL import Image
import io

client = OpenAI()

# Create extended canvas
original = Image.open("photo.png")
extended = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
extended.paste(original, (256, 256))  # Center original

# Create mask (transparent = edit)
mask = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
mask.paste(Image.new("RGBA", original.size, (0, 0, 0, 0)), (256, 256))

response = client.images.edit(
    model="dall-e-2",
    image=to_bytes(extended),
    mask=to_bytes(mask),
    prompt="Continue the landscape with mountains in the distance"
)
```

### Stable Diffusion Outpaint

```python
from diffusers import StableDiffusionInpaintPipeline

# Same as inpainting, but with extended canvas
# Original image centered, mask covers new areas

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
)

result = pipe(
    prompt="expansive landscape, same style",
    image=extended_image,
    mask_image=outpaint_mask,
    num_inference_steps=50
).images[0]
```

### Photoshop Generative Fill

1. Select > All
2. Image > Canvas Size (increase dimensions)
3. Select empty areas with Magic Wand
4. Edit > Generative Fill
5. Enter prompt or leave blank

## Aspect Ratio Expansion

**Portrait to Landscape:**
- Extend left and right
- Prompt for environmental context

**Landscape to Portrait:**
- Extend top and bottom
- Consider sky above, ground below

**Square to Cinematic (16:9):**
- Add 280px each side for 1080p
- Describe scene continuation

## Best Practices

- **Overlap slightly** — let AI see edge context
- **Match lighting direction** — describe consistent light
- **Extend in steps** — don't 4x the canvas at once
- **Describe style** — "same artistic style", "photorealistic"

## Common Issues

- **Style mismatch** — add style keywords to prompt
- **Repeated elements** — AI may duplicate objects
- **Perspective errors** — complex scenes may warp
- **Seam lines** — blend with photo editor after
