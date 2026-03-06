---
name: Larry — Autonomous TikTok Slideshow Agent
description: 1. Research — Identifies viral hooks and trending topics in your
  niche 2. Ideation — Creates 6-slide concepts linked to your affiliate articles
  3. Image Generation — Generates 6 consistent images v...
---

# Larry — Autonomous TikTok Slideshow Agent

> Automatically generates and posts TikTok slideshows for affiliate content sites.
> Inspired by the "Larry" viral slideshow format (8M views in one week).

## What this skill does

1. **Research** — Identifies viral hooks and trending topics in your niche
2. **Ideation** — Creates 6-slide concepts linked to your affiliate articles
3. **Image Generation** — Generates 6 consistent images via NVIDIA FLUX (free tier)
4. **Text Overlay** — Adds hook text (Slide 1) + subtitles to each image
5. **Posting** — Uploads as draft/scheduled post to TikTok via Postiz (self-hosted)
6. **Learning** — Logs performance data, adapts hook formulas over time

## Requirements

- [Postiz](https://github.com/gitroomhq/postiz-app) self-hosted (free) or Postiz cloud
- NVIDIA API key (free tier at build.nvidia.com — includes FLUX image generation)
- TikTok account(s) connected via Postiz

## Setup

```bash
# 1. Copy and fill config
cp ~/.openclaw/skills/larry/config.example.json ~/.openclaw/skills/larry/config.json
# Edit config.json with your API keys and portal details

# 2. Install Python dependencies
pip3 install pillow requests

# 3. Smoke test (no API calls)
python3 ~/.openclaw/skills/larry/scripts/larry.py --portal my-portal --dry-run
```

## Config

```json
{
  "nvidia_api_key": "nvapi-...",
  "postiz_api_key": "...",
  "postiz_base_url": "http://localhost:4007/api",
  "image_model": "flux.1-schnell",
  "slides_per_post": 6,
  "posts_per_day": 2,
  "post_times": ["09:00", "18:00"],
  "portals": {
    "my-portal": {
      "tiktok_account_id": "POSTIZ_INTEGRATION_ID",
      "niche": "Your Niche (e.g. Sauna & Wellness)",
      "site_url": "https://yoursite.com",
      "amazon_tag": "yourtag-21",
      "style": "brief visual style description for image generation",
      "hashtags": ["#tag1", "#tag2", "#tag3"]
    }
  }
}
```

## Usage

```
# Manual single post:
"Larry, create a TikTok post for [portal] about [topic]"

# Autonomous mode (via cron):
python3 ~/.openclaw/skills/larry/scripts/larry.py --portal my-portal --auto

# Dry run (generate slides, don't post):
python3 ~/.openclaw/skills/larry/scripts/larry.py --portal my-portal --dry-run
```

## Slide Format (TikTok sweet spot)

- **6 slides** exactly
- Slide 1: Large hook text + background image
- Slides 2–5: Tips / facts / content
- Slide 6: CTA → "Link in Bio" → article on your site
- Caption: Story-style, natural mention of site, max 5 hashtags
- Image style: realistic lifestyle photography look

## Cost

- Image generation: **€0** (NVIDIA free tier, FLUX.1-schnell)
- Postiz self-hosted: **€0** (Docker, runs locally)
- 2 posts/day × 30 days = **€0/month** running cost

## Performance Tracking

All posts logged to `~/.openclaw/skills/larry/logs/performance.json`.
Larry adapts: high-performing hook formulas → more of those, poor ones → phased out.
