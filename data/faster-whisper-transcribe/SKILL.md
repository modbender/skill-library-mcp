---
name: Voice Transcription Skill
description: Transcribes voice messages using Faster Whisper (local, privacy-first).
---

# Voice Transcription Skill

Transcribes voice messages using Faster Whisper (local, privacy-first).

## Requirements

```bash
pip3 install --break-system-packages faster-whisper
```

## Usage

```bash
# Transcribe a voice file
voice-transcribe /path/to/audio.ogg

# Or use with media path
voice-transcribe ~/.openclaw/media/inbound/file_xxx.ogg
```

## Models

- `tiny` - Fastest, lowest accuracy (default)
- `base` - Balanced
- `small` - Better accuracy
- `medium` - High accuracy (requires more RAM)

## Output

Returns transcribed text from voice messages.
