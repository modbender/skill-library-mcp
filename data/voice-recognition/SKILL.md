---
name: voice-recognition
description: Local speech-to-text with OpenAI Whisper CLI. Supports Chinese, English, 100+ languages with translation and summarization.
version: 1.0.0
---

# Voice Recognition (Whisper)

Local speech-to-text with OpenAI Whisper CLI.

## Features

- **Local processing** - No API key needed, free
- **Multi-language** - Chinese, English, 100+ languages
- **Translation** - Translate to English
- **Summarization** - Generate quick summary

## Usage

### Basic

```bash
# Chinese recognition
python3 /Users/liyi/.openclaw/workspace/scripts/voice识别_升级版.py audio.m4a

# Force Chinese
python3 /Users/liyi/.openclaw/workspace/scripts/voice识别_升级版.py audio.m4a --zh

# English recognition  
python3 /Users/liyi/.openclaw/workspace/scripts/voice识别_升级版.py audio.m4a --en

# Translate to English
python3 /Users/liyi/.openclaw/workspace/scripts/voice识别_升级版.py audio.m4a --translate

# With summary
python3 /Users/liyi/.openclaw/workspace/scripts/voice识别_升级版.py audio.m4a --summarize
```

### Quick Command (add to ~/.zshrc)

```bash
alias voice="python3 /Users/liyi/.openclaw/workspace/scripts/voice识别_升级版.py"
```

Then use:

```bash
voice ~/Downloads/audio.m4a --zh
```

## Requirements

- OpenAI Whisper CLI: `brew install openai-whisper`
- Python 3.10+

## Files

- `scripts/voice识别_升级版.py` - Main script
- `scripts/voice_tool_README.md` - Documentation

## Supported Formats

- MP3, M4A, WAV, OGG, FLAC, WebM

## Language Support

100+ languages including:
- Chinese (zh)
- English (en)
- Japanese (ja)
- Korean (ko)
- And more...

## Notes

- Default model: `medium` (balance of speed and accuracy)
- First run downloads model to `~/.cache/whisper`
- Processing time varies by audio length and model size
