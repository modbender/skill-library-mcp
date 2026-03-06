---
name: youtube-master
description: Get YouTube video info, statistics, descriptions, thumbnails, and optionally transcripts. Uses YouTube Data API (free) for basic info and Apify (optional) for transcripts.
metadata:
  {
    "openclaw": {
      "emoji": "🎬",
      "requires": {
        "env": ["YOUTUBE_API_KEY", "APIFY_TOKEN"]
      },
      "install": [
        {
          "id": "youtube_api",
          "kind": "env",
          "label": "YouTube Data API Key (YOUTUBE_API_KEY)"
        },
        {
          "id": "apify_token",
          "kind": "env",
          "label": "Apify API Token (APIFY_TOKEN) - Optional for transcripts"
        }
      ]
    }
  }
---

# 🎬 YouTube Master

Get comprehensive YouTube video data including metadata, statistics, descriptions, thumbnails, and optionally transcripts.

## Why This Skill?

YouTube videos require multiple APIs to get complete data. This skill intelligently uses:
- **YouTube Data API (FREE)** → Video metadata, stats, description
- **Apify API (OPTIONAL)** → Only when transcripts requested

## Advantages

### 💰 Cost Effective
- **Default**: YouTube API only (free quota)
- **Transcript**: Only 1 Apify request when explicitly requested
- No wasted API calls

### ⚡ Fast Performance
- YouTube API: ~200ms response
- Apify: Only loads when needed

### 📊 Complete Data

| Data | Source |
|------|--------|
| Title | ✅ YouTube API |
| Description | ✅ YouTube API |
| Channel Name | ✅ YouTube API |
| View Count | ✅ YouTube API |
| Like Count | ✅ YouTube API |
| Comment Count | ✅ YouTube API |
| Upload Date | ✅ YouTube API |
| Thumbnail URL | ✅ YouTube API |
| Tags | ✅ YouTube API |
| **Transcript** | ✅ Apify (on demand) |

## How It Works

```
┌─────────────────┐
│  Input: URL└────────┬/ID   │
────────┘
         │
         ▼
┌─────────────────┐
│ YouTube API    │ ◄── FREE, always runs
│ (viewCount,    │
│  description,   │
│  title, etc.)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌──────────────┐
│ --    │ │ --transcript │
│info   │ │ is requested │
│only   │ └──────┬───────┘
└───┬───┘        │
    │            ▼
    │    ┌─────────────────┐
    │    │ Apify API      │ ◄── Only runs if
    │    │ (transcript)   │     explicitly asked
    │    └────────┬────────┘
    │             │
    └─────┬───────┘
          │
          ▼
┌─────────────────┐
│   Full Output   │
└─────────────────┘
```

## Credentials Setup

### Option 1: Environment Variables

```bash
export YOUTUBE_API_KEY="AIzaSy..."
export APIFY_TOKEN="apify_api_..."
```

### Option 2: Credentials File (Recommended)

Add to `~/.openclaw/workspace/credentials/api-credentials.json`:

```json
{
  "google": {
    "api_key": "AIzaSy..."
  },
  "apify": {
    "api_key": "apify_api_..."
  }
}
```

### Getting YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Free quota: 10,000 units/day

### Getting Apify Token

1. Go to [Apify](https://apify.com/)
2. Sign up / Login
3. Copy API token from Settings

## Usage

### Default (Info Only - FREE)

```bash
python3 get_transcript.py "VIDEO_ID"
python3 get_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### With Transcript (Uses Apify)

```bash
python3 get_transcript.py "VIDEO_ID" --transcript
python3 get_transcript.py "VIDEO_ID" -t
python3 get_transcript.py "VIDEO_ID" --transcript --lang tr
```

### Info Only

```bash
python3 get_transcript.py "VIDEO_ID" --info-only
```

## Examples

### Basic Video Info

```bash
python3 get_transcript.py dQw4w9WgXcQ
```

### Video + Transcript

```bash
python3 get_transcript.py Oi3Z1wlZXhg --transcript --lang tr
```

### Save to File

```bash
python3 get_transcript.py VIDEO_ID > output.txt
```

## API Quotas

### YouTube Data API (Free)
- 10,000 units/day (default)
- Video list: 1 unit per request
- Enough for ~10,000 video queries/day

### Apify
- Free tier available
- Only charged when transcript requested

## Files

- `get_transcript.py` - Main script
