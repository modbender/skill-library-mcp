---
name: liblib-ai-gen
description: Generate images with Seedream4.5 and videos with Kling via LiblibAI API. Use when user asks to generate/create images, pictures, illustrations, or videos using LiblibAI, Seedream, or Kling models.
---

# LiblibAI Image & Video Generation

Generate images (Seedream4.5) and videos (Kling) via LiblibAI's API.

## Prerequisites

Environment variables must be set:
- `LIB_ACCESS_KEY` — API access key
- `LIB_SECRET_KEY` — API secret key

## Usage

Run the CLI script at `scripts/liblib_client.py`:

```bash
# Generate image
python3 scripts/liblib_client.py image "a cute cat wearing a hat" --width 2048 --height 2048

# Generate video from text
python3 scripts/liblib_client.py text2video "a rocket launching into space" --model kling-v2-6 --duration 5

# Generate video from image
python3 scripts/liblib_client.py img2video "the cat turns its head" --start-frame https://example.com/cat.jpg

# Check task status
python3 scripts/liblib_client.py status <generateUuid>
```

## Image Generation (Seedream4.5)

- Endpoint: `POST /api/generate/seedreamV4`
- Model: `doubao-seedream-4-5-251128`
- Default size: 2048×2048. For 4.5, min total pixels = 3,686,400 (e.g. 2560×1440)
- Supports reference images (1-14), prompt expansion, and sequential image generation
- Options: `--width`, `--height`, `--count` (1-15), `--ref-images`, `--prompt-magic`

## Video Generation (Kling)

### Text-to-Video
- Endpoint: `POST /api/generate/video/kling/text2video`
- Models: `kling-v2-6` (latest, supports sound), `kling-v2-1-master`, `kling-v2-5-turbo`, etc.
- Options: `--model`, `--aspect` (16:9/9:16/1:1), `--duration` (5/10s), `--mode` (std/pro), `--sound` (on/off)

### Image-to-Video
- Endpoint: `POST /api/generate/video/kling/img2video`
- Provide `--start-frame` image URL; optionally `--end-frame` (v1-6 only)
- For kling-v2-6: uses `images` array instead of startFrame/endFrame

## Async Pattern

All generation tasks are async:
1. Submit task → get `generateUuid`
2. Poll `POST /api/generate/status` with `{ "generateUuid": "..." }`
3. Result contains `images[].imageUrl` or `videos[].videoUrl`

The script auto-polls by default. Use `--no-poll` to submit only.

## Notes

- QPS limit: 1 request/second for task submission
- Max concurrent tasks: 5
- Image URLs in results expire after 7 days
- For kling-v2-5-turbo and kling-v2-6, mode must be "pro" (default)
- Sound generation only supported on kling-v2-6+
