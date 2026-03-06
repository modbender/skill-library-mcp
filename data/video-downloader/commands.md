# Command Recipes - Video Downloader

Use these commands when the user asks for explicit download settings.

## Script Wrapper (recommended)

```bash
# Best quality MP4 to Downloads
python3 download_video.py "https://example.com/video"
```

```bash
# Cap at 1080p
python3 download_video.py "https://example.com/video" -q 1080p
```

```bash
# Audio only as MP3
python3 download_video.py "https://example.com/video" --audio-only
```

```bash
# Custom format and output directory
python3 download_video.py "https://example.com/video" -q 720p -f webm -o ~/Desktop/media
```

```bash
# Metadata only (no download)
python3 download_video.py "https://example.com/video" --print-info
```

## Raw yt-dlp Fallback

Use raw commands only for advanced flags not covered by the wrapper.

```bash
# Best available video + audio
yt-dlp --no-playlist -f "bestvideo+bestaudio/best" \
  -o "%(title)s [%(id)s].%(ext)s" "https://example.com/video"
```

```bash
# Max 720p with MP4 merge
yt-dlp --no-playlist -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --merge-output-format mp4 \
  -o "%(title)s [%(id)s].%(ext)s" "https://example.com/video"
```

```bash
# Extract MP3
yt-dlp --no-playlist -x --audio-format mp3 --audio-quality 0 \
  -o "%(title)s [%(id)s].%(ext)s" "https://example.com/video"
```
