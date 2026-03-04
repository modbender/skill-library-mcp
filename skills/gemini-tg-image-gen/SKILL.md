---
name: gemini-tg-image-gen
description: Generate images via OpenRouter (google/gemini-2.5-flash-image) and send to Telegram. Use when user asks for AI-generated images in TG.
---

# Gemini TG Image Gen (OpenRouter)

## Workflow

1. Immediately notify user in Telegram: `"⏳ Идёт генерация, подождите немного..."`
2. Use OpenRouter model `google/gemini-2.5-flash-image`.
3. Read API key from env: `OPENROUTER_API_KEY`.
4. Run script to generate and save image locally.
5. Send the image to Telegram using the `message` tool (local file path).
6. NO_REPLY.

## Usage

```bash
OPENROUTER_API_KEY=... python3 scripts/generate_image.py "<prompt>"
```

The script prints a JSON object with `paths`.

## Telegram Send

```
# step 1: waiting message
message action=send channel=telegram text="⏳ Идёт генерация, подождите немного..."

# step 5: send image
message action=send channel=telegram media="/root/.openclaw/workspace/tmp/openrouter_image_*.png" caption="Generated: <prompt>"
```

After sending, use `NO_REPLY`.
