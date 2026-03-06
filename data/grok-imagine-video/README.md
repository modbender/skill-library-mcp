# Grok Imagine Video & Image

[![GitHub stars](https://img.shields.io/github/stars/DevvGwardo/grok-imagine-video?style=flat&logo=github)](https://github.com/DevvGwardo/grok-imagine-video)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A Python client and [OpenClaw](https://docs.openclaw.ai) skill for generating images and videos using [xAI's Grok Imagine APIs](https://docs.x.ai/developers/model-capabilities).

## Features

- **Text-to-Image** — Generate images from text (up to 10 variations)
- **Image Editing** — Edit images with natural language instructions
- **Text-to-Video** — Generate video clips from text descriptions
- **Image-to-Video** — Animate static images into motion video
- **Video Editing** — Apply filters, speed changes, color grading, and effects
- **Async Polling** — Non-blocking job management with progress callbacks
- **OpenClaw Integration** — Drop-in skill for Discord, Telegram, and WhatsApp bots

## Quick Start

1. **Get an API key** at [console.x.ai](https://console.x.ai/)

2. **Set your key**
   ```bash
   export XAI_API_KEY="your-key-here"
   ```

3. **Run it**
   ```python
   from scripts.grok_video_api import GrokImagineVideoClient

   client = GrokImagineVideoClient(api_key="your-key")

   # Generate a video
   result = client.text_to_video("A golden retriever running through a sunny meadow", duration=10)
   final = client.wait_for_completion(result["request_id"])
   client.download_video(final, "output.mp4")
   ```

## Usage

### Image Generation

```python
result = client.generate_image(
    prompt="A collage of London landmarks in a stenciled street-art style",
    n=4,                       # 1-10 variations
    aspect_ratio="16:9",
    response_format="b64_json" # or "url" (default)
)
```

### Image Editing

```python
result = client.edit_image(
    image_url="https://example.com/photo.jpg",
    prompt="Change the sky to a dramatic sunset"
)
```

### Text-to-Video

```python
result = client.text_to_video(
    prompt="Slow pan across a cyberpunk cityscape at night",
    duration=10,          # 1-15 seconds
    aspect_ratio="16:9",  # 16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3
    resolution="720p"     # 480p (faster) or 720p (higher quality)
)
```

### Image-to-Video

```python
result = client.image_to_video(
    image_url="https://example.com/landscape.jpg",
    prompt="Make the clouds drift slowly across the sky",
    duration=10
)
```

### Video Editing

```python
result = client.edit_video(
    video_url="https://example.com/clip.mp4",
    edit_prompt="Add a warm sunset filter and slow down to 50% speed"
)
```

## OpenClaw Skill Installation

```bash
mkdir -p ~/.openclaw/skills
cp grok-imagine-video.skill ~/.openclaw/skills/
cd ~/.openclaw/skills && unzip grok-imagine-video.skill
openclaw gateway restart
```

Then tell your bot things like *"Generate a video of a sunset over the ocean"* or *"Edit this image — make it look like a watercolor painting"*.

## API Limits

| Constraint | Value |
|---|---|
| Images per request | 1-10 |
| Video duration | 1-15 seconds |
| Video editing input limit | 8.7 seconds |
| Video resolution | 480p or 720p |
| Rate limit | 60 requests/min |
| Concurrent jobs | 15 per account |

Image and video URLs are **temporary** — download promptly after generation.

## Prompt Tips

- **Be descriptive** — *"A collage of London landmarks in a stenciled street-art style"*
- **Specify style/lighting** — *"Watercolor painting of a mountain lake at dawn with golden hour lighting"*
- **Include camera direction** for videos — *"Slow pan from left to right over a mountain range"*
- Use `n=4` to explore image variations; use 480p for fast video iteration, 720p for finals

## Project Structure

```
grok-imagine-video/
├── scripts/
│   └── grok_video_api.py      # Python client library
├── references/
│   └── api_reference.md       # Full API documentation
├── SKILL.md                   # OpenClaw skill definition
├── CHANGELOG.md               # Version history
└── README.md
```

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/) library
- xAI API key ([console.x.ai](https://console.x.ai/))
- [OpenClaw](https://docs.openclaw.ai) (only for chatbot integration)

## License

MIT
