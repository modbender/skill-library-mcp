# YoinkIt — OpenClaw Skill

Search, analyze, and transcribe content across 13 social platforms — trending topics, video transcripts, post metadata, and multi-platform research workflows.

## Features

- **Content** — Pull post/video metadata from 13 platforms (YouTube, TikTok, Instagram, Twitter/X, Facebook, LinkedIn, Reddit, Pinterest, Threads, Bluesky, Truth Social, Twitch, Kick)
- **Transcripts** — Extract video transcripts (YouTube, TikTok, Instagram, Twitter/X, Facebook)
- **Search** — Find content across YouTube, TikTok, Instagram, Reddit, Pinterest
- **Trending** — See what's trending on YouTube and TikTok (including popular creators and hashtags)
- **User Feeds** — Get recent posts/videos from specific creators (YouTube, TikTok, Instagram, Twitter/X, Facebook, Threads, Bluesky, Truth Social)
- **Research** — Automated workflows combining search + trending + transcripts across platforms

## Requirements

- [OpenClaw](https://openclaw.ai) installed
- Active [Yoinkit](https://yoinkit.ai) subscription
- API token from Yoinkit Settings → OpenClaw

## Installation

```bash
npx clawhub install yoinkit
```

Then set your API token in OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "yoinkit": {
        "env": {
          "YOINKIT_API_TOKEN": "your-token-here"
        }
      }
    }
  }
}
```

### Local Development

To test against a local server, add `YOINKIT_API_URL`:

```json
{
  "skills": {
    "entries": {
      "yoinkit": {
        "env": {
          "YOINKIT_API_TOKEN": "your-token-here",
          "YOINKIT_API_URL": "http://localhost:8000/api/v1/openclaw"
        }
      }
    }
  }
}
```

## Usage

### Commands

```bash
# Get content/metadata from any platform
yoinkit content https://youtube.com/watch?v=abc123
yoinkit content https://twitter.com/user/status/123
yoinkit content https://reddit.com/r/tech/comments/abc/post

# Get a video transcript
yoinkit transcript https://youtube.com/watch?v=abc123
yoinkit transcript https://youtube.com/shorts/abc123
yoinkit transcript https://tiktok.com/@user/video/123 --language en

# Search a platform
yoinkit search youtube "AI tools for creators"
yoinkit search youtube "AI tools" --sort relevance --time this_week
yoinkit search tiktok "productivity" --sort most-liked
yoinkit search reddit "home automation" --sort top --time month

# Get a creator's recent uploads
yoinkit feed youtube MrBeast
yoinkit feed tiktok @garyvee
yoinkit feed instagram ali-abdaal --type reels

# Get trending content
yoinkit trending youtube
yoinkit trending tiktok
yoinkit trending tiktok --type popular --order like --period 7
yoinkit trending tiktok --type hashtags --period 30

# Multi-platform research workflow
yoinkit research "AI tools" --platforms youtube,tiktok,reddit
yoinkit research "home automation" --platforms youtube,reddit --transcripts
```

### Natural Language

Just ask your assistant naturally:

> "What's trending on YouTube right now?"

> "Search TikTok for productivity tips from this week, sorted by most liked"

> "Pull the transcript from this YouTube video and summarize it"

> "Research what people are saying about AI tools across YouTube, TikTok, and Reddit"

> "What has MrBeast posted this week?"

> "Check @garyvee's latest TikToks"

> "Get me the details on this Instagram post"

## Platform Support

| Platform | Content | Transcript | Search | Trending | User Feed |
|----------|:-------:|:----------:|:------:|:--------:|:---------:|
| YouTube | ✅ | ✅ | ✅ | ✅ | ✅ |
| TikTok | ✅ | ✅ | ✅ | ✅ | ✅ |
| Instagram | ✅ | ✅ | ✅ | — | ✅ |
| Twitter/X | ✅ | ✅ | — | — | ✅ |
| Facebook | ✅ | ✅ | — | — | ✅ |
| LinkedIn | ✅ | — | — | — | — |
| Reddit | ✅ | — | ✅ | — | — |
| Pinterest | ✅ | — | ✅ | — | — |
| Threads | ✅ | — | — | — | ✅ |
| Bluesky | ✅ | — | — | — | ✅ |
| Truth Social | ✅ | — | — | — | ✅ |
| Twitch | ✅ | — | — | — | — |
| Kick | ✅ | — | — | — | — |

## Cron Examples

See the `examples/` directory for ready-to-use OpenClaw cron job configurations:

- **`creator-monitor.json`** — Check creator feeds, pull transcripts, summarize new uploads
- **`obsidian-research-collect.json`** — 7 AM: Scan feeds + trending, save daily collection note to Obsidian
- **`obsidian-research-analyze.json`** — 8 AM: Read collection note, pull transcripts, generate content ideas
- **`daily-trends.json`** — Morning trend check across YouTube and TikTok
- **`weekly-research.json`** — Deep multi-platform research every Monday
- **`viral-alert.json`** — Check for viral content every 2 hours
- **`competitor-watch.json`** — Monitor competitor content weekly
- **`niche-monitor.json`** — Daily cross-platform question/pain-point mining
- **`video-breakdown.json`** — On-demand template for analyzing a specific video

Copy any example and add it via OpenClaw's cron system.

## Documentation

- Platform reference: [references/platforms.md](references/platforms.md)

## License

MIT
