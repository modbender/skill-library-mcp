---
name: deepseek-ocr
description: OCR text recognition using DeepSeek-OCR model. Use when user asks for OCR, text recognition, image text extraction, screenshot recognition, or converting images to text/markdown.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "bins": ["curl", "jq", "base64"], "env": ["DEEPSEEK_OCR_API_KEY"] },
        "primaryEnv": "DEEPSEEK_OCR_API_KEY",
      },
  }
---

# DeepSeek OCR

Recognize text in images using the DeepSeek-OCR model.

## Quick start

```bash
{baseDir}/scripts/ocr.sh /path/to/image.jpg
```

## Usage

```bash
{baseDir}/scripts/ocr.sh <image_path> [output_format]
```

Parameters:
- `<image_path>`: Local image file (jpg, png, webp, gif, bmp)
- `[output_format]`: Optional, defaults to `markdown`. Can be `text`, `json`, etc.

## Examples

```bash
# Convert to markdown (default)
{baseDir}/scripts/ocr.sh /path/to/image.jpg

# Convert to plain text
{baseDir}/scripts/ocr.sh /path/to/image.png text

# Extract table as JSON
{baseDir}/scripts/ocr.sh /path/to/table.jpg "extract table as json"
```

## Remote URL images

The model only supports base64-encoded images. For remote URLs, download first:

```bash
curl -s -o /tmp/image.jpg "https://example.com/image.jpg"
{baseDir}/scripts/ocr.sh /tmp/image.jpg
```

## API key

Set `DEEPSEEK_OCR_API_KEY`, or configure in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    "deepseek-ocr": {
      apiKey: "YOUR_KEY_HERE",
    },
  },
}
```

Default API URL: `https://api.modelverse.cn/v1/chat/completions`
Override with `DEEPSEEK_OCR_API_URL` if needed.