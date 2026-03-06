---
name: quiverai
description: Generate and vectorize SVG graphics via the QuiverAI API (Arrow model). Use when the user asks to create logos, icons, or illustrations as SVG, convert raster images (PNG/JPEG/WebP) to SVG, or generate vector graphics from text prompts.
metadata:
  {
    "openclaw":
      {
        "emoji": "🖋️",
        "requires": { "env": ["QUIVERAI_API_KEY"] },
        "primaryEnv": "QUIVERAI_API_KEY",
      },
  }
---

# QuiverAI — AI Vector Graphics

QuiverAI generates production-ready SVGs from text prompts or raster images.

- Site: https://quiver.ai
- Docs: https://docs.quiver.ai
- API base: `https://api.quiver.ai/v1`
- Model: `arrow-preview`
- Auth: Bearer token via `QUIVERAI_API_KEY`
- Billing: 1 credit per request (regardless of `n`).

## Setup

Get an API key at https://app.quiver.ai/settings/api-keys (create account at https://quiver.ai/start first).

## Text to SVG

Generate SVGs from a text description.

**Endpoint:** `POST /v1/svgs/generations`

```bash
curl -X POST https://api.quiver.ai/v1/svgs/generations \
  -H "Authorization: Bearer $QUIVERAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "arrow-preview",
    "prompt": "A minimalist monogram logo using the letter Q",
    "n": 1,
    "stream": false
  }'
```

Node.js SDK (`npm install @quiverai/sdk`):

```typescript
import { QuiverAI } from "@quiverai/sdk";
const client = new QuiverAI({ bearerAuth: process.env.QUIVERAI_API_KEY });

const result = await client.createSVGs.generateSVG({
  model: "arrow-preview",
  prompt: "A minimalist monogram logo using the letter Q",
});
// result.data[0].svg contains the SVG markup
```

### Parameters

| Param | Type | Default | Description |
|---|---|---|---|
| `model` | string | — | Required. Use `arrow-preview`. |
| `prompt` | string | — | Required. Describes the desired SVG. |
| `instructions` | string | — | Additional style guidance (e.g. "flat monochrome, rounded corners"). |
| `references` | array | — | Up to 4 reference images (`{ url }` or `{ base64 }`). |
| `n` | int | 1 | Number of outputs (1–16). |
| `temperature` | float | 1 | Sampling temperature (0–2). Lower = more deterministic. |
| `top_p` | float | 1 | Nucleus sampling (0–1). |
| `max_output_tokens` | int | — | Upper bound for output tokens (max 131072). |
| `stream` | bool | false | SSE streaming (events: `reasoning`, `draft`, `content`). |

### Response

```json
{
  "id": "resp_01J...",
  "created": 1704067200,
  "data": [{ "svg": "<svg ...>...</svg>", "mime_type": "image/svg+xml" }],
  "usage": { "total_tokens": 1640, "input_tokens": 1200, "output_tokens": 440 }
}
```

## Image to SVG (Vectorize)

Convert a raster image (PNG/JPEG/WebP) into SVG.

**Endpoint:** `POST /v1/svgs/vectorizations`

```bash
curl -X POST https://api.quiver.ai/v1/svgs/vectorizations \
  -H "Authorization: Bearer $QUIVERAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "arrow-preview",
    "stream": false,
    "image": { "url": "https://example.com/logo.png" }
  }'
```

SDK:

```typescript
const result = await client.vectorizeSVG.vectorizeSVG({
  model: "arrow-preview",
  image: { url: "https://example.com/logo.png" },
});
```

### Additional parameters (beyond Text-to-SVG shared ones)

| Param | Type | Default | Description |
|---|---|---|---|
| `image` | object | — | Required. `{ url: "..." }` or `{ base64: "..." }`. |
| `auto_crop` | bool | false | Crop to dominant subject before vectorization. |
| `target_size` | int | — | Square resize target in px (128–4096) before inference. |

Response format is identical to Text-to-SVG.

## Error codes

| Status | Code | Meaning |
|---|---|---|
| 400 | `invalid_request` | Malformed body or missing fields. |
| 401 | `unauthorized` | Bad or missing API key. |
| 402 | `insufficient_credits` | Out of credits. |
| 429 | `rate_limit_exceeded` | Too many requests; back off and retry. |

## Tips

- Save SVG output to a `.svg` file for immediate use.
- Use `instructions` to control style without changing the prompt.
- For logos, try low `temperature` (0.3–0.5) for cleaner, more consistent results.
- Use `references` to provide visual examples the model should match.
- For vectorization, enable `auto_crop: true` when the source image has excess whitespace.
