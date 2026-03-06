---
name: local-vosk
description: Local speech-to-text using Vosk. Lightweight, fast, fully offline. Perfect for transcribing Telegram voice messages, audio files, or any speech-to-text task without cloud APIs.
---

# Local Vosk STT

Lightweight local speech-to-text using Vosk. **Fully offline** after model download.

## Use Cases

- **Telegram voice messages** — transcribe .ogg voice notes automatically
- **Audio files** — any format ffmpeg supports
- **Offline transcription** — no API keys, no cloud, no costs

## Quick Start

```bash
# Transcribe Telegram voice message
./skills/local-vosk/scripts/transcribe voice_message.ogg

# Transcribe any audio
./skills/local-vosk/scripts/transcribe audio.mp3

# With language (default: en-us)
./skills/local-vosk/scripts/transcribe audio.wav --lang en-us
```

## Supported Formats

Any format ffmpeg can decode: **ogg** (Telegram), mp3, wav, m4a, webm, flac, etc.

## Models

Default model: `vosk-model-small-en-us-0.15` (~40MB)

Other models available at https://alphacephei.com/vosk/models

## Setup (if not installed)

```bash
pip3 install vosk --user --break-system-packages

# Download model
mkdir -p ~/vosk-models && cd ~/vosk-models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

## Notes

- Quality is good for conversational speech
- For higher accuracy, use larger models or faster-whisper
- Processes audio at ~10x realtime on typical hardware
- Telegram voice messages are .ogg format — works out of the box
