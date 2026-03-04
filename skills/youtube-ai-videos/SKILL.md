---
name: youtube-ai-videos
description: Fetch latest AI-related YouTube videos from curated channels using YouTube Data API v3 and filter by keywords
requiresEnvVars:
  - YOUTUBE_API_KEY
---

# YouTube AI Videos

Fetch and display the latest AI-related videos from YouTube channels using YouTube Data API v3.

## Requirements

**This skill requires a YouTube Data API v3 key to function.** The API key can be provided in three ways (priority order):

1. **Environment variable:** `YOUTUBE_API_KEY`
2. **Secrets file:** `~/.openclaw/secrets/youtube_api_key.txt`
3. **Config file:** `config.json` (fallback, not recommended for security)

Get a free API key: https://console.cloud.google.com/apis/api/youtube.googleapis.com

## Usage

Use this skill when you need recent AI-related videos from YouTube.

## Workflow

1. Fetch recent videos from configured YouTube channels using YouTube Data API v3
2. Filter videos by keywords in title
3. Filter by max age (default: 3 days)
4. Return up to 15 videos (configurable)
5. Sort by publication date (newest first)

## Configuration

All settings are in `config.json`:

- **channels:** List of YouTube channel handles (@handle) or IDs
- **keywords:** List of keywords to search for
- **maxVideos:** Maximum number of videos to return (default: 15)
- **maxAgeDays:** Maximum video age in days (default: 3)
- **youtubeApiKey:** Fallback YouTube Data API v3 key (use environment/secrets instead)

## Adding Channels

Find YouTube channel handles or IDs:

1. Go to channel page
2. Look at URL: `youtube.com/@CHANNELNAME` or `youtube.com/channel/CHANNEL_ID`
3. Use @handle format (recommended) or channel ID

## Output Format

Each video includes:
- Number (1-15)
- Time ago (e.g., "2h ago")
- Title with keyword matches highlighted in bold
- Channel name
- Direct YouTube link

Example:
```
1. [2h ago] [OpenClaw: The Next Generation of AI Agents](https://youtube.com/watch?v=...)
   by @IchBinFabian
```

## Running the Script

```bash
./scripts/fetch_youtube_ai_videos.py
```

The script loads --> YouTube API key from environment, secrets file, or config (in that order) and outputs filtered videos.

## Security Note

For security, prefer storing your API key in:
- Environment variable: `export YOUTUBE_API_KEY="your_key"`
- Secrets file: `~/.openclaw/secrets/youtube_api_key.txt`

Avoid storing the API key directly in `config.json` as it's visible in plain text.
