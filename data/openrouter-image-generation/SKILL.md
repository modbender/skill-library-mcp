---
name: openrouter-image-generation
description: Generate or edit images through OpenRouter's multimodal image generation endpoint (`/api/v1/chat/completions`) using OpenRouter-compatible image models. Use for text-to-image or image-to-image requests when the user wants OpenRouter, `OPENROUTER_API_KEY`, model overrides, or provider-specific `image_config` options.
---

# OpenRouter Image Generation & Editing

Generate new images or edit existing ones using OpenRouter image-capable models via the Chat Completions API.

## Usage

Run the script using absolute path (do NOT cd to the skill directory first):

**Generate new image:**
```bash
# Ensure outbound directory exists first
mkdir -p ~/.openclaw/media/outbound

uv run ~/.openclaw/workspace/skills/openrouter-image-generation/scripts/generate_image.py \
  --prompt "your image description" \
  --filename "~/.openclaw/media/outbound/output-name.png" \
  --model google/gemini-2.5-flash-image \
  [--aspect-ratio 16:9] \
  [--image-size 2K]
```

**Edit existing image (image-to-image):**
```bash
# Ensure outbound directory exists first
mkdir -p ~/.openclaw/media/outbound

uv run ~/.openclaw/workspace/skills/openrouter-image-generation/scripts/generate_image.py \
  --prompt "editing instructions" \
  --filename "~/.openclaw/media/outbound/output-name.png" \
  --input-image "path/to/input.png" \
  --model google/gemini-2.5-flash-image
```

**Important:** Default OpenClaw delivery path is `~/.openclaw/media/outbound/`. Save generated images there so other OpenClaw flows can pick them up easily.

## API Key

The script checks for API key in this order:
1. `--api-key` argument
2. `OPENROUTER_API_KEY` environment variable

Optional OpenRouter attribution headers:
- `--site-url` or `OPENROUTER_SITE_URL`
- `--app-name` or `OPENROUTER_APP_NAME`

## Model + Image Config

- `--model <openrouter-model-id>` is required (no script default)
- Example model: `google/gemini-2.5-flash-image`
- Use `--aspect-ratio` for `image_config.aspect_ratio` (for example `1:1`, `16:9`)
- Use `--image-size` for `image_config.image_size` (`1K`, `2K`, `4K`)
- Use `--image-config-json '{"key":"value"}'` for advanced/provider-specific extras (merged into `image_config`)

Note: OpenRouter docs show `aspect_ratio` and `image_size` as the common image config fields for image generation. Additional keys may exist for specific providers/models (for example Sourceful features). If a request fails, remove unsupported options or switch models.

Note: The script always sends `modalities: ["image", "text"]`. Image-only models (some FLUX variants) may reject this — if you get an unexpected error with a non-Gemini model, this may be the cause. No workaround is currently exposed via CLI args.

## Default Workflow (draft -> iterate -> final)

Goal: iterate quickly before spending time on higher-quality settings.

- Draft: smaller size / faster model
  - `--image-size 1K`
- Iterate: adjust prompt in small diffs and keep a new filename each run
- Final: larger size or higher quality if the selected model supports it
  - Example: `--image-size 4K --aspect-ratio 16:9`

## Preflight + Common Failures

- Preflight:
  - `command -v uv`
  - `test -n "$OPENROUTER_API_KEY"` (or pass `--api-key`)
  - `test -d ~/.openclaw/media/outbound || mkdir -p ~/.openclaw/media/outbound`
  - If editing: `test -f "path/to/input.png"`

- Common failures:
  - `Error: No API key provided.` -> set `OPENROUTER_API_KEY` or pass `--api-key`
  - `Error loading input image:` -> bad path or unreadable file
  - `HTTP 400` with model/image config error -> unsupported model or invalid `image_config.aspect_ratio` / `image_config.image_size`
  - `HTTP 401/403` -> invalid key, no model access, or quota/credits issue
  - `No image found in response` -> model may not support image output or request format rejected

## Filename Generation

Generate filenames with the pattern: `~/.openclaw/media/outbound/yyyy-mm-dd-hh-mm-ss-name.png`

Examples:
- `~/.openclaw/media/outbound/2026-02-26-14-23-05-product-shot.png`
- `~/.openclaw/media/outbound/2026-02-26-14-25-30-sky-edit.png`

## Prompt Handling

- For generation: pass the user's description as-is unless it is too vague to be actionable.
- For editing: make the requested change explicit and preserve everything else.

Prompt template for precise edits:
- `Change ONLY: <change>. Keep identical: subject, composition/crop, pose, lighting, color palette, background, text, and overall style. Do not add new objects.`

## Output

- Save the first returned image to `~/.openclaw/media/outbound/output-name.png` by default (pass that full path in `--filename`)
- Supports OpenRouter's base64 data URL image responses (`message.images[0].image_url.url`)
- Prints the saved file path
- Do not read the image back unless the user asks

## Examples

**Generate new image:**
```bash
mkdir -p ~/.openclaw/media/outbound

uv run ~/.openclaw/workspace/skills/openrouter-image-generation/scripts/generate_image.py \
  --prompt "A cinematic product photo of a matte black mechanical keyboard on a wooden desk, warm window light" \
  --filename "~/.openclaw/media/outbound/2026-02-26-14-23-05-keyboard-product-shot.png" \
  --model google/gemini-2.5-flash-image \
  --aspect-ratio 16:9 \
  --image-size 2K
```

**Edit existing image:**
```bash
mkdir -p ~/.openclaw/media/outbound

uv run ~/.openclaw/workspace/skills/openrouter-image-generation/scripts/generate_image.py \
  --prompt "Change ONLY: make the sky dramatic with orange sunset clouds. Keep identical: subject, composition, lighting on foreground, and overall style." \
  --filename "~/.openclaw/media/outbound/2026-02-26-14-25-30-sunset-sky-edit.png" \
  --model google/gemini-2.5-flash-image \
  --input-image "original-photo.jpg"
```

## Reference

- OpenRouter docs: https://openrouter.ai/docs/guides/overview/multimodal/image-generation
