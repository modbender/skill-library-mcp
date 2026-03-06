# Skill: podcastifier (email/newsletter to podcast)

Turn incoming text (email/newsletter) into a short TTS podcast with chunking + ffmpeg concat.

## Features
- Parses plain text/HTML input and extracts story bullets.
- Generates TTS per chunk (char limit safe), concatenates via ffmpeg.
- Outputs mp3 with intro/outro; optional Signal/Telegram delivery hook.

## Usage
```bash
python podcastify.py --input newsletter.txt --voice "elevenlabs" --out briefing.mp3
```

## Options
- `--input` file or stdin
- `--voice` provider stub (implement your TTS call) 
- `--chunk` max chars per TTS call (default 3500)
- `--out` output mp3 path

## Notes
- Provide your TTS API key via env in the stub.
- Requires `ffmpeg` in PATH.
- This is a skeleton; wire your provider (e.g., ElevenLabs) in `synthesize()`.
