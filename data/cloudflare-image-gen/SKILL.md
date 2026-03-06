---
name: cloudflare-image-gen
description: Generate images using Cloudflare Workers AI flux-1-schnell model. Use when user requests image generation with text-to-image using Cloudflare Workers API.
---

# Cloudflare Image Generation

This skill generates images using Cloudflare Workers AI `@cf/black-forest-labs/flux-1-schnell` model.

## Credentials

- Account ID: `1e89d3ce76cbfef3b5c340e3984b7a52`
- Token: `aCTA2KaKa1n3ayFDL-LPmZ-JgUC0HHgA5Msy18Bk`
- Model: `@cf/black-forest-labs/flux-1-schnell`

## Usage

Run the script directly:

```bash
python3 /home/ubuntu/.openclaw/workspace/skills/cloudflare-image-gen/scripts/generate_image.py "your prompt here" -o output.png
```

Or use the Python function:

```python
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/skills/cloudflare-image-gen/scripts')
from generate_image import generate_image

output_path = generate_image("a black horse")
```

## Output

The script saves the generated image as PNG and returns the file path. Send the image to the user via Telegram.
