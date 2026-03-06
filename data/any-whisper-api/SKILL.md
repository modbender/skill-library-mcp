---
name: any-whisper-api
description: Transcribe audio via API Whisper with any compatible local servers.
homepage: https://platform.openai.com/docs/guides/speech-to-text
metadata: {"clawdbot":{"emoji":"☁️","requires":{"bins":["curl"],"env":["WHISPER_API_KEY","WHISPER_API_HOST"]}}}
---

# OpenAI Whisper API (curl)

Transcribe an audio file via OpenAI’s `/v1/audio/transcriptions` endpoint.

## Quick start

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a
```

Defaults:
- Model: `whisper-1`
- Output: `<input>.txt`

## Whisper.cpp example 
/ai/whisper.cpp/build/bin/whisper-server -m /ai/models/whisper/ggml-large-v3-turbo-q8_0.bin --host 192.168.0.55 --port 5005 -sow --vad --vad-model /ai/models/whisper/ggml-silero-v6.2.0.bin --inference-path /v1/audio/transcriptions


## Useful flags

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model whisper-1 --out /tmp/transcript.txt
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language en
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --prompt "Speaker names: Peter, Daniel"
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
```

## API key

Set `WHISPER_API_KEY` and `WHISPER_API_HOST`, or configure it in `~/.clawdbot/clawdbot.json`:

```json5
{
  skills: {
    "openai-whisper-api": {
      apiKey: "WHISPER_API_KEY_HERE",
      apiHost: "WHISPER_API_HOST_HERE"
    }
  }
}
```
