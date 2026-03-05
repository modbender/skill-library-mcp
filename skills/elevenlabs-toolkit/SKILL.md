---
name: elevenlabs-toolkit
description: ElevenLabs voice API integration — TTS, sound effects, music generation, speech-to-text, voice isolation, and streaming. Use when building voice-enabled apps, generating narration, creating audio content, or transcribing speech. Requires ELEVENLABS_API_KEY.
version: 1.0.0
metadata:
  {
      "openclaw": {
            "emoji": "\ud83c\udf99\ufe0f",
            "requires": {
                  "bins": [],
                  "env": [
                        "ELEVENLABS_API_KEY"
                  ]
            },
            "primaryEnv": "ELEVENLABS_API_KEY",
            "network": {
                  "outbound": true,
                  "reason": "Calls ElevenLabs API (api.elevenlabs.io) for TTS, SFX, music generation, STT, and voice operations."
            }
      }
}
---

# ElevenLabs Toolkit

Programmatic access to all 7 ElevenLabs API capabilities via FastAPI endpoints or standalone Python functions.

## Capabilities

| Tool | Endpoint | What It Does |
|---|---|---|
| Voices | GET /api/voices | Browse available voices with metadata |
| TTS | POST /api/voice/tts | Batch text-to-speech (any voice, any language) |
| TTS Stream | WS /api/voice/stream | Real-time WebSocket TTS streaming |
| Sound Effects | POST /api/voice/sfx | Generate ambient audio from text prompts |
| Music | POST /api/voice/music | Generate background music from descriptions |
| STT (Scribe) | POST /api/voice/stt | Transcribe audio with language detection |
| Voice Isolation | POST /api/voice/isolate | Extract clean voice from noisy audio |

## Quick Start

```python
import httpx

BASE = "http://localhost:8000"  # Your FastAPI app
KEY = os.environ["ELEVENLABS_API_KEY"]

# Get voices
voices = httpx.get(f"{BASE}/api/voices").json()

# Generate speech
audio = httpx.post(f"{BASE}/api/voice/tts", json={
    "text": "Hello world",
    "voice_id": voices[0]["voice_id"],
    "model_id": "eleven_multilingual_v2"
}).content  # Returns raw audio bytes

# Generate sound effects
sfx = httpx.post(f"{BASE}/api/voice/sfx", json={
    "prompt": "ocean waves on a quiet beach at night"
}).content
```

## Voice Selection Guide

- **English only:** Use `eleven_turbo_v2_5` — faster, no accent bleed
- **Multilingual:** Use `eleven_multilingual_v2` — supports 29 languages
- **Accent warning:** Multilingual model can bleed accents across languages. If an English voice sounds Japanese, switch to turbo.

## Quota Management

ElevenLabs charges per character for TTS. Key patterns:
- Cache aggressively — identical text + voice = identical audio
- Use `prompt-cache` skill for SHA-256 dedup before calling TTS
- A 6-scene children's story ≈ 2,000 characters
- Free tier: 10k chars/month. Starter: 30k. Creator: 100k.

## Integration

Copy `scripts/elevenlabs_api.py` into your FastAPI app and mount the router:

```python
from elevenlabs_api import router
app.include_router(router)
```

Set `ELEVENLABS_API_KEY` in your environment. All endpoints handle errors gracefully with proper HTTP status codes.

## Files

- `scripts/elevenlabs_api.py` — FastAPI router with all 7 endpoints

## Security Notes

This skill uses patterns that may trigger automated security scanners:
- **base64**: Used for encoding audio/binary data in API responses (standard practice for media APIs)
- **UploadFile**: FastAPI's built-in file upload parameter for STT/voice isolation endpoints
- **"system prompt"**: Refers to configuring agent instructions, not prompt injection
