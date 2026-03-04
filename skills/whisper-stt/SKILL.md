---
name: whisper-stt
description: |
  Free local speech-to-text transcription using OpenAI Whisper.
  Transcribe audio files (mp3, wav, m4a, ogg, etc.) to text without API costs.
  Use when: (1) User needs audio/video transcription, (2) Converting voice memos to text,
  (3) Generating subtitles (SRT/VTT), (4) Free local STT without cloud API costs.
---

# Whisper STT Skill

Free, local speech-to-text using OpenAI Whisper.

## Prerequisites

Install dependencies (one-time setup):

```bash
pip install openai-whisper torch
```

Optional: Install ffmpeg for broader format support:
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`

## Usage

### Transcribe an audio file

```bash
python ~/.openclaw/skills/whisper-stt/scripts/transcribe.py <audio_file>
```

### Options

| Option | Description |
|--------|-------------|
| `--model` | Model size: tiny, base, small, medium, large, large-v3-turbo (default: base) |
| `--language, -l` | Language code: zh, en, ja, etc. (auto-detect if not specified) |
| `--output, -o` | Output format: json, txt, srt, vtt (default: json) |

### Examples

**Chinese audio to text:**
```bash
python ~/.openclaw/skills/whisper-stt/scripts/transcribe.py recording.m4a --language zh --output txt
```

**Generate subtitles (SRT):**
```bash
python ~/.openclaw/skills/whisper-stt/scripts/transcribe.py video.mp4 --output srt > subtitles.srt
```

**Use faster model:**
```bash
python ~/.openclaw/skills/whisper-stt/scripts/transcribe.py audio.mp3 --model tiny --output txt
```

**High accuracy (slower):**
```bash
python ~/.openclaw/skills/whisper-stt/scripts/transcribe.py audio.mp3 --model large-v3 --output txt
```

## Model Selection Guide

| Model | Speed | Accuracy | VRAM/RAM | Best For |
|-------|-------|----------|----------|----------|
| tiny | ~32x | Basic | ~1GB | Quick tests, low resource |
| base | ~16x | Good | ~1GB | Balanced speed/accuracy |
| small | ~6x | Better | ~2GB | Better accuracy |
| medium | ~2x | Very Good | ~5GB | High accuracy |
| large | 1x | Excellent | ~10GB | Best quality |
| large-v3-turbo | ~8x | Excellent | ~6GB | Fast + accurate (recommended) |

## Troubleshooting

**"ModuleNotFoundError: No module named 'whisper'"**
→ Run: `pip install openai-whisper torch`

**"ffmpeg not found"**
→ Install ffmpeg or convert audio to WAV format first

**Slow transcription**
→ Use smaller model (tiny/base) or ensure GPU is available (Apple Silicon MPS, NVIDIA CUDA)

**Poor accuracy on Chinese**
→ Use `--language zh` explicitly and consider larger model (medium/large)

## Output Formats

- **json**: Full result with segments, timestamps, and metadata
- **txt**: Plain text transcription only
- **srt**: SubRip subtitle format with timing
- **vtt**: WebVTT subtitle format for web players

## Credits

Powered by [OpenAI Whisper](https://github.com/openai/whisper) - open source speech recognition.
