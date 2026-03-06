---
name: video-watcher
description: Fetch and read transcripts from YouTube and Bilibili videos. Use when you need to summarize a video, answer questions about its content, or extract information from it.
author: adapted from youtube-watcher
version: 1.1.0
triggers:
  - "watch video"
  - "summarize video"
  - "video transcript"
  - "youtube summary"
  - "bilibili summary"
  - "analyze video"
metadata: {"clawdbot":{"emoji":"📺","requires":{"bins":["yt-dlp"]},"install":[{"id":"brew","kind":"brew","formula":"yt-dlp","bins":["yt-dlp"],"label":"Install yt-dlp (brew)"},{"id":"pip","kind":"pip","package":"yt-dlp","bins":["yt-dlp"],"label":"Install yt-dlp (pip)"}]}}
---

# Video Watcher

Fetch transcripts from **YouTube** and **Bilibili** videos to enable summarization, QA, and content extraction.

## Supported Platforms

- ✅ **YouTube** (youtube.com, youtu.be)
- ✅ **Bilibili** (bilibili.com, b23.tv)

## Usage

### Get Transcript (Auto-detect Platform)

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL"
```

### Specify Language

```bash
python3 {baseDir}/scripts/get_transcript.py "VIDEO_URL" --lang zh-CN
```

## Examples

### YouTube Video
```bash
python3 {baseDir}/scripts/get_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Bilibili Video
```bash
python3 {baseDir}/scripts/get_transcript.py "https://www.bilibili.com/video/BV1xx411c7mD"
```

### With Custom Language
```bash
# Get English subtitles for a Bilibili video
python3 {baseDir}/scripts/get_transcript.py "https://bilibili.com/video/..." --lang en

# Get Chinese subtitles for a YouTube video
python3 {baseDir}/scripts/get_transcript.py "https://youtube.com/watch?v=..." --lang zh-CN
```

## Default Languages

| Platform | Default Language |
|----------|-----------------|
| YouTube  | `en` (English)  |
| Bilibili | `zh-CN` (Chinese) |

## Common Language Codes

- `en` - English
- `zh-CN` - Simplified Chinese (简体中文)
- `zh-TW` - Traditional Chinese (繁體中文)
- `ja` - Japanese
- `ko` - Korean
- `es` - Spanish
- `fr` - French
- `de` - German

## Notes

- Requires `yt-dlp` to be installed and available in PATH
- Works with videos that have closed captions (CC) or auto-generated subtitles
- Automatically detects platform from URL
- If no subtitles available, the script will fail with an error message
- yt-dlp natively supports both YouTube and Bilibili
