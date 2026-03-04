---
name: telnyx-stt
description: Transcribe audio files to text using Telnyx Speech-to-Text API. Use when you need to convert audio recordings, voice messages, or spoken content to text.
metadata: {"openclaw":{"emoji":"🎤","requires":{"bins":["python3"],"env":["TELNYX_API_KEY"]},"primaryEnv":"TELNYX_API_KEY"}}
---

# Telnyx Speech-to-Text

Transcribe audio files to text using the Telnyx STT API (powered by Whisper).

## Usage

To transcribe an audio file, run:

```bash
{baseDir}/scripts/telnyx-stt.py /path/to/audio.mp3
```

The script outputs the transcribed text to stdout.

## Supported Formats

- MP3
- WAV
- OGG
- M4A
- WebM

## Example

```bash
{baseDir}/scripts/telnyx-stt.py /tmp/voice-message.ogg
```

Output:
```
Hello, this is a test transcription.
```

## Environment

Requires `TELNYX_API_KEY` environment variable to be set.
