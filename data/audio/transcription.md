# Transcription Workflow

## Tools

| Tool | Use Case | Notes |
|------|----------|-------|
| **Whisper** | Local transcription | Free, accurate, many languages |
| **Whisper.cpp** | Fast local (C++ port) | Lower memory usage |
| **AssemblyAI** | API-based | Speaker diarization, paid |
| **Deepgram** | API-based | Fast, real-time capable |

---

## Whisper Local Transcription

### Install
```bash
pip install openai-whisper

# Or with conda
conda install -c conda-forge whisper
```

### Model Sizes

| Model | Size | Speed | Accuracy | VRAM |
|-------|------|-------|----------|------|
| tiny | 39M | Fastest | Lower | ~1GB |
| base | 74M | Fast | Good | ~1GB |
| small | 244M | Medium | Better | ~2GB |
| medium | 769M | Slow | Great | ~5GB |
| large | 1550M | Slowest | Best | ~10GB |
| turbo | 809M | Fast | Great | ~6GB |

**Recommendation:** Use `medium` or `turbo` for good balance.

### Basic Transcription
```bash
# Simple transcription (auto-detect language)
whisper audio.mp3 --model medium

# Specify language
whisper audio.mp3 --model medium --language en

# Output specific format
whisper audio.mp3 --model medium --output_format srt

# All formats at once
whisper audio.mp3 --model medium --output_format all
# Creates: .txt, .srt, .vtt, .json, .tsv
```

### Prepare Audio for Whisper
```bash
# Convert to 16kHz WAV (Whisper's preferred format)
ffmpeg -i input.mp3 -ar 16000 -ac 1 -acodec pcm_s16le whisper_ready.wav
```

---

## Subtitle Formats

### SRT (SubRip)
```
1
00:00:01,000 --> 00:00:04,500
This is the first subtitle line.

2
00:00:05,000 --> 00:00:08,000
This is the second line.
```

### VTT (WebVTT)
```
WEBVTT

00:00:01.000 --> 00:00:04.500
This is the first subtitle line.

00:00:05.000 --> 00:00:08.000
This is the second line.
```

### Convert Between Formats
```bash
# SRT to VTT
ffmpeg -i subtitles.srt subtitles.vtt

# VTT to SRT
ffmpeg -i subtitles.vtt subtitles.srt
```

---

## Speaker Diarization

Whisper alone doesn't identify speakers. Options:

### Option 1: pyannote.audio (Local)
```bash
pip install pyannote.audio

# Requires Hugging Face token for models
```

### Option 2: WhisperX (Whisper + diarization)
```bash
pip install whisperx

whisperx audio.mp3 --diarize --hf_token YOUR_TOKEN
```

### Option 3: AssemblyAI API
```bash
# Upload and transcribe with speakers
curl -X POST "https://api.assemblyai.com/v2/transcript" \
  -H "authorization: YOUR_API_KEY" \
  -d '{"audio_url": "URL", "speaker_labels": true}'
```

---

## Subtitle Timing Adjustments

```bash
# Shift all subtitles by 2 seconds later
ffmpeg -i subtitles.srt -itsoffset 2 subtitles_shifted.srt

# Speed up subtitles (for faster video)
# Multiply timestamps by factor (e.g., 0.5 for 2x speed)
# Requires external tool or script
```

### Python Script for Timing Adjustment
```python
import re

def shift_srt(input_file, output_file, shift_ms):
    """Shift all SRT timestamps by shift_ms milliseconds."""
    with open(input_file, 'r') as f:
        content = f.read()
    
    def shift_time(match):
        h, m, s, ms = map(int, match.groups())
        total_ms = h*3600000 + m*60000 + s*1000 + ms + shift_ms
        h = total_ms // 3600000
        m = (total_ms % 3600000) // 60000
        s = (total_ms % 60000) // 1000
        ms = total_ms % 1000
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    shifted = re.sub(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', shift_time, content)
    
    with open(output_file, 'w') as f:
        f.write(shifted)

# Usage: shift_srt('input.srt', 'output.srt', 2000)  # +2 seconds
```

---

## Burn Subtitles into Video

```bash
# Basic burn-in
ffmpeg -i video.mp4 -vf "subtitles=captions.srt" output.mp4

# Styled subtitles
ffmpeg -i video.mp4 -vf "subtitles=captions.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2'" output.mp4

# TikTok/Reels style (centered, bold)
ffmpeg -i video.mp4 -vf "subtitles=captions.srt:force_style='FontName=Arial Bold,FontSize=28,Alignment=2,MarginV=50'" output.mp4
```

---

## Transcription Quality Tips

1. **Clean audio first** — Remove noise before transcribing
   ```bash
   ffmpeg -i input.mp3 -af "highpass=f=80,lowpass=f=8000" cleaned.mp3
   whisper cleaned.mp3 --model medium
   ```

2. **Use appropriate model** — Larger models = better accuracy for unclear audio

3. **Specify language** — Don't rely on auto-detect for better results
   ```bash
   whisper audio.mp3 --language es --model medium
   ```

4. **Initial prompt for context** — Help Whisper with jargon or names
   ```bash
   whisper audio.mp3 --initial_prompt "Podcast about machine learning with hosts Alice and Bob"
   ```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Wrong language detected | Auto-detect confused | Specify `--language` |
| Hallucinations (repeated text) | Silence or noise | Clean audio, use larger model |
| Missing words | Audio too quiet | Normalize first |
| Wrong punctuation | Model limitation | Post-process transcript |
| Speaker confusion | No diarization | Use WhisperX or API |
