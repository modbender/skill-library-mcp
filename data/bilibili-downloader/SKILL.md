---
name: bilibili-downloader
description: Download videos, audio, subtitles, and covers from Bilibili using bilibili-api. Use when working with Bilibili content for downloading videos in various qualities, extracting audio, getting subtitles and danmaku, downloading covers, and managing download preferences.
---

# Bilibili Downloader

## Quick Start

Download a video by URL:
```bash
pip install bilibili-api-python
python -c "
from bilibili_api import video, sync
v = video.Video(bvid='BV1xx411c7m2')
sync(v.download(output='./video.mp4'))
"
```

## Download Options

### Video Quality
- Specify quality with `qn` parameter (127=8K, 126=杜比, 125=1080P+, etc.)
- Default selects best available quality

### Audio Download
- Download original soundtrack: `v.download_audious(output='./audio.mp3')`
- Supports various audio formats

### Subtitles
- Get available subtitles: `v.get_subtitle()`
- Download subtitle files: `sync(v.download_subtitle(output='./'))`

### Covers and Thumbnails
- Get cover URL: `v.get_cover()`
- Download cover: `sync(v.download_cover(output='./cover.jpg'))`

## Common Tasks

### Download Single Video
```python
from bilibili_api import video, sync
v = video.Video(bvid='BV1xx411c7m2')
sync(v.download(output='./video.mp4'))
```

### Download with Specific Quality
```python
from bilibili_api import video, sync
v = video.Video(bvid='BV1xx411c7m2')
info = v.get_download_url(qn=127)  # 8K quality
```

### Download Entire Playlist
```python
from bilibili_api import video, sync
from bilibili_api import playlist

pl = playlist.Playlist(playlist_id='123456')
for v in sync(pl.get_videos()):
    sync(v.download(output=f'./playlist/{v["title"]}.mp4'))
```

### Download Audio Only
```python
from bilibili_api import video, sync
v = video.Video(bvid='BV1xx411c7m2')
sync(v.download_audio(output='./audio.mp3'))
```

## Authentication

For premium content, use browser cookies:
1. Login to Bilibili in browser
2. Export SESSDATA cookie value
3. Set environment variable: `export BILIBILI_SESSDATA='your_cookie_value'`

## Requirements

- bilibili-api-python: `pip install bilibili-api-python`
- ffmpeg: Required for video/audio processing
- Python 3.8+

## Resources

### scripts/
Utility scripts for common download operations.

### references/
- API documentation from bilibili-api repo
- Quality codes reference (qn values)
- Cookie setup guide

### assets/
Download templates and configuration examples.
