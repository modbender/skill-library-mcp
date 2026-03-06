---
name: pollinations
version: 1.0.2
description: "Pollinations.ai API for AI generation and analysis - text, images, videos, audio, vision, and transcription. Use when user requests AI-powered content (text completion, image generation/editing, video generation, audio/TTS, image/video analysis, audio transcription) or mentions Pollinations. Supports 25+ models with OpenAI-compatible endpoints."
metadata: {"openclaw":{"emoji":"🧬","homepage":"https://pollinations.ai","os":["darwin","linux","win32"],"requires":{"bins":["curl","jq","base64"],"env":["POLLINATIONS_API_KEY"]},"primaryEnv":"POLLINATIONS_API_KEY","install":[{"id":"jq-brew","kind":"brew","formula":"jq","bins":["jq"],"label":"Install jq via Homebrew","os":["darwin"]},{"id":"jq-apt","kind":"shell","command":"sudo apt-get install -y jq","bins":["jq"],"label":"Install jq via apt","os":["linux"]}]}}
---

# Pollinations v1.0.2

Unified AI platform for generating and analyzing text, images, videos, and audio with 25+ models.

## API Key

Get free or paid keys at https://enter.pollinations.ai
- Secret Keys (`sk_`): Server-side, no rate limits (recommended)
- Optional for many operations (free tier available)

### Runtime Requirements

| Type | Name | Required |
|------|------|----------|
| Env | `POLLINATIONS_API_KEY` | Optional (free tier works without) |
| Bin | `curl` | Yes |
| Bin | `jq` | Yes |
| Bin | `base64` | Yes |

## Operations & Scripts

### 1. Text/Chat Generation (`scripts/chat.sh`)

Generate text using 25+ LLM models with OpenAI-compatible API.

**Usage:**
```bash
scripts/chat.sh "your message"
scripts/chat.sh "your message" --model claude --temp 0.7
scripts/chat.sh "explain quantum physics" --model openai --max-tokens 500
scripts/chat.sh "list 3 colors" --json --model openai
scripts/chat.sh "solve this step by step" --model o3 --reasoning-effort high
scripts/chat.sh "translate to French" --system "You are a translator" --model gemini
```

**Options:**
- `--model MODEL` — Model name (default: openai)
- `--temp N` — Temperature 0-2 (default: 1)
- `--max-tokens N` — Max response length
- `--top-p N` — Nucleus sampling 0-1
- `--seed N` — Reproducibility (-1 = random)
- `--system "PROMPT"` — System prompt
- `--json` — Force structured JSON response
- `--reasoning-effort LVL` — For o1/o3/R1 models: high/medium/low/minimal/none
- `--thinking-budget N` — Token budget for reasoning models

**Models:** openai, claude, gemini, gemini-large, gemini-search, mistral, deepseek, grok, qwen, perplexity, o1, o3, gpt-4, and 15+ more. Use `scripts/models.sh text` to list all.

**Simple text (no script needed):**
```bash
curl "https://gen.pollinations.ai/text/Hello%20world"
```

### 2. Image Generation (`scripts/image.sh`)

Generate images from text prompts with multiple models and options.

**Usage:**
```bash
scripts/image.sh "a sunset over mountains"
scripts/image.sh "a portrait" --model flux --width 1024 --height 1024
scripts/image.sh "logo design" --model gptimage --quality hd --transparent
scripts/image.sh "photo" --enhance --nologo --private
scripts/image.sh "art" --negative "blurry, low quality" --seed 42
```

**Options:**
- `--model MODEL` — Model (default: flux)
- `--width N` — Width 16-2048px (default: 1024)
- `--height N` — Height 16-2048px (default: 1024)
- `--seed N` — Reproducibility
- `--output FILE` — Output filename
- `--enhance` — AI prompt improvement
- `--negative "TEXT"` — Negative prompt (what to avoid)
- `--nologo` — Remove watermark
- `--private` — Private generation
- `--safe` — Enable NSFW filter
- `--quality LEVEL` — low/medium/high/hd (gptimage only)
- `--transparent` — Transparent background PNG (gptimage only)
- `--image-url URL` — Source image for image-to-image

**Models:** flux (default), turbo, gptimage, kontext, seedream, nanobanana, nanobanana-pro. Use `scripts/models.sh image` to list all.

### 3. Image Editing / Image-to-Image (`scripts/image-edit.sh`)

Transform or edit existing images using AI.

**Usage:**
```bash
scripts/image-edit.sh "make it blue" --source "https://example.com/photo.jpg"
scripts/image-edit.sh "add sunglasses" --source photo.jpg --model kontext
scripts/image-edit.sh "convert to watercolor" --source input.png --output watercolor.jpg
```

**Options:**
- `--source URL/FILE` — Source image (URL or local file, required)
- `--model MODEL` — Model (default: kontext)
- `--seed N` — Reproducibility
- `--negative "TEXT"` — Negative prompt
- `--output FILE` — Output filename

### 4. Video Generation (`scripts/image.sh` with video models)

Generate videos from text prompts or images.

**Usage:**
```bash
scripts/image.sh "a cat playing piano" --model veo --duration 6
scripts/image.sh "ocean waves" --model seedance --duration 8 --aspect-ratio 16:9
scripts/image.sh "timelapse" --model veo --duration 4 --audio
scripts/image.sh "animate this" --model seedance --image-url "https://example.com/photo.jpg"
```

**Options (in addition to image options):**
- `--model veo|seedance` — Video model (required)
- `--duration N` — Length in seconds (veo: 4/6/8, seedance: 2-10)
- `--aspect-ratio RATIO` — 16:9 or 9:16
- `--audio` — Enable audio generation (veo only)
- `--image-url URL` — Source image for image-to-video

**Frame interpolation (veo):** Pass two images for first/last frame interpolation using the API directly:
```
https://gen.pollinations.ai/image/prompt?model=veo&image[0]=first_frame_url&image[1]=last_frame_url
```

**Models:** veo (4-8s, audio support, frame interpolation), seedance (2-10s, image-to-video)

### 5. Text-to-Speech / Audio (`scripts/tts.sh`)

Convert text to speech with multiple voices and formats.

**Usage:**
```bash
scripts/tts.sh "Hello world"
scripts/tts.sh "Bonjour le monde" --voice nova --format mp3
scripts/tts.sh "Welcome" --voice coral --format wav --output welcome.wav
```

**Options:**
- `--voice VOICE` — Voice selection (default: nova)
- `--format FORMAT` — Output format (default: mp3)
- `--model MODEL` — Model (default: openai-audio)
- `--output FILE` — Output filename

**Voices (13):** alloy, amuch, ash, ballad, coral, dan, echo, fable, nova, onyx, sage, shimmer, verse

**Formats (5):** mp3, wav, flac, opus, pcm16

### 6. Image Analysis / Vision (`scripts/analyze-image.sh`)

Analyze and describe images using vision-capable AI models.

**Usage:**
```bash
scripts/analyze-image.sh "https://example.com/photo.jpg"
scripts/analyze-image.sh photo.jpg --prompt "What objects are in this image?"
scripts/analyze-image.sh image.png --model claude --prompt "Extract all text from this image"
```

**Options:**
- `--prompt "TEXT"` — Analysis question (default: "Describe this image in detail")
- `--model MODEL` — Vision model (default: gemini)

**Input:** URL or local file (jpg, png, gif, webp)

**Models:** gemini, gemini-large, claude, openai, and other vision-capable models. Use `scripts/models.sh vision` to list all.

### 7. Video Analysis (`scripts/analyze-video.sh`)

Analyze video content using AI vision models.

**Usage:**
```bash
scripts/analyze-video.sh "https://example.com/video.mp4"
scripts/analyze-video.sh recording.mp4 --prompt "Summarize the key moments"
scripts/analyze-video.sh clip.mov --model gemini-large --prompt "Count the people"
```

**Options:**
- `--prompt "TEXT"` — Analysis question (default: "Describe this video in detail")
- `--model MODEL` — Video-capable model (default: gemini)

**Input:** URL or local file (mp4, mov, avi)

**Models:** gemini, gemini-large, claude, openai (video-capable models)

### 8. Audio Transcription (`scripts/transcribe.sh`)

Transcribe audio files to text.

**Usage:**
```bash
scripts/transcribe.sh recording.mp3
scripts/transcribe.sh podcast.wav --model gemini-large
scripts/transcribe.sh "https://example.com/audio.mp3" --prompt "Transcribe in French"
```

**Options:**
- `--prompt "TEXT"` — Transcription instructions (default: accurate transcription)
- `--model MODEL` — Audio-capable model (default: gemini)

**Input:** Local file or URL (mp3, wav, flac, ogg, m4a)

**Models:** gemini, gemini-large, gemini-legacy, openai-audio

### 9. List Available Models (`scripts/models.sh`)

Dynamically list all available models from the API.

**Usage:**
```bash
scripts/models.sh              # List all models
scripts/models.sh text         # Text/chat models only
scripts/models.sh image        # Image generation models
scripts/models.sh video        # Video generation models
scripts/models.sh vision       # Vision/analysis models
scripts/models.sh audio        # Audio/TTS models
```

## API Endpoints Reference

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Simple Text | `/text/{prompt}` | GET |
| Chat Completion | `/v1/chat/completions` | POST |
| Image Generation | `/image/{prompt}?{params}` | GET |
| Image-to-Image | `/image/{prompt}?image={url}&{params}` | GET |
| Video Generation | `/image/{prompt}?model=veo&{params}` | GET |
| Image Analysis | `/v1/chat/completions` (with image_url) | POST |
| Video Analysis | `/v1/chat/completions` (with video_url) | POST |
| Audio/TTS | `/v1/chat/completions` (openai-audio) | POST |
| Audio Transcription | `/v1/chat/completions` (with input_audio) | POST |
| List Text Models | `/v1/models` | GET |
| List Image Models | `/image/models` | GET |
| List Vision Models | `/text/models` | GET |

## Tips

1. **Free tier available**: Many operations work without an API key (rate limited)
2. **OpenAI-compatible**: Chat endpoint works with existing OpenAI integrations
3. **Reproducibility**: Use `seed` parameter for consistent outputs across all operations
4. **Image enhancement**: Use `--enhance` for AI-improved prompts on image generation
5. **JSON mode**: Use `--json` flag on chat for structured data extraction
6. **Reasoning models**: Use `--reasoning-effort` with o1/o3/R1 for controlled thinking depth
7. **Video from images**: Use `--image-url` with seedance for image-to-video, or veo frame interpolation
8. **Audio on video**: Use `--audio` with veo model for videos with sound
9. **Local files**: Analysis scripts (image, video, transcription) accept both URLs and local files
10. **Private mode**: Use `--private` to keep generations off public feed

## API Documentation

Full docs: https://enter.pollinations.ai/api/docs
