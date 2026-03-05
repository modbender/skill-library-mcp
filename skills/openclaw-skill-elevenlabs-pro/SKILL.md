---
name: elevenlabs-pro
description: ElevenLabs advanced TTS for converting text to speech, listing voices, and managing credits
license: MIT
metadata:
  version: 1.0.0
  author: Jack2
  tags: tts, audio, elevenlabs, voice
---

# ElevenLabs Pro Skill

Advanced text-to-speech using the ElevenLabs API. Supports voice selection, language/gender filtering, audio file generation, and credit tracking.

## Prerequisites

Set your API key as an environment variable:
```bash
export ELEVENLABS_API_KEY=sk_...
```

Or pass it directly with `--api-key`.

## Usage

### Convert text to speech
```bash
python3 scripts/elevenlabs.py "Hello world" --voice Sarah --output audio.mp3
```

### List available voices
```bash
python3 scripts/elevenlabs.py --list-voices
python3 scripts/elevenlabs.py --list-voices --lang en --gender female
python3 scripts/elevenlabs.py --list-voices --json
```

### Check remaining credits
```bash
python3 scripts/elevenlabs.py --credits
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--voice NAME` | Rachel | Voice name (partial match supported) |
| `--voice-id ID` | — | Direct voice ID (overrides --voice) |
| `--output PATH` | output.mp3 | Output MP3 file path |
| `--model ID` | eleven_turbo_v2_5 | Model ID |
| `--stability` | 0.5 | Voice stability (0–1) |
| `--similarity` | 0.75 | Similarity boost (0–1) |
| `--style` | 0.0 | Style exaggeration (0–1) |
| `--lang CODE` | — | Filter voices by language (e.g. en, fr) |
| `--gender` | — | Filter voices by gender (male/female) |
| `--json` | — | Output as JSON |
| `--api-key KEY` | — | API key (overrides env var) |

## Available Models

| Model ID | Description |
|----------|-------------|
| `eleven_turbo_v2_5` | Fastest, lowest latency (free tier supported) |
| `eleven_multilingual_v2` | Best quality, multilingual |
| `eleven_flash_v2_5` | Ultra-low latency |

## Importable API

```python
import sys
sys.path.insert(0, "path/to/skills/elevenlabs-pro/scripts")
from elevenlabs import list_voices, get_voice_id, text_to_speech, get_credits

api_key = "sk_..."
# TTS
voice_id = get_voice_id(api_key, "Sarah")
path = text_to_speech(api_key, "Hello!", voice_id, "out.mp3")

# Credits
info = get_credits(api_key)
print(info["characters_remaining"])
```

## References

See `references/voices.md` for popular voices and voice parameter guidance.
