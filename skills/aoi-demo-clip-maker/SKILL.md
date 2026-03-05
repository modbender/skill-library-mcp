# AOI Demo Clip Maker (macOS)

S-DNA: `AOI-2026-0215-SDNA-CLIP01`

## What this is
A **terminal-only** (public-safe) utility skill to create hackathon demo clips on **macOS**.

It wraps `ffmpeg/ffprobe` to:
- list capture devices (avfoundation)
- record a screen for N seconds
- crop the top bar (menu/title)
- trim clips
- use simple presets

## What this is NOT
- No YouTube upload
- No form submission
- No external posting
- No secret handling

## Requirements
- macOS
- `ffmpeg` and `ffprobe` installed
- Screen Recording permission granted to your terminal app

## Commands
### 1) List devices (avfoundation)
```bash
aoi-clip devices
```

### 2) Record (screen capture)
```bash
# pixel_format auto-fallback is enabled by default
# (tries: uyvy422 → nv12 → yuyv422 → 0rgb → bgr0)
aoi-clip record --out tempo_demo_raw.mp4 --duration 15 --fps 30 --screen "Capture screen 0"

# optionally force a specific pixel format
# aoi-clip record --out tempo_demo_raw.mp4 --duration 15 --fps 30 --screen "Capture screen 0" --pixel uyvy422
```

### 3) Crop top bar
```bash
# explicit crop
aoi-clip crop --in tempo_demo_raw.mp4 --out tempo_demo_crop.mp4 --top 150

# auto-recommend top crop based on video height (still applies crop, but chooses a value)
aoi-clip crop --in tempo_demo_raw.mp4 --out tempo_demo_crop.mp4 --top auto
```

### 4) Trim
```bash
aoi-clip trim --in tempo_demo_crop.mp4 --out tempo_demo_15s.mp4 --from 0 --to 15
```

### 5) Preset: terminal
```bash
aoi-clip preset terminal --out demo.mp4
```

## Security / Audit posture
This skill runs local `ffmpeg/ffprobe` only, using a **strict allowlist** of binaries and arguments.

## Release governance (public)
We publish AOI skills for free and keep improving them. Every release must pass our Security Gate and include an auditable changelog. We do not ship updates that weaken security or licensing clarity. Repeated violations trigger progressive restrictions (warnings → publish pause → archive).

## Support
- Issues / bugs / requests: https://github.com/edmonddantesj/aoi-skills/issues
- Please include the skill slug: `aoi-demo-clip-maker`

## License
MIT
