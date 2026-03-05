---
name: edge-tts-unlimited
version: 1.0.0
description: |
  Free, unlimited text-to-speech using Microsoft Edge's neural voices via Python edge-tts.
  No API key, no credits, no character limits. Handles long-form content (tested 55+ minutes).
  Use when: (1) Converting text to speech for audio briefs, podcasts, or voice notes.
  (2) Generating long-form audio (news briefs, articles, stories) without hitting API limits.
  (3) Need TTS on a headless server (Fly.io, VPS, Docker) with zero setup cost.
  NOT for: Real-time streaming TTS, voice cloning, or premium voice acting (use ElevenLabs for that).
---

# Edge TTS Unlimited

Free, unlimited neural TTS. No API key. No credits. No character limits.

## Why This Over Other TTS Skills?

| Problem | Other skills | This skill |
|---------|-------------|------------|
| Long text (>5K chars) | Fail or need chunking | Works natively via `--file` |
| Cost | ElevenLabs burns $5/mo in 4 briefs | Free forever |
| API keys | Required | None needed |
| Server deployment | Some need native deps | Pure Python, works on Fly.io/Docker |
| 55-minute audio | Not tested/supported | Tested and confirmed |

## Quick Start

Generate speech from text:
```bash
scripts/speak.sh "Hello world" -o output.mp3
```

Generate from file (recommended for long text):
```bash
scripts/speak.sh --file /tmp/my-script.txt -o output.mp3
```

With voice and speed:
```bash
scripts/speak.sh --file script.txt -v en-US-GuyNeural -r "+5%" -o brief.mp3
```

## Requirements

- Python 3.8+ (pre-installed on most systems)
- `uv` package manager OR `pip` — script auto-detects

The script auto-installs `edge-tts` on first run via `uv run --with edge-tts` (no venv needed).

## Voice Presets

Use `--preset` for quick voice selection:

| Preset | Voice | Style |
|--------|-------|-------|
| `news-us` | en-US-GuyNeural +5% | Lively US news anchor |
| `news-bbc` | en-GB-RyanNeural | Authoritative British |
| `calm` | en-US-AndrewNeural -10% | Warm, relaxed |
| `fast` | en-US-ChristopherNeural +20% | Speed-read |

```bash
scripts/speak.sh --file brief.txt --preset news-us -o brief.mp3
```

## All Options

```
scripts/speak.sh [TEXT] [OPTIONS]
  TEXT              Text to speak (or use --file)
  --file, -f FILE   Read text from file (recommended for long content)
  --voice, -v NAME  Voice name (default: en-US-GuyNeural)
  --rate, -r RATE   Speed adjustment: "+5%", "-10%", etc.
  --preset, -p NAME Use a voice preset (see above)
  --output, -o FILE Output path (default: /tmp/tts-{timestamp}.mp3)
  --list            List available voices
  --list-filter STR Filter voice list (e.g. "british", "female")
```

## Popular Voices

Run `scripts/speak.sh --list` for all voices, or filter:
```bash
scripts/speak.sh --list-filter british
scripts/speak.sh --list-filter female
```

**English highlights:**
- `en-US-GuyNeural` — Male, news/passion (best for briefs)
- `en-US-ChristopherNeural` — Male, authoritative
- `en-US-AriaNeural` — Female, confident
- `en-GB-RyanNeural` — Male, British steady
- `en-GB-SoniaNeural` — Female, British

## Tested Limits

| Chars | Duration | File Size | Result |
|-------|----------|-----------|--------|
| 7,400 | ~6 min | 2.6 MB | ✅ |
| 18,000 | ~21 min | 7.3 MB | ✅ |
| 46,200 | ~55 min | 18.8 MB | ✅ |

No hard limit found. Microsoft Edge TTS service handles arbitrarily long text.

## Tips

- **Always use `--file`** for text longer than a sentence — avoids shell quoting issues
- **Rate "+5%"** sounds natural for news; "+20%" for speed-listening
- Edge TTS interprets `[short pause]` as literal text — use commas and periods for natural pauses
- Audio is 48kbps mono MP3 by default — good enough for voice, small file size
