# WaveSpeed AI — Image & Video Generation for AI Agents

700+ AI models (Google, OpenAI, ByteDance, Kling, Luma) via one unified API.  
Images in **< 2 seconds**, videos in **< 2 minutes**.

---

## What you can do

- **Generate images** from text prompts — FLUX, Seedream, Qwen
- **Edit photos** while keeping faces identical — nano-banana-pro changes outfits, backgrounds without touching the face
- **Animate images** → video — Wan, Kling, Hailuo
- **Generate videos** from text — Sora, Veo, Wan T2V
- **Upscale videos** to 4K

---

## Quick Start

```bash
# Install dependencies
npm install axios form-data

# Set your API key
export WAVESPEED_API_KEY=your_key_here

# Generate an image (7 seconds)
node wavespeed.js generate --model flux-schnell --prompt "sunset over mountains" --output out.png

# Edit a photo — keeps face, changes everything else
node wavespeed.js edit --model nbp --prompt "change outfit to black hoodie, dark background" \
  --image https://example.com/photo.jpg --output result.png

# Animate image to video
node wavespeed.js video --model wan-i2v --prompt "slow cinematic zoom" \
  --image https://example.com/frame.jpg --output clip.mp4
```

---

## Get your API key

Sign up at **[wavespeed.ai](https://wavespeedai.pxf.io/3kPoRd)** → Dashboard → API Keys.  
New accounts get free credits. Pay-as-you-go — no subscription needed.

---

## Key Models

| Task | Alias | Speed | Notes |
|------|-------|-------|-------|
| Edit photo (face-safe) | `nbp` | ~10s | Best for portraits — face stays identical |
| Fast image gen | `flux-schnell` | ~7s | Drafts and previews |
| Best image quality | `seedream` | ~15s | Final outputs |
| Image → Video | `wan-i2v` | ~90s | Fast and affordable |
| Premium video | `kling` | ~2min | Cinematic quality |
| Text → Video | `sora` / `veo` | ~3min | Story videos |
| 4K upscale | `upscale` | ~60s | Video resolution enhancement |

Run `node wavespeed.js models` to see all 700+ available models.

---

## Usage

```bash
# Generate
node wavespeed.js generate --model <alias> --prompt "..." --output out.png

# Edit (face-preserving)
node wavespeed.js edit --model nbp --prompt "..." --image <url> --output result.png

# Video from image
node wavespeed.js video --model wan-i2v --prompt "..." --image <url> --output clip.mp4

# Check task status
node wavespeed.js status --id task_abc123

# List all model aliases
node wavespeed.js models
```

---

## License

MIT
