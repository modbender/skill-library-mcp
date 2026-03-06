# ProductAI Integration for OpenClaw

Generate professional AI product photos directly from OpenClaw using the ProductAI.photo API.

## What is ProductAI?

ProductAI.photo is an AI-powered service that transforms product images with:
- Background replacement and scene generation
- Multi-image compositing
- Professional upscaling
- Multiple AI models for different quality levels

Perfect for e-commerce, marketing, and content creation.

## Quick Links

- **[ProductAI Website](https://www.productai.photo)** — Sign up & get API key
- **[Quick Start Guide](QUICKSTART.md)** — Get running in 5 minutes
- **[Setup Guide](SETUP-GUIDE.md)** — Detailed setup instructions & FAQ
- **[Skill Documentation](SKILL.md)** — Full feature reference
- **[API Reference](references/API.md)** — Complete API documentation

## Installation

### 1. Get Your API Key

Visit [ProductAI Studio](https://www.productai.photo) → **API Access** → Copy your key

### 2. Run Setup

```bash
cd ~/.openclaw/workspace/productai
./scripts/setup.py
```

Paste your API key when prompted. That's it!

### 3. Generate Images

```bash
./scripts/generate_photo.py \
  --image "https://example.com/product.jpg" \
  --prompt "white studio background" \
  --output result.png
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `setup.py` | Configure API credentials |
| `generate_photo.py` | Generate product photos |
| `upscale_image.py` | Upscale images (20 tokens) |
| `batch_generate.py` | Batch process multiple images |

## Common Use Cases

### Clean Product Backgrounds
```bash
./scripts/generate_photo.py \
  --image "https://example.com/messy.jpg" \
  --prompt "pure white background" \
  --output clean.png
```

### Lifestyle Photography
```bash
./scripts/generate_photo.py \
  --image "https://example.com/watch.jpg" \
  --prompt "wrist wearing watch, business setting" \
  --output lifestyle.png
```

### Multi-Image Compositing
```bash
./scripts/generate_photo.py \
  --image "url1" "url2" \
  --prompt "Combine both products" \
  --model nanobanana \
  --output combo.png
```

### High Quality (Nano Banana Pro)
```bash
./scripts/generate_photo.py \
  --image "https://example.com/product.jpg" \
  --prompt "luxury marble countertop" \
  --model nanobananapro \
  --output premium.png
```

## Models & Pricing

| Model | Cost | Quality |
|-------|------|---------|
| `gpt-low` | 2 tokens | Low |
| `gpt-medium` | 3 tokens | Medium |
| `nanobanana` | 3 tokens | **Recommended** |
| `kontext-pro` | 3 tokens | Good |
| `seedream` | 3 tokens | Creative |
| `gpt-high` | 8 tokens | High |
| `nanobananapro` | 8 tokens | Premium |
| **Upscale** | 20 tokens | — |

**Multi-image support:** `nanobanana`, `nanobananapro`, `seedream` (max 2 images)

## Documentation

- **New users:** Start with [QUICKSTART.md](QUICKSTART.md)
- **Setup help:** See [SETUP-GUIDE.md](SETUP-GUIDE.md)
- **Feature reference:** Read [SKILL.md](SKILL.md)
- **API details:** Check [API.md](references/API.md)
- **Security:** See [SECURITY.md](SECURITY.md)

## Troubleshooting

**"Config file not found"**
→ Run `./scripts/setup.py` first

**"OUT_OF_TOKENS"**
→ Purchase more tokens at [productai.photo](https://www.productai.photo)

**"Unauthorized" (401)**
→ Check your API key in ProductAI Studio → API Access

**Rate limited (429)**
→ Wait a minute (limit: 15 requests/minute)

More help in [SETUP-GUIDE.md](SETUP-GUIDE.md#troubleshooting)

## Security Features

✅ **HTTPS-only URLs** — Blocks HTTP to prevent insecure requests  
✅ **SSRF Prevention** — Blocks private IPs and localhost  
✅ **Request Timeouts** — All HTTP requests timeout after 30s  
✅ **Rate Limiting** — Batch processing respects 15 req/min limit  
✅ **Path Traversal Protection** — Sanitizes all filenames

See [SECURITY.md](SECURITY.md) for full details.

## Support

- **Website:** https://www.productai.photo
- **Get API Key:** ProductAI Studio → API Access
- **Issues:** Contact ProductAI support via dashboard

---

**Ready to create amazing product photos?** Start with [QUICKSTART.md](QUICKSTART.md)!
