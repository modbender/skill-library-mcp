---
name: m3u8-downloader
description: Download encrypted m3u8/HLS videos using parallel downloads. Use when given an m3u8 URL to download a video, especially encrypted HLS streams with AES-128.
---

# M3U8 Video Downloader

Download HLS/m3u8 videos with parallel segment downloads and automatic decryption.

## Prerequisites

- `aria2c` (install: `brew install aria2`)
- `ffmpeg` (install: `brew install ffmpeg`)

## Full Workflow (From Webpage to MP4)

### Step 1: Extract m3u8 URL from webpage

If given a webpage URL (not a direct m3u8), use browser automation to find the stream URL:

```javascript
// In browser console or via browser tool evaluate
(() => {
  // Check HLS.js player instance
  if (window.hls && window.hls.url) return window.hls.url;
  if (window.player && window.player.hls && window.player.hls.url) return window.player.hls.url;
  
  // Search window objects for m3u8 URLs
  const allVars = Object.keys(window).filter(k => {
    try {
      return window[k] && typeof window[k] === 'object' && 
             window[k].url && window[k].url.includes('m3u8');
    } catch(e) { return false; }
  });
  return allVars.length > 0 ? allVars.map(k => window[k].url) : 'not found';
})()
```

Use `profile=openclaw` (isolated browser) to avoid browser history.

### Step 2: Handle Master Playlist (Multi-Quality)

Master playlists list quality variants, not segments:

```bash
curl -s "https://example.com/playlist.m3u8"
# Output example:
# #EXT-X-STREAM-INF:BANDWIDTH=8247061,RESOLUTION=1920x1080
# 1080p/video.m3u8
# #EXT-X-STREAM-INF:BANDWIDTH=4738061,RESOLUTION=1280x720
# 720p/video.m3u8
```

Pick the highest quality (e.g., 1080p) and fetch that sub-playlist:

```bash
BASE_URL="https://example.com"
curl -s "${BASE_URL}/1080p/video.m3u8"
```

### Step 3: Extract Segment URLs

Segments may have non-standard extensions (e.g., `.jpeg` instead of `.ts`):

```bash
mkdir -p /tmp/video_download && cd /tmp/video_download

BASE_URL="https://example.com/1080p"
curl -s "${BASE_URL}/video.m3u8" | grep -E "^[^#]" | while read seg; do
  echo "${BASE_URL}/${seg}"
done > urls.txt

# Count segments
wc -l urls.txt
```

### Step 4: Parallel Download with aria2c

```bash
aria2c -i urls.txt -j 16 -x 16 -s 16 --file-allocation=none -c true \
  --console-log-level=warn --summary-interval=30
```

- `-j 16`: 16 concurrent downloads
- `-x 16`: 16 connections per file  
- `-c true`: continue partial downloads

### Step 5: Merge with ffmpeg

```bash
# Get segment count
NUM_SEGMENTS=$(wc -l < urls.txt)

# Generate file list (adjust filename pattern as needed)
for i in $(seq 0 $((NUM_SEGMENTS-1))); do
  echo "file 'video${i}.jpeg'"  # or video${i}.ts
done > filelist.txt

# Merge (copy streams, no re-encoding)
ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy ~/Downloads/output.mp4
```

### Step 6: Cleanup

```bash
rm -rf /tmp/video_download
```

## Quick Script Usage

```bash
~/clawd/skills/m3u8-downloader/scripts/download.sh "https://example.com/video.m3u8" "output_name"
```

Note: The script may not handle all edge cases (master playlists, non-standard extensions). Use manual process above for complex streams.

## Handling Encrypted Streams (AES-128)

Look for `#EXT-X-KEY:METHOD=AES-128,URI="enc.key"` in the playlist:

```bash
curl -s "https://example.com/path/enc.key" -o enc.key
ffmpeg -allowed_extensions ALL -i local_playlist.m3u8 -c copy output.mp4
```

## Output

Final video saved as `~/Downloads/<output_name>.mp4`
