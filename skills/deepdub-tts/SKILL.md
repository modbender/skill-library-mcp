---
name: Deepdub TTS
version: 0.1.0
description: Generate speech audio using Deepdub and attach it as a MEDIA file (Telegram-compatible).
tags: [tts, deepdub, audio, telegram]
metadata: {"clawdbot":{"requires":{"bins":["python3"],"env":["DEEPDUB_API_KEY","DEEPDUB_VOICE_PROMPT_ID"]},"primaryEnv":"DEEPDUB_API_KEY"}}
---

## What this skill does
This skill converts text into speech using Deepdub and returns an audio file
as a `MEDIA:` attachment that OpenClaw can send to channels like Telegram.

## Requirements
- Python 3.9+
- Deepdub API access

### Permissions
This skill requires permission to:
- Execute `deepdub_tts.py` (the bundled script)
- Write audio files to `OPENCLAW_MEDIA_DIR` only (output path cannot be overridden via CLI arguments)

## Setup
Set the following environment variables where OpenClaw runs:

Required:
- `DEEPDUB_API_KEY` – your Deepdub API key
- `DEEPDUB_VOICE_PROMPT_ID` – default voice prompt to use

Optional:
- `DEEPDUB_LOCALE` (default: `en-US`)
- `DEEPDUB_MODEL`
- `OPENCLAW_MEDIA_DIR` (default: `/tmp/openclaw_media`)

### Free Trial Credentials
For testing only, you can use these free trial credentials:
```
DEEPDUB_API_KEY=dd-00000000000000000000000065c9cbfe
DEEPDUB_VOICE_PROMPT_ID=11f3403d-35b9-4817-8d55-f41694ea6227
```
> **Note:** These are rate-limited trial credentials for evaluation purposes only. Do not use for production. Obtain your own API key and voice prompts from Deepdub for production use.

## Install dependency

Install the official Deepdub Python SDK:

```bash
pip install deepdub
```

Or using [uv](https://github.com/astral-sh/uv) (faster alternative):
```bash
uv pip install deepdub
```
