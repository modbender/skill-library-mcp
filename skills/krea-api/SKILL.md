---
name: krea-api
description: Generate images via Krea.ai API (Flux, Imagen, Ideogram, Seedream, etc.)
version: 0.2.4
metadata:
  credentials:
    - id: krea
      description: Krea.ai API key (format: KEY_ID:SECRET)
      envVar: null
      file: ~/.openclaw/credentials/krea.json
      required: true
---

# Krea.ai Image Generation Skill

Generate images using Krea.ai's API with support for multiple models including Flux, Imagen 4, Ideogram 3.0, and more.

## Features

- ✅ Async job-based generation (POST → poll → result)
- ✅ Support for multiple image models
- ✅ Configurable parameters (width, height, steps, guidance, seed)
- ✅ Stdlib-only dependencies (no `requests` required)
- ✅ Secure credential handling with file permissions

## Security

This skill prioritizes security:

- **No webhook support** - Removed to prevent SSRF risks
- **Stdlib dependencies** - Minimal attack surface (uses `urllib` only)
- **File-based credentials** - Primary credential source with secure permissions
- **Input validation** - All parameters validated before API calls

### Credential Sources (in order of precedence)

1. **CLI arguments**: `--key-id` and `--secret` (for one-off use)
2. **File**: `~/.openclaw/credentials/krea.json`

### Note on Subprocess

The `--usage` flag uses `webbrowser.open()` (stdlib) to open the usage dashboard in a browser. No subprocess calls.

## Setup

1. Get your Krea.ai API credentials from https://docs.krea.ai/developers/api-keys-and-billing
2. Create the credentials file:
```bash
mkdir -p ~/.openclaw/credentials
```

3. Add your credentials:
```bash
echo '{"apiKey": "YOUR_KEY_ID:YOUR_SECRET"}' > ~/.openclaw/credentials/krea.json
```

4. Set secure permissions:
```bash
chmod 600 ~/.openclaw/credentials/krea.json
```

## Usage

### Command Line

```bash
# Generate an image
python3 krea_api.py --prompt "A sunset over the ocean"

# With specific model
python3 krea_api.py --prompt "Cyberpunk city" --model imagen-4

# Custom size
python3 krea_api.py --prompt "Portrait" --width 1024 --height 1280

# List available models
python3 krea_api.py --list-models

# Check recent jobs
python3 krea_api.py --jobs 10
```

### Python Script

```python
from krea_api import KreaAPI

api = KreaAPI()  # Reads from ~/.openclaw/credentials/krea.json

# Generate and wait
urls = api.generate_and_wait(
    prompt="A serene Japanese garden",
    model="flux",
    width=1024,
    height=1024
)
print(urls)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| prompt | str | required | Image description (max 1800 chars) |
| model | str | "flux" | Model name from table below |
| width | int | 1024 | Image width (512-2368) |
| height | int | 1024 | Image height (512-2368) |
| steps | int | 25 | Generation steps (1-100) |
| guidance_scale | float | 3.0 | Guidance scale (0-24) |
| seed | str | None | Random seed for reproducibility |

### Available Models

| Model | Best For |
|-------|----------|
| flux | General purpose, high quality |
| imagen-4 | Latest Google model |
| ideogram-3.0 | Text in images |
| seedream-4 | Fast generations |
| nano-banana | Quick previews |

Run `python3 krea_api.py --list-models` for full list.

## Check Usage

Krea.ai doesn't provide a public usage API. Check your usage at:

https://www.krea.ai/settings/usage-statistics

Or list recent jobs:

```bash
python3 krea_api.py --jobs 10
```

## File Locations

| Purpose | Path |
|---------|------|
| Credentials | `~/.openclaw/credentials/krea.json` |
| Script | `{skill}/krea_api.py` |
| Skill docs | `{skill}/SKILL.md` |

## Troubleshooting

### "API credentials required"

1. Check credentials file exists:
```bash
ls -la ~/.openclaw/credentials/krea.json
# Should show: -rw-------
```

2. Verify format (must have colon):
```json
{"apiKey": "KEY_ID:SECRET"}
```

⚠️ **Security**: Do NOT use `cat` to view the credentials file — it contains secrets.

### Model not found

Run `python3 krea_api.py --list-models` to see available models.

## Credits

Thanks to Claude Opus 4.5 for researching the correct API structure. The docs incorrectly suggest `/v1/images/flux` but the working endpoint is `/generate/image/bfl/flux-1-dev`.
