---
name: whisnap
description: macOS CLI for transcribing audio and video files using local Whisper models or Whisnap Cloud.
homepage: https://whisnap.com
metadata: {"clawdbot":{"emoji":"🎙️","requires":{"bins":["whisnap"]},"install":[{"id":"app","kind":"manual","label":"Install via Whisnap app Settings → Advanced → Enable CLI"}]}}
---

# whisnap

Use `whisnap` for transcribing audio/video files from the terminal. Requires the Whisnap macOS app with at least one model downloaded.

Setup (once)
- Open Whisnap app → Settings → Advanced → Enable CLI (creates `/usr/local/bin/whisnap` symlink)
- Download at least one Whisper model in the app

Common commands
- Transcribe audio: `whisnap recording.wav`
- Transcribe video: `whisnap meeting.mp4`
- Cloud transcription: `whisnap recording.wav --cloud`
- JSON output with timestamps: `whisnap lecture.m4a --json`
- Specific model: `whisnap interview.wav -m small-q5_1`
- Cloud + JSON: `whisnap recording.wav --cloud --json`
- List downloaded models: `whisnap --list-models`
- Verbose diagnostics: `whisnap recording.wav -v`

Supported formats
- Audio: WAV, MP3, FLAC, M4A, OGG
- Video: MP4, MOV, MKV, WebM

Flags
- `-c, --cloud` — Use Whisnap Cloud instead of local model (requires sign-in)
- `-m, --model <ID>` — Override model (e.g., `small-q5_1`). Defaults to app's selected model.
- `-j, --json` — Structured JSON output with text, segments, timestamps, model info
- `-v, --verbose` — Print progress and diagnostics to stderr
- `--list-models` — List available models and exit

JSON output format
```json
{
  "text": "transcribed text",
  "segments": [{ "start_ms": 0, "end_ms": 1000, "text": "segment" }],
  "model": "small-q5_1",
  "backend": "whisper",
  "processing_time_ms": 5000
}
```

Notes
- The CLI reuses models and settings from the Whisnap app (`~/Library/Application Support/com.whisnap.desktop/`).
- Cloud mode requires authentication — sign in via the app first.
- For scripting, use `--json` and pipe stdout. Diagnostics go to stderr.
- Exit code `0` = success, `1` = error.
- Only Whisper models are supported in CLI mode (not Parakeet).
- Confirm the file path exists before transcribing — the CLI validates but does not search.
