# Upscaling

Increase image resolution with AI enhancement.

## Tools

### Real-ESRGAN (Local, Free)

```bash
# Install
pip install realesrgan

# CLI
realesrgan-ncnn-vulkan -i input.jpg -o output.png -n realesrgan-x4plus
```

```python
from realesrgan import RealESRGAN
import torch

model = RealESRGAN(torch.device("cuda"), scale=4)
model.load_weights("weights/RealESRGAN_x4plus.pth")

result = model.predict(input_image)
```

**Models:**
- `realesrgan-x4plus` — General images (4x)
- `realesrgan-x4plus-anime` — Anime/illustrations
- `realesr-general-x4v3` — Latest general model

### Topaz Gigapixel AI

Commercial desktop app:
- Up to 6x upscale
- Face recovery built-in
- Batch processing
- ~$99 one-time

### Magnific AI

```bash
curl -X POST "https://api.magnific.ai/v1/upscale" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "image=@photo.jpg" \
  -F "scale=2"
```

**Features:**
- "Creativity" slider adds AI detail
- Best for artistic enhancement
- ~$0.50/image

### Replicate (Various Models)

```python
import replicate

output = replicate.run(
    "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
    input={
        "image": open("photo.jpg", "rb"),
        "scale": 4,
        "face_enhance": True
    }
)
```

## Scale Factors

| Original | 2x | 4x | 8x |
|----------|-----|-----|-----|
| 512x512 | 1024 | 2048 | 4096 |
| 1080p | 4K | 8K | — |
| 720p | 1440p | 4K | 8K |

**Rule:** Don't upscale beyond 4x in one pass for best quality.

## When to Upscale

- **Print production** — need 300 DPI
- **Large displays** — billboards, banners
- **Old photos** — restore low-res originals
- **AI-generated images** — increase from 1024px

## Pipeline Order

1. **Restore faces first** — GFPGAN/CodeFormer
2. **Remove artifacts** — denoise if needed
3. **Upscale** — Real-ESRGAN or similar
4. **Sharpen** — light unsharp mask if soft

## Quality Tips

- **Don't over-upscale** — 4x max in one pass
- **Match model to content** — anime model for anime
- **Face enhance** — enable for portraits
- **Check artifacts** — AI can add weird textures
- **Preserve grain** — add back film grain if needed

## Comparison

| Tool | Scale | Speed | Quality | Cost |
|------|-------|-------|---------|------|
| Real-ESRGAN | 4x | Fast | Good | Free |
| Topaz | 6x | Medium | Excellent | $99 |
| Magnific | 2-4x | Medium | Best (creative) | $$$ |
| Replicate | Varies | Fast | Good | Per-use |
