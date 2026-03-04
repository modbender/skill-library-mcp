# Voice.ai API Reference

Production API endpoints used by this pipeline.
Based on the [Voice.ai TTS SDK](https://github.com/gizmoGremlin/openclaw-skill-voice-ai-voices).

## Authentication

Bearer token in the `Authorization` header:

```
Authorization: Bearer <VOICE_AI_API_KEY>
```

Get your key at [voice.ai/dashboard](https://voice.ai/dashboard).

## Base URL

```
https://dev.voice.ai
```

Override via `VOICEAI_API_BASE` environment variable.

API path prefix: `/api/v1`

---

## Endpoints

### `GET /api/v1/tts/voices` — List available voices

**Query Parameters:**

| Param        | Type    | Default | Description                |
|--------------|---------|---------|----------------------------|
| `limit`      | integer | 10      | Max voices to return       |
| `offset`     | integer | 0       | Pagination offset          |
| `visibility` | string  | —       | `PUBLIC` or `PRIVATE`      |

**Response:**

```json
{
  "voices": [
    {
      "voice_id": "d1bf0f33-8e0e-4fbf-acf8-45c3c6262513",
      "name": "Ellie",
      "language": "en",
      "visibility": "PUBLIC",
      "status": "AVAILABLE"
    }
  ]
}
```

### `POST /api/v1/tts/speech` — Generate speech

**Request Body:**

```json
{
  "text": "Hello, world!",
  "voice_id": "d1bf0f33-8e0e-4fbf-acf8-45c3c6262513",
  "audio_format": "wav",
  "temperature": 1.0,
  "top_p": 0.8,
  "model": "voiceai-tts-v1-latest",
  "language": "en"
}
```

| Field          | Type   | Required | Default                     | Description                         |
|----------------|--------|----------|-----------------------------|-------------------------------------|
| `text`         | string | ✅       | —                           | Text to synthesize (max 5000 chars) |
| `voice_id`     | string | No       | built-in default            | Voice UUID or omit for default      |
| `audio_format` | string | No       | `mp3`                       | `mp3`, `wav`, `pcm`, etc.           |
| `temperature`  | number | No       | 1.0                         | Variation (0.0–2.0)                 |
| `top_p`        | number | No       | 0.8                         | Nucleus sampling (0.0–1.0)          |
| `model`        | string | No       | auto-selected by language   | `voiceai-tts-v1-latest` or `voiceai-tts-multilingual-v1-latest` |
| `language`     | string | No       | `en`                        | ISO 639-1 code                      |

**Response:** Binary audio data in the requested format.

### `POST /api/v1/tts/speech/stream` — Streaming speech

Same body as `/tts/speech`. Returns chunked transfer-encoded audio for low-latency playback.

---

## Audio Formats

| Format            | Description                |
|-------------------|----------------------------|
| `mp3`             | MP3 at 32kHz (default)     |
| `wav`             | WAV at 32kHz               |
| `pcm`             | Raw PCM 16-bit             |
| `mp3_44100_128`   | MP3 44.1kHz 128kbps        |
| `mp3_44100_192`   | MP3 44.1kHz 192kbps        |
| `wav_22050`       | WAV 22.05kHz               |
| `wav_24000`       | WAV 24kHz                  |
| `opus_48000_128`  | Opus 48kHz 128kbps         |

## Models

| Model ID                                    | Languages |
|---------------------------------------------|-----------|
| `voiceai-tts-v1-latest`                     | English   |
| `voiceai-tts-multilingual-v1-latest`        | 11 langs  |

Multilingual model supports: en, es, fr, de, it, pt, pl, ru, nl, sv, ca.

## Popular Voices

| Alias    | Voice ID (UUID)                              | Gender | Style                    |
|----------|----------------------------------------------|--------|--------------------------|
| `ellie`  | `d1bf0f33-8e0e-4fbf-acf8-45c3c6262513`      | F      | Youthful, vibrant vlogger|
| `oliver` | `f9e6a5eb-a7fd-4525-9e92-75125249c933`      | M      | Friendly British         |
| `lilith` | `4388040c-8812-42f4-a264-f457a6b2b5b9`      | F      | Soft, feminine           |
| `smooth` | `dbb271df-db25-4225-abb0-5200ba1426bc`      | M      | Deep, smooth narrator    |
| `corpse` | `72d2a864-b236-402e-a166-a838ccc2c273`      | M      | Deep, distinctive        |
| `skadi`  | `559d3b72-3e79-4f11-9b62-9ec702a6c057`      | F      | Anime character          |
| `zhongli`| `ed751d4d-e633-4bb0-8f5e-b5c8ddb04402`      | M      | Deep, authoritative      |
| `flora`  | `a931a6af-fb01-42f0-a8c0-bd14bc302bb1`      | F      | Cheerful, high pitch     |
| `chief`  | `bd35e4e6-6283-46b9-86b6-7cfa3dd409b9`      | M      | Heroic, commanding       |

The CLI accepts both aliases (`--voice ellie`) and full UUIDs (`--voice d1bf0f33-...`).

---

## Error Codes

| Code | Meaning            | Action                           |
|------|--------------------|----------------------------------|
| 401  | Invalid API key    | Check `VOICE_AI_API_KEY`         |
| 402  | Out of credits     | Top up at voice.ai/dashboard     |
| 422  | Validation error   | Check text length, voice_id      |
| 429  | Rate limited       | Wait and retry                   |

---

## Mock Mode

When `--mock` is passed, the pipeline runs end-to-end without any network calls:

- Voice listing returns the 9 popular voices above
- TTS returns generated WAV files with an audible test tone
- No API key required
- All output files (review.html, chapters, captions, etc.) are produced identically
