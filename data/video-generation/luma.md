# Luma AI (Dream Machine)

**Best for:** Camera movements, cinematic shots, interpolation

**API:** https://docs.lumalabs.ai/

## Setup

1. Get API key: https://lumalabs.ai/dream-machine/api/keys
2. Use as Bearer token in requests

## Quick Start (curl)

```bash
curl -X POST https://api.lumalabs.ai/dream-machine/v1/generations \
  -H "Authorization: Bearer luma-xxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "an old lady laughing underwater",
    "model": "ray-2",
    "resolution": "720p",
    "duration": "5s"
  }'
```

## Models

- `ray-2` — Current best
- `ray-flash-2` — Faster, lower quality

## Resolutions

540p, 720p, 1080p, 4K

## Features

- `keyframes.frame0` / `frame1` — Start/end images
- `loop: true` — Seamless loop
- `concepts` — Camera motions (dolly_zoom, etc.)
- Extend/interpolate existing generations

## Pricing

- ~$0.032 per second (ray-2)
- ~$0.008 per second (ray-flash-2)
