---
name: xai-image-gen
description: Generate images using xAI's Grok API (grok-imagine-image model).
---

# xai-image-gen

Generate images using xAI's Grok API (grok-imagine-image model).

## Description

Production-ready CLI tool for generating images via xAI's image generation API. Supports multiple output formats, resolutions, and batch generation. Automatically outputs MEDIA: paths for OpenClaw auto-attachment.

**Features:**
- 🎨 Simple CLI interface: `xai-gen "<prompt>"`
- 🖼️ Multiple output formats: URL download, base64 encoding
- 🔢 Batch generation (multiple images per prompt)
- ⚡ Fast, pure API implementation (Pi-safe)
- 🛡️ Robust error handling with user-friendly messages
- 📎 Auto-attaches generated images in OpenClaw
- 🎯 Uses xAI's native resolution (no size parameter needed)

## Installation

```bash
# Navigate to skills directory
cd ~/.openclaw/workspace/skills

# Clone or copy this skill
# (or install via clawhub when published)

# Install dependencies
pip3 install requests

# Ensure the script is executable
chmod +x xai-image-gen/xai-gen
```

**Set your xAI API key:**

```bash
export XAI_API_KEY="your-api-key-here"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`) to persist:

```bash
echo 'export XAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

## Usage

### Basic Usage

```bash
# Generate with simple prompt
xai-gen "sunset over mountains"

# Custom filename
xai-gen "cyberpunk city" --filename city.png

# Generate multiple images
xai-gen "futuristic vehicle" --n 3

# Base64 output (no download)
xai-gen "logo design" --format b64

# Verbose mode
xai-gen "space station" --verbose
```

### Options

```
positional arguments:
  prompt                Text description of the image to generate

options:
  -h, --help            Show help message
  --model MODEL         Model name (default: grok-imagine-image)
  --filename FILENAME   Output filename (default: out.png)
  --format {url,png,b64}
                        Response format: url (download), png (alias), b64 (base64)
  --n N                 Number of images to generate (default: 1)
  --verbose, -v         Show detailed progress
```

### Examples

**Generate a meme:**
```bash
xai-gen "dumbest trade meme: YOLO panic fail" --filename trade_meme.png
```

**Batch generation:**
```bash
xai-gen "logo variations for tech startup" --n 5
# Outputs: out_1.png, out_2.png, out_3.png, out_4.png, out_5.png
```

**High-quality artwork:**
```bash
xai-gen "photorealistic portrait of a cat astronaut" --filename cat_astronaut.png
```

### Integration with OpenClaw

The tool outputs `MEDIA: /path/to/image.png` which OpenClaw automatically detects and attaches to messages. Use in agent workflows:

```bash
# In an agent skill or automation
xai-gen "chart showing Q1 sales data" --filename sales_chart.png
# → Image auto-attaches to response
```

## API Details

- **Endpoint:** `https://api.x.ai/v1/images/generations`
- **Model:** `grok-imagine-image`
- **Authentication:** Bearer token via `XAI_API_KEY`
- **Rate Limits:** Subject to xAI API limits (check xAI docs)
- **Timeout:** 60s for generation, 30s for download

## Error Handling

The tool handles common errors gracefully:

- ❌ Missing API key → Clear instructions
- ❌ Network errors → Descriptive messages
- ❌ API timeouts → Retry suggestions
- ❌ Invalid parameters → Usage hints
- ❌ File write errors → Permission checks

## Requirements

- **Python:** 3.7+
- **Dependencies:** `requests`
- **API Key:** xAI API key (get from https://console.x.ai)
- **Network:** Internet connection required

## Platform Compatibility

- ✅ Linux (tested on Raspberry Pi)
- ✅ macOS
- ✅ Windows (via WSL or native Python)
- ✅ ARM64 / ARMv7 (Pi-safe, pure API calls)

## Troubleshooting

**"XAI_API_KEY not found"**
```bash
export XAI_API_KEY="xai-..."
```

**"requests library not found"**
```bash
pip3 install requests
```

**Permission denied**
```bash
chmod +x xai-gen
```

**API errors**
- Check API key validity
- Verify account has credits
- Check xAI status page

## License

MIT License - Free to use and modify

## Author

Built for OpenClaw by subagent xAI Image Gen Skill Builder

## Version

1.0.0 - Initial release
