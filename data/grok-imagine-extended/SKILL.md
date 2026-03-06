---
name: grok-imagine
description: "Generate images and videos using xAI Grok Imagine Extended. Text-to-image, image editing, text-to-video, image-to-video. Use when: user asks to generate, create, or draw an image, or create/animate a video. NOT for: image analysis/understanding (use the image tool instead). Triggers: generate image, create image, draw, grok imagine, make a picture, text to image, generate video, animate, text to video."
homepage: https://docs.x.ai/docs/guides/image-generations
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "env": ["XAI_API_KEY"] },
        "primaryEnv": "XAI_API_KEY",
      },
  }
---

# Grok Imagine Extended (xAI Image & Video Generation)

Generate images and videos from text prompts using the xAI API.

## Image Generation

```bash
python3 {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png"
```

With options:

```bash
python3 {baseDir}/scripts/generate_image.py --prompt "a cyberpunk city at night" --filename "city.png" --resolution 2k --aspect-ratio 16:9
```

## Image Editing

Single source image:

```bash
python3 {baseDir}/scripts/generate_image.py --prompt "make it a watercolor painting" --filename "edited.png" -i "/path/to/source.jpg"
```

Multiple source images (up to 3):

```bash
python3 {baseDir}/scripts/generate_image.py --prompt "combine into one scene" --filename "combined.png" -i img1.png -i img2.png
```

## Video Generation

Text-to-video:

```bash
python3 {baseDir}/scripts/generate_image.py --prompt "a cat walking through flowers" --filename "cat.mp4" --video --duration 5
```

Image-to-video (animate a still):

```bash
python3 {baseDir}/scripts/generate_image.py --prompt "add gentle camera zoom and wind" --filename "animated.mp4" --video -i photo.jpg --duration 5
```

## Models

| Model | Type | Cost |
|-------|------|------|
| `grok-imagine-image` | Image (default) | $0.02/img |
| `grok-imagine-image-pro` | Image (high quality) | $0.07/img |
| `grok-imagine-video` | Video (auto for --video) | $0.05/sec |

Select model with `--model grok-imagine-image-pro`. Video mode always uses `grok-imagine-video`.

## All Options

| Flag | Description |
|------|-------------|
| `--prompt`, `-p` | Text description (required) |
| `--filename`, `-f` | Output path (required) |
| `-i` | Input image for editing/animation (repeatable, max 3 for images, 1 for video) |
| `--model`, `-m` | Image model (default: grok-imagine-image) |
| `--aspect-ratio`, `-a` | 1:1, 16:9, 9:16, 4:3, 3:4, etc. |
| `--resolution`, `-r` | Image: 1k/2k. Video: 480p/720p |
| `--n` | Number of images 1-10 (default 1) |
| `--video` | Generate video instead of image |
| `--duration`, `-d` | Video duration 1-15 seconds (default 5) |
| `--api-key`, `-k` | Override XAI_API_KEY |

## API Key

- `XAI_API_KEY` env var
- Or set `skills."grok-imagine".apiKey` / `skills."grok-imagine".env.XAI_API_KEY` in `~/.openclaw/openclaw.json`
- Or auto-read from `~/keys.txt`

## Notes

- Use timestamps in filenames: `2026-03-01-cyberpunk-city.png`
- The script prints a `MEDIA:` line for OpenClaw to auto-attach on supported chat providers
- Do not read the image back; report the saved path only
- Image URLs from xAI are temporary; the script downloads them immediately
- Video generation is async and polls until done (can take 1-5 minutes)
- 2k resolution returns PNG; 1k returns JPEG
