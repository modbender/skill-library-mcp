---
name: skill-runway-video-gen
version: 1.0.0
description: Generate short product videos from images using Runway Gen4 Turbo. Use for TikTok ads, UGC-style product demos, Reels, and YouTube Shorts.
metadata:
  openclaw:
    requires: { bins: ["uv"] }
---

# skill-runway-video-gen

Wraps Runway Gen4 Turbo image-to-video API. Point at a product image, describe the motion, get an MP4. No browser needed.

## Usage

```bash
uv run scripts/generate_video.py \
  --image product.jpg \
  --prompt "water droplets falling, soft bokeh, slow motion" \
  --output output.mp4 \
  --duration 10 \
  --ratio 720:1280
```

## Args

| Arg | Default | Description |
|---|---|---|
| `--image` | required | Path to source product image |
| `--prompt` | `""` | Motion description (optional but recommended) |
| `--output` | required | Output MP4 path |
| `--duration` | `10` | Video length: 5 or 10 seconds |
| `--ratio` | `720:1280` | Aspect ratio (vertical for TikTok) |

## Config

API key is read from (in order):
1. `RUNWAY_API_KEY` environment variable
2. `~/tiktok-api.json` → `runway.apiKey`

## Cost

| Duration | Cost |
|---|---|
| 5s | $0.25 |
| 10s | $0.50 |

Always use 10s — you get more content to work with.

## Known quirks

**Last 1–2s often freezes.** Fix: stretch to 12s at 0.83x speed using MoviePy:

```python
from moviepy import VideoFileClip
clip = VideoFileClip("output.mp4")
slow = clip.with_effects([vfx.MultiplySpeed(0.83)])
slow.write_videofile("output_12s.mp4", fps=30)
```

## Rate limits

No per-minute quota (unlike Veo). Runway charges per second of output.

## Pipeline integration

This skill feeds into `skill-tiktok-video-pipeline` as the video generation step. The pipeline handles slowmo stretch and caption overlay automatically.
