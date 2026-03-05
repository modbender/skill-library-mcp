# Edge-TTS Skill Distribution

## Overview

This document provides information for distributing the Edge-TTS skill package.

## Package Contents

- `SKILL.md` - Complete skill documentation
- `scripts/` - Python scripts for TTS conversion and configuration

## Installation Requirements

### System Requirements

- Python 3.8+
- Internet connection for TTS service

### Dependencies

- `edge-tts` - Microsoft Edge TTS service wrapper (Python)

## Installation

```bash
pip install edge-tts
```

## Usage

### Basic TTS

```bash
python3 scripts/tts_converter.py "Hello, world!" -o output.mp3
```

### Advanced Usage

```bash
# Convert text with custom voice
python3 scripts/tts_converter.py "Hello, world!" --voice en-US-GuyNeural -o output.mp3

# Read from file
python3 scripts/tts_converter.py -f input.txt -v zh-CN-XiaoxiaoNeural -o output.mp3

# List available voices
python3 scripts/tts_converter.py --list-voices

# Filter voices by language
python3 scripts/tts_converter.py --list-voices --lang-filter zh

# Configure default settings
python3 scripts/config_manager.py --set voice en-US-AriaNeural
```

## Testing

```bash
# Test TTS conversion
python3 scripts/tts_converter.py "This is a test." -o test.mp3

# Verify voice list
python3 scripts/tts_converter.py --list-voices --lang-filter en

# Check configuration
python3 scripts/config_manager.py --get
```

## Voice Testing

Test different voices and preview audio quality at: https://tts.travisvn.com/

## License

MIT License
