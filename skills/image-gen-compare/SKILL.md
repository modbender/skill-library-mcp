---
name: image-gen-compare
version: 1.0.0
description: Side-by-side comparison of paid vs local image generation models — DALL-E 3, FLUX.1-schnell, Gemini Imagen, and others. Generates images from the same prompt, logs metadata, and stores run history. Use when evaluating which image model to use for a project.
metadata:
  {"openclaw": {"emoji": "🖼️", "requires": {"bins": ["python3"], "env": ["OPENAI_API_KEY"]}, "primaryEnv": "OPENAI_API_KEY", "network": {"outbound": true, "reason": "Calls OpenAI DALL-E API for paid image generation. Local models (FLUX via mflux) run on-device."}}}
---

# Image Gen Compare

Generate images from the same prompt across multiple models and compare results. Tracks costs, generation time, and quality for informed model selection.

## Supported Models

| Model | Type | Cost | Speed (M4) |
|---|---|---|---|
| DALL-E 3 | Cloud (OpenAI) | ~$0.04-0.08/img | 5-10s |
| FLUX.1-schnell | Local (mflux) | Free | ~105s |
| Gemini Imagen 4.0 | Cloud (Google) | $0.04-0.13/img | 3-8s |
| SDXL-Turbo | Local (diffusers) | Free | ~15s (512px) |

## Usage

```bash
python3 scripts/image_gen_compare.py --prompt "cyberpunk alley at night"
python3 scripts/image_gen_compare.py --model dalle3  # Single model
python3 scripts/image_gen_compare.py --list           # Previous runs
```

## Key Lesson

Gemini (Imagen 4.0) beats fine-tuned SD 1.5 with zero training. Use commercial APIs for production quality; local models for experimentation, privacy, and offline use.

## Files

- `scripts/image_gen_compare.py` — Comparison script with metadata logging
