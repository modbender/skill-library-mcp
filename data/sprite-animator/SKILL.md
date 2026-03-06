---
name: sprite-animator
description: Generate animated pixel art sprites from any image using AI. Send a photo, get a 16-frame animated GIF.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎮",
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---

# Sprite Animator

Generate animated pixel art sprites from any image. Uses nano-banana-pro (Gemini) to create a 16-frame sprite sheet in a single request, then assembles it into an animated GIF.

## Quick Start

```bash
# Wave animation (default 16 frames)
uv run --with sprite-animator sprite-animator -i photo.png -o sprite.gif -a wave

# Bounce animation with larger sprites
uv run --with sprite-animator sprite-animator -i avatar.png -o bounce.gif -a bounce -s 256

# Keep the raw sprite sheet and individual frames
uv run --with sprite-animator sprite-animator -i pet.jpg -o dance.gif -a dance --keep-sheet --keep-frames
```

## Animations

| Type | Description |
|------|-------------|
| `idle` | Subtle breathing + blinking loop |
| `wave` | Arm raises, waves back and forth, lowers |
| `bounce` | Crouch → jump → land → recover |
| `dance` | Lean, spin, jump — fun and energetic |

## Options

| Flag | Description |
|------|-------------|
| `-i, --input` | Input image (photo, drawing, etc.) |
| `-o, --output` | Output GIF path |
| `-a, --animation` | Animation type: idle, wave, bounce, dance (default: idle) |
| `-d, --duration` | Frame duration in ms (default: 100) |
| `-s, --size` | Output sprite size in px (default: 128) |
| `-r, --resolution` | Generation resolution: 1K or 2K (default: 1K) |
| `--keep-sheet` | Save the raw sprite sheet |
| `--keep-frames` | Save individual frame PNGs |
| `-v, --verbose` | Verbose output |

## How It Works

1. Creates a labeled 4x4 grid template (16 cells)
2. Sends the template + source image to Gemini in ONE request
3. AI fills each cell with a pixel art frame following the animation sequence
4. Frames are extracted from the sheet and assembled into a looping GIF

Single-request generation ensures consistent style across all frames.

## Source

https://github.com/Olafs-World/sprite-animator
