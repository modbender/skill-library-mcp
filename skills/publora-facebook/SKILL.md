---
name: publora-facebook
description: >
  Post or schedule content to Facebook Pages using the Publora API. Use this
  skill when the user wants to publish or schedule Facebook posts via Publora.
---

# Publora — Facebook

Post and schedule Facebook Page content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Platform ID Format

`facebook-{pageId}` — get your exact ID from `GET /api/v1/platform-connections`.

## Account Requirements

- **Facebook Pages only** — personal profiles are NOT supported via the API
- Each connected Page gets its own `facebook-{pageId}` platform ID
- **Multiple pages:** can post to multiple pages in a single API call by including multiple IDs in the `platforms` array

## Supported Content

| Type | Supported | Notes |
|------|-----------|-------|
| Text only | ✅ | Up to 63,206 chars |
| Single image | ✅ | JPEG/PNG; WebP auto-converted to JPEG |
| Multiple images | ✅ | Becomes album/carousel |
| Video | ✅ | MP4 only; cannot mix with images in same post |
| Link preview | ✅ | Auto-generated from URLs in text (Facebook behavior) |

## Text Limit

Up to **63,206 characters** (no hard API limit, but this is Facebook's recommended maximum).

## Post to a Facebook Page

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Big news from our team today! We just crossed 10,000 customers. 🎉\n\nThank you all for your support. Here is what is coming next...',
    platforms: ['facebook-PAGE_ID']
  })
});
```

## Post to Multiple Pages

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Announcement going out to all our brand pages!',
    platforms: ['facebook-PAGE_ID_1', 'facebook-PAGE_ID_2', 'facebook-PAGE_ID_3']
  })
});
```

## Post with Images (Album)

Multiple images create a Facebook album. Use the 3-step upload workflow, calling `get-upload-url` once per image with the same `postGroupId`.

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'Photos from our annual company retreat! Great time with the team.',
    'platforms': ['facebook-PAGE_ID'],
    'scheduledTime': '2026-03-16T10:00:00.000Z'
}).json()
post_group_id = post['postGroupId']

# Steps 2+3: Upload each image (all use same postGroupId)
for img_path in ['retreat1.jpg', 'retreat2.jpg', 'retreat3.jpg']:
    upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
        'fileName': img_path, 'contentType': 'image/jpeg',
        'type': 'image', 'postGroupId': post_group_id
    }).json()
    with open(img_path, 'rb') as f:
        requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

**WebP note:** WebP images are automatically converted to JPEG by Publora.

## Post a Video

Videos must be posted separately — cannot mix images and video in the same post.

```python
# Step 1: Create post
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'Watch our product demo — 2 minutes to see everything! 🎬',
    'platforms': ['facebook-PAGE_ID']
}).json()

# Step 2: Get upload URL
upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'demo.mp4', 'contentType': 'video/mp4',
    'type': 'video', 'postGroupId': post['postGroupId']
}).json()

# Step 3: Upload to S3
with open('demo.mp4', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'video/mp4'}, data=f)
```

## Schedule a Facebook Post

```javascript
body: JSON.stringify({
  content: 'Weekly update post — scheduled for Monday morning.',
  platforms: ['facebook-PAGE_ID'],
  scheduledTime: '2026-03-16T08:00:00.000Z'
})
```

## Token Auto-Refresh

Facebook access tokens expire after **59 days**. Publora automatically refreshes them.

- If auto-refresh **succeeds:** no action needed
- If auto-refresh **fails:** reconnect the page via the Publora dashboard (Settings → Connections)

## Link Previews

When you include a URL in your post text, Facebook **automatically generates a link preview** (title, description, thumbnail). This is Facebook's native behavior — Publora does not control it.

## Tips for Facebook

- **Pages only** — personal profiles cannot be used via the API
- **Multiple pages** in one call → include all `facebook-{pageId}` values in `platforms` array
- **Images and videos don't mix** in one post — choose one
- **Link preview** is automatic when a URL is in the text
- **Token expires every 59 days** — Publora auto-refreshes, but watch for reconnect prompts
- **Long-form content works** — Facebook supports up to 63,206 chars, great for detailed announcements
