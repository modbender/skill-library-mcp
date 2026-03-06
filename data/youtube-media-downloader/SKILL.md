---
name: youtube-downloader
description: Download audio (MP3) and video (MP4) files from YouTube URLs. Use when users want to convert YouTube videos to files, extract music/songs, download videos for offline viewing, save educational content, or process playlists. Handles single videos, playlists, and batch downloads with quality options.
---

# YouTube Media Downloader

Download high-quality audio and video files from YouTube for offline use, music conversion, and content archiving.

## Overview

This skill provides comprehensive YouTube downloading capabilities with quality control, batch processing, and format options. Perfect for music extraction, video archiving, educational content, and playlist processing.

## Quick Start

### Single Video/Audio
```bash
# Download as MP3 (default)
scripts/download_media.sh "https://www.youtube.com/watch?v=VIDEO_ID"

# Download as MP4 video
scripts/download_media.sh -v "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom filename and directory
scripts/download_media.sh -o ~/Downloads "https://www.youtube.com/watch?v=VIDEO_ID" "my_song"
```

### Playlist/Batch Download
```bash
# Entire playlist as MP3
scripts/batch_download.sh "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Playlist items 5-10 as 720p video
scripts/batch_download.sh -v -q 720p -s 5 -e 10 "PLAYLIST_URL"

# From file list of URLs
scripts/batch_download.sh -f urls.txt
```

## Core Capabilities

### Audio Extraction
- **Format**: High-quality MP3
- **Quality**: Best available audio automatically selected
- **Use cases**: Music, podcasts, lectures, interviews
- **Command**: Default behavior (no flags needed)

### Video Download  
- **Format**: MP4 (maximum compatibility)
- **Quality options**: best, 720p, 480p, 360p, worst
- **Use cases**: Offline viewing, archiving, educational content
- **Command**: Use `-v/--video` flag

### Batch Processing
- **Playlists**: Full playlist support with range selection
- **URL files**: Process text files with multiple URLs
- **Organization**: Auto-numbered for playlists
- **Control**: Start/end positions, max downloads

## Quality Selection Guide

### Audio (MP3)
- **Best quality**: Automatic selection from source
- **File size**: ~3-10MB per song
- **Compatibility**: Universal MP3 support

### Video Quality Options
- **best**: Highest available (1080p+, large files)
- **720p**: HD quality, balanced size (~50-200MB)
- **480p**: SD quality, mobile-friendly (~20-80MB)
- **360p**: Low quality, minimal size (~10-30MB)

## Advanced Usage

### Organization Options
```bash
# Specific output directory
-o ~/Downloads/Music

# Date-based folders
-o ~/Downloads/$(date +%Y-%m-%d)
```

### Playlist Range Control
```bash
# Specific range (items 10-20)
-s 10 -e 20

# From specific item to end
-s 25

# Limit total downloads
-m 50
```

### File Input Processing
Create `urls.txt` with one URL per line:
```
https://www.youtube.com/watch?v=video1
https://www.youtube.com/watch?v=video2
```
Then: `batch_download.sh -f urls.txt`

## Script Reference

### download_media.sh
**Purpose**: Single video/audio downloads
**Key flags**:
- `-a/--audio`: MP3 extraction (default)
- `-v/--video`: MP4 video download
- `-q/--quality`: Quality selection
- `-o/--output`: Output directory

### batch_download.sh  
**Purpose**: Playlist and bulk downloads
**Key flags**:
- `-s/--start`, `-e/--end`: Range selection
- `-m/--max-downloads`: Limit downloads
- `-f/--file`: Process URL file
- All single download flags supported

## Best Practices & Patterns

For detailed usage patterns, quality guidelines, and troubleshooting, see [download-patterns.md](references/download-patterns.md).

## Technical Notes

- **Auto-installation**: Scripts install yt-dlp and ffmpeg automatically if needed
- **Portable setup**: Downloads portable binaries, no system admin required
- **Resume support**: Interrupted downloads can be resumed
- **Error handling**: Batch processing continues despite individual failures
- **Format preference**: Always attempts MP4 for video, MP3 for audio
- **Naming**: Auto-generated from video titles unless specified

## Legal & Ethical Use

- **Personal use**: Download content for your own offline viewing
- **Respect copyrights**: Don't redistribute copyrighted material
- **Terms compliance**: Follow YouTube's terms of service
- **Fair use**: Consider fair use guidelines for educational content