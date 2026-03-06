# xai-image-gen

🎨 **Generate images using xAI's Grok API**

Production-ready OpenClaw skill for generating images via xAI's `grok-imagine-image` model. Fast, reliable, and Pi-safe.

## Quick Start

```bash
# Install
pip3 install requests
export XAI_API_KEY="your-key-here"

# Generate
./xai-gen "sunset over mountains"
```

## Features

✅ Simple CLI: `xai-gen "<prompt>"`  
✅ Multiple formats (URL download, base64)  
✅ Batch generation (`--n 3`)  
✅ Auto-attachment in OpenClaw (outputs `MEDIA:` paths)  
✅ Robust error handling  
✅ Pi-safe (pure API calls, no heavy deps)

## Installation

```bash
cd ~/.openclaw/workspace/skills
# Copy or clone this skill
pip3 install -r xai-image-gen/requirements.txt
chmod +x xai-image-gen/xai-gen
export XAI_API_KEY="xai-..."
```

## Usage

```bash
# Basic
xai-gen "cyberpunk city"

# With options
xai-gen "abstract art" --filename art.png --n 3 --verbose

# Base64 format
xai-gen "logo design" --format b64
```

## Documentation

See [SKILL.md](SKILL.md) for complete documentation.

## Requirements

- Python 3.7+
- `requests` library
- xAI API key ([get one here](https://console.x.ai))

## License

MIT - See [LICENSE](LICENSE)
