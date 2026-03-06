---
name: video-to-text
description: Video to text converter. Downloads videos from Bilibili using bilibili-api, from other sites using yt-dlp, then transcribes audio using faster-whisper. Use when you need to convert video content (B站/YouTube/local files) into text transcripts or subtitles.
---

# Video to Text

Convert video URLs or local files to text transcripts.

## Usage

```bash
python3 scripts/video_to_text.py <video_url_or_local_file> [options]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| url | Video URL or local file path (required) | - |
| -m, --model | Whisper model size | base |
| -l, --language | Specify language code | Auto-detect |
| -o, --output | Output file path | Print to terminal |
| --keep-files | Keep downloaded audio/video files | No |
| --sessdata | Bilibili SESSDATA | From config |
| --bili-jct | Bilibili bili_jct | From config |
| --buvid3 | Bilibili buvid3 | From config |

## Model Selection

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | ~75MB | Fastest | Lowest |
| base | ~150MB | Fast | Basic |
| small | ~500MB | Medium | Good |
| medium | ~1.5GB | Slow | Very Good |
| large | ~3GB | Slowest | Best |

## Examples

```bash
# Bilibili video (requires auth)
python3 scripts/video_to_text.py "https://www.bilibili.com/video/BVxxx"

# Specify Chinese language
python3 scripts/video_to_text.py "https://www.bilibili.com/video/BVxxx" -l zh

# Local file
python3 scripts/video_to_text.py "/path/to/video.mp4" -m small

# Save to file
python3 scripts/video_to_text.py "https://www.bilibili.com/video/BVxxx" -o result.txt
```

## Supported Platforms

- Bilibili (bilibili.com) - Requires auth
- YouTube - via yt-dlp
- TikTok/Douyin - via yt-dlp
- Twitter/X - via yt-dlp
- Any site supported by yt-dlp
- Local files - supports mp4, wav, m4a, webm, mkv, etc.

## Bilibili Auth Setup

### Method 1: Config File

Edit BILIBILI_CREDENTIALS dict in the script:

```python
BILIBILI_CREDENTIALS = {
    "sessdata": "your_sessdata",
    "bili_jct": "your_bili_jct",
    "buvid3": "your_buvid3"
}
```

### Method 2: Command Line

```bash
python3 scripts/video_to_text.py "https://www.bilibili.com/video/BVxxx" \
    --sessdata "xxx" \
    --bili-jct "xxx" \
    --buvid3 "xxx"
```

### How to Get Auth Info

1. Login to Bilibili web (bilibili.com)
2. Press F12 to open Developer Tools
3. Application -> Cookies -> bilibili.com
4. Copy these values:
   - SESSDATA
   - bili_jct
   - buvid3

WARNING: These are your login credentials. Don't share with others!

## Installation

```bash
# Install dependencies
pip3 install bilibili-api-python yt-dlp faster-whisper aiohttp requests

# Ensure ffmpeg is installed
# Ubuntu/Debian: sudo apt install ffmpeg
# CentOS: sudo yum install ffmpeg
```

## Dependencies

- bilibili-api-python - Bilibili API
- yt-dlp - Video download
- ffmpeg - Audio/video processing
- faster-whisper - Speech transcription
- aiohttp - Async HTTP
- requests - HTTP requests
