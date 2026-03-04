---
name: wavespeed
description: "Generate and edit images and videos using WaveSpeed AI's 700+ model library. Use when the user wants to generate images from text prompts (FLUX, Seedream, Qwen), edit or retouch photos (nano-banana-pro/edit keeps faces identical while changing clothes/background), generate videos from images or text (Kling, Veo, Sora, Wan, Hailuo), or upscale videos to 4K. Triggers include: generate an image, edit this photo, change the background, swap the outfit, make a video from this image, animate this photo, upscale this video, use WaveSpeed, use nano banana pro."
---

# WaveSpeed AI

700+ AI models (Google, OpenAI, ByteDance, Kling, Luma) via one API. Images in <2s, videos in <2min.

## API Key — check in this order

1. **`WAVESPEED_API_KEY` env var** — already set in all Clawster containers, just use it directly
2. `TOOLS.md` in the workspace — look for `WaveSpeed AI` section
3. Ask the user

**Never search for the key** — if `WAVESPEED_API_KEY` is in the environment, it's ready to go. Check with:
```bash
echo $WAVESPEED_API_KEY
```

### Get your API key

Sign up at **[wavespeed.ai](https://wavespeedai.pxf.io/3kPoRd)** → Dashboard → API Keys.  
New accounts get free credits. Pay-as-you-go pricing — no subscription required.

```bash
export WAVESPEED_API_KEY=your_key_here
```

The skill script is at `skills/wavespeed/scripts/wavespeed.js`.

## Usage

```bash
# Image generation
node wavespeed.js generate --model flux --prompt "sunset over mountains" --output out.png
node wavespeed.js generate --model seedream --prompt "..." --size 1024x1024

# Image editing (face/portrait-safe — preserves identity)
node wavespeed.js edit --model nbp --prompt "change bathrobe to black hoodie, dark background" \
  --image https://example.com/photo.jpg --output result.png

# Video from image
node wavespeed.js video --model wan-i2v --prompt "slow cinematic zoom" \
  --image https://example.com/frame.jpg --output clip.mp4

# List all aliases
node wavespeed.js models

# Check task status
node wavespeed.js status --id task_abc123
```

## Key Models (Quick Reference)

| Task | Alias | Best for |
|------|-------|---------|
| Edit photo keeping face | `nbp` | Portrait retouching, outfit/bg change |
| Fast image gen | `flux-schnell` | Drafts, quick tests |
| Best image quality | `flux-pro` / `seedream` | Final outputs |
| Image → Video | `wan-i2v` | Fast, affordable |
| Premium video | `kling` / `veo` | Cinematic quality |
| Text → Video | `sora` / `veo` | Story videos |

See `references/models.md` for full model list with IDs, params, and pricing.

## Important Notes

- **Image editing** (`nbp`, `nb-edit`): always pass images as `images: [url]` array — this is required
- **Face preservation**: `google/nano-banana-pro/edit` is the best model for editing photos while keeping the person's face identical
- Output files are saved to current directory by default; use `--output` to specify path
- Videos can take 2-5 minutes; script auto-polls with progress indicator
- For multiple input images (multi-reference editing), use `--images url1,url2`
