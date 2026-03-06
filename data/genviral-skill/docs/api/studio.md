# Studio AI

Generate AI images and videos through the Partner API. Same model catalog and credit rules as the Genviral web app.

All commands are key-scoped and use the standard Partner API response envelope.

## Commands

| Command | API | Description |
|---------|-----|-------------|
| `studio-models` | `GET /studio/models` | List available image/video models |
| `studio-generate-image` | `POST /studio/images/generate` | Generate an image synchronously |
| `studio-generate-video` | `POST /studio/videos/generate` | Start async video generation |
| `studio-video-status` | `GET /studio/videos/{videoId}` | Poll video generation status |

---

## studio-models

List available Studio models with capabilities, credit costs, and supported params.

```bash
genviral.sh studio-models                  # all models
genviral.sh studio-models --mode image     # image models only
genviral.sh studio-models --mode video     # video models only
genviral.sh studio-models --json           # raw JSON output
```

### Options

| Flag | Type | Description |
|------|------|-------------|
| `--mode` | `image` or `video` | Filter by model type. Omit for both |
| `--json` | flag | Output raw JSON data |

### Response Data

Each model includes:
- `id` - Model ID to use in generation requests (e.g., `google/nano-banana`)
- `mode` - `image` or `video`
- `name` - Display name
- `provider` - Provider label
- `credits.default_cost` - Credit estimate per generation
- `inputs` - Required/optional input fields
- `params` - Supported normalized params

**Always call this first** to discover model IDs and what params they support before generating.

---

## studio-generate-image

Generate one AI image synchronously. Returns hosted output URL immediately.

```bash
# Basic image generation
genviral.sh studio-generate-image \
  --model-id "google/nano-banana" \
  --prompt "A cinematic beach sunset with palm trees" \
  --aspect-ratio "16:9"

# With output format
genviral.sh studio-generate-image \
  --model-id "google/nano-banana" \
  --prompt "Minimalist product photo, white background" \
  --output-format jpeg \
  --aspect-ratio "1:1"

# With reference images
genviral.sh studio-generate-image \
  --model-id "some/model" \
  --prompt "Transform this photo into anime style" \
  --image-urls "https://example.com/photo.jpg"

# With model-specific raw params
genviral.sh studio-generate-image \
  --model-id "google/nano-banana" \
  --prompt "Abstract art" \
  --raw-params '{"seed": 42}'
```

### Options

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--model-id` | string | Yes | Model ID from `studio-models` |
| `--prompt` | string | Yes | Generation prompt |
| `--image-urls` | string | No | Comma-separated input/reference image URLs |
| `--aspect-ratio` | string | No | e.g., `16:9`, `9:16`, `1:1` |
| `--resolution` | string | No | Target resolution |
| `--output-format` | string | No | e.g., `jpeg`, `png` |
| `--size` | string | No | Size hint |
| `--max-images` | number | No | Max images to return |
| `--scale-factor` | number | No | Upscale factor |
| `--raw-params` | JSON | No | Model-specific passthrough params |
| `--json` | flag | No | Output raw JSON data |

### Response

Returns `file_id`, `output_url`, `preview_url`, `credits_used`, `model_id`, and `provider`.

The `output_url` is a hosted CDN URL you can use directly in slideshows, posts, or download.

---

## studio-generate-video

Start async video generation. Returns a `video_id` for polling.

```bash
# Text-to-video
genviral.sh studio-generate-video \
  --model-id "openai/sora-2" \
  --prompt "A drone shot over neon city streets at night" \
  --duration-seconds 8 \
  --aspect-ratio "16:9"

# Image-to-video
genviral.sh studio-generate-video \
  --model-id "some/img2vid-model" \
  --prompt "Slowly zoom in with cinematic motion" \
  --image-url "https://cdn.example.com/photo.jpg" \
  --duration-seconds 5

# With speech/lipsync
genviral.sh studio-generate-video \
  --model-id "some/talking-model" \
  --speech-text "Welcome to our channel" \
  --voice-id "voice_abc" \
  --image-url "https://cdn.example.com/avatar.jpg"

# Video-to-video
genviral.sh studio-generate-video \
  --model-id "some/vid2vid-model" \
  --prompt "Apply cinematic color grading" \
  --video-url "https://cdn.example.com/input.mp4"
```

### Options

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--model-id` | string | Yes | Model ID from `studio-models` |
| `--prompt` | string | No | Main generation prompt |
| `--speech-text` | string | No | Speech script for talking/lipsync models |
| `--voice-id` | string | No | Voice identifier (used with `--speech-text`) |
| `--image-url` | string | No | Input image URL for image-to-video |
| `--video-url` | string | No | Input video URL for video-to-video |
| `--audio-url` | string | No | External audio URL |
| `--negative-prompt` | string | No | Negative prompt |
| `--duration-seconds` | number | No | Video duration in seconds |
| `--aspect-ratio` | string | No | e.g., `16:9`, `9:16` |
| `--resolution` | string | No | Target resolution |
| `--fps` | number | No | Frames per second |
| `--generate-audio` | bool | No | Auto-generate audio |
| `--raw-params` | JSON | No | Model-specific passthrough params |
| `--json` | flag | No | Output raw JSON data |

### Response

Returns `video_id`, `status` (`processing`), `credits_used`, `model_id`, and `provider`.

**Important:** Video generation is async. Use `studio-video-status` to poll for completion.

---

## studio-video-status

Poll video generation status. Supports both one-shot checks and auto-polling.

```bash
# One-shot status check
genviral.sh studio-video-status --video-id "22222222-2222-2222-2222-222222222222"

# Auto-poll until done (default: every 5s, max 120s)
genviral.sh studio-video-status --video-id VIDEO_UUID --poll

# Custom poll intervals
genviral.sh studio-video-status --video-id VIDEO_UUID --poll --poll-interval 10 --poll-max 300
```

### Options

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--video-id` | string | Yes | Video UUID from `studio-generate-video` |
| `--poll` | flag | No | Auto-poll until succeeded/failed |
| `--poll-interval` | number | No | Seconds between polls (default: 5) |
| `--poll-max` | number | No | Max seconds to poll (default: 120) |
| `--json` | flag | No | Output raw JSON data |

### Status Values

- `processing` - Still generating
- `succeeded` - Done. `output_url` available
- `failed` - Generation failed. Check `error` field

---

## Typical Workflow

### Image Generation
```bash
# 1. Check available models
genviral.sh studio-models --mode image

# 2. Generate image
genviral.sh studio-generate-image \
  --model-id "google/nano-banana" \
  --prompt "Your prompt" \
  --aspect-ratio "9:16"
# → instant output_url

# 3. Use in a slideshow or post
genviral.sh create-post \
  --caption "Check this out" \
  --media-type slideshow \
  --media-urls "OUTPUT_URL_HERE" \
  --accounts "ACCOUNT_ID"
```

### Video Generation
```bash
# 1. Check available models
genviral.sh studio-models --mode video

# 2. Start generation
genviral.sh studio-generate-video \
  --model-id "openai/sora-2" \
  --prompt "Your prompt" \
  --duration-seconds 8
# → video_id

# 3. Poll until ready
genviral.sh studio-video-status --video-id VIDEO_ID --poll
# → output_url when succeeded

# 4. Post the video
genviral.sh create-post \
  --caption "New video drop" \
  --media-type video \
  --media-url "OUTPUT_URL_HERE" \
  --accounts "ACCOUNT_ID"
```

## Input Contract

Studio uses normalized partner input (`snake_case`) through the `params` object, with optional `raw_params` for model-specific passthrough:

- **params** - stable normalized keys: `aspect_ratio`, `duration_seconds`, `resolution`, `fps`, `output_format`, `size`, `max_images`, `scale_factor`, `generate_audio`
- **raw_params** - optional advanced passthrough for model-specific controls

This keeps payloads consistent across models while allowing fine-grained control when needed.

## Error Codes

| Code | Meaning |
|------|---------|
| `401` | Auth failed (missing/invalid/revoked token) |
| `402 subscription_required` | Active Creator/Professional/Business plan required |
| `403 tier_not_allowed` | Scheduler tier cannot use Partner API |
| `403 insufficient_credits` | Not enough credits |
| `404 video_not_found` | Invalid video ID |
| `422 invalid_payload` | Bad request body or unsupported model_id |
| `422 model_requires_image` | Model needs an input image |
| `422 model_input_not_supported` | Input type not supported by model |
| `500 generation_failed` | Server-side generation error |
