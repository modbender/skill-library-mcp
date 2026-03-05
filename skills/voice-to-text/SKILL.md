---
name: voice-to-text
version: 1.0.0
description: Convert voice messages and audio files to text using Vosk offline speech recognition. Use when a user sends a voice message, audio file, or asks to transcribe speech to text.
homepage: https://alphacephei.com/vosk/
metadata:
  {
    "openclaw":
      {
        "emoji": "🎤",
        "os": ["darwin", "linux"],
        "requires": { "bins": ["ffmpeg"], "python": ["vosk"] },
        "install":
          [
            {
              "id": "brew-ffmpeg",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install ffmpeg via Homebrew",
            },
            {
              "id": "pip-vosk",
              "kind": "pip",
              "package": "vosk",
              "label": "Install Vosk via pip",
            },
          ],
      },
  }
---

# Voice to Text

Convert voice messages and audio files to text using Vosk, an offline speech recognition toolkit.

## Setup

1. Install dependencies:
   ```bash
   # macOS
   brew install ffmpeg
   pip install vosk

   # Linux
   apt-get install ffmpeg
   pip install vosk
   ```

2. Download a Vosk model:
   ```bash
   mkdir -p ~/.vosk/models && cd ~/.vosk/models

   # Chinese (small, fast)
   curl -LO https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip
   unzip vosk-model-small-cn-0.22.zip

   # English (small)
   curl -LO https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   ```

## Usage

When the user provides a voice message or audio file path, run the transcription:

```bash
python3 ~/skills/voice-to-text/transcribe.py "<audio_file_path>"
```

For specific model selection, set the environment variable:
```bash
VOSK_MODEL_PATH=~/.vosk/models/vosk-model-cn-0.22 python3 ~/skills/voice-to-text/transcribe.py "<audio_file_path>"
```

## Supported Audio Formats

- MP3, WAV, M4A, OGG, FLAC, AAC, WEBM
- Voice messages from WeChat, Telegram, WhatsApp, etc.

## Available Models

| Model | Language | Size | Notes |
|-------|----------|------|-------|
| vosk-model-small-cn-0.22 | Chinese | 42M | Fast, good accuracy |
| vosk-model-cn-0.22 | Chinese | 1.3G | High accuracy |
| vosk-model-small-en-us-0.15 | English | 40M | Fast, good accuracy |
| vosk-model-en-us-0.22 | English | 1.8G | High accuracy |

Download models from: https://alphacephei.com/vosk/models

## Example Workflow

1. User sends a voice message via WeChat/Telegram
2. OpenClaw receives the audio file
3. Run: `python3 transcribe.py /path/to/voice.ogg`
4. Return transcribed text to user

## Troubleshooting

- **No model found**: Download a model to `~/.vosk/models/`
- **ffmpeg not found**: Install via `brew install ffmpeg` or `apt install ffmpeg`
- **Poor accuracy**: Try a larger model for better results

## Notes

- Works completely offline after model download
- Supports multiple languages (download appropriate model)
- Audio is converted to 16kHz mono WAV for processing
