---
name: pywayne-tts
description: Text-to-speech conversion tool. Use when converting text to speech audio files (opus or mp3 format). Supports macOS native 'say' command and Google TTS (gTTS) service with ffmpeg audio conversion.
---

# Pywayne TTS

Text-to-speech (TTS) tool that converts text to audio files (opus or mp3 format).

## Functions

### text_to_speech_output_opus - Convert text to Opus format

```python
from pywayne.tts import text_to_speech_output_opus

# Output: test.opus
text_to_speech_output_opus("你好，世界", "test.opus")
```

**Parameters:**
- `text` - Text to convert
- `opus_filename` - Output .opus filename
- `use_say` - If True, use macOS 'say' command; otherwise use gTTS (default True)

**Behavior:**
- On macOS, prefers native 'say' command when `use_say=True`
- On other platforms, uses Google TTS (gTTS) service
- Uses ffmpeg to convert audio to opus format (16kHz, mono channel)
- Automatically cleans up temporary files

### text_to_speech_output_mp3 - Convert text to MP3 format

```python
from pywayne.tts import text_to_speech_output_mp3

# Output: test.mp3
text_to_speech_output_mp3("你好，世界", "test.mp3")
```

**Parameters:**
- `text` - Text to convert
- `mp3_filename` - Output .mp3 filename
- `use_say` - If True, use macOS 'say' command; otherwise use gTTS (default True)

**Behavior:**
- On macOS, prefers native 'say' command when `use_say=True`
- On other platforms, uses Google TTS (gTTS) service
- Uses ffmpeg to convert audio to mp3 format
- Automatically cleans up temporary files

## Quick Start

```bash
# Convert text to Opus format (default: macOS uses 'say')
text_to_speech_output_opus "你好，世界" "test.opus"

# Convert text to MP3 format
text_to_speech_output_mp3 "你好，世界" "test.mp3"

# Force use gTTS instead of macOS 'say'
text_to_speech_output_mp3 "你好，世界" "test.mp3" use_say=False
```

## Requirements

- **ffmpeg**: Required for audio conversion
  - macOS: `brew install ffmpeg`
  - Windows: Download from https://ffmpeg.org and add to PATH
  - Linux: `sudo apt install ffmpeg` or package manager
- **gtts**: Python library for Google TTS service

## Platform Detection

Module automatically detects platform and prompts for ffmpeg installation if missing.

## Audio Formats

- **Opus**: Better quality, smaller file size, suitable for voice calls
- **MP3**: Better compatibility, suitable for multimedia playback

## Notes

- Requires network connection for gTTS service
- Temporary files are automatically cleaned up
- Ensure output directory has write permissions
