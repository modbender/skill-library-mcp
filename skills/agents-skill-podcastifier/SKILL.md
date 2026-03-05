---
name: podcastifier
description: Turn incoming text (email/newsletter) into a short TTS podcast with chunking + ffmpeg concat.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["python3", "ffmpeg"] },
      "category": "media"
    }
  }
---

# podcastifier

Turn incoming text (email/newsletter) into a short TTS podcast with chunking + ffmpeg concat.

## Features
- Parses plain text/HTML input and extracts story bullets.
- Generates TTS per chunk (char limit safe), concatenates via ffmpeg.
- Outputs mp3 with intro/outro.

## Usage
```bash
python podcastify.py --input newsletter.txt --voice "elevenlabs" --out briefing.mp3
```
