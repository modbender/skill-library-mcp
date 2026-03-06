---
name: skill-x-post-ai-image
description: Generate an AI image via Gemini and post it to X (Twitter) using OAuth1. Supports text-only or text+image tweets.
metadata:
  openclaw:
    requires: { bins: ["uv", "xurl"] }
---

# X Post with AI-Generated Image

Generate a Gemini AI image from a text prompt, compress it, and post it as a tweet — all in one command.

## Prerequisites
- `xurl` CLI (X/Twitter auth) — see xurl skill
- `GEMINI_API_KEY` env var
- `nano-banana-pro` skill installed (OpenClaw)
- `uv` Python runner

## Setup

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export X_CONSUMER_KEY="..."
export X_CONSUMER_SECRET="..."
export X_ACCESS_TOKEN="..."
export X_ACCESS_TOKEN_SECRET="..."
```

## Usage

```bash
# Post tweet with AI-generated image
python3 scripts/post_with_image.py \
  --text "Your tweet text here" \
  --prompt "AI image prompt — describe the visual"

# Text-only tweet
python3 scripts/post_with_image.py \
  --text "Your tweet text" \
  --no-image
```

## How it works
1. Calls Gemini image generation with prompt → PNG
2. Compresses + resizes to 1200×675 JPEG (Twitter optimal)
3. Uploads via Twitter media API (OAuth1)
4. Posts tweet with media via `xurl`

## Inputs
| Param | Description |
|-------|-------------|
| `--text` | Tweet text (required) |
| `--prompt` | Image generation prompt (optional) |
| `--no-image` | Skip image, post text only |

## Output
Tweet posted; media ID and confirmation logged to stdout.
