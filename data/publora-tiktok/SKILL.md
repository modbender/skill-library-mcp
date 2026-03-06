---
name: publora-tiktok
description: >
  Post or schedule video content to TikTok using the Publora API. Use this skill
  when the user wants to publish or schedule TikTok videos via Publora.
---

# Publora — TikTok

Post and schedule TikTok video content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Platform ID Format

`tiktok-{userId}` — where `{userId}` is assigned during OAuth account connection in the Publora dashboard.

Get your exact ID from `GET /api/v1/platform-connections`.

## Requirements

- TikTok account connected via **OAuth** through the Publora dashboard
- **Video is required** — TikTok does not support text-only or image-only posts

## Supported Content

| Type | Supported | Notes |
|------|-----------|-------|
| Text only | ❌ | Not supported |
| Images | ❌ | Not supported as standalone posts |
| Video | ✅ | MP4 format, minimum 23 FPS |

## Character Limits

| Element | Limit |
|---------|-------|
| Video caption | 2,200 characters |
| Hashtags | Included in caption character count |

## Post a TikTok Video

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post with TikTok settings
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'How we built our startup in 60 seconds #startup #tech #coding',
    'platforms': ['tiktok-99887766'],
    'platformSettings': {
        'tiktok': {
            'viewerSetting': 'PUBLIC_TO_EVERYONE',
            'allowComments': True,
            'allowDuet': True,
            'allowStitch': True,
            'commercialContent': False,
            'brandOrganic': False,
            'brandedContent': False
        }
    }
}).json()
post_group_id = post['postGroupId']

# Step 2: Get upload URL
upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'video.mp4', 'contentType': 'video/mp4',
    'type': 'video', 'postGroupId': post_group_id
}).json()

# Step 3: Upload to S3
with open('video.mp4', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'video/mp4'}, data=f)
```

## Post a Private/Restricted Video

```python
json={
    'content': 'Preview of our upcoming feature for close friends only',
    'platforms': ['tiktok-99887766'],
    'platformSettings': {
        'tiktok': {
            'viewerSetting': 'MUTUAL_FOLLOW_FRIENDS',
            'allowComments': True,
            'allowDuet': False,
            'allowStitch': False,
            'commercialContent': False,
            'brandOrganic': False,
            'brandedContent': False
        }
    }
}
```

## Schedule a TikTok Post

```python
json={
    'content': 'Day in the life of a founder 📱 #founder #startup #dayinthelife',
    'platforms': ['tiktok-99887766'],
    'scheduledTime': '2026-03-16T18:00:00.000Z',
    'platformSettings': {
        'tiktok': {
            'viewerSetting': 'PUBLIC_TO_EVERYONE',
            'allowComments': True,
            'allowDuet': True,
            'allowStitch': True,
            'commercialContent': False,
            'brandOrganic': False,
            'brandedContent': False
        }
    }
}
```

## platformSettings Reference

### Viewer Settings

| Value | Description |
|-------|-------------|
| `PUBLIC_TO_EVERYONE` | Anyone can view the video |
| `MUTUAL_FOLLOW_FRIENDS` | Only mutual followers can view |
| `FOLLOWER_OF_CREATOR` | Only your followers can view |
| `SELF_ONLY` | Only you can view (draft-like behavior) |

### Interaction Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `allowComments` | boolean | `true` | Whether viewers can comment |
| `allowDuet` | boolean | `true` | Whether viewers can create Duets |
| `allowStitch` | boolean | `true` | Whether viewers can Stitch your video |

### Commercial Content Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `commercialContent` | boolean | `false` | Whether this is commercial content |
| `brandOrganic` | boolean | `false` | Organic brand promotion (your own brand) |
| `brandedContent` | boolean | `false` | Paid partnership or sponsored content |

⚠️ **Important:** If `brandOrganic` or `brandedContent` is `true`, then `commercialContent` must also be `true`. Publora returns a validation error if this rule is violated.

## Platform Quirks

- **Video required** — TikTok rejects text-only or image-only posts
- **Minimum 23 FPS** — videos below this frame rate are rejected by TikTok
- **MP4 only** — convert other formats before uploading
- **Commercial content disclosure** — required for branded/sponsored content; violating TikTok guidelines risks account penalties
- **SELF_ONLY** posts cannot receive comments from others
- **Processing time** — TikTok processes videos after upload; the post may not appear immediately on the profile
- **Max upload size:** 512 MB

## Tips for TikTok

- **Vertical 9:16 format** — anything else gets cropped
- **Hook in first 1–3 seconds** — critical for watch time and algorithm performance
- **Caption up to 2,200 chars** — use it for context, but the video tells the story
- **Best lengths:** 7–15 seconds for viral content; 60+ for educational
- **Best times:** 6–10 PM weekdays; 9–11 AM weekends
- **Trending sounds** dramatically increase reach when applicable
- **Hashtags count toward caption** character limit
