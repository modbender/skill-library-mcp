---
name: alicloud-ai-image-qwen-image-edit
description: Edit images with Alibaba Cloud Model Studio Qwen Image Edit Max (qwen-image-edit-max). Use when modifying existing images (inpaint, replace, style transfer, local edits), preserving subject consistency, or documenting image edit request/response mappings.
---

Category: provider

# Model Studio Qwen Image Edit

Use Qwen Image Edit models for instruction-based image editing instead of text-to-image generation.

## Critical model names

Use one of these exact model strings:
- `qwen-image-edit-max`
- `qwen-image-edit-max-2026-01-16`

## Prerequisites

- Install SDK in a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install dashscope
```
- Set `DASHSCOPE_API_KEY` in your environment, or add `dashscope_api_key` to `~/.alibabacloud/credentials`.

## Normalized interface (image.edit)

### Request
- `prompt` (string, required)
- `image` (string | bytes, required) source image URL/path/bytes
- `mask` (string | bytes, optional) inpaint region mask
- `size` (string, optional) e.g. `1024*1024`
- `seed` (int, optional)

### Response
- `image_url` (string)
- `seed` (int)
- `request_id` (string)

## Operational guidance

- Keep prompts task-oriented: describe what to change and what to preserve.
- Use masks for deterministic local edits.
- Save output assets to object storage and persist only URLs.
- For subject consistency, provide explicit constraints in prompt.

## Local helper script

Prepare a normalized request JSON and validate response schema:

```bash
.venv/bin/python skills/ai/image/alicloud-ai-image-qwen-image-edit/scripts/prepare_edit_request.py \
  --prompt "Replace the sky with sunset, keep buildings unchanged" \
  --image "https://example.com/input.png"
```

## Output location

- Default output: `output/ai-image-qwen-image-edit/images/`
- Override base dir with `OUTPUT_DIR`.

## References

- `references/sources.md`
