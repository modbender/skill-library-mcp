# SiliconFlow TTS Generation Skill

Text-to-Speech using SiliconFlow API with CosyVoice2 model.

## Features

- 🎙️ **8 Preset Voices**: 4 male + 4 female voices
- 🌍 **Multilingual**: Chinese, English, Japanese, Korean
- 🗣️ **Chinese Dialects**: Cantonese, Sichuan, Shanghai, Tianjin, Wuhan
- ⚡ **Ultra Low Latency**: 150ms first packet delay
- 🎵 **Voice Cloning**: 3-second rapid voice cloning

## Quick Start

```bash
# Install
npx clawhub install siliconflow-tts-gen

# Set API key
export SILICONFLOW_API_KEY="your-api-key"

# Generate speech
python3 scripts/generate.py "你好，世界"
```

## Available Voices

| Gender | ID | Name |
|--------|-----|------|
| Male | alex | 沉稳男声 |
| Male | benjamin | 低沉男声 |
| Male | charles | 磁性男声 |
| Male | david | 欢快男声 |
| Female | anna | 沉稳女声 |
| Female | bella | 激情女声 |
| Female | claire | 温柔女声 |
| Female | diana | 欢快女声 |

## Usage Examples

```bash
# List voices
python3 scripts/generate.py --list-voices

# Basic usage
python3 scripts/generate.py "Hello World"

# With voice selection
python3 scripts/generate.py "欢迎收听" --voice claire

# Adjust speed
python3 scripts/generate.py "你好" --speed 0.9

# Save to specific file
python3 scripts/generate.py "Hello" --output greeting.mp3
```

## Author

MaxStorm Team

## License

MIT
