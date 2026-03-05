---
name: deAPI AI Media Suite
description: The cheapest AI media API on the market. Transcribe YouTube videos, generate images with Flux and Z-Image models, convert text to speech in 54+ voices across 8 languages, extract text with OCR, create videos, remove backgrounds, upscale images, apply style transfer - all through one unified API. Free $5 credit on signup - enough for hundreds of hours of transcription or thousands of generated images. Fraction of the cost of any alternative.
homepage: https://deapi.ai
source: https://github.com/zrewolwerowanykaloryfer/deapi-clawdbot-skill
author: zrewolwerowanykaloryfer
license: MIT
requiredEnv:
  - DEAPI_API_KEY
metadata: {"clawdbot":{"requires":{"env":["DEAPI_API_KEY"]}}}
tags:
  - media
  - transcription
  - image-generation
  - tts
  - ocr
  - video
  - audio
  - embeddings
---

# deAPI Media Generation

AI-powered media tools via decentralized GPU network. Get your API key at [deapi.ai](https://deapi.ai) (free $5 credit on signup).

## Setup

```bash
export DEAPI_API_KEY=your_api_key_here
```

## Available Functions

| Function | Use when user wants to... |
|----------|---------------------------|
| Transcribe | Transcribe YouTube, Twitch, Kick, X videos, or audio files |
| Generate Image | Generate images from text descriptions (Flux models) |
| Generate Audio | Convert text to speech (TTS, 54+ voices, 8 languages) |
| Generate Video | Create video from text or animate images |
| OCR | Extract text from images |
| Remove Background | Remove background from images |
| Upscale | Upscale image resolution (2x/4x) |
| Transform Image | Apply style transfer to images (multi-image support) |
| Embeddings | Generate text embeddings for semantic search |
| Check Balance | Check account balance |

---

## Async Pattern (Important!)

**All deAPI requests are asynchronous.** Follow this pattern for every operation:

### 1. Submit Request
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/{endpoint}" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

Response contains `request_id`.

### 2. Poll Status (loop every 10 seconds)
```bash
curl -s "https://api.deapi.ai/api/v1/client/request-status/{request_id}" \
  -H "Authorization: Bearer $DEAPI_API_KEY"
```

### 3. Handle Status
- `processing` → wait 10s, poll again
- `done` → fetch result from `result_url`
- `failed` → report error to user

### Common Error Handling
| Error | Action |
|-------|--------|
| 401 Unauthorized | Check DEAPI_API_KEY |
| 429 Rate Limited | Wait 60s and retry |
| 500 Server Error | Wait 30s and retry once |

---

## Transcription (YouTube, Audio, Video)

**Use when:** user wants to transcribe video from YouTube, X, Twitch, Kick or audio files.

**Endpoints:**
- Video (YouTube, mp4, webm): `vid2txt`
- Audio (mp3, wav, m4a, flac, ogg): `aud2txt`

**Request (video):**
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/vid2txt" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "{VIDEO_URL}", "include_ts": true, "model": "WhisperLargeV3"}'
```

**Request (audio):**
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/aud2txt" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"audio_url": "{AUDIO_URL}", "include_ts": true, "model": "WhisperLargeV3"}'
```

**After polling:** Present transcription with timestamps in readable format.

---

## Image Generation (Flux)

**Use when:** user wants to generate images from text descriptions.

**Endpoint:** `txt2img`

**Models:**
| Model | API Name | Steps | Max Size | Notes |
|-------|----------|-------|----------|-------|
| Klein (default) | `Flux_2_Klein_4B_BF16` | 4 (fixed) | 1536px | Fastest, recommended |
| Flux | `Flux1schnell` | 4-10 | 2048px | Higher resolution |
| Turbo | `ZImageTurbo_INT8` | 4-10 | 1024px | Fastest inference |

**Request:**
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2img" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "{PROMPT}",
    "model": "Flux_2_Klein_4B_BF16",
    "width": 1024,
    "height": 1024,
    "steps": 4,
    "seed": {RANDOM_0_TO_999999}
  }'
```

**Note:** Klein model does NOT support `guidance` parameter - omit it.

---

## Text-to-Speech (54+ Voices)

**Use when:** user wants to convert text to speech.

**Endpoint:** `txt2audio`

**Popular Voices:**
| Voice ID | Language | Description |
|----------|----------|-------------|
| `af_bella` | American EN | Warm, friendly (best quality) |
| `af_heart` | American EN | Expressive, emotional |
| `am_adam` | American EN | Deep, authoritative |
| `bf_emma` | British EN | Elegant (best British) |
| `jf_alpha` | Japanese | Natural Japanese female |
| `zf_xiaobei` | Chinese | Mandarin female |
| `ef_dora` | Spanish | Spanish female |
| `ff_siwis` | French | French female (best quality) |

Voice format: `{lang}{gender}_{name}` (e.g., `af_bella` = American Female Bella)

**Request:**
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2audio" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "{TEXT}",
    "voice": "af_bella",
    "model": "Kokoro",
    "lang": "en-us",
    "speed": 1.0,
    "format": "mp3",
    "sample_rate": 24000
  }'
```

**Parameters:** 
- `lang`: `en-us`, `en-gb`, `ja`, `zh`, `es`, `fr`, `hi`, `it`, `pt-br`
- `speed`: 0.5-2.0
- `format`: mp3/wav/flac/ogg
- `sample_rate`: 22050/24000/44100/48000

---

## Video Generation

**Use when:** user wants to generate video from text or animate an image.

**Endpoints:**
- Text-to-Video: `txt2video` (multipart/form-data)
- Image-to-Video: `img2video` (multipart/form-data)

**⚠️ IMPORTANT: Model-specific constraints for `Ltxv_13B_0_9_8_Distilled_FP8`:**
- `guidance`: MUST be 0 (max value!)
- `steps`: MUST be 1 (max value!)
- `fps`: minimum 30

**Request (text-to-video):**
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2video" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "prompt={PROMPT}" \
  -F "model=Ltxv_13B_0_9_8_Distilled_FP8" \
  -F "width=512" \
  -F "height=512" \
  -F "guidance=0" \
  -F "steps=1" \
  -F "frames=120" \
  -F "fps=30" \
  -F "seed={RANDOM_0_TO_999999}"
```

**Parameters:**
| Parameter | Required | Constraints | Description |
|-----------|----------|-------------|-------------|
| `prompt` | Yes | - | Video description |
| `model` | Yes | - | `Ltxv_13B_0_9_8_Distilled_FP8` |
| `width` | Yes | 256-768 | Video width (e.g., 512) |
| `height` | Yes | 256-768 | Video height (e.g., 512) |
| `guidance` | Yes | **max 0** | Must be 0 for this model |
| `steps` | Yes | **max 1** | Must be 1 for this model |
| `frames` | Yes | 30-300 | Number of frames |
| `fps` | Yes | **min 30** | Frames per second |
| `seed` | Yes | 0-999999 | Random seed |

**Request (image-to-video):**
```bash
# Download image first if URL provided
curl -s -o {LOCAL_IMAGE_PATH} "{IMAGE_URL}"

curl -s -X POST "https://api.deapi.ai/api/v1/client/img2video" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "first_frame_image=@{LOCAL_IMAGE_PATH}" \
  -F "prompt=gentle movement, cinematic" \
  -F "model=Ltxv_13B_0_9_8_Distilled_FP8" \
  -F "width=512" \
  -F "height=512" \
  -F "guidance=0" \
  -F "steps=1" \
  -F "frames=120" \
  -F "fps=30" \
  -F "seed={RANDOM_0_TO_999999}"
```

**Note:** Video generation can take 1-3 minutes.

---

## OCR (Image to Text)

**Use when:** user wants to extract text from an image.

**Endpoint:** `img2txt` (multipart/form-data)

**Request:**
```bash
# Download image first if URL provided
curl -s -o {LOCAL_IMAGE_PATH} "{IMAGE_URL}"

# Send OCR request
curl -s -X POST "https://api.deapi.ai/api/v1/client/img2txt" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@{LOCAL_IMAGE_PATH}" \
  -F "model=Nanonets_Ocr_S_F16"
```

---

## Background Removal

**Use when:** user wants to remove background from an image.

**Endpoint:** `img-rmbg` (multipart/form-data)

**Request:**
```bash
# Download image first if URL provided
curl -s -o {LOCAL_IMAGE_PATH} "{IMAGE_URL}"

# Send remove-bg request
curl -s -X POST "https://api.deapi.ai/api/v1/client/img-rmbg" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@{LOCAL_IMAGE_PATH}" \
  -F "model=Ben2"
```

**Result:** PNG with transparent background.

---

## Image Upscale (2x/4x)

**Use when:** user wants to upscale/enhance image resolution.

**Endpoint:** `img-upscale` (multipart/form-data)

**Models:**
| Scale | Model |
|-------|-------|
| 2x | `RealESRGAN_x2` |
| 4x | `RealESRGAN_x4` |

**Request:**
```bash
# Download image first if URL provided
curl -s -o {LOCAL_IMAGE_PATH} "{IMAGE_URL}"

# Send upscale request
curl -s -X POST "https://api.deapi.ai/api/v1/client/img-upscale" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@{LOCAL_IMAGE_PATH}" \
  -F "model=RealESRGAN_x4"
```

---

## Image Transformation (Style Transfer)

**Use when:** user wants to transform image style, combine images, or apply AI modifications.

**Endpoint:** `img2img` (multipart/form-data)

**Models:**
| Model | API Name | Max Images | Guidance | Steps | Notes |
|-------|----------|------------|----------|-------|-------|
| Klein (default) | `Flux_2_Klein_4B_BF16` | 3 | N/A (ignore) | 4 (fixed) | Faster, multi-image |
| Qwen | `QwenImageEdit_Plus_NF4` | 1 | 7.5 | 10-50 (default 20) | More control |

**Request (Klein, supports up to 3 images):**
```bash
# Download images first
curl -s -o {LOCAL_IMAGE_1} "{IMAGE_URL_1}"
curl -s -o {LOCAL_IMAGE_2} "{IMAGE_URL_2}"  # optional

# Send transform request (Klein - no guidance)
curl -s -X POST "https://api.deapi.ai/api/v1/client/img2img" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@{LOCAL_IMAGE_1}" \
  -F "image=@{LOCAL_IMAGE_2}" \
  -F "prompt={STYLE_PROMPT}" \
  -F "model=Flux_2_Klein_4B_BF16" \
  -F "steps=4" \
  -F "seed={RANDOM_0_TO_999999}"
```

**Request (Qwen, higher quality single image):**
```bash
# Download image first
curl -s -o {LOCAL_IMAGE_1} "{IMAGE_URL}"

# Send transform request (Qwen - with guidance)
curl -s -X POST "https://api.deapi.ai/api/v1/client/img2img" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -F "image=@{LOCAL_IMAGE_1}" \
  -F "prompt={STYLE_PROMPT}" \
  -F "model=QwenImageEdit_Plus_NF4" \
  -F "guidance=7.5" \
  -F "steps=20" \
  -F "seed={RANDOM_0_TO_999999}"
```

**Example prompts:** "convert to watercolor painting", "anime style", "cyberpunk neon aesthetic"

---

## Text Embeddings

**Use when:** user needs embeddings for semantic search, clustering, or RAG.

**Endpoint:** `txt2embedding`

**Request:**
```bash
curl -s -X POST "https://api.deapi.ai/api/v1/client/txt2embedding" \
  -H "Authorization: Bearer $DEAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "{TEXT}", "model": "Bge_M3_FP16"}'
```

**Result:** 1024-dimensional vector (BGE-M3, multilingual)

---

## Check Balance

**Use when:** user wants to check remaining credits.

**Request:**
```bash
curl -s "https://api.deapi.ai/api/v1/client/balance" \
  -H "Authorization: Bearer $DEAPI_API_KEY"
```

**Response:** `{ "data": { "balance": 4.25 } }`

---

## Pricing (Approximate)

| Operation | Cost |
|-----------|------|
| Transcription | ~$0.02/hour |
| Image Generation | ~$0.002/image |
| TTS | ~$0.001/1000 chars |
| Video Generation | ~$0.05/video |
| OCR | ~$0.001/image |
| Remove BG | ~$0.001/image |
| Upscale | ~$0.002/image |
| Embeddings | ~$0.0001/1000 tokens |

Free $5 credit on signup at [deapi.ai](https://deapi.ai).

---

*Converted from [deapi-ai/claude-code-skills](https://github.com/deapi-ai/claude-code-skills) for Clawdbot/OpenClaw.*

---

## Security & Privacy Note

This skill provides documentation for the **deAPI.ai** REST API, a legitimate decentralized AI media service. 

**Security:**
- All `curl` commands are **examples** showing how to call the API
- Requests go to `api.deapi.ai` (official deAPI endpoint)
- Local file paths (e.g., `{LOCAL_IMAGE_PATH}`) are placeholders - use any suitable temporary location
- The skill itself does not execute code or download binaries
- API key is required and must be set by user via `DEAPI_API_KEY` environment variable

**Privacy considerations:**
- Media URLs you submit (YouTube links, images) are sent to deapi.ai for processing
- Generated results are returned via `result_url` which may be temporarily accessible via direct link
- Results are stored on deAPI's infrastructure - review their privacy policy for retention details
- Do not process sensitive/confidential media without understanding data handling

**Provenance:**
- Service provider: [deapi.ai](https://deapi.ai)
- Original skill source: [github.com/deapi-ai/claude-code-skills](https://github.com/deapi-ai/claude-code-skills)
- API documentation: [docs.deapi.ai](https://docs.deapi.ai)
