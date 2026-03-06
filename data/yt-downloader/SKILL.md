---
name: youtube-downloader
description: Download YouTube videos as MP4 at highest quality. Use when user sends a YouTube URL and wants to download/save it. Triggers on YouTube links (youtube.com, youtu.be) with download intent. Stores videos as assets with labels and registers them for the dashboard.
---

# YouTube Downloader

Download YouTube videos as high-quality MP4 files and register them as assets.

## Usage

When user sends a YouTube URL to download:

```bash
bash ~/. openclaw/workspace/skills/youtube-downloader/scripts/download.sh "YOUTUBE_URL" "label"
```

**Parameters:**
- `YOUTUBE_URL` - Full YouTube URL (youtube.com/watch, youtu.be, youtube.com/shorts)
- `label` - Short descriptive label (e.g., "honey-b-interview", "og-event-recap")

## Example

User: "download this https://youtube.com/watch?v=abc123 and label it event-recap"

```bash
bash ~/.openclaw/workspace/skills/youtube-downloader/scripts/download.sh "https://youtube.com/watch?v=abc123" "event-recap"
```

## Output

- **Video location:** `~/.openclaw/workspace/assets/videos/{label}_{videoId}_{timestamp}.mp4`
- **Registry:** `~/.openclaw/workspace/assets/registry.json` - JSON log of all downloaded assets

## Registry Format

Each download adds an entry:
```json
{
  "type": "video",
  "source": "youtube",
  "videoId": "abc123",
  "label": "event-recap",
  "filename": "event-recap_abc123_20260201_234500.mp4",
  "path": "/full/path/to/file.mp4",
  "url": "https://youtube.com/watch?v=abc123",
  "downloadedAt": "2026-02-01T23:45:00Z",
  "filesize": "150M"
}
```

## Quality

Downloads best available quality:
- Video: Highest resolution (up to 4K)
- Audio: Best quality, merged
- Format: MP4 (h264 + aac)

## Limitations

- No live streams
- Private/deleted videos will fail
- Age-restricted may need cookies
