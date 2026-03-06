---
name: whisper-transcribe
description: Transcribe audio files to text using OpenAI Whisper. Supports speech-to-text with auto language detection, multiple output formats (txt, srt, vtt, json), batch processing, and model selection (tiny to large). Use when transcribing audio recordings, podcasts, voice messages, lectures, meetings, or any audio/video file to text. Handles mp3, wav, m4a, ogg, flac, webm, opus, aac formats.
---

# Whisper Transcribe

Transcribe audio with `scripts/transcribe.sh`:

```bash
# Basic (auto-detect language, base model)
scripts/transcribe.sh recording.mp3

# German, small model, SRT subtitles
scripts/transcribe.sh --model small --language de --format srt lecture.wav

# Batch process, all formats
scripts/transcribe.sh --format all --output-dir ./transcripts/ *.mp3

# Word-level timestamps
scripts/transcribe.sh --timestamps interview.m4a
```

## Models

| Model | RAM | Speed | Accuracy | Best for |
|-------|-----|-------|----------|----------|
| tiny | ~1GB | ⚡⚡⚡ | ★★ | Quick drafts, known language |
| base | ~1GB | ⚡⚡ | ★★★ | General use (default) |
| small | ~2GB | ⚡ | ★★★★ | Good accuracy |
| medium | ~5GB | 🐢 | ★★★★★ | High accuracy |
| large | ~10GB | 🐌 | ★★★★★ | Best accuracy (slow on Pi) |

## Output Formats

- **txt** — Plain text transcript
- **srt** — SubRip subtitles (for video)
- **vtt** — WebVTT subtitles
- **json** — Detailed JSON with timestamps and confidence
- **all** — Generate all formats at once

## Requirements

- `whisper` CLI (`pip install openai-whisper`)
- `ffmpeg` (for audio decoding)
- First run downloads the model (~150MB for base)
