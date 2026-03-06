---
name: piper-tts
description: Local text-to-speech using Piper for voice message delivery. Use when the user asks for voice responses, audio messages, TTS, text-to-speech, voice notes, or wants to hear something spoken aloud. Converts text to speech locally (no cloud APIs, no cost, no latency) and delivers as voice messages on Telegram, Discord, or any channel supporting audio.
---

# Piper TTS — Local Voice Messages

Generate voice messages using [Piper](https://github.com/rhasspy/piper), a fast local TTS engine. Zero cloud calls, zero cost, zero API keys.

## Setup

If Piper is not installed, run the setup script:

```bash
scripts/setup-piper.sh
```

This installs `piper-tts` via pip and downloads a default voice (`en_US-kusal-medium`).

## Generating Voice Messages

Use `scripts/piper-speak.sh` to generate and deliver voice:

```bash
scripts/piper-speak.sh "<text>" [voice]
```

- `text`: The text to speak (required)
- `voice`: Piper voice name (default: `en_US-kusal-medium`)

The script outputs an MP3 path. Include it in your reply as:

```
[[audio_as_voice]]
MEDIA:<path-to-mp3>
```

This delivers the audio as a native voice message on supported channels (Telegram, Discord, etc.).

## Example Workflow

1. User asks: "Tell me a joke as audio"
2. Run: `scripts/piper-speak.sh "Why do programmers prefer dark mode? Because light attracts bugs!"`
3. Get MP3 path from output
4. Reply with `[[audio_as_voice]]` + `MEDIA:<path>`

## Available Voices

After setup, download additional voices:

```bash
scripts/setup-piper.sh --voice en_US-ryan-high
scripts/setup-piper.sh --voice en_GB-northern_english_male-medium
```

Popular voices:
- `en_US-kusal-medium` — Clear male voice (default, recommended)
- `en_US-ryan-high` — High quality US male
- `en_US-hfc_male-medium` — US male
- `en_GB-northern_english_male-medium` — British male
- Browse all: https://huggingface.co/rhasspy/piper-voices

## Important Notes

- **Speed**: Local generation is ~0.5-1s. Much faster than cloud TTS.
- **No API keys**: Works completely offline after setup.
- **Platform**: macOS (Apple Silicon + Intel), Linux. Requires Python 3.9+.
- **Do NOT** set `messages.tts.auto: "always"` in OpenClaw config — it makes every response slow. Keep TTS on-demand.
