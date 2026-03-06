---
name: eleven-stt
description: Transcribe audio files with ElevenLabs Speech-to-Text (Scribe v2) from the local CLI. Supports diarization, events, JSON output, webhooks, and advanced STT options.
metadata: {"openclaw":{"requires":{"bins":["curl","jq","python3","ffmpeg","websocat"],"env":["ELEVENLABS_API_KEY"]}}}
---

# ElevenLabs Speech-to-Text (Local CLI)

## Use

Run the script in `scripts/transcribe.sh` with an audio file path or URL.

Examples:

```bash
scripts/transcribe.sh /path/to/audio.mp3
scripts/transcribe.sh /path/to/audio.mp3 --diarize --lang en
scripts/transcribe.sh /path/to/audio.mp3 --json
scripts/transcribe.sh /path/to/audio.mp3 --webhook --webhook-metadata '{"job":"call-001"}'
scripts/transcribe.sh --url https://example.com/audio.mp3 --lang en
```

## Environment

Set `ELEVENLABS_API_KEY` in your shell or OpenClaw env before running.

## Notes

- Defaults to `scribe_v2` (the Speech-to-Text model) and uses a filesystem lock to avoid parallel requests.
- Requires `curl` and `jq`.
- For async workflows, use `--webhook` with optional `--webhook-id` and `--webhook-metadata`.
- Realtime streaming is available via `scripts/realtime.sh` (requires `ffmpeg` + `websocat`) and uses the `scribe_v2_realtime` model.
- Live listener mode is available via `scripts/live_listen.sh` with toggle/always-on modes and optional TTS response.
