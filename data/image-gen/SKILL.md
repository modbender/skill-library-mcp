---
name: image-gen
version: 2.0.0
author: "wells"
emoji: "🎨"
tags:
  - image-generation
  - midjourney
  - flux
  - gemini
  - fal
  - ideogram
  - recraft
description: >
  Generate stunning images with 8 AI models — Midjourney, Flux, Gemini (Nano Banana), Ideogram, and more. One command, zero complexity. The skill handles all async polling automatically.
homepage: https://github.com/wells1137/image-gen-skill
metadata:
  openclaw:
    emoji: "🎨"
    primaryEnv: FAL_KEY
    requires:
      env:
        - FAL_KEY
        - LEGNEXT_KEY
    install:
      - id: node
        kind: node
        package: "@fal-ai/client"
        label: "Install fal.ai client"
---

# 🎨 Image Generation Skill

**Use when:** User asks to generate, draw, create, or make any kind of image, photo, illustration, icon, logo, or artwork.

Generate images with 8 state-of-the-art AI models. This skill automatically picks the best model for the job and handles all the complexity — including Midjourney's async polling — so you can focus on the conversation.

---

## Quick Reference

| User Intent | Model | Speed |
|---|---|---|
| Artistic, cinematic, painterly | `midjourney` | ~15s |
| Photorealistic, portrait, product | `flux-pro` | ~8s |
| General purpose, balanced | `flux-dev` | ~10s |
| Quick draft, fast iteration | `flux-schnell` | ~2s |
| Image with text, logo, poster | `ideogram` | ~10s |
| Vector art, icon, flat design | `recraft` | ~8s |
| Anime, stylized illustration | `sdxl` | ~5s |
| Gemini-powered, consistent style | `nano-banana` | ~12s |

---

## How to Generate an Image

### Step 1 — Enhance the prompt

Before calling the script, expand the user's prompt with style, lighting, and quality descriptors appropriate for the chosen model.

- **Midjourney**: Add `cinematic lighting`, `ultra detailed`, `--v 7`, `--style raw`
- **Flux**: Add `masterpiece`, `highly detailed`, `sharp focus`, `professional photography`
- **Ideogram**: Be explicit about text content, font style, and layout
- **Recraft**: Specify `vector illustration`, `flat design`, `icon style`

### Step 2 — Run the script

```bash
node {baseDir}/tools/generate.js \
  --model <model_id> \
  --prompt "<enhanced prompt>" \
  --aspect-ratio <ratio>
```

**All parameters:**

| Parameter | Default | Description |
|---|---|---|
| `--model` | `flux-dev` | Model ID from the table above |
| `--prompt` | *(required)* | The image generation prompt |
| `--aspect-ratio` | `1:1` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `21:9` |
| `--num-images` | `1` | Number of images (1–4; Midjourney always returns 4) |
| `--negative-prompt` | — | Things to avoid (not supported by Midjourney) |
| `--seed` | — | Seed for reproducibility |

### Step 3 — Return the result

The script always waits and returns the final image URL(s). No polling required.

```json
{
  "success": true,
  "model": "flux-pro",
  "imageUrl": "https://...",
  "images": ["https://..."]
}
```

Send the `imageUrl` to the user.

---

## Midjourney Actions

After generating a 4-image grid with Midjourney, offer the user these options:

```bash
# Upscale image #2 (subtle, preserves details)
node {baseDir}/tools/generate.js \
  --model midjourney \
  --action upscale \
  --index 2 \
  --job-id <job_id>

# Create a strong variation of image #3
node {baseDir}/tools/generate.js \
  --model midjourney \
  --action variation \
  --index 3 \
  --job-id <job_id> \
  --variation-type 1

# Regenerate with same prompt
node {baseDir}/tools/generate.js \
  --model midjourney \
  --action reroll \
  --job-id <job_id>
```

**Upscale types:** `0` = Subtle (default, best for photos), `1` = Creative (best for illustrations)

**Variation types:** `0` = Subtle (default), `1` = Strong (dramatic changes)

---

## Example Conversations

**User:** "帮我画一只在雪山上的雪豹，电影感光效"

```bash
# Choose midjourney for artistic quality
node {baseDir}/tools/generate.js \
  --model midjourney \
  --prompt "a majestic snow leopard on a snowy mountain peak, cinematic lighting, dramatic atmosphere, ultra detailed --ar 16:9 --v 7" \
  --aspect-ratio 16:9
```

> 🎨 生成完成！想放大哪张？(U1-U4) 还是创建变体？(V1-V4)

---

**User:** "用 Flux 生成一张香水产品海报，白色背景"

```bash
# Choose flux-pro for photorealistic product shots
node {baseDir}/tools/generate.js \
  --model flux-pro \
  --prompt "a luxury perfume bottle on a clean white background, professional product photography, soft shadows, 8k, highly detailed" \
  --aspect-ratio 3:4
```

---

**User:** "快速给我看个草稿"

```bash
# flux-schnell for instant previews
node {baseDir}/tools/generate.js \
  --model flux-schnell \
  --prompt "..." \
  --aspect-ratio 1:1
```

---

**User:** "帮我做一个 App 图标，扁平风格，蓝色系"

```bash
# recraft for vector/icon style
node {baseDir}/tools/generate.js \
  --model recraft \
  --prompt "a minimal flat design app icon, blue color scheme, simple geometric shapes, vector style, white background"
```

---

## Setup

Configure in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "image-gen": {
        "enabled": true,
        "env": {
          "FAL_KEY": "your_fal_key_here",
          "LEGNEXT_KEY": "your_legnext_key_here"
        }
      }
    }
  }
}
```

| Variable | Required For | Where to Get |
|---|---|---|
| `FAL_KEY` | Flux, SDXL, Nano Banana, Ideogram, Recraft | [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys) |
| `LEGNEXT_KEY` | Midjourney | [legnext.ai/dashboard](https://legnext.ai/dashboard) |

---

## Changelog

### v2.0.0
- **Simplified async**: The script now blocks until Midjourney completes. No more `--async` / `--poll` flags needed in SKILL.md instructions.
- **Unified output format**: All models return the same `{ success, imageUrl, images }` shape.
- **Reference images for Nano Banana**: Pass `--reference-images "url1,url2"` for character/style consistency across generations.

### v1.3.0
- Added non-blocking async mode for Midjourney (`--async` + `--poll`).

### v1.2.0
- Midjourney turbo mode enabled by default (~10-20s).

### v1.1.0
- Switched Midjourney provider from TTAPI to Legnext.ai for better stability.

### v1.0.0
- Initial release with Midjourney, Flux, SDXL, Nano Banana, Ideogram, Recraft.
