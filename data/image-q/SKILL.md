---
name: image-gen
description: Generate images using multiple AI models — Midjourney (via Legnext.ai), Flux, SDXL, Nano Banana (Gemini), and more via fal.ai. Automatically picks the best model based on user intent, or lets the user specify one explicitly.
homepage: https://legnext.ai
metadata: {"openclaw":{"emoji":"🎨","primaryEnv":"FAL_KEY","requires":{"env":["FAL_KEY","LEGNEXT_KEY"]},"install":[{"id":"node","kind":"node","package":"@fal-ai/client","label":"Install fal.ai client (npm)"}]},"proxy":{"url":"https://image-gen-proxy.vercel.app","freeLimit":100}}
---

# Image Generation Skill

This skill enables you to generate images using a variety of state-of-the-art AI models. It supports:

- **Midjourney** (via [Legnext.ai](https://legnext.ai)) — Best for artistic, cinematic, and highly detailed images. Faster and more stable than other MJ providers.
- **Flux 1.1 Pro** (via fal.ai) — Best for photorealistic images and complex scenes.
- **Flux Dev** (via fal.ai) — Fast, high-quality generation for general use.
- **Flux Schnell** (via fal.ai) — Ultra-fast generation (<2s), great for quick drafts.
- **SDXL** (via fal.ai `fal-ai/fast-sdxl`) — Fastest SDXL endpoint, great for stylized art and LoRA support.
- **Nano Banana Pro** (via fal.ai `fal-ai/nano-banana-pro`) — Google Gemini-powered image generation and editing.
- **Ideogram v3** (via fal.ai) — Best for images with text, logos, and typography.
- **Recraft v3** (via fal.ai) — Best for vector-style, icon, and design assets.

---

## Model Selection Guide

When the user does not specify a model, use this guide to pick the best one:

| User Intent | Recommended Model | Model ID |
|---|---|---|
| Artistic, cinematic, painterly, highly detailed | Midjourney | `midjourney` |
| Photorealistic, portrait, product photo | Flux 1.1 Pro | `flux-pro` |
| General purpose, balanced quality/speed | Flux Dev | `flux-dev` |
| Quick draft, fast iteration (<2s) | Flux Schnell | `flux-schnell` |
| Image with text, logo, poster, typography | Ideogram v3 | `ideogram` |
| Vector art, icon, flat design, illustration | Recraft v3 | `recraft` |
| Stylized anime, illustration, concept art | SDXL | `sdxl` |
| Gemini-powered generation or editing | Nano Banana Pro | `nano-banana` |

---

## How to Use This Skill

### Basic Usage

When a user asks to generate an image, follow these steps:

1. **Understand the request**: Identify the subject, style, and any specific requirements.
2. **Select a model**: Use the guide above, or honor the user's explicit model choice.
3. **Enhance the prompt**: Expand the user's prompt with relevant style, lighting, and quality descriptors appropriate for the chosen model.
4. **Call the generation script**: Use the `exec` tool to run the generation script.
5. **Return the result**: Present the image URL(s) to the user.

### User Experience Rules (important)

- **Same-turn polling for Midjourney:** After submitting a Midjourney job, do **not** reply "已提交，完成后通知你" and end your turn. The bot cannot push a message later — the user would have to ask "还没好?" to trigger the next turn. Instead, in the **same** turn, keep calling `--poll --job-id` every ~15s until `status: "completed"`, then send the result in that same turn. For multiple parallel jobs, poll all job_ids until all are completed, then send one message with all results.
- **Links for Midjourney (Legnext):** When sending the result, use **only** `displayImageUrl` or `imageUrls` from the script output. **Never** send `imageUrl` (the grid) — it is `cdn.legnext.ai/temp/...` and expires (shows as broken). Use only `cdn.legnext.ai/mj/...` links.

### Calling the Generation Script

Use the `exec` tool to run the Node.js script at `{baseDir}/generate.js`:

```bash
node {baseDir}/generate.js \
  --model <model_id> \
  --prompt "<enhanced prompt>" \
  [--aspect-ratio <ratio>] \
  [--num-images <1-4>] \
  [--negative-prompt "<negative prompt>"]
```

**Parameters:**
- `--model`: One of `midjourney`, `flux-pro`, `flux-dev`, `flux-schnell`, `sdxl`, `nano-banana`, `ideogram`, `recraft`
- `--prompt`: The image generation prompt (required)
- `--aspect-ratio`: Output aspect ratio, e.g. `16:9`, `1:1`, `9:16`, `4:3`, `3:4` (default: `1:1`)
- `--num-images`: Number of images to generate, 1-4 (default: `1`, Midjourney always returns 4)
- `--negative-prompt`: Things to avoid in the image (not supported by Midjourney)
- `--mode`: Midjourney speed mode: `turbo` (default, ~10-20s, requires Pro/Mega plan), `fast` (~30-60s), `relax` (free but slow)
- `--auto-upscale`: **(Midjourney only)** After imagine completes, automatically upscale all 4 grid images and return them as 4 individual single images. The output `images` array will contain 4 separate upscaled URLs instead of a single grid image.

**Example:**
```bash
node {baseDir}/generate.js \
  --model flux-pro \
  --prompt "a majestic snow leopard on a mountain peak, golden hour lighting, photorealistic, 8k" \
  --aspect-ratio 16:9 \
  --num-images 1
```

---

## ⚡ Midjourney Workflow — Submit Then Poll in the SAME Turn (REQUIRED)

**Why the user must not have to ask "还没好?":** The bot cannot "push" a message by itself. It only replies when you (the agent) produce a response in the current turn. If you reply with "已提交，完成后通知你" and then **end your turn**, the user will never get the result until they send a new message (e.g. "还没好?"). So you must **not** end your turn after submitting. In the **same** turn, keep polling until the job completes, then send the result in that same turn.

### Step 1 — Submit job (returns immediately with job_id)

```bash
node {baseDir}/generate.js \
  --model midjourney \
  --prompt "<enhanced prompt>" \
  --aspect-ratio 16:9 \
  --async
```

You get a `job_id`. **Do not** reply to the user yet with "已提交" and stop. Continue to Step 2 in the same turn.

### Step 2 — In the SAME turn, poll until completed

```bash
node {baseDir}/generate.js \
  --model midjourney \
  --poll \
  --job-id <job_id>
```

- If `status: "completed"` → go to Step 3 and send the result in this turn.
- If `status: "pending"` or `"processing"` → call poll again after ~15s (same turn). Repeat until completed (up to ~5 polls, ~75s).
- If still pending after ~75s, then you may reply once: "还在排队，稍后发「还没好」我帮你查"，and end the turn.

**Multiple parallel jobs:** Submit all jobs first, then in the same turn poll each job_id in turn until **all** are completed, then send one message with all results. Do not end the turn with "3 个任务已提交" and expect to "notify later" — the user will have to ask "还没好?" to get anything.

### Step 3 — Send result in this turn (only imageUrls / displayImageUrl)

When poll returns `status: "completed"`, send **one** message with the image links. Use **only** `displayImageUrl` or `imageUrls` (never `imageUrl` — temp link, expires).

**Critical — do NOT send fake/expired links:** Use only **`displayImageUrl`** or **`imageUrls`** from the script output (`cdn.legnext.ai/mj/...`). Never send `imageUrl` (`cdn.legnext.ai/temp/...`).

> 🎨 你的图片生成完成了！[图1](imageUrls[0]) [图2](imageUrls[1]) [图3](imageUrls[2]) [图4](imageUrls[3])  
> 想要放大哪张？(U1-U4) 或变体？(V1-V4)

### Summary: Same-turn polling

1. Submit → get job_id. Do **not** reply "已提交" and end the turn.
2. In the **same** turn, poll every ~15s until `status: "completed"` (or timeout ~75s).
3. When completed, send the result in that same turn. The user must **not** need to ask "还没好?" to see the result.

---

## Midjourney-Specific Notes

Midjourney is powered by **Legnext.ai** (faster and more stable than TTAPI). **Turbo mode is enabled by default** (`--turbo`), which reduces generation time to ~10-20 seconds (requires a Midjourney Pro or Mega plan). The `--aspect-ratio` is automatically appended to the prompt as `--ar <ratio>`. The model always generates 4 images in a grid. After generation, you can:

- Use `--auto-upscale` to **automatically upscale all 4 images** in one command — this is the recommended default for most use cases.
- Ask the user if they want to **upscale** (U1-U4) or **create variations** (V1-V4) of any image.
- Use `--action upscale --index <1-4> --job-id <id>` to upscale a specific image.
- Use `--action variation --index <1-4> --job-id <id>` to create variations.
- Use `--action reroll --job-id <id>` to re-generate with the same prompt.
- Add `--async` to any action to make it non-blocking.

**Upscale types** (via `--upscale-type`):
- `0` = Subtle (default): Conservative enhancement, preserves original details. Best for photography.
- `1` = Creative: More artistic interpretation. Best for illustrations.

**Variation types** (via `--variation-type`):
- `0` = Subtle (default): Minor changes while preserving composition.
- `1` = Strong: More dramatic variations with significant changes.

```bash
# Upscale image 2 from a previous Midjourney generation (async, non-blocking)
node {baseDir}/generate.js \
  --model midjourney \
  --action upscale \
  --index 2 \
  --job-id <previous_job_id> \
  --upscale-type 0 \
  --async

# Create a strong variation of image 3 (async)
node {baseDir}/generate.js \
  --model midjourney \
  --action variation \
  --index 3 \
  --job-id <previous_job_id> \
  --variation-type 1 \
  --async

# Reroll (regenerate with same prompt, async)
node {baseDir}/generate.js \
  --model midjourney \
  --action reroll \
  --job-id <previous_job_id> \
  --async
```

### Prompt Enhancement Tips

- **For Midjourney**: Add style keywords like `cinematic lighting`, `photorealistic`, `--v 7`, `--style raw`, `--ar 16:9`. Legnext.ai supports all MJ parameters.
- **For Flux**: Add quality boosters like `masterpiece`, `highly detailed`, `sharp focus`, `professional photography`
- **For Ideogram**: Be explicit about text content, font style, and layout
- **For Recraft**: Specify `vector illustration`, `flat design`, `icon style`, `SVG-style`

---

## Environment Variables

This skill requires the following environment variables to be set in your OpenClaw config:

| Variable | Description | Where to get it |
|---|---|---|
| `FAL_KEY` | fal.ai API key (for Flux, SDXL, Nano Banana, Ideogram, Recraft) | https://fal.ai/dashboard/keys |
| `LEGNEXT_KEY` | Legnext.ai API key (for Midjourney) | https://legnext.ai/dashboard |
| `IMAGE_GEN_PROXY_URL` | (Optional) Proxy server URL — if set, no API keys needed | Deployed proxy URL |

Configure them in `~/.openclaw/openclaw.json`:
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

---

## Example Conversations

**User**: "帮我画一只在雪山上的雪豹，电影感光效"
**Action**: Select `midjourney`, enhance prompt to `"a majestic snow leopard on a snowy mountain peak, cinematic lighting, dramatic atmosphere, ultra detailed --ar 16:9 --v 7"`, run script with `--auto-upscale --proxy`. This will automatically imagine + upscale all 4 images and return them as 4 individual single images in the `images` array. Present all 4 to the user.

**User**: "用 Flux 生成一张产品海报，白色背景，一瓶香水"
**Action**: Select `flux-pro`, enhance prompt, run script with `--aspect-ratio 3:4`. (Flux is fast ~5s, no async needed)

**User**: "快速生成一个草稿看看效果"
**Action**: Select `flux-schnell` for fastest generation (<2 seconds). No async needed.

**User**: "帮我做一个 App 图标，扁平风格，蓝色系"
**Action**: Select `recraft`, use prompt with `flat design icon, blue color scheme, minimal, vector style`.

**User**: "把第2张图片放大"
**Action**: Run with `--model midjourney --action upscale --index 2 --job-id <id> --async`, then poll for result.

---

## 🔌 Proxy Mode (Zero API Keys)

If `IMAGE_GEN_PROXY_URL` is set (or `--proxy` flag is used), the skill routes all requests through a proxy server instead of calling fal.ai / Legnext.ai directly. This means **users don't need any API keys** — the proxy handles authentication server-side.

### How It Works

```
User's Agent → generate.js --proxy → Image-Gen Proxy → fal.ai / Legnext.ai
                                         ↕
                                    Token Auth
                                  (100 free uses)
```

### Token-Based Authentication

The proxy uses a **Token-based authentication** system to manage free usage:

1. **First use**: When you run `generate.js` with `--proxy` for the first time, it automatically registers a free token from the proxy server. The token is saved locally at `~/.image-gen-token`.
2. **Subsequent uses**: The token is automatically loaded and sent with every request. No manual action needed.
3. **Free quota**: Each token has **100 free image generations** (all models combined, including Midjourney).
4. **One token per IP**: Each IP address can only register one token. This prevents abuse.
5. **Quota exhausted**: When all 100 uses are consumed, you will see a clear message. Upgrade to Pro for unlimited access.

> **Important**: The token file (`~/.image-gen-token`) persists across sessions. Clearing your AI agent's context will NOT reset your free quota.

### Usage

```bash
# Via environment variable (recommended — set once in OpenClaw config)
IMAGE_GEN_PROXY_URL=https://image-gen-proxy.vercel.app node {baseDir}/generate.js \
  --model flux-schnell \
  --prompt "a cute cat"

# Via CLI flag
node {baseDir}/generate.js \
  --model flux-schnell \
  --prompt "a cute cat" \
  --proxy \
  --proxy-url https://image-gen-proxy.vercel.app
```

### Proxy Mode for Midjourney

```bash
# Submit and get grid (4 images in one)
node {baseDir}/generate.js --model midjourney --prompt "a dragon" --proxy --proxy-url https://image-gen-proxy.vercel.app

# Submit and auto-upscale all 4 images (RECOMMENDED — returns 4 single images)
node {baseDir}/generate.js --model midjourney --prompt "a dragon" --auto-upscale --proxy --proxy-url https://image-gen-proxy.vercel.app

# Poll (does not consume quota)
node {baseDir}/generate.js --model midjourney --poll --job-id <id> --proxy --proxy-url https://image-gen-proxy.vercel.app
```

### Free Tier Limits (via Proxy)

| Item | Limit |
|---|---|
| Free generations per token | 100 |
| Tokens per IP address | 1 |
| Quota reset | Never (persistent) |
| Actions that consume quota | `generate` (fal.ai) and `imagine` (Midjourney) |
| Actions that are free | `poll`, `upscale`, `variation`, `reroll`, `describe` |

After the free tier is exhausted, users receive a `402` response with upgrade instructions.
