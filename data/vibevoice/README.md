# VibeVoice TTS Skill

🎙️ Local Spanish text-to-speech for OpenClaw using Microsoft's VibeVoice model.

## Features

- **Natural Spanish voice** - High quality TTS with slight Mexican accent
- **WhatsApp optimized** - Outputs .ogg (Opus) for voice messages
- **Fast** - RTF ~0.24x (faster than realtime)
- **Local** - Runs on your GPU, no API costs
- **Configurable** - Multiple voices, adjustable speed

## Requirements

- NVIDIA GPU with ~2GB VRAM
- Python 3.10+
- ffmpeg
- [VibeVoice](https://github.com/microsoft/VibeVoice) installed at `~/VibeVoice`

## Installation

1. Install VibeVoice:
```bash
git clone https://github.com/microsoft/VibeVoice.git ~/VibeVoice
cd ~/VibeVoice
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install torch torchaudio
```

2. Install this skill:
```bash
clawhub install vibevoice
```

## Usage

```bash
# Basic
./scripts/vv.sh "Hola mundo" -o /tmp/audio.ogg

# With options
./scripts/vv.sh "Texto largo aquí" -v sp-Spk1_man -s 1.15 -o /tmp/audio.ogg
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VIBEVOICE_DIR` | `~/VibeVoice` | Installation path |
| `VIBEVOICE_VOICE` | `sp-Spk1_man` | Default voice |
| `VIBEVOICE_SPEED` | `1.15` | Playback speed |

## Author

Created by [Estudios Durero](https://estudiosdurero.com) for internal use with OpenClaw.

## License

MIT
