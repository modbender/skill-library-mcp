# Video Watcher

Universal transcript fetcher for **YouTube** and **Bilibili** videos.

## Features

- ✅ **YouTube Support** - youtube.com, youtu.be
- ✅ **Bilibili Support** - bilibili.com, b23.tv
- ✅ **Auto Platform Detection** - Automatically identifies video platform from URL
- ✅ **Smart Language Defaults** - zh-CN for Bilibili, en for YouTube
- ✅ **Custom Language** - Override with `--lang` flag
- ✅ **Dual Format** - Supports both VTT and SRT subtitle formats

## Installation

### Prerequisites

Install [yt-dlp](https://github.com/yt-dlp/yt-dlp):

```bash
# macOS
brew install yt-dlp

# Linux
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod +x /usr/local/bin/yt-dlp

# Python
pip install yt-dlp
```

### Install via ClawHub

```bash
clawhub install video-watcher
```

### Manual Installation

1. Download this skill folder
2. Place it in your OpenClaw workspace: `~/.openclaw/workspace/skills/video-watcher/`

## Usage

### Basic Usage (Auto-detect)

```bash
# YouTube
python3 ~/.openclaw/workspace/skills/video-watcher/scripts/get_transcript.py \
  "https://www.youtube.com/watch?v=VIDEO_ID"

# Bilibili
python3 ~/.openclaw/workspace/skills/video-watcher/scripts/get_transcript.py \
  "https://www.bilibili.com/video/BVxxxxx"
```

### Specify Language

```bash
# Get English subtitles for a Bilibili video
python3 scripts/get_transcript.py "https://bilibili.com/video/..." --lang en

# Get Chinese subtitles for a YouTube video
python3 scripts/get_transcript.py "https://youtube.com/watch?v=..." --lang zh-CN
```

## Default Languages

| Platform | Default | Common Alternatives |
|----------|---------|-------------------|
| YouTube  | `en`    | `zh-CN`, `ja`, `es`, `fr` |
| Bilibili | `zh-CN` | `en`, `zh-TW`, `ja` |

## Output Format

```markdown
# Platform: Bilibili
# Language: zh-CN
# URL: https://www.bilibili.com/video/...

[Clean transcript text without timestamps...]
```

## Troubleshooting

### "yt-dlp not found"
Install yt-dlp first (see Installation section).

### "HTTP Error 412" (Bilibili)
Your IP may be rate-limited. Solutions:
1. Use cookies: `yt-dlp --cookies-from-browser chrome "URL"`
2. Use proxy: `export HTTP_PROXY="http://proxy:port"`
3. Wait and retry

### "No subtitles found"
The video may not have subtitles available. Try:
- Check if the video has CC (closed captions)
- Try different language: `--lang en` or `--lang zh-CN`

## License

MIT

## Credits

Adapted from [youtube-watcher](https://clawhub.ai/Michaelgathara/youtube-watcher) by Michael Gathara.
