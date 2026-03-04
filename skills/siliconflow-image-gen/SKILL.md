---
name: siliconflow-image-gen
description: Generate images using SiliconFlow API (FLUX.1, Stable Diffusion, etc.)
env:
  - SILICONFLOW_API_KEY
files:
  config:
    - ~/.openclaw/openclaw.json
---

# SiliconFlow Image Generation Skill

Generate images using SiliconFlow API with support for FLUX.1, Stable Diffusion, and more.

## Features

- 🎨 **Multiple Models**: FLUX.1-schnell (free), FLUX.1-dev, Stable Diffusion 3.5
- 🔑 **Auto API Key Detection**: Reads from environment or OpenClaw config
- 💾 **Auto Download**: Saves generated images locally
- 📱 **OpenClaw Ready**: Designed for OpenClaw Agent integration

## Requirements

- **Environment Variable**: `SILICONFLOW_API_KEY`
- **Optional Config File**: `~/.openclaw/openclaw.json` (for auto-detect)

## Installation

```bash
npx clawhub install siliconflow-image-gen
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

### Command Line

```bash
# Generate with default model (FLUX.1-schnell)
python3 scripts/generate.py "A cup of coffee on wooden table"

# Specify model
python3 scripts/generate.py "Sunset over mountains" --model "black-forest-labs/FLUX.1-dev"

# Save to file
python3 scripts/generate.py "Cute cat" --output ~/Desktop/cat.png
```

## Available Models

| Model | Cost | Quality | Speed |
|-------|------|---------|-------|
| `black-forest-labs/FLUX.1-schnell` | Free | Good | Fast |
| `black-forest-labs/FLUX.1-dev` | Paid | Excellent | Medium |
| `stabilityai/stable-diffusion-3-5-large` | Paid | Excellent | Medium |

## Security Notes

- This skill requires an API key to call SiliconFlow services
- The script reads `~/.openclaw/openclaw.json` only to auto-detect API keys
- No sensitive data is transmitted except to `api.siliconflow.cn`
- Review the code at `scripts/generate.py` before providing credentials

## Author

MaxStorm Team

## License

MIT
