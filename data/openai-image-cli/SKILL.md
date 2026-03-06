---
name: openai-image-cli
version: 1.0.0
description: Generate, edit, and manage images via OpenAI's GPT Image and DALL-E models.
metadata:
  {
    "openclaw": { "emoji": "🎨", "requires": { "bins": ["openai-image"], "envs": ["OPENAI_API_KEY"] } },
  }
---

# OpenAI Image CLI

Generate, edit, and create variations of images using OpenAI's latest models.

## Installation

```bash
npm install -g @versatly/openai-image-cli
```

## Authentication

```bash
# Via environment variable
export OPENAI_API_KEY=sk-...

# Or via config
openai-image config set api-key sk-...
```

## Quick Start

```bash
# Generate an image
openai-image generate "A futuristic city at sunset"

# High quality landscape
openai-image generate "Mountain panorama" -s 1536x1024 -q high

# Multiple images with transparency
openai-image generate "Logo design" -n 4 -b transparent

# Edit an existing image
openai-image edit photo.png "Add sunglasses to the person"

# Create variations (DALL-E 2)
openai-image vary original.png -n 3
```

## Available Models

| Model | Description | Notes |
|-------|-------------|-------|
| `gpt-image-1.5` | Latest GPT Image (default) | Best quality, recommended |
| `gpt-image-1` | GPT Image | Good balance |
| `gpt-image-1-mini` | GPT Image Mini | Cost-effective |
| `dall-e-3` | DALL-E 3 | Deprecated May 2026 |
| `dall-e-2` | DALL-E 2 | Deprecated May 2026, supports variations |

## Commands

### generate

Create images from text prompts.

```bash
openai-image generate "prompt" [options]

Options:
  -m, --model <model>        Model (default: gpt-image-1.5)
  -s, --size <size>          Size: 1024x1024, 1536x1024, 1024x1536, auto
  -q, --quality <quality>    Quality: auto, high, medium, low
  -n, --count <n>            Number of images (1-10)
  -f, --format <format>      Format: png, jpeg, webp
  -o, --output <path>        Output file/directory
  -b, --background <bg>      Background: auto, transparent, opaque
  --compression <0-100>      Compression level for jpeg/webp
  --moderation <level>       Content moderation: auto, low
  --stream                   Enable streaming with partial images
  --partial-images <0-3>     Partial images during streaming
  --json                     Output JSON response
  --dry-run                  Show request without executing
```

### edit

Edit existing images with prompts.

```bash
openai-image edit <image> "instructions" [options]

Options:
  --mask <path>              Mask image for inpainting
  --images <paths...>        Additional reference images (up to 16)
  -s, --size <size>          Output size
  -q, --quality <quality>    Quality level
  -n, --count <n>            Number of variations
  -f, --format <format>      Output format
  -o, --output <path>        Output path
```

**Examples:**
```bash
# Simple edit
openai-image edit photo.png "Add sunglasses"

# Inpainting with mask
openai-image edit room.png "Add a plant" --mask mask.png

# Multi-image composite
openai-image edit base.png "Create gift basket" --images item1.png item2.png
```

### vary

Create variations of an image (DALL-E 2 only).

```bash
openai-image vary <image> [options]

Options:
  -n, --count <n>            Number of variations (1-10)
  -s, --size <size>          Size: 256x256, 512x512, 1024x1024
  -o, --output <path>        Output path/directory
```

### batch

Generate multiple images from a file or stdin.

```bash
openai-image batch [options]

Options:
  -i, --input <file>         Input file (text or JSONL)
  --stdin                    Read from stdin
  -m, --model <model>        Model for all generations
  -o, --output-dir <dir>     Output directory
  --parallel <n>             Concurrent requests (default: 3)
  --delay <ms>               Delay between requests (default: 100)
```

**JSONL format:**
```json
{"prompt": "A red car", "size": "1024x1024", "quality": "high"}
{"prompt": "A blue boat", "size": "1536x1024"}
```

### config

Manage CLI configuration.

```bash
openai-image config set <key> <value>
openai-image config get <key>
openai-image config list
openai-image config reset
openai-image config path
```

**Keys:** `api-key`, `default-model`, `default-size`, `default-quality`, `default-format`, `output-dir`

### models

List available models.

```bash
openai-image models [--json]
```

### history

View local generation history.

```bash
openai-image history [-n <limit>] [--json] [--clear]
```

## Output Formats

### Default (human-readable)
```
✓ Generated image saved to ./generated-1707500000.png
  Model: gpt-image-1.5
  Size: 1024x1024
  Quality: high
  Tokens: 150 (text: 10, image: 140)
```

### JSON (`--json`)
```json
{
  "success": true,
  "file": "./generated-1707500000.png",
  "model": "gpt-image-1.5",
  "size": "1024x1024",
  "quality": "high",
  "usage": {
    "total_tokens": 150,
    "input_tokens": 50,
    "output_tokens": 100
  }
}
```

## Size Options

| Model | Sizes |
|-------|-------|
| GPT Image | 1024x1024, 1536x1024 (landscape), 1024x1536 (portrait), auto |
| DALL-E 3 | 1024x1024, 1792x1024, 1024x1792 |
| DALL-E 2 | 256x256, 512x512, 1024x1024 |

## Tips

1. **Transparent backgrounds**: Use `-b transparent -f png` for logos
2. **Batch processing**: Use JSONL for per-image options
3. **Cost control**: Use `gpt-image-1-mini` for drafts
4. **History tracking**: Enabled by default, view with `openai-image history`

## Links

- npm: https://www.npmjs.com/package/@versatly/openai-image-cli
- GitHub: https://github.com/Versatly/openai-image-cli
