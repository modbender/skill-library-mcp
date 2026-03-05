---
name: venice-api-kit
description: Complete Venice AI API toolkit - image generation, video, audio, embeddings, transcription, characters, models, and admin functions. Privacy-focused inference with zero data retention.
homepage: https://venice.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "🏛️",
        "requires": { "bins": ["uv", "python3"], "env": ["VENICE_API_KEY"] },
        "primaryEnv": "VENICE_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
            {
              "id": "python-brew",
              "kind": "brew",
              "formula": "python@3.12",
              "bins": ["python3"],
              "label": "Install Python 3.12 (brew)",
            },
            {
              "id": "httpx-pip",
              "kind": "pip",
              "package": "httpx",
              "label": "Install httpx (pip)",
            },
          ],
      },
  }
---

# Venice API Kit

Complete toolkit for the entire Venice AI API. Includes all inference endpoints (image, video, audio, embeddings), discovery tools (models, characters), and admin functions (billing, usage, API keys).

**API Base URL:** `https://api.venice.ai/api/v1`
**Documentation:** [docs.venice.ai](https://docs.venice.ai)

## Setup

1. Get your API key from [venice.ai](https://venice.ai) → Settings → API Keys
2. Set the environment variable:

```bash
export VENICE_API_KEY="your_api_key_here"
```

Or configure in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "venice-api-kit": {
        apiKey: "your_api_key_here"
      }
    }
  }
}
```

---

## Image Generation

Generate images using Venice's image models. Returns base64 image data.

```bash
uv run {baseDir}/scripts/image_generate.py --prompt "a serene mountain landscape at sunset"
```

**Options:**

- `--prompt` (required): Description of the image (max 7500 chars, model-dependent)
- `--output`: Output filename (default: auto-generated timestamp)
- `--model`: Model ID (default: `flux-2-max`)
- `--size`: Image size: `1024x1024`, `1536x1024`, `1024x1536`, `1792x1024`, `1024x1792` (default: `1024x1024`)
- `--style-id`: Style preset ID (use `--list-styles` to see available)
- `--negative-prompt`: What to avoid in the image
- `--seed`: Seed for reproducible generation

**List available styles:**

```bash
uv run {baseDir}/scripts/image_generate.py --list-styles
```

---

## Image Upscaling

Upscale images 1-4x with optional AI enhancement. Returns binary PNG.

```bash
uv run {baseDir}/scripts/image_upscale.py --image input.png --scale 2
```

**Options:**

- `--image` (required): Input image path or URL
- `--output`: Output filename (default: `upscaled-{timestamp}.png`)
- `--scale`: Scale factor 1-4 (default: `2`). Scale of 1 requires `--enhance`
- `--enhance`: Enable AI enhancement during upscaling
- `--enhance-creativity`: How much AI can change (0-1, higher = more creative)
- `--enhance-prompt`: Style to apply (e.g., "gold", "marble", "cinematic")
- `--replication`: Preserve original lines/noise (0-1, higher = less hallucination)

**Example with enhancement:**

```bash
uv run {baseDir}/scripts/image_upscale.py --image photo.png --scale 2 --enhance --enhance-prompt "cinematic lighting"
```

---

## Image Editing

Edit images with AI using text prompts. Returns binary PNG.

```bash
uv run {baseDir}/scripts/image_edit.py --image photo.png --prompt "add sunglasses"
```

**Options:**

- `--image` (required): Input image path or URL
- `--prompt` (required): Edit instructions (e.g., "remove the tree", "change sky to sunset")
- `--output`: Output filename (default: `edited-{timestamp}.png`)
- `--model`: Edit model (default: `qwen-edit`). Available: `qwen-edit`, `flux-2-max-edit`, `gpt-image-1-5-edit`, `nano-banana-pro-edit`, `seedream-v4-edit`
- `--aspect-ratio`: Output aspect ratio: `auto`, `1:1`, `3:2`, `16:9`, `21:9`, `9:16`, `2:3`, `3:4`

---

## Background Removal

Remove backgrounds from images. Returns binary PNG with transparency.

```bash
uv run {baseDir}/scripts/image_background_remove.py --image photo.png
```

**Options:**

- `--image` (required): Input image path or URL
- `--output`: Output filename (default: `no-background-{timestamp}.png`)

---

## Text-to-Speech

Convert text to speech with multiple voices and formats. Returns binary audio.

```bash
uv run {baseDir}/scripts/audio_speech.py --text "Hello, welcome to Venice AI"
```

**Options:**

- `--text` (required): Text to convert (max 4096 characters)
- `--output`: Output filename (default: `speech-{timestamp}.{format}`)
- `--voice`: Voice ID (default: `af_nicole`)
- `--model`: TTS model (default: `tts-kokoro`)
- `--speed`: Speed multiplier 0.25-4.0 (default: `1.0`)
- `--format`: Audio format: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (default: `mp3`)
- `--streaming`: Stream audio sentence by sentence

**Available voices:**

- American Female: `af_alloy`, `af_aoede`, `af_bella`, `af_heart`, `af_jadzia`, `af_jessica`, `af_kore`, `af_nicole`, `af_nova`, `af_river`, `af_sarah`, `af_sky`
- American Male: `am_adam`, `am_echo`, `am_eric`
- British Female: `bf_emma`, `bf_isabella`, `bf_alice`
- British Male: `bm_george`, `bm_lewis`, `bm_daniel`

---

## Audio Transcription

Transcribe audio files to text using Whisper-based speech recognition.

```bash
uv run {baseDir}/scripts/transcribe.py --file audio.mp3
```

**Options:**

- `--file` (required): Audio file to transcribe (WAV, MP3, FLAC, M4A, AAC)
- `--output`: Save transcription to file
- `--model`: ASR model (default: `openai/whisper-large-v3`)
- `--format`: Output format: `json` or `text` (default: `json`)
- `--timestamps`: Include word/segment timestamps
- `--language`: Language hint (ISO 639-1: en, es, fr, etc.)

---

## Embeddings

Generate vector embeddings for RAG applications.

```bash
uv run {baseDir}/scripts/embeddings.py --text "Your text to embed"
```

**Options:**

- `--text`: Text to embed (use this OR `--file`)
- `--file`: Read text from file
- `--output`: Save embeddings to JSON file
- `--model`: Embedding model (default: `text-embedding-3-small`)

---

## Video Generation

Generate videos from text prompts. Some models require a reference image. Async with polling.

**Text-to-video:**

```bash
uv run {baseDir}/scripts/video_generate.py --prompt "a cat playing piano"
```

**Image-to-video (requires reference image):**

```bash
uv run {baseDir}/scripts/video_generate.py --prompt "a cat playing piano" --image reference.png
```

**Options:**

- `--prompt` (required): Video description (max 2500 characters)
- `--image`: Reference image (path or URL) - required for image-to-video models
- `--output`: Output filename (default: `venice-video-{timestamp}.mp4`)
- `--model`: Video model (default: `wan-2.6-image-to-video`). Also: `wan-2.6-text-to-video`, `wan-2.6-flash-image-to-video`
- `--duration`: Video duration: `5s` or `10s` (default: `5s`)
- `--resolution`: Resolution: `480p`, `720p`, `1080p` (default: `720p`)
- `--aspect-ratio`: Aspect ratio (e.g., `16:9`, `9:16`, `1:1`)
- `--negative-prompt`: What to avoid in the video
- `--max-wait`: Max seconds to wait for completion (default: `600`)

---

## Models Explorer

List and explore all available Venice AI models. No API key required.

```bash
uv run {baseDir}/scripts/models.py
```

**Options:**

- `--type`: Filter by type: `all`, `text`, `image`, `video`, `tts`, `asr`, `embedding`, `code`, `upscale`, `inpaint` (default: `all`)
- `--format`: Output format: `table`, `json`, `names` (default: `table`)
- `--output`: Save to file

**Examples:**

```bash
uv run {baseDir}/scripts/models.py --type image
uv run {baseDir}/scripts/models.py --format json --output models.json
```

---

## Characters Browser

Browse and discover Venice AI character personas.

```bash
uv run {baseDir}/scripts/characters.py
```

**Options:**

- `--search`: Search by name or description
- `--tag`: Filter by tag
- `--limit`: Max results (default: 20)
- `--format`: Output format: `table`, `json`, `list` (default: `table`)
- `--output`: Save to file

**Examples:**

```bash
uv run {baseDir}/scripts/characters.py --search "coding"
uv run {baseDir}/scripts/characters.py --tag "assistant" --format json
```

---

## Admin: Check Balance

Check your DIEM and USD balances. **Requires Admin API key.**

```bash
uv run {baseDir}/scripts/balance.py
```

Shows current balance, consumption currency, and DIEM epoch allocation.

---

## Admin: Usage History

View detailed usage history with filtering. **Requires Admin API key.**

```bash
uv run {baseDir}/scripts/usage.py
```

**Options:**

- `--currency`: Filter by currency: `DIEM`, `USD`, `VCU` (default: `DIEM`)
- `--start-date`: Start date (ISO format: 2024-01-01)
- `--end-date`: End date (ISO format: 2024-12-31)
- `--limit`: Results per page, max 200 (default: 50)
- `--page`: Page number (default: 1)
- `--sort`: Sort order: `asc`, `desc` (default: `desc`)
- `--format`: Output format: `json`, `csv` (default: `json`)
- `--output`: Save to file

**Examples:**

```bash
uv run {baseDir}/scripts/usage.py --currency USD --limit 100
uv run {baseDir}/scripts/usage.py --start-date 2024-01-01 --format csv --output usage.csv
```

---

## Admin: List API Keys

List all your API keys with metadata. **Requires Admin API key.**

```bash
uv run {baseDir}/scripts/api_keys_list.py
```

Shows key ID, name, type, creation date, last used date, and rate limits.

---

## Admin: Get API Key Details

Get detailed information for a specific API key. **Requires Admin API key.**

```bash
uv run {baseDir}/scripts/api_key_get.py --id "key_abc123"
```

**Options:**

- `--id` (required): API key ID to get details for

---

## Admin: Create API Key

Create a new API key. **Requires Admin API key.**

```bash
uv run {baseDir}/scripts/api_key_create.py --name "My New Key"
```

**Options:**

- `--name` (required): Name for the new API key
- `--type`: Key type: `INFERENCE` (default) or `ADMIN`

**Important:** The full key is only shown once on creation. Save it immediately.

---

## Admin: Update API Key

Update an existing API key's settings. **Requires Admin API key.**

```bash
uv run {baseDir}/scripts/api_key_update.py --id "key_abc123" --name "New Name"
```

**Options:**

- `--id` (required): API key ID to update
- `--name`: New name for the key

---

## Admin: Delete API Key

Delete an API key. This action is **irreversible**. **Requires Admin API key.**

```bash
uv run {baseDir}/scripts/api_key_delete.py --id "key_abc123" --force
```

**Options:**

- `--id` (required): API key ID to delete
- `--force` (required): Confirm deletion

---

## Rate Limits

Get current rate limits and balance information.

```bash
uv run {baseDir}/scripts/rate_limits.py
```

Shows requests/minute, tokens/minute, tokens/day limits and current usage.

---

## Runtime Note

This skill uses `uv run` which automatically installs Python dependencies (httpx) via [PEP 723](https://peps.python.org/pep-0723/) inline script metadata. No manual Python package installation required - `uv` handles everything.

---

## Security Notes

- **Privacy:** All inference is private—no logging, no training on your data
- **API Key:** Store securely, never commit to version control
- **Admin vs Inference Keys:** Admin keys can access billing/usage—use inference keys for everyday work
- **Data:** Venice does not retain request/response data
- **Trust:** Verify you trust Venice.ai before sending sensitive data

## API Reference

| Endpoint | Description | Response |
|----------|-------------|----------|
| `/image/generate` | Full image generation | JSON with base64 images |
| `/images/generations` | OpenAI-compatible generation | JSON with base64 |
| `/image/upscale` | Image upscaling with enhancement | Binary PNG |
| `/image/edit` | AI image editing | Binary PNG |
| `/image/background-remove` | Background removal | Binary PNG (transparent) |
| `/audio/speech` | Text-to-speech | Binary audio |
| `/audio/transcriptions` | Speech-to-text | JSON with text |
| `/embeddings` | Vector embeddings | JSON |
| `/video/queue` | Queue video generation | JSON with queue_id |
| `/video/retrieve` | Retrieve completed video | Binary MP4 or JSON status |
| `/models` | List available models | JSON |
| `/characters` | List character personas | JSON |
| `/billing/balance` | Check account balance | JSON (Admin key) |
| `/billing/usage` | View usage history | JSON (Admin key) |
| `/api_keys` | List API keys | JSON (Admin key) |
| `/api_keys/{id}` | Get/Update/Delete API key | JSON (Admin key) |
| `/api_keys/rate_limits` | Get rate limits & balances | JSON |

Full API docs: [docs.venice.ai](https://docs.venice.ai)
