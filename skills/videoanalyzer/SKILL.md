---
name: video-watcher
description: Download videos, extract transcripts, capture frames. Analyze YouTube, tutorials, DD videos with yt-dlp + Whisper + ffmpeg.
metadata: {"clawdbot":{"requires":{"bins":["yt-dlp","ffmpeg","whisper"]}}}
---

# Video Watcher

Download, transcribe, and screenshot videos for analysis.

## Requirements

```bash
brew install yt-dlp ffmpeg openai-whisper
```

## Quick Start

```bash
./scripts/analyze.sh "https://youtube.com/watch?v=..."
```

## Output

```
outputs/
├── video.mp4           # Downloaded video
├── audio.mp3           # Extracted audio
├── transcript.txt      # Plain text
├── transcript.srt      # Subtitles
└── frames/             # Screenshots every 30s
```

## Commands

### Analyze video
```bash
./scripts/analyze.sh "URL" [output-dir] [frame-interval] [whisper-model]
```

### Summarize transcript
```bash
./scripts/summarize.sh ./outputs/transcript.txt
```

Or with AI:
```bash
cat outputs/transcript.txt | clawdbot ask "Summarize this"
```

## Config

`config.json`:
```json
{
  "whisper_model": "medium",
  "frame_interval": 30,
  "output_dir": "./outputs"
}
```

## Use Cases

- DD (Due Diligence) videos
- Lecture notes
- Podcast summaries
- Tutorial documentation
- Meeting recordings
