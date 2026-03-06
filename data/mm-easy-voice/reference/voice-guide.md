# Voice Management Guide

Create and manage custom voices.

## List Voices

View all available voices:

```bash
python mmvoice.py list-voices
```

Shows system voices and any custom (cloned/designed) voices.

## Voice Cloning

Create a custom voice from an audio sample:

```bash
# Quick clone
python mmvoice.py clone audio_file.mp3 --voice-id my-custom-voice

# With preview
python mmvoice.py clone audio.mp3 --voice-id my-voice --preview "Test text" --preview-output preview.mp3
```

**Requirements:**
- Audio duration: 10s–5min
- File size: ≤20MB
- Formats: mp3, wav, m4a

## Voice Design

Design a voice from a text description:

```bash
python mmvoice.py design "A warm, gentle female voice" --voice-id designed-voice
```

## Notes

- Custom voices expire after 7 days if not used
- Use a voice with TTS to keep it permanently
