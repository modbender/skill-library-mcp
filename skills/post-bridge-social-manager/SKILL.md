---
name: post-bridge-social-manager
version: 1.0.6
title: Social Media Assistant (via post-bridge.com)
description: Turn your OpenClaw into an autonomous social media manager using Post Bridge API. Use when scheduling, posting, or managing content across TikTok, Instagram Reels, YouTube Shorts, Twitter/X, LinkedIn, Pinterest, Facebook, Threads, or Bluesky. Covers media upload, post creation, scheduling, platform-specific configs, draft mode, and post result tracking.
license: MIT
author: Jack Friks <jack@frikit.net>
homepage: https://clawhub.ai/jackfriks/post-bridge-social-manager
repository: https://github.com/jackfriks/post-bridge-social-manager
keywords: social-media, automation, post-bridge, tiktok, instagram, youtube, twitter, linkedin
metadata:
  openclaw:
    requires:
      env:
        - POST_BRIDGE_API_KEY
      bins:
        - ffmpeg
    primaryEnv: POST_BRIDGE_API_KEY
---

# Social Media Assistant (via post-bridge.com)

Autonomously manage social media posting via [Post Bridge](https://post-bridge.com) API.

## Setup

1. Create a Post Bridge account at [post-bridge.com](https://post-bridge.com)
2. Connect your social accounts (TikTok, Instagram, YouTube, Twitter, etc.)
3. Enable API access (Settings → API)
4. Store your API key in workspace `.env`:
   ```
   POST_BRIDGE_API_KEY=pb_live_xxxxx
   ```
5. Download API docs: `https://api.post-bridge.com/reference` → save to workspace as `post-bridge-api.json`

## Auth

All requests use Bearer token:
```
Authorization: Bearer <POST_BRIDGE_API_KEY>
```

Base URL: `https://api.post-bridge.com`

## Core Workflow

### 1. Get Social Accounts
```
GET /v1/social-accounts
```
Returns array of connected accounts with `id`, `platform`, `username`. Store these IDs — you need them for every post.

### 2. Upload Media
```
POST /v1/media/create-upload-url
Body: { "mime_type": "video/mp4", "size_bytes": <int>, "name": "video.mp4" }
```
Returns `media_id` + `upload_url`. Then:
```
PUT <upload_url>
Content-Type: video/mp4
Body: <binary file>
```

### 3. Create Post
```
POST /v1/posts
Body: {
  "caption": "your caption here #hashtags",
  "media": ["<media_id>"],
  "social_accounts": [<account_id_1>, <account_id_2>],
  "scheduled_at": "2026-01-01T14:00:00Z",  // omit for instant post
  "platform_configurations": { ... }  // optional, see below
}
```

### 4. Check Results
```
GET /v1/posts/<post_id>
```
Returns status: `processing`, `scheduled`, `posted`, `failed`.

### 5. Analytics (TikTok)
```
GET /v1/analytics?platform=tiktok
```
Retrieve performance data (views, likes, shares, etc.) for TikTok posts. Supports filtering by `timeframe` (7d, 30d, 90d, all) and `post_result_id`.

```
POST /v1/analytics/sync
```
Manually trigger a sync of TikTok analytics. This is rate-limited—wait between calls.

## Platform Configurations

Pass inside `platform_configurations` object on post creation. **Crucial:** Always wrap these in the correct platform key to ensure they only apply to the target platform and don't cause issues on other platforms in the same post.

**TikTok (`tiktok`):**
- `draft: true` — save as draft (publish manually on TikTok with trending sound)
- `video_cover_timestamp_ms: 3000` — cover thumbnail
- `is_aigc: true` — label as AI-generated content

**Example of correct multi-platform config:**
```json
{
  "caption": "Default caption",
  "social_accounts": [44029, 44030],
  "platform_configurations": {
    "tiktok": {
      "draft": true,
      "is_aigc": false
    },
    "instagram": {
      "is_trial_reel": false
    }
  }
}
```

**Instagram (`instagram`):**
- `video_cover_timestamp_ms: 3000` — cover thumbnail
- `is_trial_reel: true` — trial reel mode (needs 1000+ followers)
- `trial_graduation: "SS_PERFORMANCE"` — auto-graduate based on performance

**YouTube:**
- `video_cover_timestamp_ms: 3000` — cover thumbnail
- `title: "My Short Title"` — override post title

**Twitter/X:**
- `caption: "override caption"` — platform-specific caption

All platforms support `caption` and `media` overrides for per-platform customization.

## Recommended Workflow for Video Content

1. Store videos in a local folder
2. Extract a frame with ffmpeg to read any text overlays:
   ```
   ffmpeg -i video.mp4 -ss 00:00:04 -frames:v 1 frame.jpg -y
   ```
3. Write caption based on video content + hashtags
4. Upload → create post → schedule or post instantly
5. Move posted videos to a `posted/` subfolder to avoid duplicates
6. Set a cron to check post status 5 mins after scheduled time
7. Track performance by browsing platform pages or checking post results

## Tips

- Post to multiple platforms simultaneously by including multiple account IDs
- Stagger posts throughout the day (e.g. 9am + 3pm) for better reach
- Use `scheduled_at` to pre-schedule batches — Post Bridge handles the timing
- TikTok draft mode lets you add trending sounds manually before publishing
- Keep hashtags to 4-5 per post for best engagement
- Monitor what works and iterate on captions/formats
