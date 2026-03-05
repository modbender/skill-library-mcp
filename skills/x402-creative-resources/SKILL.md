---
name: x402-creative-resources
description: Access Xona's x402 creative resource APIs on api.xona-agent.com. Includes creative director (design research), image generation (nano-banana, seedream, grok-imagine, qwen, designer), video generation, X news extraction, and PumpFun token intelligence. Use when the user asks to research design trends, generate images or videos, get latest news from X, or check PumpFun trending tokens.
---

# x402 Creative Resources

All endpoints live on `https://api.xona-agent.com` and are paid via x402 (Solana USDC micropayments). The agent wallet pays automatically.

## How to Call x402 Endpoints

Use the `x402-fetch.js` script in the workspace scripts folder. It handles the 402 payment flow automatically using the agent's Solana wallet.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js <endpoint> [payload_json]
```

**POST example:**
```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /image/creative-director '{"idea":"futuristic Solana DeFi dashboard"}'
```

**GET example:**
```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /token/pumpfun-trending
```

The script outputs JSON. Parse the response and extract relevant fields (`image_url`, `video_url`, `banner_url`, etc.) to present to the user.

## Resource Discovery

```bash
curl -s https://api.xona-agent.com/x402-resources
```

---

## Creative Director (Design Research) — $0.03

Research trending design ideas on X and Google, analyze user intent, return refined creative direction.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /image/creative-director \
  '{"idea":"futuristic Solana DeFi dashboard aesthetic","reference_images":["https://example.com/ref.jpg"]}'
```

| Field | Required | Description |
|-------|----------|-------------|
| `idea` | Yes | Creative idea or design research query |
| `reference_images` | No | Array of reference image URLs |

**Response:** `{ success, data: { intent, research, direction } }`

The `direction` array contains generation plans with `output_metadata.prompt` — feed these into an image generation endpoint.

---

## Image Generation

All image endpoints accept:

| Field | Required | Description |
|-------|----------|-------------|
| `prompt` | Yes | Detailed image description |
| `aspect_ratio` | No | `1:1` (default), `16:9`, `9:16`, `4:3`, `3:4` |
| `referenceImage` | No | Array of reference image URLs |

All return: `{ success, data: { image_url, image_description, metadata } }`

### Designer (Style Blending) — $0.08

Also accepts `style` (array of keywords to blend into prompt).

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /image/designer \
  '{"prompt":"a glowing Solana logo floating in space","style":["digital art","futuristic","neon"],"aspect_ratio":"16:9"}'
```

### Grok Imagine — $0.04

Artistic, handles text-in-image well. Cheapest option.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /image/grok-imagine \
  '{"prompt":"...","aspect_ratio":"1:1"}'
```

### Qwen Image — $0.05

Balanced quality and cost.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /image-model/qwen-image \
  '{"prompt":"...","aspect_ratio":"1:1"}'
```

### Seedream 4.5 — $0.08

ByteDance photorealistic model. Best for high-detail, realistic images.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /image-model/seedream-4.5 \
  '{"prompt":"...","aspect_ratio":"1:1"}'
```

### Nano Banana — $0.10

Fast creative generation. Good default.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /image/nano-banana \
  '{"prompt":"...","aspect_ratio":"1:1"}'
```

### Nano Banana Pro — $0.20

Highest quality.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /image/nano-banana-pro \
  '{"prompt":"...","aspect_ratio":"1:1"}'
```

### Model Selection Guide

| Model | Endpoint | Price | Best for |
|-------|----------|-------|----------|
| Grok Imagine | `/image/grok-imagine` | $0.04 | Artistic, text-in-image |
| Qwen Image | `/image-model/qwen-image` | $0.05 | Balanced quality/cost |
| Designer | `/image/designer` | $0.08 | Style-blended, art-directed |
| Seedream 4.5 | `/image-model/seedream-4.5` | $0.08 | Photorealistic |
| Nano Banana | `/image/nano-banana` | $0.10 | Fast creative, good default |
| Nano Banana Pro | `/image/nano-banana-pro` | $0.20 | Highest quality |

---

## Video Generation — $0.50

10-second AI video using Grok Imagine Video. Supports text-to-video and image-to-video.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /video/short-generation \
  '{"prompt":"camera slowly orbiting a glowing Solana logo in deep space","aspect_ratio":"16:9"}'
```

For image-to-video, pass a previously generated `image_url` as `image`:

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /video/short-generation \
  '{"prompt":"smooth zoom into center","aspect_ratio":"16:9","image":"https://cdn.example.com/img.jpg"}'
```

| Field | Required | Description |
|-------|----------|-------------|
| `prompt` | Yes | Video description with motion cues |
| `aspect_ratio` | No | Aspect ratio (default: `16:9`) |
| `image` | No | Still image URL to animate |

**Response:** `{ success, data: { video_url, duration, model, metadata } }`

Takes up to 5 minutes. Let the user know it's processing.

---

## X News Extraction — $0.50

Extract latest news from any X account, generate tweet draft and banner.

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /ai/x-news \
  '{"x_username":"solana"}'
```

| Field | Required | Description |
|-------|----------|-------------|
| `x_username` | Yes | X username (with or without @) |
| `x_persona` | No | X username whose style to mimic for tweet draft |

**Response:** `{ success, data: { x_username, trending_news: { title, tweet_draft, banner_url } } }`

---

## PumpFun Token Intelligence

### Trending Tokens — $0.10

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /token/pumpfun-trending
```

**Response:** `{ success, data: { summary, suggestions, trending_tokens, count } }`

### Top Movers — $0.10

```bash
node /home/node/.openclaw/workspace/scripts/x402-fetch.js /token/pumpfun-movers
```

Same response format as trending.

---

## Recommended Workflows

### Full Creative Pipeline
1. Call `/image/creative-director` with the user's idea
2. Use the returned `direction[].output_metadata.prompt` to call an image endpoint
3. Pass the generated `image_url` to `/video/short-generation` to animate it

### News + Visual Pipeline
1. Call `/ai/x-news` with a target X account
2. Present the `tweet_draft` and `banner_url`

### Market Intelligence
1. Call `/token/pumpfun-trending` for current meta
2. Call `/token/pumpfun-movers` for biggest moves
3. Generate themed images based on the dominant narrative
