---
name: publora-youtube
description: >
  Upload and publish video content to YouTube using the Publora API. Use this
  skill when the user wants to upload or schedule YouTube videos via Publora.
---

# Publora — YouTube

Upload and publish YouTube video content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Platform ID Format

`youtube-{channelId}` — where `{channelId}` is your YouTube channel ID assigned during Google OAuth connection in the Publora dashboard.

Get your exact ID from `GET /api/v1/platform-connections`.

## Requirements

- YouTube channel connected via **Google OAuth** through the Publora dashboard
- **Video is required** — YouTube does not support text-only or image-only posts

## Supported Content

| Type | Supported | Notes |
|------|-----------|-------|
| Text only | ❌ | Not supported |
| Images | ❌ | Not supported as standalone posts |
| Video | ✅ | MP4 format |

## Character Limits

| Element | Limit |
|---------|-------|
| Video title | 100 characters |
| Video description | 5,000 characters |
| Auto-generated title | First 70 characters of `content` |

## Upload a Public Video

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post with YouTube settings
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'How to Build a REST API in 10 Minutes - A complete tutorial covering Express.js setup, routing, middleware, error handling, and deployment to production. Perfect for beginners who want to get started with backend development.',
    'platforms': ['youtube-UCxxxxxxxx'],
    'platformSettings': {
        'youtube': {
            'privacy': 'public',
            'title': 'How to Build a REST API in 10 Minutes'
        }
    }
}).json()
post_group_id = post['postGroupId']

# Step 2: Get upload URL
upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'tutorial.mp4', 'contentType': 'video/mp4',
    'type': 'video', 'postGroupId': post_group_id
}).json()

# Step 3: Upload to S3
with open('tutorial.mp4', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'video/mp4'}, data=f)
```

## Upload an Unlisted Video

Unlisted videos are accessible via direct link but don't appear in search results.

```python
json={
    'content': 'Internal demo recording for the team. This video covers the new dashboard features and upcoming roadmap items.',
    'platforms': ['youtube-UCxxxxxxxx'],
    'platformSettings': {
        'youtube': {
            'privacy': 'unlisted',
            'title': 'Internal Demo - Q1 Dashboard Features'
        }
    }
}
```

## Upload a Private Video

```python
json={
    'content': 'Draft recording — not ready to share yet.',
    'platforms': ['youtube-UCxxxxxxxx'],
    'platformSettings': {
        'youtube': {
            'privacy': 'private',
            'title': 'Draft - Review Before Publishing'
        }
    }
}
```

## Auto-Generated Title

If you omit `title` in platform settings, Publora automatically uses the **first 70 characters** of the `content` field as the video title. The full `content` becomes the description.

```python
json={
    'content': 'Weekly Vlog: What I learned shipping 3 features in 5 days. This week was intense but incredibly productive...',
    'platforms': ['youtube-UCxxxxxxxx']
    # No platformSettings — title auto-generated from first 70 chars of content
}
# Title will be: "Weekly Vlog: What I learned shipping 3 features in 5 days. This week"
# Description will be the full content
```

⚠️ Recommendation: always set `title` explicitly to avoid truncated titles.

## Schedule a Video Upload

```python
json={
    'content': 'Full tutorial: building a SaaS in 30 days. Everything I learned, mistakes included.',
    'platforms': ['youtube-UCxxxxxxxx'],
    'scheduledTime': '2026-03-16T14:00:00.000Z',
    'platformSettings': {
        'youtube': {
            'privacy': 'public',
            'title': 'Building a SaaS in 30 Days — Full Story'
        }
    }
}
```

## platformSettings Reference

```json
{
  "platformSettings": {
    "youtube": {
      "privacy": "public",
      "title": "My Video Title"
    }
  }
}
```

| Setting | Values | Default | Description |
|---------|--------|---------|-------------|
| `privacy` | `"public"`, `"private"`, `"unlisted"` | `"public"` | Video visibility |
| `title` | string (max 100 chars) | First 70 chars of `content` | Video title |

### Privacy Settings

| Value | Description |
|-------|-------------|
| `public` | Anyone can search for and view the video |
| `private` | Only you can view the video |
| `unlisted` | Anyone with the link can view; does not appear in search |

## Platform Quirks

- **Video required** — YouTube rejects text-only or image-only posts
- **MP4 only** — convert other formats before uploading
- **Content is description** — the full `content` field becomes the YouTube video description
- **Title fallback** — if no title set, first 70 chars of content are used (often truncated; set explicitly)
- **Processing time** — YouTube processes video after upload; may take seconds to minutes depending on length and resolution
- **Daily upload quota** — YouTube enforces daily limits; if hit, Publora returns the YouTube API error
- **Privacy changes** — you can upload as `private` or `unlisted` and manually change to `public` later via YouTube Studio
- **Max upload size:** 512 MB

## Tips for YouTube

- **Always set a title** — auto-generated titles from content often get truncated
- **Content = description** — write a full description in `content`; it's used as the video description
- **Use `private` for drafts** — upload privately, review, then publish via YouTube Studio
- **Upload quota** — if you hit daily limits, wait until the quota resets (midnight Pacific)
- **Scheduling works** — use `scheduledTime` in ISO 8601 UTC
- **Unlisted for sharing** — great for sharing with a specific audience without public indexing
