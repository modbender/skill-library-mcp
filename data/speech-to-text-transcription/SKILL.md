---
name: Speech to Text Transcription
slug: speech-to-text-transcription
version: 1.0.0
homepage: https://clawic.com/skills/speech-to-text-transcription
description: Transcribe audio and video files to text with speaker detection, timestamps, and format conversion.
metadata: {"clawdbot":{"emoji":"🎤","requires":{"bins":["ffmpeg"]},"os":["linux","darwin","win32"]}}
changelog: Initial release with multi-provider support and batch processing.
---

## Setup

On first use, read `setup.md` and start helping with transcription needs.

## When to Use

User has audio or video files that need transcription. Agent handles local files, URLs, voice memos, podcasts, interviews, meetings, and lectures.

## Architecture

Memory lives in `~/speech-to-text-transcription/`. See `memory-template.md` for structure.

```
~/speech-to-text-transcription/
├── memory.md        # Provider preferences, defaults
├── transcripts/     # Saved transcriptions
└── temp/            # Processing workspace
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. Detect File Type First
Before transcription, identify the input:
- Local file path → verify exists, check format
- URL → download to temp, then process
- Meeting recording → likely needs speaker diarization
- Voice memo → usually single speaker, shorter

### 2. Choose Provider Based on Context
| Scenario | Best Provider | Why |
|----------|---------------|-----|
| Quick local transcription | Whisper (local) | No API key, free, private |
| High accuracy needed | OpenAI Whisper API | Best quality |
| Speaker identification | AssemblyAI | Native diarization |
| Real-time/streaming | Deepgram | Low latency |
| Long content (>2 hours) | Split + batch | Avoid timeouts |

### 3. Handle Long Audio
Files over 25MB or 2 hours:
1. Split into chunks (use ffmpeg)
2. Process each chunk
3. Merge transcripts with proper timestamps
4. Never attempt single upload for large files

### 4. Preserve Context
After transcription:
- Ask if user wants the transcript saved
- Suggest filename based on content
- Offer to extract action items or summary

### 5. Output Formats
Default to plain text. Offer alternatives:
- `.txt` — clean text, no timestamps
- `.srt` / `.vtt` — subtitles with timing
- `.json` — structured with word-level timing
- `.md` — formatted with speaker labels

## Common Traps

- **Assuming one provider works for all** → Whisper fails on diarization, AssemblyAI needs API key
- **Uploading huge files directly** → Timeouts, memory errors. Split first.
- **Ignoring audio quality** → Noisy audio needs preprocessing (ffmpeg noise reduction)
- **Not checking language** → Whisper auto-detects but can fail on mixed-language content
- **Losing speaker context** → Multi-speaker content without diarization becomes unusable

## Requirements

**Required:** ffmpeg (for audio processing)

**Optional API keys (only if using cloud providers):**
- `OPENAI_API_KEY` — for OpenAI Whisper API
- `ASSEMBLYAI_API_KEY` — for AssemblyAI (speaker diarization)
- `DEEPGRAM_API_KEY` — for Deepgram (real-time)

Local Whisper works without any API keys.

## Provider Quick Reference

### Local Whisper (No API Key)
```bash
# Install
pip install openai-whisper

# Basic transcription
whisper audio.mp3 --model base --output_format txt

# With timestamps
whisper audio.mp3 --model medium --output_format srt
```

Models: `tiny` (fast) → `base` → `small` → `medium` → `large` (accurate)

### OpenAI Whisper API
```bash
curl -X POST https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@audio.mp3" \
  -F model="whisper-1"
```

### AssemblyAI (Speaker Diarization)
```bash
# Upload
curl -X POST https://api.assemblyai.com/v2/upload \
  -H "Authorization: $ASSEMBLYAI_API_KEY" \
  --data-binary @audio.mp3

# Transcribe with speakers
curl -X POST https://api.assemblyai.com/v2/transcript \
  -H "Authorization: $ASSEMBLYAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"audio_url": "URL", "speaker_labels": true}'
```

## Audio Preprocessing

### Extract Audio from Video
```bash
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

### Reduce Noise
```bash
ffmpeg -i noisy.wav -af "afftdn=nf=-25" clean.wav
```

### Split Long Audio
```bash
# Split into 10-minute chunks
ffmpeg -i long.mp3 -f segment -segment_time 600 -c copy chunk_%03d.mp3
```

## Security & Privacy

**Data that stays local:**
- Transcripts in ~/speech-to-text-transcription/transcripts/
- Local Whisper processes entirely on-device

**Data that leaves your machine (if using APIs):**
- Audio file sent to chosen provider (OpenAI, AssemblyAI, Deepgram)
- Transcript returned and stored locally

**This skill does NOT:**
- Store API keys in plain text (use environment variables)
- Auto-upload without confirmation
- Retain files on external servers after processing

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| api.openai.com/v1/audio | Audio file | Whisper API transcription |
| api.assemblyai.com/v2 | Audio file | AssemblyAI transcription |
| api.deepgram.com/v1 | Audio stream | Deepgram transcription |

Only called when user explicitly chooses cloud provider. Local Whisper sends nothing.

## Trust

By using cloud transcription providers, audio data is sent to OpenAI, AssemblyAI, or Deepgram. Only install if you trust these services with your audio. For sensitive content, use local Whisper.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `audio` — General audio processing
- `ffmpeg` — Video and audio conversion
- `podcast` — Podcast creation and editing

## Feedback

- If useful: `clawhub star speech-to-text-transcription`
- Stay updated: `clawhub sync`
