# Style Transfer

Transform image style while preserving content.

## Techniques

### img2img (Stable Diffusion)

```python
from diffusers import StableDiffusionImg2ImgPipeline
import torch

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe.to("cuda")

result = pipe(
    prompt="oil painting style, impressionist",
    image=init_image,
    strength=0.6,  # 0=no change, 1=full generation
    guidance_scale=7.5
).images[0]
```

**Strength parameter:**
- 0.3-0.4 — Light style, preserves most detail
- 0.5-0.6 — Balanced transformation
- 0.7-0.8 — Heavy restyle, may lose detail

### ControlNet

```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny",
    torch_dtype=torch.float16
)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16
)

# Extract edges for structure guidance
import cv2
canny = cv2.Canny(image, 100, 200)

result = pipe(
    prompt="anime style illustration",
    image=canny,
    num_inference_steps=30
).images[0]
```

**ControlNet modes:**
- `canny` — Edge detection
- `depth` — Depth map
- `pose` — Human pose
- `lineart` — Line drawing

### IP-Adapter (Style Reference)

```python
from diffusers import StableDiffusionPipeline
from transformers import CLIPVisionModelWithProjection

# Use reference image as style guide
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models")
pipe.set_ip_adapter_scale(0.6)

result = pipe(
    prompt="a portrait",
    ip_adapter_image=style_reference,  # Your style image
    image=content_image
).images[0]
```

## Style Types

| Style | Prompt Keywords |
|-------|-----------------|
| Oil painting | oil painting, brushstrokes, impasto |
| Watercolor | watercolor, soft edges, wet medium |
| Anime | anime style, cel shaded, studio ghibli |
| Pencil sketch | pencil drawing, graphite, sketch |
| 3D render | 3D render, octane, blender |
| Pixel art | pixel art, 8-bit, retro |
| Photorealistic | hyperrealistic, photography, DSLR |

## Workflow

1. **Choose technique** based on control needed
2. **Start with low strength** (0.3-0.4)
3. **Iterate** — adjust strength and prompt
4. **ControlNet** for precise structure preservation
5. **Post-process** — color match to original if needed

## Best Practices

- **Lower strength = more original** — start low
- **ControlNet for precision** — when structure matters
- **Style reference images** — IP-Adapter for specific styles
- **Consistent results** — lock seed, batch variations
- **Resolution** — match input resolution

## Common Issues

- **Lost detail** — reduce strength
- **Wrong style** — add more specific keywords
- **Artifacts** — increase steps, reduce guidance
- **Color shift** — color correct after
