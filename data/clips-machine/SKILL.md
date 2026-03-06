---
name: clips-machine
description: Transform long videos into viral short-form clips. Auto-detect best moments, add trendy captions, export for TikTok/Reels/Shorts. Self-contained, no external modules. 100% free tools.
version: 1.1.0
author: Mayank8290
homepage: https://github.com/Mayank8290/openclaw-video-skills
tags: video, clips, tiktok, reels, shorts, viral, captions, transcription
metadata: { "openclaw": { "requires": { "bins": ["ffmpeg", "yt-dlp", "whisper-cpp"] } } }
---

# Clips Machine

Transform long videos into viral short-form clips. Auto-detect the best moments, add trendy captions, export for TikTok/Reels/Shorts.

**100% FREE tools** - Runs entirely on your machine.

> **Love this skill?** Support the creator and help keep it free: **[Buy Me a Coffee](https://buymeacoffee.com/mayank8290)**

## What This Skill Does

1. **Input** any long video (YouTube URL, podcast, stream, local file)
2. **Transcribe** with timestamps using Whisper (free, local)
3. **Detect** viral-worthy moments using AI analysis
4. **Cut** the best 30-60 second segments
5. **Caption** with animated, trendy text styles
6. **Export** in vertical 9:16 format ready for upload

## Quick Start

```
Turn this podcast into viral clips: https://youtube.com/watch?v=xyz
```

```
Extract the 5 best moments from my-interview.mp4 and add captions
```

## Commands

### From YouTube URL
```
/clips-machine https://youtube.com/watch?v=VIDEO_ID
```

### From Local File
```
/clips-machine /path/to/video.mp4
```

### Custom Number of Clips
```
/clips-machine VIDEO --clips 10
```

### Caption Styles
```
/clips-machine VIDEO --style [style]
```

Available styles:
- `hormozi` - Alex Hormozi style (bold, word-by-word highlight) - **Most Viral**
- `minimal` - Clean white text
- `karaoke` - Word-by-word color change
- `news` - Lower third style
- `meme` - Impact font, top/bottom

## How Viral Detection Works

The AI analyzes the transcript looking for:

1. **Hook Potential** - Strong opening statements
2. **Emotional Peaks** - Passion, excitement, surprise
3. **Quotable Lines** - Memorable one-liners
4. **Controversial Takes** - Debate-worthy opinions
5. **Surprising Facts** - "Did you know" moments
6. **Actionable Advice** - Clear takeaways

Each moment gets a "virality score" from 1-100.

## Output Structure

```
~/Videos/OpenClaw/clips-[video-name]/
├── transcript.json      # Full transcript with timestamps
├── viral_moments.json   # Detected moments with scores
├── clip_001.mp4         # First viral clip (vertical, captioned)
├── clip_002.mp4         # Second viral clip
├── clip_003.mp4         # ...
└── summary.md           # Overview of all clips
```

## Supported Sources

| Source | Example |
|--------|---------|
| YouTube | `https://youtube.com/watch?v=...` |
| TikTok | `https://tiktok.com/@user/video/...` |
| Twitter/X | `https://twitter.com/user/status/...` |
| Twitch VOD | `https://twitch.tv/videos/...` |
| Local MP4 | `/path/to/file.mp4` |

## Requirements

- FFmpeg (`brew install ffmpeg`)
- yt-dlp (`brew install yt-dlp`)
- Whisper.cpp (`brew install whisper-cpp`)

## Setup

```bash
# Install dependencies
brew install ffmpeg yt-dlp whisper-cpp

# Or on Linux
sudo apt install ffmpeg
pip install yt-dlp
# Build whisper.cpp from source
```

## Monetization

| Method | Potential |
|--------|-----------|
| Clip service for creators | $50-150/video |
| Monthly retainer | $500-2,000/client |
| Podcast clipping agency | $2,000-5,000/mo |
| Sell this skill | $100-300 on ClawHub |

## Examples

### Podcast to Clips
```
Take this 2-hour podcast and find the 10 best moments:
https://youtube.com/watch?v=PODCAST_ID
Make them Hormozi-style with bold captions.
```

### Interview Highlights
```
/clips-machine interview.mp4 --clips 5 --style minimal
```

### Gaming Stream
```
Extract funny moments from my Twitch VOD:
https://twitch.tv/videos/12345
Add meme-style captions
```

---

## Support This Project

If this skill saved you time or made you money, consider buying me a coffee!

**[Buy Me a Coffee](https://buymeacoffee.com/mayank8290)**

Every coffee helps me build more free tools for the community.

---

Built for OpenClaw | Powered by Whisper + FFmpeg | [Support the Creator](https://buymeacoffee.com/mayank8290)
