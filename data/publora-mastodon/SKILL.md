---
name: publora-mastodon
description: >
  Post or schedule content to Mastodon using the Publora API. Use this skill
  when the user wants to publish or schedule Mastodon posts via Publora.
---

# Publora — Mastodon

Post and schedule Mastodon content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Platform ID Format

`mastodon-{accountId}` — get your exact ID from `GET /api/v1/platform-connections`.

## Instance Support

⚠️ **mastodon.social only** — Publora currently supports only mastodon.social. Other Mastodon instances are not yet supported.

## Character Limit

**500 characters STRICT.** The API returns an error if exceeded.

Unlike X/Threads, Mastodon does **NOT auto-thread** when you exceed the limit. Your post will be rejected.

## Supported Content

| Type | Supported | Notes |
|------|-----------|-------|
| Text only | ✅ | Up to 500 chars |
| Images | ✅ | JPEG and PNG only (up to 4 per post) |
| Videos | ✅ | MP4 |
| Hashtags | ✅ | Work and **count toward 500 char limit** |
| Content warnings | ❌ | Not supported via API yet |

## Post to Mastodon

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Just shipped a new open-source tool for managing social media posts. Check it out! 🎉 #opensource #developer #tools',
    platforms: ['mastodon-ACCOUNT_ID']
  })
});
```

## Schedule a Post

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Weekly update: what we shipped this week. Thread below ⬇️ #indiedev #buildinpublic',
    platforms: ['mastodon-ACCOUNT_ID'],
    scheduledTime: '2026-03-16T09:00:00.000Z'
  })
});
```

## Post with Images

**JPEG and PNG only.** Up to 4 images per post. Uses the standard 3-step upload workflow.

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'New UI screenshot! Fresh redesign dropping soon 👀 #design #ux',
    'platforms': ['mastodon-ACCOUNT_ID']
}).json()
post_group_id = post['postGroupId']

# Step 2: Get upload URL
upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'screenshot.png', 'contentType': 'image/png',
    'type': 'image', 'postGroupId': post_group_id
}).json()

# Step 3: Upload to S3
with open('screenshot.png', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/png'}, data=f)
```

⚠️ **WebP and GIF are not supported** — use JPEG or PNG only for Mastodon.

## Hashtags

Hashtags work and become clickable on Mastodon. However, **they count toward the 500 character limit** — budget for them in your character count.

```
Building in public: day 47.

Shipped the new API today. Docs are live.

#buildinpublic #indiedev #mastodon
```
The above is ~97 chars — well within 500.

## Visibility

Posts are **public by default** and appear on the federated timeline (visible to users across other Mastodon instances).

## Federation

After posting, expect a **few seconds delay** for your post to propagate to other federated instances. This is normal Mastodon behavior.

## Limitations

- **mastodon.social only** — other instances (fosstodon.org, hachyderm.io, etc.) not yet supported
- **No content warnings (CW)** via API — not yet implemented
- **No auto-threading** — if your content exceeds 500 chars, the API returns an error; split manually
- **JPEG/PNG only** — no WebP, GIF not supported for images

## Tips for Mastodon

- **500 char limit is strict** — count including hashtags
- **Public by default** — federated timeline exposure
- **JPEG or PNG only** for images — no other formats
- **Up to 4 images** per post
- **No auto-threading** — keep each post under 500 chars
