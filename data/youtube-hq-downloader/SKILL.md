---
name: youtube-hq-downloader
description: Youtube Highest Quality Downloader - Download highest quality silent video and pure audio from YouTube, then merge into video with sound
---

# YouTube Highest Quality Downloader

Download the highest quality silent video and pure audio from YouTube, then merge into a video with sound using ffmpeg.
从YouTube下载视频的最高清无声版本和纯音频，然后使用ffmpeg合并为有声视频。

## Features / 功能

- 🎬 Download highest quality silent video from YouTube (bestvideo) / 下载YouTube视频最高清无声版本
- 🎵 Download pure audio from YouTube (bestaudio) / 下载YouTube视频纯音频
- 🔧 Merge video and audio using ffmpeg / 使用ffmpeg合并视频和音频
- 🖥️ Runs independently, no dependencies on other skills / 独立运行，无需依赖其他技能

## Usage / 使用方法

### Quick Start

```bash
# Run the download script directly
python3 ~/clawd/skills/youtube-hq-downloader/download.py "YouTube_URL" [output_directory]
```

### Full Workflow

```bash
# 1. Enter the skill directory
cd ~/clawd/skills/youtube-hq-downloader

# 2. Create virtual environment (first run)
python3 -m venv .venv
source .venv/bin/activate
pip install yt-dlp

# 3. Run download and merge
python3 download.py "https://www.youtube.com/watch?v=xxxxx"

# Or run step by step manually
./download.sh "YouTube_URL"
```

### Manual Commands

```bash
# Activate environment
cd ~/clawd/skills/youtube-hq-downloader
source .venv/bin/activate

# Download video (highest quality, silent)
yt-dlp -f "bestvideo[ext=mp4]" "YouTube_URL" -o "%(title)s_video.%(ext)s"

# Download audio
yt-dlp -x --audio-format m4a "YouTube_URL" -o "%(title)s_audio.%(ext)s"

# Merge video and audio
ffmpeg -i "*.mp4" -i "*.m4a" -c:v copy -c:a aac -shortest "output.mp4" -y
```

## Parameters / 参数说明

### yt-dlp Video Download
- `-f "bestvideo"`: Download highest quality video format (may be WebM or MP4)
- Output template: `%(title)s_video.%(ext)s`

### yt-dlp Audio Download
- `-x`: Extract audio
- `--audio-format m4a`: Output as M4A format

### ffmpeg Merge
- `-i "video.mp4" -i "audio.m4a"`: Input files
- `-c:v copy`: Copy video stream, no re-encoding
- `-c:a aac`: Convert audio to AAC encoding
- `-shortest`: Use shorter duration
- `-y`: Overwrite output file

## Dependencies / 依赖

- **ffmpeg**: Video processing tool (macOS: `brew install ffmpeg`)
- **Python 3.8+**: Runtime environment
- **yt-dlp**: Will be auto-installed on first run

## Auto Install / 自动安装

The script will automatically detect and use system-installed yt-dlp. If not found:

```bash
# Manual install yt-dlp
pip install yt-dlp

# Or use uv
pip install uv && uv pip install yt-dlp
```

## FAQ / 常见问题

### Q: Downloaded video has no sound?
A: This is normal. Using `bestvideo` only downloads the video track. You need to download audio separately and merge.

### Q: Video resolution is too low?
A: YouTube may have regional or quality restrictions on certain videos. Try other formats like `best` instead of `bestvideo`.

### Q: ffmpeg error "No such file"?
A: Make sure ffmpeg is installed: `brew install ffmpeg`

### Q: How to specify output directory?
A: Pass the second parameter as output directory when running the script, or modify the OUTPUT_DIR variable in the script.
