---
name: telnyx-tts
description: Generate speech audio from text using Telnyx Text-to-Speech API. Use when you need to convert text to spoken audio, create voice messages, or generate audio content.
metadata: {"openclaw":{"emoji":"🔊","requires":{"bins":["python3"],"env":["TELNYX_API_KEY"]},"primaryEnv":"TELNYX_API_KEY"}}
---

# Telnyx Text-to-Speech

Generate high-quality speech audio from text using the Telnyx TTS API.

## Usage

To convert text to speech, run the script:

```bash
{baseDir}/scripts/telnyx-tts.py "Your text here" -o /tmp/output.mp3
```

The script outputs the path to the generated audio file on success.

## Options

- `-o, --output PATH`: Output file path (default: output.mp3)
- `--voice VOICE`: Voice ID (default: Telnyx.NaturalHD.astra)

## Available Voices

Telnyx provides multiple voice options:

- **Telnyx NaturalHD**: Premium voices with refined prosody
  - `Telnyx.NaturalHD.astra` (default)
  - `Telnyx.NaturalHD.luna`
  - `Telnyx.NaturalHD.andersen_johan`
- **Telnyx KokoroTTS**: Budget-friendly for high-volume
  - `Telnyx.KokoroTTS.af`
  - `Telnyx.KokoroTTS.am`

## Example

Generate speech and return as media:

```bash
{baseDir}/scripts/telnyx-tts.py "Hello! This is a test of Telnyx text to speech." -o /tmp/tts-output.mp3
```

Then return the audio file:
```
MEDIA: /tmp/tts-output.mp3
```

For Telegram voice notes, the audio will be sent as a voice message.

## Environment

Requires `TELNYX_API_KEY` environment variable to be set.
