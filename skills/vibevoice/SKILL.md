---
name: vibevoice
description: Local Spanish TTS using Microsoft VibeVoice. Generate natural voice audio from text, optimized for WhatsApp voice messages.
metadata:
  author: estudiosdurero
  version: "1.0.0"
  homepage: https://github.com/microsoft/VibeVoice
  openclaw:
    emoji: "🎙️"
    requires:
      bins: ["ffmpeg", "python3"]
      env: []
    install:
      - id: "vibevoice-clone"
        kind: "manual"
        label: "Clone VibeVoice repo and setup venv"
        instructions: |
          git clone https://github.com/microsoft/VibeVoice.git ~/VibeVoice
          cd ~/VibeVoice
          python3 -m venv venv
          source venv/bin/activate
          pip install -e .
          pip install torch torchaudio
---

# VibeVoice TTS

Local text-to-speech using Microsoft's VibeVoice model. Generates natural Spanish voice audio, perfect for WhatsApp voice messages.

## Quick Start

```bash
# Basic usage
{baseDir}/scripts/vv.sh "Hola, esto es una prueba" -o /tmp/audio.ogg

# From file
{baseDir}/scripts/vv.sh -f texto.txt -o /tmp/audio.ogg

# Different voice
{baseDir}/scripts/vv.sh "Texto" -v en-Wayne -o /tmp/audio.ogg

# Adjust speed (0.5-2.0)
{baseDir}/scripts/vv.sh "Texto" -s 1.2 -o /tmp/audio.ogg
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Voice | `sp-Spk1_man` | Spanish male voice (slight Mexican accent) |
| Speed | `1.15` | 15% faster than normal |
| Format | `.ogg` | Opus codec for WhatsApp |

## Available Voices

Spanish:
- `sp-Spk1_man` - Male, slight Mexican accent (default)

English:
- `en-Wayne` - Male
- `en-Denise` - Female
- Other voices in `~/VibeVoice/demo/voices/streaming_model/`

## Output Formats

- `.ogg` - Opus codec (WhatsApp compatible, recommended)
- `.mp3` - MP3 format
- `.wav` - Uncompressed WAV

## For WhatsApp

Always use `.ogg` format with `asVoice=true` in the message tool:

```bash
# Generate
{baseDir}/scripts/vv.sh "Tu mensaje aquí" -o /tmp/mensaje.ogg

# Send via message tool
message action=send channel=whatsapp to="+34XXXXXXXXX" filePath=/tmp/mensaje.ogg asVoice=true
```

## Requirements

- **GPU**: NVIDIA with ~2GB VRAM
- **VibeVoice**: Installed at `~/VibeVoice`
- **ffmpeg**: For audio conversion
- **Python 3.10+**: With torch, torchaudio

## Performance

- RTF: ~0.24x (generates faster than realtime)
- 1 minute of audio ≈ 15 seconds to generate

## Notes

- First run loads model (~10s), subsequent runs are faster
- Audio rule: Only send voice if user requests it or speaks via audio
- Keep text under 1500 chars for best quality
