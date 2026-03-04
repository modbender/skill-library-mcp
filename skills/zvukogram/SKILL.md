---
name: zvukogram
description: Text-to-Speech via Zvukogram API with SSML support. Use when you need to generate speech from text, create podcasts, voice notifications, or work with audio. Supports speed control, stress marks, English word transcription, and audio fragment merging.
requires:
  env: [ZVUKOGRAM_TOKEN, ZVUKOGRAM_EMAIL]
  credentials: zvukogram_api
---

# Zvukogram TTS

Speech generation via Zvukogram API with SSML markup support.

## Requirements

To use this skill, you need:
- **Zvukogram API token** — get it at https://zvukogram.com/
- **Zvukogram account email**

### Setup

Create file `~/.config/zvukogram/config.json`:
```bash
mkdir -p ~/.config/zvukogram
```

```json
{
  "token": "your_api_token_here",
  "email": "your_email@example.com"
}
```

Or use environment variables:
```bash
export ZVUKOGRAM_TOKEN=your_api_token_here
export ZVUKOGRAM_EMAIL=your_email@example.com
```

## Quick Start

```bash
# Simple TTS
python3 scripts/tts.py --text "Hello, world!" --voice Алена --output hello.mp3

# With +20% speed
python3 scripts/tts.py --text "Fast text" --voice Алена --speed 1.2 --output fast.mp3

# Check balance
python3 scripts/balance.py
```

## Features

- **TTS generation** — text to speech
- **SSML support** — stress marks, pauses, speed
- **Audio merging** — combine fragments via ffmpeg
- **Transcription** — proper pronunciation of English words

## SSML Markup

### Stress Marks
Use `+` before stressed vowel:
```
З+амок — stress on "a"
зам+ок — stress on "o"
```

### Aliases (Transcription)
```xml
<sub alias="Оупен Эй Ай">OpenAI</sub>
<sub alias="Самсунг">Samsung</sub>
<sub alias="Ал+ьтман">Альтман</sub>
```

### Speed
```xml
<prosody rate="1.2">20% faster</prosody>
<prosody rate="fast">Fast text</prosody>
```

### Pauses
```xml
<break time="500ms"/>
```

## Available Voices

- **Алена** — female, neutral (recommended)
- **Андрей** — male, neutral (recommended)
- **Александра** — female, soft
- **Антон** — male, business

Full list: see [references/VOICES.md](references/VOICES.md)

## Examples

See [references/EXAMPLES.md](references/EXAMPLES.md) for:
- Dialogs and podcasts
- News voiceover
- Voice notifications
- Long texts

## Transcription

See [references/TRANSCRIPTION.md](references/TRANSCRIPTION.md) for proper pronunciation:
- OpenAI → Оупен Эй Ай
- GPT → Джи Пи Ти
- Samsung → Самсунг
- Altman → Ал+ьтман

## SSML Reference

See [references/SSML_CHEATSHEET.md](references/SSML_CHEATSHEET.md) for quick tag lookup.

## Troubleshooting

See [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) for:
- API errors
- Audio issues
- Diagnostics

## API Limitations

- Max 1000 characters per request (`/text`)
- Up to 1M characters via `/longtext`
- SSML with `<voice>` not supported via API (web only)
- For multi-voice — merge fragments

## Links

- API docs: https://zvukogram.com/node/api/
- Voice rating: https://zvukogram.com/rating/
- Support: https://t.me/zvukogram
