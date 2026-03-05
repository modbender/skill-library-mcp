---
name: salute-speech
description: >
  Transcribe audio files using Sber Salute Speech async API.
  Russian-first STT with support for ru-RU, en-US, kk-KZ, ky-KG, uz-UZ.
metadata: { "openclaw": { "requires": { "bins": ["uv"], "env": ["SALUTE_AUTH_DATA"] }, "primaryEnv": "SALUTE_AUTH_DATA" } }
---

# Audio Transcription with Sber Salute Speech

Transcribe audio/video files to text with timestamps via Salute Speech async REST API.

## Requirements

- **API Key**: Environment variable `SALUTE_AUTH_DATA` must be set (Base64-encoded `client_id:client_secret` or raw authorization key from https://developers.sber.ru/studio/).
- **SSL note**: The script disables SSL verification by default (`verify_ssl=False`) because Sber's certificate chain is non-standard. This is expected.

## Supported formats & encodings

| Audio encoding | Content-Type | Typical extensions |
|---------------|-------------|--------------------|
| `MP3` | `audio/mpeg` | `.mp3` |
| `PCM_S16LE` | `audio/wav` | `.wav` |
| `OPUS` | `audio/ogg` | `.ogg`, `.opus` |
| `FLAC` | `audio/flac` | `.flac` |
| `ALAW` | `audio/alaw` | `.alaw` |
| `MULAW` | `audio/mulaw` | `.mulaw` |

## Supported languages

`ru-RU`, `en-US`, `kk-KZ` (Kazakh), `ky-KG` (Kyrgyz), `uz-UZ` (Uzbek).

## Workflow

1. **Identify input files** — from user request.
2. **Read API key** from host environment.
3. **Run transcription** — execute `salute_transcribe.py` with `uv` and appropriate arguments.
4. **Deliver results** — present to user human-readable transcript with timestamps to the user and give a direct link to files.

## Usage

```bash
uv run --with requests {baseDir}/salute_transcribe.py \
  --file /path/to/audio.mp3 \
  --output_dir ~/.openclaw/workspace/transcriptions \
  --lang ru-RU
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--file` | **Yes** | — | Path to audio/video file |
| `--output_dir` | No | `~/.openclaw/workspace/transcribations` | Output directory for results |
| `--lang` | No | `ru-RU` | Language code: `ru-RU`, `en-US`, `kk-KZ`, `ky-KG`, `uz-UZ` |
| `--audio-encoding` | No | `MP3` | Codec: `MP3`, `PCM_S16LE`, `OPUS`, `FLAC`, `ALAW`, `MULAW` |
| `--model` | No | `general` | Recognition model: `general` or `callcenter` |
| `--hyp-count` | No | `1` | Number of alternative hypotheses: `1` or `2` |
| `--max-wait-time` | No | `300` | Max seconds to wait for async result |
| `--print` | No | off | Also print transcription to stdout |

### Content-Type mapping

When the file extension doesn't match `audio/mpeg`, adjust `content_type` in the script or add logic. Current default is `audio/mpeg` (MP3). For `.wav` files use `audio/wav`, etc.

## Output files

For input file `meetingABC.mp3` the script produces:

| File | Description |
|------|-------------|
| `meetingABC_recognition_orig.json` | Raw API response (full JSON with all hypotheses, timing, confidence) |
| `meetingABC_pretty.txt` | Formatted human-readable transcript with timestamps |

### Output text format

```
[00:01 - 00:20]:
Ну, даже если сосредоточиться на идее узкой щели.

[00:20 - 00:45]:
Следующий фрагмент текста здесь.
```

## Notes

- Token is valid for ~30 minutes; the script fetches a new one each run.
- Large files (>1 hour) may need `--max-wait-time` increased beyond 300s.
- The `callcenter` model is optimized for telephony audio (8kHz, mono).
- Profanity filter is disabled by default (`enable_profanity_filter=False`).
- The script uses **normalized text** by default (numbers as digits, abbreviations expanded). Raw text is also available in the JSON output.