---
name: multishot-ugc
description: |
  Generate 10 perspective/angle variations from a single image for multi-shot UGC videos.
  
  ✅ USE WHEN:
  - Have a hero image and need camera angle variations
  - Creating multi-scene UGC videos (need different shots)
  - Want close-ups, wide shots, side angles from one source
  - Building a video with scene changes
  
  ❌ DON'T USE WHEN:
  - Don't have a hero image yet → use morpheus-fashion-design first
  - Need completely different scenes/locations → use Morpheus multiple times
  - Just need one image → skip this step
  - Want to edit images manually → use nano-banana-pro
  
  INPUT: Single image (person with product)
  OUTPUT: 10 PNG variations with different perspectives
  
  TYPICAL PIPELINE: Morpheus → multishot-ugc → select best 4 → veed-ugc each → Remotion edit
---

# Multishot-UGC

Generate 10 perspective variations of an image using ComfyDeploy's MULTISHOT-UGC workflow.

## Overview

Multishot-UGC takes a single image and generates 10 different variations exploring different perspectives, angles, and compositions. These variations are designed to be used in VEED lip-sync workflows to create dynamic UGC-style promotional videos with varied camera shots.

## API Details

**Endpoint:** `https://api.comfydeploy.com/api/run/deployment/queue`
**Deployment ID:** `9ccbb29a-d982-48cc-a465-bae916f2c7fd`

## Required Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `input_image` | URL or path to the source image | Required |
| `text` | Description for exploration | "Explora distintas perspectivas de esta escena" |
| `resolution` | Output resolution | "2K" |
| `aspect_ratio` | Output aspect ratio | "9:16" |

## Usage

```bash
uv run ~/.clawdbot/skills/multishot-ugc/scripts/generate.py \
  --image "./person-with-product.png" \
  --output-dir "./multishot-output" \
  [--text "Custom exploration prompt"] \
  [--resolution 1K|2K|4K] \
  [--aspect-ratio 9:16|16:9|1:1|4:3|3:4]
```

### With URL:
```bash
uv run ~/.clawdbot/skills/multishot-ugc/scripts/generate.py \
  --image "https://example.com/image.png" \
  --output-dir "./variations"
```

## Output

The workflow generates 10 PNG images with variations:
- `1_00001_.png` through `10_00001_.png`

Each image explores a different perspective/angle of the original scene while maintaining subject identity and composition coherence.

## Workflow Integration

### Typical Pipeline

1. **Generate hero image with Morpheus/Ad-Ready**
   ```bash
   uv run morpheus... --output hero.png
   ```

2. **Create 10 angle variations**
   ```bash
   uv run multishot-ugc... --image hero.png --output-dir ./shots
   ```

3. **Select best variations for VEED lip-sync**
   ```bash
   # Review shots, then generate videos for chosen ones
   uv run veed-ugc... --image ./shots/3_00001_.png --brief "..."
   ```

## Notes

- Source image should be high quality (at least 1K resolution)
- Works best with images containing a clear subject/person
- Generation takes ~2-3 minutes for 10 variations
- All variations maintain the original aspect ratio unless specified
