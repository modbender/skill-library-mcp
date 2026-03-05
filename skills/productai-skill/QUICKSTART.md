# ProductAI Quick Start Guide

Get started with ProductAI in 5 minutes.

## Step 1: Get Your API Key

1. Visit **[ProductAI Studio](https://www.productai.photo)**
2. Click on **API Access** in the navigation
3. Find or generate your API key
4. Copy it to clipboard

> **Where to find it:**
> 
> ![API Access Screenshot - Shows where to find your API key in the ProductAI dashboard]

## Step 2: Run Setup

```bash
cd ~/.openclaw/workspace/productai
./scripts/setup.py
```

When prompted:
- **API Key:** Paste your key from Step 1
- **API Endpoint:** Press Enter (uses default: `https://api.productai.photo/v1`)
- **Default Model:** Press Enter (uses `nanobanana`)
- **Default Resolution:** Press Enter (uses `1024x1024`)
- **Your Plan:** Enter your plan (`basic`, `standard`, or `pro`)

The setup script will:
- Create `config.json` with your settings
- Secure the file (permissions: 600)
- Confirm everything is ready

## Step 3: Generate Your First Image

Try a simple generation:

```bash
./scripts/generate_photo.py \
  --image "https://example.com/your-product.jpg" \
  --prompt "white studio background with soft lighting" \
  --output my-first-result.png
```

**What happens:**
1. API request sent to ProductAI
2. Job created (you'll see the job ID)
3. Script polls for completion (~5-30 seconds)
4. Image downloads to `my-first-result.png`

## Common Use Cases

### Clean Product Backgrounds

```bash
./scripts/generate_photo.py \
  --image "https://example.com/messy-bg.jpg" \
  --prompt "pure white background" \
  --output clean.png
```

### Lifestyle Shots

```bash
./scripts/generate_photo.py \
  --image "https://example.com/watch.jpg" \
  --prompt "wrist wearing the watch, business attire, office desk background" \
  --output lifestyle.png
```

### Combine Multiple Products

```bash
./scripts/generate_photo.py \
  --image "https://example.com/lipstick.jpg" "https://example.com/box.jpg" \
  --prompt "Place the lipstick on top of the cosmetic box" \
  --model nanobanana \
  --output combo.png
```

### High Quality (Nano Banana Pro)

```bash
./scripts/generate_photo.py \
  --image "https://example.com/product.jpg" \
  --prompt "luxury marble countertop, golden hour lighting" \
  --model nanobananapro \
  --output premium.png
```

> **Note:** Nano Banana Pro costs 8 tokens vs 3 for regular models

### Upscale for Print

```bash
./scripts/upscale_image.py \
  --image "https://example.com/product.jpg" \
  --output upscaled.png
```

> **Note:** Upscaling costs 20 tokens

## Available Models

| Model | Token Cost | Best For |
|-------|------------|----------|
| `gpt-low` | 2 | Quick tests, drafts |
| `gpt-medium` | 3 | Standard quality |
| `gpt-high` | 8 | High quality |
| `kontext-pro` | 3 | Product placement |
| `nanobanana` | 3 | **Default** — fast & good |
| `nanobananapro` | 8 | Premium quality |
| `seedream` | 3 | Creative scenes |

**Multi-image support:** `nanobanana`, `nanobananapro`, `seedream` (max 2 images)

## Async Workflow (For Batch Jobs)

Instead of waiting for each job, start them all and check later:

```bash
# Start 3 jobs (collect job IDs)
./scripts/generate_photo.py --image "url1" --prompt "prompt1" --no-wait  # → Job ID: 101
./scripts/generate_photo.py --image "url2" --prompt "prompt2" --no-wait  # → Job ID: 102
./scripts/generate_photo.py --image "url3" --prompt "prompt3" --no-wait  # → Job ID: 103

# Later, download results
./scripts/generate_photo.py --job-id 101 --output result1.png
./scripts/generate_photo.py --job-id 102 --output result2.png
./scripts/generate_photo.py --job-id 103 --output result3.png
```

## Troubleshooting

### "Config file not found"
Run `./scripts/setup.py` first.

### "OUT_OF_TOKENS"
Check your token balance in ProductAI Studio. Purchase more tokens or upgrade plan.

### "Invalid API key" (401)
Regenerate your API key in ProductAI Studio → API Access.

### Job stuck at "RUNNING"
Jobs usually complete in 5-30 seconds. If stuck after 5 minutes, check ProductAI Studio for service status.

### Image not downloaded
Check that the image URL is publicly accessible and under 10MB (PNG, JPG, or WebP).

## Next Steps

- Read [SKILL.md](SKILL.md) for full feature documentation
- Check [API.md](references/API.md) for detailed API reference
- Explore batch processing with `batch_generate.py`
- Set up webhooks for production workflows

## Support

- **Website:** https://www.productai.photo
- **API Docs:** [references/API.md](references/API.md)
- **Issues:** Contact ProductAI support via dashboard

---

**Happy generating! 🚀**
