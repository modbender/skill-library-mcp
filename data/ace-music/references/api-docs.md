# ACE-Step OpenRouter API Reference

**Base URL:** `https://api.acemusic.ai`
**Auth:** `Authorization: Bearer <api-key>`
**Get API Key:** https://acemusic.ai/playground/api-key

## Generate Music

**POST** `/v1/chat/completions`

### Request Parameters

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | string | No | auto | Model ID |
| `messages` | array | **Yes** | - | Chat message list |
| `stream` | boolean | No | false | Enable streaming |
| `audio_config` | object | No | null | Audio config (see below) |
| `temperature` | float | No | 0.85 | LM sampling temperature |
| `top_p` | float | No | 0.9 | Nucleus sampling |
| `seed` | int/string | No | null | Random seed |
| `lyrics` | string | No | "" | Lyrics (takes priority over messages) |
| `sample_mode` | boolean | No | false | LLM auto-generates prompt/lyrics |
| `thinking` | boolean | No | false | LLM thinking mode |
| `use_format` | boolean | No | false | Enhance prompt/lyrics via LLM |
| `use_cot_caption` | boolean | No | true | Rewrite music description via CoT |
| `use_cot_language` | boolean | No | true | Auto-detect language via CoT |
| `guidance_scale` | float | No | 7.0 | Classifier-free guidance |
| `batch_size` | int | No | 1 | Number of samples |
| `task_type` | string | No | "text2music" | Task: text2music, cover, repaint |
| `repainting_start` | float | No | 0.0 | Repaint start (seconds) |
| `repainting_end` | float | No | null | Repaint end (seconds) |
| `audio_cover_strength` | float | No | 1.0 | Cover strength (0.0-1.0) |

### audio_config Object

| Field | Type | Default | Description |
|---|---|---|---|
| `duration` | float | null | Duration in seconds |
| `bpm` | integer | null | Beats per minute |
| `vocal_language` | string | "en" | Language code (en, zh, ja, etc.) |
| `instrumental` | boolean | null | Instrumental only (no vocals) |
| `format` | string | "mp3" | Output format |
| `key_scale` | string | null | Musical key (e.g. "C major") |
| `time_signature` | string | null | Time signature (e.g. "4/4") |

## Input Modes

### Mode 1: Tagged (Recommended)
```json
{
  "messages": [{"role": "user", "content": "<prompt>A gentle acoustic ballad, female vocal</prompt>\n<lyrics>[Verse 1]\nSunlight through the window\n\n[Chorus]\nWe are the dreamers</lyrics>"}],
  "audio_config": {"duration": 30, "vocal_language": "en"}
}
```

### Mode 2: Natural Language (sample_mode)
```json
{
  "messages": [{"role": "user", "content": "Generate an upbeat pop song about summer"}],
  "sample_mode": true,
  "audio_config": {"vocal_language": "en"}
}
```

### Mode 3: Lyrics Only
```json
{
  "messages": [{"role": "user", "content": "[Verse 1]\nWalking down the street\n\n[Chorus]\nDance with me tonight"}],
  "audio_config": {"duration": 30}
}
```

### Mode 4: Separate lyrics + prompt
Use `lyrics` field for lyrics, `messages` text becomes the prompt.

## Audio Input (for covers/repainting)

Multimodal messages with base64 audio:
```json
{
  "messages": [{"role": "user", "content": [
    {"type": "text", "text": "Cover this song in jazz style"},
    {"type": "input_audio", "input_audio": {"data": "<base64>", "format": "mp3"}}
  ]}],
  "task_type": "cover"
}
```

## Response

Audio is returned as base64 data URL in `choices[0].message.audio[0].audio_url.url`:
- Format: `data:audio/mpeg;base64,<base64_data>`
- Metadata in `choices[0].message.content` (caption, BPM, duration, key, lyrics)

## List Models

**GET** `/v1/models` — returns available models

## Health Check

**GET** `/health` — returns `{"status": "ok"}`
