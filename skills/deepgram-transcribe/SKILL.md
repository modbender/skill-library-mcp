---
name: deepgram-transcribe
description: Transcribe audio via Deepgram Nova-3 API (5.26% WER, 40x faster than Whisper, built-in speaker diarization). Use when user asks to transcribe audio, podcasts, meetings, voice recordings, or voice memos. Supports mp3, wav, m4a, ogg, flac, webm, aiff. Falls back to OpenAI Whisper skill if DEEPGRAM_API_KEY is not set.
---

# Deepgram Nova-3 Transcription

Transcribe audio files using Deepgram's Nova-3 model — more accurate and faster than OpenAI Whisper.

## Why Deepgram over Whisper
- 5.26% word error rate (vs ~8-10% for Whisper)
- 40x faster for batch processing
- Built-in speaker diarization (who said what)
- Smart formatting (numbers, dates, punctuation)
- $200 free credits on signup at deepgram.com

## Setup

Store your API key:
```bash
echo "YOUR_DEEPGRAM_API_KEY" > ~/.openclaw/secrets/deepgram-api-key.txt
```

Or set the environment variable:
```bash
export DEEPGRAM_API_KEY="your-key-here"
```

## Usage

```bash
bash scripts/transcribe.sh /path/to/audio.mp3
bash scripts/transcribe.sh recording.mp3 --out transcript.txt
bash scripts/transcribe.sh recording.mp3 --json --out full.json
bash scripts/transcribe.sh recording.mp3 --language es
bash scripts/transcribe.sh recording.mp3 --model nova-2
```

## Models

| Model | WER | Cost/min | Best for |
|-------|-----|----------|----------|
| nova-3 (default) | 5.26% | $0.0077 | Best accuracy |
| nova-2 | ~8% | $0.0043 | Budget-friendly |
| whisper-large | ~8-10% | $0.0048 | Whisper parity |

## Supported Formats

mp3, wav, m4a, ogg, flac, webm, aiff

## Fallback

If `DEEPGRAM_API_KEY` is not set, use the OpenAI Whisper skill instead (if installed).
