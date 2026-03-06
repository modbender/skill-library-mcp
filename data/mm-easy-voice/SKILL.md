---
name: mm-easy-voice
description: Simple text-to-speech skill using MiniMax Voice API. Converts text to audio with customizable voice selection. Use for generating speech audio from text.
---

# MiniMax Easy Voice

Simple text-to-speech skill powered by MiniMax Voice API. Converts any text into natural-sounding audio with customizable voice selection.


## Usage
### [Step 1] Preparation

**IMPORTANT:** Before using this skill, always verify the environment:

```bash
python check_environment.py
```

**If API key is not set:**
```bash
export MINIMAX_VOICE_API_KEY="your-api-key-here"
```

**Requirements:**
- Python 3.8+
- MINIMAX_VOICE_API_KEY environment variable (required)
- FFmpeg (optional, for audio merging/conversion)


### [Step 2] Generate speech audio from text

Convert any text to speech in one command:

```bash
# Default voice (male-qn-qingse)
python mmvoice.py tts "Hello, this is a test." -o test.mp3

# Chinese text
python mmvoice.py tts "你好，这是一个测试。" -o test_cn.mp3

# Specify a different voice by "-v voice_id"
python mmvoice.py tts "Hello world" -v female-shaonv -o hello.mp3

# Specify output path
python mmvoice.py tts "Your text" -o /path/to/output.mp3
```

**Required parameters:**
- `text`: The text you want to convert to speech
- `-o OUTPUT`: Output audio file path (required)

**Optional parameters:**
- `-v VOICE_ID`: Voice to use (default: male-qn-qingse)


### Usage Details

**Text length limits:**
- Up to 10,000 characters per request
- For longer text, split into multiple requests and merge later

**Pause insertion:** Use `<#x#>` where x = pause duration in seconds
- Example: `"Hello<#1.5#>world"` = 1.5 second pause between words
- Range: 0.01 to 99.99 seconds

**Emotion matching:** speech-2.8 models automatically match emotions to your text content



## Voice Selection

Choose the right voice for your content by consulting the voice catalog:

```bash
# List all available voices
python mmvoice.py list-voices
```

**Voice catalog:** `reference/voice_catalog.md`

Contains:
- All available system voices (male, female)
- Voice characteristics and recommended use cases
- How to select the right voice for your content


## Advanced Options

### Voice Management

**List available voices:**
```bash
python mmvoice.py list-voices
```

**Clone a voice from audio sample:**
```bash
python mmvoice.py clone audio_file.mp3 --voice-id my-custom-voice
```

**Design a voice from description:**
```bash
python mmvoice.py design "A warm, gentle female voice" --voice-id designed-voice
```


### Audio Processing

**Merge multiple audio files:**
```bash
python mmvoice.py merge file1.mp3 file2.mp3 file3.mp3 -o combined.mp3
```

**Convert audio format:**
```bash
python mmvoice.py convert input.wav -o output.mp3 --format mp3
```


## Reference Documents

Open these when needed for more details:

|| Document | When to Use |
||----------|-------------|
|| `reference/voice_catalog.md` | Choosing a voice_id |
|| `reference/getting-started.md` | Environment setup |
|| `reference/audio-guide.md` | Audio processing |
|| `reference/voice-guide.md` | Voice cloning and design |
|| `reference/troubleshooting.md` | Common issues and solutions |


## Troubleshooting

Common issues:

1. **API key not set:** Run `export MINIMAX_VOICE_API_KEY="your-key"`
2. **FFmpeg missing:** Install with `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Ubuntu)
3. **Voice not found:** Use `python mmvoice.py list-voices` to see available voices

Run environment check:
```bash
python check_environment.py
```

See `reference/troubleshooting.md` for more solutions.
