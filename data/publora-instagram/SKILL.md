---
name: publora-instagram
description: >
  Post or schedule content to Instagram using the Publora API. Use this skill
  when the user wants to publish images, reels, stories, or carousels to
  Instagram via Publora.
---

# Publora — Instagram

Post and schedule Instagram content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Platform ID Format

`instagram-{accountId}` — get your exact ID from `GET /api/v1/platform-connections`.

## Account Requirements

- **Business or Creator account required** — personal accounts are NOT supported
- Must be **linked to a Facebook Page** in Meta Business Suite
- Text-only posts are **NOT supported** — every Instagram post must include media

## Supported Content

| Type | Supported | Notes |
|------|-----------|-------|
| Text only | ❌ | Must have media |
| Single image | ✅ | JPEG or PNG |
| Carousel | ✅ | 2–10 images (minimum 2), same `postGroupId` |
| Reels (video) | ✅ | MP4, default video type |
| Stories (video) | ✅ | MP4, set `videoType: "STORIES"` in platformSettings |
| WebP images | ✅ | Auto-converted to JPEG |

## Caption Limits

| Element | Limit |
|---------|-------|
| Caption | 2,200 characters max |
| Hashtags | 30 max |

## Aspect Ratios

Instagram enforces aspect ratio requirements:
- **Portrait:** 4:5 (0.8) minimum
- **Landscape:** 1.91:1 maximum
- Content outside this range **may be cropped** by Instagram

## Post a Single Image

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'New product drop 🔥 Available now! #launch #product #design',
    'platforms': ['instagram-456789']
}).json()
post_group_id = post['postGroupId']

# Step 2: Get upload URL
upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'product.jpg', 'contentType': 'image/jpeg',
    'type': 'image', 'postGroupId': post_group_id
}).json()

# Step 3: Upload to S3 (no auth needed)
with open('product.jpg', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

## Post a Carousel (Multiple Images)

Carousel requires **2–10 images**. Upload all images to the same `postGroupId` — Publora handles the Instagram multi-step carousel API internally.

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'Behind the scenes of our launch week 👀 Swipe to see it all! #buildinpublic',
    'platforms': ['instagram-456789']
}).json()
post_group_id = post['postGroupId']

# Steps 2+3: Upload each image (2-10 images, all same postGroupId)
images = ['slide1.jpg', 'slide2.jpg', 'slide3.jpg', 'slide4.jpg']
for img in images:
    upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
        'fileName': img, 'contentType': 'image/jpeg',
        'type': 'image', 'postGroupId': post_group_id
    }).json()
    with open(img, 'rb') as f:
        requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

## Post a Reel (Video)

Default video type is REELS. Use `platformSettings.instagram.videoType` to control.

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'How we 10x our productivity in 60 seconds ⚡ #productivityhacks #startup',
    platforms: ['instagram-456789'],
    platformSettings: {
      instagram: {
        videoType: 'REELS'
      }
    }
  })
});
// Then upload video using 3-step media workflow with returned postGroupId
```

## Post a Story

Stories disappear after 24 hours. Set `videoType: "STORIES"`:

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Flash sale — 24 hours only! 🔥',
    platforms: ['instagram-456789'],
    platformSettings: {
      instagram: {
        videoType: 'STORIES'
      }
    }
  })
});
// Then upload video using 3-step media workflow
```

## platformSettings Reference

```json
{
  "platformSettings": {
    "instagram": {
      "videoType": "REELS"
    }
  }
}
```

| Setting | Values | Default | Description |
|---------|--------|---------|-------------|
| `videoType` | `"REELS"`, `"STORIES"` | `"REELS"` | Video post type |

## Tips for Instagram

- **No text-only posts** — always include media
- **Carousel minimum is 2 images** — a single image upload is not a carousel
- **Stories expire in 24h** — use for time-sensitive content
- **30 hashtag max** — over this limit may reduce reach
- **Aspect ratio matters** — shoot/crop to 4:5 portrait for feed, 9:16 for Stories/Reels
- **Caption first 125 chars** shown before "more" — put the hook there
