---
name: video-intel
description: >
  Download videos and get transcripts, summaries, or metadata from YouTube, TikTok, Instagram, and X (Twitter).
  Use when the user shares a video URL and wants a transcript, summary, key points, quotes, or to download the video.
  Triggers on phrases like "transcript this video", "summarize this YouTube video", "what does this video say",
  "download this TikTok", "get captions from", or any video URL from youtube.com, youtu.be, tiktok.com, instagram.com, x.com, twitter.com.
  Requires: yt-dlp, python3, curl. Optional: ffmpeg (for TikTok/Instagram/X audio), OPENAI_API_KEY (Whisper fallback — uploads audio to OpenAI).
---

# video-intel

Downloads videos and extracts transcripts using `yt-dlp` (captions) with OpenAI Whisper fallback.

## Required Dependencies

| Dependency | Purpose | Required? |
|---|---|---|
| `yt-dlp` | Fetch captions and download audio/video | ✅ Always |
| `python3` | Parse VTT/SRT caption files | ✅ Always |
| `curl` | Call OpenAI Whisper API | ✅ For Whisper fallback |
| `ffmpeg` | Extract audio from TikTok/Instagram/X | ⚠️ Non-YouTube only |
| `OPENAI_API_KEY` | Authenticate with OpenAI Whisper API | ⚠️ Only if captions unavailable |

Install binaries:
```bash
# yt-dlp
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/bin/yt-dlp && chmod +x ~/bin/yt-dlp

# ffmpeg (Debian/Ubuntu)
sudo apt install ffmpeg
```

## ⚠️ Privacy Notice — OpenAI Audio Upload

When captions are unavailable (common for TikTok, Instagram, X), the script **downloads the audio and uploads it to OpenAI's transcription API** (`https://api.openai.com/v1/audio/transcriptions`). This means:

- Audio content leaves your machine and is sent to OpenAI
- Requires `OPENAI_API_KEY` to be set
- If you don't want external transmission: don't set `OPENAI_API_KEY`, or use a local transcription model

YouTube videos almost always have captions and will **not** trigger an upload.

## Script

```
~/.openclaw/skills/video-intel/scripts/video-intel.sh
```

## Workflows

### Get transcript
```bash
~/.openclaw/skills/video-intel/scripts/video-intel.sh transcript <url>
```
- YouTube: uses built-in captions/auto-subs (fast, no audio download or external upload)
- TikTok/Instagram/X: downloads audio → uploads to OpenAI Whisper for transcription
- Preferred language: `--lang pt` for Portuguese

### Get video info
```bash
~/.openclaw/skills/video-intel/scripts/video-intel.sh info <url>
```

### List available caption tracks
```bash
~/.openclaw/skills/video-intel/scripts/video-intel.sh captions <url>
```

### Download video
```bash
~/.openclaw/skills/video-intel/scripts/video-intel.sh download <url> [--format audio|720p|best]
```

## After getting transcript

- **Summary**: Summarize in 3-5 bullet points
- **Key quotes**: Extract most notable quotes
- **Full summary**: Write a paragraph summary with context
- **Translation**: Translate to the user's language if different

## Notes

- YouTube auto-captions are usually available even without ffmpeg
- TikTok/Instagram/X require ffmpeg for audio extraction
- Large videos (>25MB audio) may hit OpenAI's file size limit — use `--format audio` to get a smaller mp3
- Output cached in `/tmp/video-intel/` by default
