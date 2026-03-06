---
name: productai
description: Generate professional AI product photos using ProductAI.photo service. Use when users need to create, enhance, or transform product images for e-commerce, marketing, catalogs, or campaigns. Supports background replacement, product placement, scene generation, adaptive templates, and video ads. Use for tasks involving product photography, lifestyle shots, mockups, or marketing visuals.
---

# ProductAI Integration

ProductAI.photo is an AI-powered service that generates professional product photos from existing images. It enables e-commerce businesses, marketers, and designers to create studio-quality product photography without hiring photographers.

## Quick Start

**1. Get Your API Key**

Visit [ProductAI Studio](https://www.productai.photo) → **API Access** → Copy your API key

**2. Run Setup**

```bash
cd ~/.openclaw/workspace/productai
scripts/setup.py
# Paste your API key when prompted
```

**3. Generate Images**

```bash
# Generate product photo with custom background
scripts/generate_photo.py \
  --image https://example.com/product.jpg \
  --prompt "modern living room with natural lighting" \
  --output result.png

# Use multiple reference images (nanobanana/seedream support 2 images)
scripts/generate_photo.py \
  --image https://example.com/product1.jpg https://example.com/product2.jpg \
  --prompt "Put the first image on top of the second image" \
  --output result.png

# High quality with Nano Banana Pro
scripts/generate_photo.py \
  --image https://example.com/product.jpg \
  --prompt "white studio background" \
  --model nanobananapro \
  --output hq.png

# Upscale an image (20 tokens)
scripts/upscale_image.py \
  --image https://example.com/photo.jpg \
  --output upscaled.png
```

## Core Capabilities

**Photo Generation (`/api/generate`)**
- Background replacement with AI-generated scenes
- Product placement in realistic environments
- Multi-image compositing (up to 2 reference images with certain models)
- Custom prompts for full creative control

**Image Upscaling (`/api/upscale`)**
- Professional AI upscaling (Magnific Precision Upscale)
- Preserves image details without distortion
- 20 tokens per upscale

**Models Available**
- **gpt-low** — GPT Low Quality (2 tokens)
- **gpt-medium** — GPT Medium Quality (3 tokens)
- **gpt-high** — GPT High Quality (8 tokens)
- **kontext-pro** — Kontext Pro (3 tokens)
- **nanobanana** — Nano Banana (3 tokens) — **DEFAULT**
- **nanobananapro** — Nano Banana Pro (8 tokens)
- **seedream** — Seedream (3 tokens)

**Multi-Image Support:**
`nanobanana`, `nanobananapro`, and `seedream` support up to 2 reference images for advanced compositing.

## Configuration

### API Setup

**Step 1: Get Your API Key**

1. Visit [ProductAI Studio](https://www.productai.photo)
2. Navigate to **API Access** section
3. Click **Generate API Key** or copy existing key

**Step 2: Run Setup Script**

```bash
cd ~/.openclaw/workspace/productai
scripts/setup.py
```

This will interactively create `config.json` with your credentials:

```json
{
  "api_key": "your-api-key-here",
  "api_endpoint": "https://api.productai.photo/v1",
  "default_model": "nanobanana",
  "default_resolution": "1024x1024",
  "plan": "standard"
}
```

The config file is automatically secured with 600 permissions.

### Installation

The integration scripts require Python 3.7+ with these dependencies:

```bash
pip install requests pillow
```

All dependencies are handled automatically by the scripts.

## Usage Examples

### E-commerce Product Photos

Generate clean product shots for online stores:

```bash
scripts/generate_photo.py \
  --image https://example.com/raw-product.jpg \
  --prompt "white studio background with soft shadows" \
  --output store-listing.png
```

### Marketing Campaign Visuals

Create lifestyle shots for advertising:

```bash
scripts/generate_photo.py \
  --image https://example.com/bottle.jpg \
  --prompt "outdoor picnic scene with blanket and basket, golden hour lighting" \
  --output campaign-hero.png \
  --model kontext-pro
```

### Multi-Image Compositing

Combine multiple products into one scene:

```bash
scripts/generate_photo.py \
  --image https://example.com/product1.jpg https://example.com/product2.jpg \
  --prompt "Place the lipstick on top of the cosmetics box" \
  --model nanobanana \
  --output composite.png
```

### High-Quality Output

Use Nano Banana Pro for premium results:

```bash
scripts/generate_photo.py \
  --image https://example.com/product.jpg \
  --prompt "luxury marble countertop setting with morning light" \
  --model nanobananapro \
  --output premium.png
```

### Image Upscaling

Upscale images for print or high-res displays:

```bash
scripts/upscale_image.py \
  --image https://example.com/product.jpg \
  --output upscaled.png
```

### Async Workflow (No Wait)

Start generation and check later:

```bash
# Start job (prints job ID)
scripts/generate_photo.py \
  --image https://example.com/product.jpg \
  --prompt "studio background" \
  --no-wait

# Output: Job created: 12345

# Later, resume and download
scripts/generate_photo.py \
  --job-id 12345 \
  --output result.png
```

## API Reference

See [API.md](references/API.md) for complete endpoint documentation, request/response formats, and authentication details.

## Pricing & Token Costs

ProductAI uses a token-based pricing system:

| Operation | Token Cost |
|-----------|------------|
| GPT Low Quality Generation | 2 tokens |
| GPT Medium Quality Generation | 3 tokens |
| GPT High Quality Generation | 8 tokens |
| Kontext Pro | 3 tokens |
| Nano Banana Pro | 8 tokens |
| Nano Banana | 3 tokens |
| Seedream | 3 tokens |
| Magnific Precision Upscale | 20 tokens |

**Subscription Plans:**

Visit [ProductAI.photo](https://www.productai.photo) for current plans and token packages.

**Rate Limits:**
- 15 requests per minute
- Daily limits based on subscription plan

**Note:** Tokens are deducted when each operation **starts** (not on completion).

## Troubleshooting

**API Key Issues**
- Verify `config.json` exists: `cat ~/.openclaw/workspace/productai/config.json`
- Check API key in ProductAI Studio → API Access
- Regenerate key if needed

**OUT_OF_TOKENS Error**
- Check your token balance in ProductAI Studio
- Purchase more tokens or upgrade plan
- Remember: tokens are deducted when jobs **start**, not on completion

**Rate Limit (429)**
- Maximum 15 requests per minute
- Wait before retrying
- Use `--no-wait` for batch jobs and check status later

**Job Failed (ERROR status)**
- Check image URL is accessible and under 10MB
- Verify image format (PNG, JPG, or WebP only)
- Check prompt length and content
- Try a different model

**Multi-Image Not Working**
- Only `nanobanana`, `nanobananapro`, and `seedream` support multiple images
- Maximum 2 reference images
- Use array format: `--image url1 url2`

## Support

- Website: https://www.productai.photo
- Documentation: See references/API.md
- Contact: support@productai.photo (or team contact when available)

## Advanced Topics

For detailed API specifications, authentication flows, webhook integration, and batch processing patterns, see [API.md](references/API.md).
