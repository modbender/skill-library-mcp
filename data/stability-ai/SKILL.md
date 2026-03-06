---
name: stability-ai
description: Generate high-quality images via Stability AI API (SDXL, SD3, Stable Image Core). Use when user asks to "generate image", "make a picture", or "draw this".
---

# Stability AI Skill

## Setup
1. Copy `.env.example` to `.env`.
2. Set `STABILITY_API_KEY` in `.env`.
3. Optional: Set `API_HOST` if using a custom endpoint.

## Usage
- **Role**: Digital Artist.
- **Trigger**: "Draw a cat", "Generate cyberpunk city", "Create an image".
- **Output**: Local file path to the generated image and JSON metadata.

## Commands
(The script automatically handles dependencies on first run)

```bash
# Basic generation
scripts/generate "A futuristic city with neon lights"

# Aspect ratio (1:1, 16:9, 9:16, 21:9, 4:3, 3:4)
scripts/generate "Landscape painting" --ratio 16:9

# Style preset
scripts/generate "Portrait of a warrior" --style photographic

# Seed for reproducibility
scripts/generate "Abstract art" --seed 42

# Negative prompt
scripts/generate "Beautiful sunset" --negative "blurry, low quality"

# Output format (png, jpg, webp)
scripts/generate "Nature scene" --format webp

# Advanced: Custom model, steps, CFG scale
scripts/generate "Fantasy landscape" \
  --model stable-diffusion-3-medium \
  --steps 50 \
  --cfg 7.0 \
  --ratio 21:9

# V2 API (experimental)
scripts/generate "Modern architecture" --v2

# Combined options
scripts/generate "Cyberpunk street at night" \
  --ratio 16:9 \
  --style neon-punk \
  --seed 123 \
  --format jpg \
  --steps 45 \
  --cfg 6.5
```

## Features

### Style Presets
Available styles: enhance, anime, photographic, digital-art, comic-book, fantasy-art, line-art, analog-film, neon-punk, isometric, low-poly, origami, modeling-compound, cinematic, 3d-model, pixel-art, tile-texture

### Aspect Ratios
Supported: 1:1 (default), 16:9, 9:16, 21:9, 4:3, 3:4

### Output Formats
- PNG (default, lossless)
- JPEG/JPG (lossy, smaller size)
- WebP (modern, efficient)

### Metadata
Each generated image includes a JSON metadata file with:
- Prompt and negative prompt
- Model, parameters, and settings
- Generation timestamp
- API version used

## Models
- Default: SDXL 1.0 (`stable-diffusion-xl-1024-v1-0`)
- See `references/models.md` for complete model list, API versions, and credit costs.

## Auto-Cleanup
Automatically keeps the last 20 generated images. Older files and their metadata are removed to save disk space.
