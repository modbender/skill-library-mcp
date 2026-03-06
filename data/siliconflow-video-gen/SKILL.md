---
name: siliconflow-video-gen
description: Generate videos using SiliconFlow API with Wan2.2 model. Supports both Text-to-Video and Image-to-Video.
env:
  - SILICONFLOW_API_KEY
files:
  config:
    - ~/.openclaw/openclaw.json
---

# SiliconFlow Video Generation Skill

Generate videos using SiliconFlow API with Wan2.2 model. Supports both Text-to-Video and Image-to-Video.

## Features

- 🎬 **Text-to-Video**: Generate videos from text descriptions
- 🖼️ **Image-to-Video**: Animate static images with motion
- 🎥 **Cinematic Quality**: Powered by Wan2.2 (14B params)
- 🔑 **Auto API Key Detection**: Reads from environment or OpenClaw config

## Requirements

- **Environment Variable**: `SILICONFLOW_API_KEY`
- **Optional Config File**: `~/.openclaw/openclaw.json` (for auto-detect)

## Installation

```bash
npx clawhub install siliconflow-video-gen
```

## Configuration

Set your SiliconFlow API key:

```bash
export SILICONFLOW_API_KEY="your-api-key"
```

Or configure in OpenClaw:

```json
{
  "models": {
    "providers": {
      "siliconflow": {
        "apiKey": "your-api-key"
      }
    }
  }
}
```

## Usage

### Text-to-Video

```bash
python3 scripts/generate.py "A woman walking in a blooming garden, cinematic shot"
```

### Image-to-Video

```bash
python3 scripts/generate.py "Camera slowly zooming in" --image-url https://example.com/image.jpg
```

## Models

| Model | Type | Cost |
|-------|------|------|
| `Wan-AI/Wan2.2-T2V-A14B` | Text-to-Video | ¥2/video |
| `Wan-AI/Wan2.2-T2V-A14B` | Image-to-Video | ¥2/video |

## Security Notes

- This skill requires an API key to call SiliconFlow services
- The script reads `~/.openclaw/openclaw.json` only to auto-detect API keys
- No sensitive data is transmitted except to `api.siliconflow.cn`
- Review the code at `scripts/generate.py` before providing credentials

## Author

MaxStorm Team

## License

MIT
