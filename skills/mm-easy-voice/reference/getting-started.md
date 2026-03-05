# Getting Started

Quick setup guide for MiniMax Voice Maker.

## Environment Setup

### 1. Install dependencies

```bash
# Navigate to project directory
cd mmVoiceMaker

# Install Python packages
pip install -r requirements.txt

# Install FFmpeg (required for audio processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg
```

### 2. Set API key

```bash
export MINIMAX_VOICE_API_KEY="your-api-key-here"
```

### 3. Verify setup

```bash
python check_environment.py
```

## Quick Test

```bash
# Basic TTS test
python mmvoice.py tts "Hello, this is a test." -o test.mp3
```

## Next Steps

- **Choose a voice**: See `reference/voice_catalog.md`
- **Audio processing**: See `reference/audio-guide.md`
- **Voice cloning/design**: See `reference/voice-guide.md`
- **Troubleshooting**: See `reference/troubleshooting.md`
