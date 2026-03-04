---
name: echoforge-moss-voice
description: Voice-first OpenClaw skill powered by MOSS APIs. Use when a user wants spoken replies in a preferred timbre, either from an existing voice_id or from a reference audio clip.
---

# EchoForge Moss Voice

Use this skill to run voice interaction with user-preferred timbre.

## Required runtime config

- `MOSI_API_KEY` (required)
- `MOSI_BASE_URL` (optional, default `https://studio.mosi.cn`)

Always send:

- `Authorization: Bearer <MOSI_API_KEY>`

## Inputs

Collect:

- `text` (required, what to speak)
- Voice source (one of):
  - `voice_id` (preferred when available), or
  - `reference_audio` (public URL), or
  - local audio path (upload first, then clone voice)

Optional:

- `expected_duration_sec`
- `sampling_params`:
  - `max_new_tokens` (default 512)
  - `temperature` (default 1.7)
  - `top_p` (default 0.8)
  - `top_k` (default 25)
- `meta_info` (default false)

## Workflow

1. Resolve voice source.
   - If `voice_id` is available, use it directly.
   - If only local audio path is available:
     - Upload file: `POST /api/v1/files/upload` with multipart field `file`.
     - Clone voice: `POST /api/v1/voice/clone` with `file_id` (or `url`).
     - If returned voice status is not active, poll `GET /api/v1/voices/{voice_id}` until `ACTIVE` or timeout.
   - If `reference_audio` URL is available, use it directly in TTS.
2. Run TTS: `POST /v1/audio/tts`.
   - Required payload:
     - `model: "moss-tts"`
     - `text`
     - one of `voice_id` or `reference_audio`
3. Parse response:
   - Decode `audio_data` (base64) to WAV.
   - Read `duration_s` and `usage` when present.
4. Return a concise result:
   - `voice_id` used
   - output file path
   - duration
   - brief status message

## Error handling

- If `4010` or `4011`: API key missing/invalid, ask user to fix `MOSI_API_KEY`.
- If `4020`: insufficient credits, ask user to recharge.
- If `4029`: rate limited, retry with exponential backoff.
- If `5002`: invalid audio URL or decode failed, ask user for another clip.
- If `5004`: timeout, shorten text and retry.

## Operational constraints

- Keep request rate <= 5 RPM.
- Keep single request text short enough to avoid timeout.
- Never print or log raw API keys.
- Prefer reusing stable `voice_id` for multi-turn voice chat to reduce latency.
