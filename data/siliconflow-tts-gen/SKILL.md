---
name: siliconflow-tts-gen
description: Text-to-Speech using SiliconFlow API (CosyVoice2). Supports multiple voices, languages, and dialects.
env:
  - SILICONFLOW_API_KEY
files:
  config:
    - ~/.openclaw/openclaw.json
---

# SiliconFlow TTS Generation Skill

Text-to-Speech using SiliconFlow API with CosyVoice2 model. Supports 8 preset voices, multiple languages, and Chinese dialects.

## Features

- 🎙️ **8 Preset Voices**: 4 male + 4 female voices
- 🌍 **Multilingual**: Chinese, English, Japanese, Korean
- 🗣️ **Chinese Dialects**: Cantonese, Sichuan, Shanghai, Tianjin, Wuhan
- ⚡ **Ultra Low Latency**: 150ms first packet delay
- 🎵 **Voice Cloning**: 3-second rapid voice cloning
- 💾 **Auto Download**: Saves audio files locally

## Requirements

- **Environment Variable**: `SILICONFLOW_API_KEY`
- **Optional Config File**: `~/.openclaw/openclaw.json` (for auto-detect)

## Installation

```bash
npx clawhub install siliconflow-tts-gen
```

## Configuration

Set your SiliconFlow API key:

```bash
export SILICONFLOW_API_KEY="your-api-key"
```

## Usage

### List Available Voices

```bash
python3 scripts/generate.py --list-voices
```

### Generate Speech

```bash
# Basic usage (default voice: alex)
python3 scripts/generate.py "你好，世界"

# Specify voice
python3 scripts/generate.py "Hello World" --voice bella

# Adjust speed
python3 scripts/generate.py "你好" --voice claire --speed 0.9

# Save to file
python3 scripts/generate.py "欢迎收听" --output welcome.mp3

# Change format
python3 scripts/generate.py "Hello" --format wav
```

## Available Voices

### Male Voices
| ID | Name | Characteristic |
|----|------|----------------|
| alex | 沉稳男声 | Mature and steady |
| benjamin | 低沉男声 | Deep and low |
| charles | 磁性男声 | Magnetic |
| david | 欢快男声 | Cheerful |

### Female Voices
| ID | Name | Characteristic |
|----|------|----------------|
| anna | 沉稳女声 | Mature and elegant |
| bella | 激情女声 | Passionate |
| claire | 温柔女声 | Gentle and kind |
| diana | 欢快女声 | Sweet and happy |

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `--voice` | string | alex | - | Voice ID |
| `--speed` | float | 1.0 | 0.25-4.0 | Speech speed |
| `--format` | string | mp3 | mp3/opus/wav/pcm | Output format |
| `--output` | string | output.mp3 | - | Output file path |

## Security Notes

- This skill requires an API key to call SiliconFlow services
- The script reads `~/.openclaw/openclaw.json` only to auto-detect API keys
- No sensitive data is transmitted except to `api.siliconflow.cn`
- Review the code at `scripts/generate.py` before providing credentials

## Author

MaxStorm Team

## License

MIT
