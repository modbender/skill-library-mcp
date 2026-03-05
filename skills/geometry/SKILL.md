---
name: Geometry
slug: geometry
version: 1.0.0
description: Generate AI images from text prompts. Pay per request with USDC on Solana via x402. No API keys, no accounts.
author: geometry
tags: [image-generation, ai, solana, x402, usdc, flux, ideogram, imagen]
homepage: https://geometry.sh
docs: https://app.geometry.sh/developers
---

# Geometry — AI Image Generation API

> Generate images from text prompts. Pay per request with USDC on Solana via [x402](https://x402.org). No API keys, no accounts.

- **Homepage:** https://geometry.sh
- **Agent Card:** https://api.geometry.sh/.well-known/agent.json
- **Docs:** https://app.geometry.sh/developers

## Payment

| Field | Value |
|-------|-------|
| Protocol | x402 (version 2) |
| Network | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` |
| Scheme | exact |
| Currency | USDC |
| Facilitator | https://facilitator.payai.network |
| Pay To | `79BLYwUdsNpPzDktxjibFR4DKMhHV2Q8iBu7Fk7R9fuU` |

## Endpoints

### GET /api/x402/generate/quote

Get the USDC price for a model. **Free — no payment required.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | no | Model slug (default: `flux-dev`) |

**Example response:**

```json
{
  "success": true,
  "data": {
    "model": "flux-dev",
    "costUsdc": 0.0325,
    "paymentNetwork": "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",
    "payTo": "79BLYwUdsNpPzDktxjibFR4DKMhHV2Q8iBu7Fk7R9fuU"
  }
}
```

### POST /api/x402/generate

Generate an AI image from a text prompt. **Requires x402 USDC payment.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| prompt | string | yes | Text prompt (1–1000 chars) |
| model | string | no | Model slug (default: `flux-dev`) |

**Example request:**

```json
{
  "prompt": "A neon-lit Tokyo alley in the rain",
  "model": "flux-dev"
}
```

**Example response:**

```json
{
  "success": true,
  "data": {
    "id": "ab0e4a1b-179f-4a6e-b505-53206a3e2e4b",
    "status": "completed",
    "prompt": "A neon-lit Tokyo alley in the rain",
    "model": "flux-dev",
    "costUsdc": 0.0325,
    "imageUrl": "https://cdn.geometry.sh/generations/user-id/gen-id.png",
    "createdAt": "2026-02-15T17:29:17.256Z"
  }
}
```

## Available Models

| Slug | Name | Price (USDC) |
|------|------|-------------|
| bagel | Bagel | $0.1300 |
| bytedance-seedream-v4.5-text-to-image | Bytedance | $0.0520 |
| bytedance-seedream-v3-text-to-image | Bytedance | $0.0390 |
| bytedance-dreamina-v3.1-text-to-image | Bytedance | $0.0390 |
| bytedance-seedream-v4-text-to-image | Bytedance Seedream v4 | $0.0390 |
| emu-3.5-image-text-to-image | Emu 3.5 Image | $0.1950 |
| flux-pro-kontext-max-text-to-image | FLUX.1 Kontext [max] | $0.1040 |
| flux-pro-kontext-text-to-image | FLUX.1 Kontext [pro] | $0.0520 |
| flux-dev | FLUX.1 [dev] | $0.0325 |
| flux-pro-v1.1-ultra | FLUX1.1 [pro] ultra | $0.0780 |
| bria-fibo-generate | Fibo | $0.0520 |
| bria-fibo-lite-generate | Fibo Lite | $0.0468 |
| gemini-25-flash-image | Gemini 2.5 Flash Image | $0.0517 |
| gemini-3-pro-image-preview | Gemini 3 Pro Image Preview | $0.1950 |
| xai-grok-imagine-image | Grok Imagine Image | $0.0260 |
| ideogram-v3 | Ideogram Text to Image | $0.0390 |
| ideogram-v2 | Ideogram V2 | $0.1040 |
| imagen4-preview | Imagen 4 | $0.0520 |
| imagen4-preview-fast | Imagen 4 | $0.0260 |
| imagen4-preview-ultra | Imagen 4 Ultra | $0.0780 |
| kling-image-v3-text-to-image | Kling Image | $0.0364 |
| kling-image-o3-text-to-image | Kling Image | $0.0364 |
| minimax-image-01 | MiniMax (Hailuo AI) Text to Image | $0.0130 |
| nano-banana | Nano Banana | $0.0517 |
| nano-banana-pro | Nano Banana Pro | $0.1950 |
| qwen-image-max-text-to-image | Qwen Image Max | $0.0975 |
| recraft-v3-text-to-image | Recraft V3 | $0.0520 |
| reve-text-to-image | Reve | $0.0520 |
| vidu-q2-text-to-image | Vidu | $0.0650 |
| wan-v2.2-5b-text-to-image | Wan | $0.0208 |
| wan-v2.2-a14b-text-to-image | Wan | $0.0325 |
| wan-25-preview-text-to-image | Wan 2.5 Text to Image | $0.0650 |
| wan-v2.2-a14b-text-to-image-lora | Wan v2.2 A14B Text-to-Image A14B with LoRAs | $0.0650 |

## Quick Start

### JavaScript

```javascript
import { createKeyPairSignerFromBytes } from "@solana/kit";
import { wrapFetchWithPayment, x402Client } from "@x402/fetch";
import { ExactSvmScheme } from "@x402/svm/exact/client";

const signer = await createKeyPairSignerFromBytes(keypairBytes);
const client = new x402Client();
client.register("solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp", new ExactSvmScheme(signer));

const fetchWithPay = wrapFetchWithPayment(fetch, client);

const res = await fetchWithPay("https://api.geometry.sh/api/x402/generate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt: "A cat in space" }),
});

const { data } = await res.json();
console.log(data.imageUrl);
```

### cURL

```bash
# Step 1: Get a quote (free)
curl https://api.geometry.sh/api/x402/generate/quote?model=flux-dev

# Step 2: POST to generate (returns 402 with payment instructions)
curl -X POST https://api.geometry.sh/api/x402/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cat in space", "model": "flux-dev"}'

# Step 3: Use an x402 client to handle payment automatically
# npm install @x402/fetch @x402/svm
```
