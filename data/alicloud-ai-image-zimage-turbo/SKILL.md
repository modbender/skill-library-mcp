---
name: alicloud-ai-image-zimage-turbo
description: Generate images with Alibaba Cloud Model Studio Z-Image Turbo (z-image-turbo) via DashScope multimodal-generation API. Use when creating text-to-image outputs, controlling size/seed/prompt_extend, or documenting request/response mapping for Z-Image.
---

Category: provider

# Model Studio Z-Image Turbo

Use Z-Image Turbo for fast text-to-image generation via the DashScope multimodal-generation API.

## Critical model name

Use ONLY this exact model string:
- `z-image-turbo`

## Prerequisites

- Set `DASHSCOPE_API_KEY` in your environment, or add `dashscope_api_key` to `~/.alibabacloud/credentials` (env takes precedence).
- Choose region endpoint (Beijing or Singapore). If unsure, pick the most reasonable region or ask the user.

## Normalized interface (image.generate)

### Request
- `prompt` (string, required)
- `size` (string, optional) e.g. `1024*1024`
- `seed` (int, optional)
- `prompt_extend` (bool, optional; default false)
- `base_url` (string, optional) override API endpoint

### Response
- `image_url` (string)
- `width` (int)
- `height` (int)
- `prompt` (string)
- `rewritten_prompt` (string, optional)
- `reasoning` (string, optional)
- `request_id` (string)

## Quick start (curl)

```bash
curl -sS 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -d '{
    "model": "z-image-turbo",
    "input": {
      "messages": [
        {
          "role": "user",
          "content": [{"text": "A calm lake at dawn, a lone angler casting a line, cinematic lighting"}]
        }
      ]
    },
    "parameters": {
      "size": "1024*1024",
      "prompt_extend": false
    }
  }'
```

## Local helper script

```bash
python skills/ai/image/alicloud-ai-image-zimage-turbo/scripts/generate_image.py \
  --request '{"prompt":"a fishing scene at dawn, cinematic, realistic","size":"1024*1024"}' \
  --output output/ai-image-zimage-turbo/images/fishing.png \
  --print-response
```

## Size notes

- Total pixels must be between `512*512` and `2048*2048`.
- Prefer common sizes like `1024*1024`, `1280*720`, `1536*864`.

## Cost note

- `prompt_extend=true` is billed higher than `false`. Only enable when you need rewritten prompts.

## Output location

- Default output: `output/ai-image-zimage-turbo/images/`
- Override base dir with `OUTPUT_DIR`.

## References

- `references/api_reference.md` for request/response schema and regional endpoints.
- `references/sources.md` for official docs.
