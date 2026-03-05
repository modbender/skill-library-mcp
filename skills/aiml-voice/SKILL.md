---
name: aimlapi-voice
description: Transcribe audio files (ogg, mp3, wav, etc.) using AIMLAPI. Use when the user provides audio messages or local audio files. Provides a reliable Python script with retries and polling.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "requires": { "bins": ["python"], "env": ["AIMLAPI_API_KEY"] },
        "primaryEnv": "AIMLAPI_API_KEY",
      },
  }
---

# AIMLAPI Voice Transcription

## Overview

A robust skill for transcribing audio via AIMLAPI's specialized speech-to-text endpoints. It handles queuing, polling for results, and automatic MIME-type detection.

## Quick Start

```bash
# Set your API key first (if not in env)
# export AIMLAPI_API_KEY="your-key-here"

# Transcribe a file
python {baseDir}/scripts/transcribe.py path/to/audio.ogg
```

## Tasks

### Process Voice Messages

When an audio file is received, use this script to extract the text.

```bash
python {baseDir}/scripts/transcribe.py <file_path> \
  --model "#g1_whisper-medium" \
  --verbose
```

### Arguments

- `file`: (Required) Path to the audio file.
- `--model`: Model ID (default: `#g1_whisper-medium`).
- `--out`: Path to save the transcript text.
- `--poll-interval`: Seconds between status checks (default: 5).
- `--max-wait`: Stop waiting after N seconds (default: 300).

## Dependencies

- Python 3
- `AIMLAPI_API_KEY` set in environment or provided via `--apikey-file`.
