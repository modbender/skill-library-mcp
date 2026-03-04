# Gettr Transcript

Download audio from a GETTR post or streaming page and transcribe it locally with MLX Whisper on Apple Silicon.

## What it does

- Extracts audio/video URL from GETTR pages via browser automation
- Downloads audio as 16kHz mono WAV (handles both direct `.m4a` and HLS `.m3u8`)
- Transcribes locally with MLX Whisper (no API keys required)
- Outputs VTT with timestamps for precise outline generation

## Quick start

```bash
# 1. Use browser automation to get the audio/video URL:
#    - /streaming/ URLs: derive .m4a from og:video (replace .m3u8 → /audio.m4a)
#    - /post/ URLs: extract og:video .m3u8 URL from rendered DOM
#    See SKILL.md Step 1 for details

# 2. Run download + transcription (slug is the last path segment of the URL)
bash scripts/run_pipeline.sh "<AUDIO_OR_VIDEO_URL>" "<SLUG>"
```

Outputs to `./out/gettr-transcribe/<slug>/`:

- `audio.wav` – extracted audio
- `audio.vtt` – timestamped transcript

## Prerequisites

- `mlx_whisper` (`pip install mlx-whisper`)
- `ffmpeg` (`brew install ffmpeg`)

## Features

- Direct `.m4a` audio download for streaming URLs (faster, more reliable)
- Falls back to HLS `.m3u8` for post URLs
- Transcribes in original language (auto-detected)
- Prevents hallucination propagation with `--condition_on_previous_text False`

## Note

This build was republished to refresh ClawHub scan-state sync.
