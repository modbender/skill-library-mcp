---
name: lh-edge-tts
description: |
  Text-to-speech conversion using Python edge-tts for generating audio from text.
  Supports multiple voices, languages, speed adjustment, pitch control, and subtitle generation.
  Use when: (1) User requests audio/voice output with the "tts" trigger or keyword. (2) Content needs to be spoken rather than read (multitasking, accessibility, driving, cooking). (3) User wants a specific voice, speed, pitch, or format for TTS output.
---

# Edge-TTS Skill

## Overview

Generate high-quality text-to-speech audio using Microsoft Edge's neural TTS service via Python edge-tts. Supports multiple languages, voices, adjustable speed/pitch, and subtitle generation (SRT/VTT).

## Quick Start

When you detect TTS intent from triggers or user request:

1. **Call the tts tool** (Clawdbot built-in) to convert text to speech
2. The tool returns a MEDIA: path
3. Clawdbot routes the audio to the current channel

## Trigger Detection

Recognize "tts" keyword as TTS requests. The skill automatically filters out TTS-related keywords from text before conversion.

## Advanced Customization

### Using the Python Scripts

For more control, use the bundled scripts directly:

#### TTS Converter
```bash
cd scripts
python3 tts_converter.py "Your text" --voice en-US-AriaNeural --rate +10% -o output.mp3
python3 tts_converter.py -f input.txt --voice zh-CN-XiaoxiaoNeural -o output.mp3
python3 tts_converter.py -f input.txt -v zh-CN-YunxiNeural -r "+10%" -o output.mp3 -s output.vtt
```

**Options:**
- `--voice, -v`: Voice name (default: en-US-MichelleNeural)
- `--lang, -l`: Language code (e.g., en-US, zh-CN)
- `--rate, -r`: Rate adjustment (e.g., +10%, -20%)
- `--volume`: Volume adjustment (e.g., +0%, -50%)
- `--pitch`: Pitch adjustment (e.g., +0Hz, -10Hz)
- `--output, -o`: Output file path (default: temp file)
- `--subtitles, -s`: Save subtitles to file (.vtt or .srt)
- `--file, -f`: Read text from file
- `--proxy, -p`: Proxy URL
- `--timeout`: Receive timeout in seconds (default: 60)
- `--list-voices, -L`: List available voices
- `--lang-filter`: Filter voices by language (used with --list-voices)

#### Configuration Manager
```bash
cd scripts
python3 config_manager.py --set voice zh-CN-XiaoxiaoNeural
python3 config_manager.py --set rate "+10%"
python3 config_manager.py --get
python3 config_manager.py --reset
```

### Voice Selection

Common voices (use `--list-voices` for full list):

**English:**
- `en-US-MichelleNeural` (female, natural, **default**)
- `en-US-AriaNeural` (female, natural)
- `en-US-GuyNeural` (male, natural)
- `en-GB-SoniaNeural` (female, British)
- `en-GB-RyanNeural` (male, British)

**Chinese:**
- `zh-CN-XiaoxiaoNeural` (female)
- `zh-CN-YunyangNeural` (male, news style)
- `zh-CN-YunxiNeural` (male, natural)

**Other Languages:**
- `es-ES-ElviraNeural` (Spanish)
- `fr-FR-DeniseNeural` (French)
- `de-DE-KatjaNeural` (German)
- `ja-JP-NanamiNeural` (Japanese)
- `ar-SA-ZariyahNeural` (Arabic)

### Rate Guidelines

Rate values use percentage format:
- `"+0%"`: Normal speed (default)
- `"-20%"` to `"-10%"`: Slow, clear (tutorials, stories, accessibility)
- `"+10%"` to `"+20%"`: Slightly fast (summaries)
- `"+30%"` to `"+50%"`: Fast (news, efficiency)

## Resources

### scripts/tts_converter.py
Main TTS conversion script using edge-tts. Generates audio files with customizable voice, rate, volume, pitch. Supports subtitle generation (VTT/SRT) and voice listing.

### scripts/config_manager.py
Manages persistent user preferences for TTS settings. Stores config in `~/.tts-config.json`.

### Voice Testing
Test different voices and preview audio quality at: https://tts.travisvn.com/

## Installation

```bash
pip install edge-tts
```

## Workflow

1. **Detect intent**: Check for "tts" trigger or keyword in user message
2. **Choose method**: Use built-in `tts` tool for simple requests, or `scripts/tts_converter.py` for customization
3. **Generate audio**: Convert the target text
4. **Return to user**: The tts tool returns a MEDIA: path; Clawdbot handles delivery

## Testing

### Basic Test
```bash
cd scripts
python3 tts_converter.py "Hello, this is a test." -o test-output.mp3
```

### Chinese Test
```bash
python3 tts_converter.py "这是一个测试" -v zh-CN-XiaoxiaoNeural -o test-zh.mp3
```

### List Voices
```bash
python3 tts_converter.py --list-voices --lang-filter zh
```

### Configuration Test
```bash
python3 config_manager.py --get
python3 config_manager.py --set voice en-US-GuyNeural
python3 config_manager.py --get voice
```

## Notes

- edge-tts uses Microsoft Edge's online TTS service
- No API key needed (free service)
- Output is MP3 format by default
- Requires internet connection
- Supports subtitle generation (standard VTT/SRT format)
- **Temporary File Handling**: By default, audio files are saved to the system's temporary directory with unique filenames. Specify a custom output path with `--output` for permanent storage.
- **TTS keyword filtering**: Automatically filters out TTS-related keywords from text before conversion
- Neural voices (ending in `Neural`) provide higher quality
