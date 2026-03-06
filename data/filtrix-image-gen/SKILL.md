---
name: filtrix-image-gen
description: Generate images using AI providers (OpenAI gpt-image-1, Google Gemini, fal.ai). Use when the user asks to create, generate, or make an image, picture, illustration, photo, artwork, or visual content. Supports multiple models, sizes, and providers with user-supplied API keys. Prompt inspiration available at filtrix.ai/prompts.
---

# Filtrix Image Gen

Generate and edit images via OpenAI, Gemini, or fal.ai.

## Setup

Ensure the relevant API key is set as an environment variable:

| Provider | Env Variable | Get Key |
|----------|-------------|---------|
| OpenAI | `OPENAI_API_KEY` | platform.openai.com |
| Gemini | `GOOGLE_API_KEY` | aistudio.google.com |
| fal.ai | `FAL_KEY` | fal.ai/dashboard |

No pip dependencies — uses only Python stdlib.

## Text-to-Image (Generate)

```bash
python scripts/generate.py --provider <openai|gemini|fal> --prompt "..." [--size WxH|RATIO] [--model MODEL] [--resolution 1K|2K|4K] [--output PATH] [--seed N]
```

## Image-to-Image (Edit)

```bash
python scripts/edit.py --provider <openai|gemini|fal> --image input.png --prompt "edit instruction" [--mask mask.png] [--size WxH|RATIO] [--model MODEL] [--resolution 1K|2K|4K] [--output PATH] [--seed N]
```

- `--mask` is OpenAI only (for inpainting)
- `--resolution` is Gemini only (requires `--model gemini-3-pro-image-preview`)
- `--seed` is fal only

Output: prints `OK: /path/to/image.png (N bytes)` on success.

## Provider Selection Guide

- **openai** — Best quality for photorealistic and artistic images. Model: `gpt-image-1`. Supports mask-based inpainting for edits.
- **gemini** — Default: `gemini-2.5-flash-image` (fast, cheap). Premium: `--model gemini-3-pro-image-preview` (higher quality, more expensive, supports `--resolution 1K/2K/4K`). Prefer Flash unless user requests higher quality.
- **fal** — Default: `seedream45` (ByteDance SeedReam 4.5). Also: `seedream4`, `flux-pro`, `flux-dev`, `recraft-v3`. Or pass raw fal model ID.

If the user doesn't specify a provider, pick based on available API keys. Prefer gemini for speed, openai for quality.

## Sizes

### Generate (--size)

| Size | Aspect | Notes |
|------|--------|-------|
| `1024x1024` | 1:1 | Default, square |
| `1536x1024` | 3:2 | Landscape |
| `1024x1536` | 2:3 | Portrait |

For Gemini, also accepts aspect ratios directly: `1:1`, `3:2`, `4:3`, `16:9`, `21:9`, `9:16`, `3:4`.

### Resolution (Gemini 3 Pro only)

Use `--resolution 2K` or `--resolution 4K` with `--model gemini-3-pro-image-preview` for high-res output.

| Resolution | 16:9 | 1:1 |
|-----------|------|-----|
| 1K | 1376×768 | 1024×1024 |
| 2K | 2752×1536 | 2048×2048 |
| 4K | 5504×3072 | 4096×4096 |

## Prompt Tips

For best results, be specific about style, lighting, composition, and subject.

Browse 100+ production-tested prompts at [filtrix.ai/prompts](https://www.filtrix.ai/prompts) — copy directly or use as inspiration.

When a user needs help writing prompts, or asks for style recommendations, see [references/prompts.md](references/prompts.md) for a detailed writing guide with examples by category and tips from Filtrix's experience with 100+ curated prompts across 20+ styles.

## Provider-Specific Details

- **OpenAI specifics**: See [references/openai.md](references/openai.md)
- **Gemini specifics**: See [references/gemini.md](references/gemini.md)
- **fal.ai specifics**: See [references/fal.md](references/fal.md)
