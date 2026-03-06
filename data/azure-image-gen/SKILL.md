---
name: azure-image-gen
description: Generate images using Azure OpenAI DALL-E. Supports batch generation, custom prompts, and outputs a gallery.
metadata:
  author: kai
  version: "1.0.0"
  tags:
    - image generation
    - azure
    - dall-e
    - ai art
---

# Azure Image Gen

Generate images using Azure OpenAI's DALL-E deployment.

## Setup

### Required Environment Variables

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_DALLE_DEPLOYMENT="your-dalle-deployment-name"
```

Or create a `.env` file in the skill directory.

### API Version

Default: `2024-02-01` (supports DALL-E 3)

## Usage

### Basic Generation

```bash
python3 /Users/abhi/clawd/skills/azure-image-gen/scripts/generate.py --prompt "A futuristic city at sunset"
```

### Multiple Images

```bash
python3 /Users/abhi/clawd/skills/azure-image-gen/scripts/generate.py \
  --prompt "Professional blog header for a tech startup" \
  --count 4
```

### Custom Size & Quality

```bash
python3 /Users/abhi/clawd/skills/azure-image-gen/scripts/generate.py \
  --prompt "Minimalist illustration of cloud computing" \
  --size 1792x1024 \
  --quality hd
```

### Specify Output Directory

```bash
python3 /Users/abhi/clawd/skills/azure-image-gen/scripts/generate.py \
  --prompt "Abstract data visualization" \
  --out-dir ./blog-images
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--prompt` | Required | Image description |
| `--count` | 1 | Number of images to generate |
| `--size` | 1024x1024 | Image size: `1024x1024`, `1792x1024`, `1024x1792` |
| `--quality` | standard | Quality: `standard` or `hd` |
| `--style` | vivid | Style: `vivid` or `natural` |
| `--out-dir` | ./azure-images | Output directory |
| `--api-version` | 2024-02-01 | Azure OpenAI API version |

## Output

- PNG images saved to output directory
- `manifest.json` with prompt-to-file mapping
- `index.html` gallery for easy preview

## Blog Image Prompts

For blog headers, try prompts like:

```
# Tech/SaaS
"Minimalist isometric illustration of cloud migration, blue and white color scheme, clean lines, professional"

# Comparison posts
"Split screen illustration showing old vs new technology, warm vs cool colors, modern flat design"

# How-to guides
"Clean illustration of a step-by-step process, numbered steps floating in space, soft gradients"

# Cost/pricing
"Abstract visualization of savings and growth, upward arrows, green accents, professional business style"
```

## Troubleshooting

**401 Unauthorized**: Check your `AZURE_OPENAI_API_KEY`

**404 Not Found**: Verify your `AZURE_OPENAI_DALLE_DEPLOYMENT` name matches exactly

**Content Policy**: Azure has strict content filters. Rephrase prompts that get blocked.
