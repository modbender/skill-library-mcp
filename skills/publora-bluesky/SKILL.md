---
name: publora-bluesky
description: >
  Post or schedule content to Bluesky using the Publora API. Use this skill
  when the user wants to publish or schedule Bluesky posts via Publora.
---

# Publora — Bluesky

Post and schedule Bluesky content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Platform ID Format

`bluesky-{did}` — Bluesky uses **DID-based IDs**, NOT numeric.

Example: `bluesky-did:plc:abc123xyz`

Get your exact DID from `GET /api/v1/platform-connections`.

## Authentication

Bluesky requires:
- **Username** (handle, e.g. `yourname.bsky.social`)
- **App password** — **NOT your main account password**

Generate an app password at: Bluesky Settings → **App Passwords** → Add App Password.

⚠️ Using your main password is a security risk. Always use app passwords for API integrations.

## Character Limit

**300 characters strict.** The API returns an error if exceeded.

## Supported Content

| Type | Supported | Notes |
|------|-----------|-------|
| Text only | ✅ | Up to 300 chars |
| Images | ✅ | Up to 4 per post; JPEG preferred; WebP auto-converted |
| Videos | ❌ | Not currently supported |
| Hashtags | ✅ | Auto-detected and become clickable facets |
| URLs | ✅ | Auto-detected and become clickable links |

## Post to Bluesky

```python
import requests

response = requests.post(
    'https://api.publora.com/api/v1/create-post',
    headers={
        'Content-Type': 'application/json',
        'x-publora-key': 'sk_YOUR_KEY'
    },
    json={
        'content': 'Dashboard live! #buildinpublic',
        'platforms': ['bluesky-did:plc:abc123xyz']
    }
)
print(response.json())
```

## Post with Images

Up to **4 images** per post. Each image requires its own `get-upload-url` call with the same `postGroupId`.

Use `altTexts` array for image accessibility — maps positionally to uploaded images (first altText → first uploaded image).

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

# Step 1: Create post with altTexts
post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'Dashboard live! #buildinpublic',
    'platforms': ['bluesky-did:plc:abc123xyz'],
    'altTexts': ['Screenshot of analytics dashboard showing user growth charts']
}).json()
post_group_id = post['postGroupId']

# Step 2: Get upload URL (one call per image)
upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'dashboard.jpg', 'contentType': 'image/jpeg',
    'type': 'image', 'postGroupId': post_group_id
}).json()

# Step 3: Upload to S3
with open('dashboard.jpg', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

### Multiple Images with altTexts

```python
json={
    'content': 'New features shipping this week! 🚀 #indiedev',
    'platforms': ['bluesky-did:plc:abc123xyz'],
    'altTexts': [
        'Screenshot of the new dashboard with dark mode enabled',
        'Mobile view of the app showing the updated navigation',
        'Code editor integration screenshot'
    ]
}
# Then upload 3 images with same postGroupId
# altTexts map positionally: index 0 → first uploaded image, etc.
```

**WebP note:** WebP images are automatically converted to JPEG by Publora.

## Rich Text — Auto-Detection

Publora automatically detects and converts **hashtags** and **URLs** into clickable Bluesky facets:

- `#hashtag` → becomes a clickable hashtag link
- `https://example.com` → becomes a clickable URL

You do not need to do anything special — just include them in your content string. Publora handles the byte-offset calculations required by the Bluesky AT Protocol internally.

## Schedule a Post

```python
json={
    'content': 'Shipping on Friday! Stay tuned 👀 #buildinpublic',
    'platforms': ['bluesky-did:plc:abc123xyz'],
    'scheduledTime': '2026-03-16T10:00:00.000Z'
}
```

## Tips for Bluesky

- **DID format** — platform ID is `bluesky-did:plc:xyz`, not a number
- **App password required** — never use main account password
- **300 char limit** — tight, be concise
- **Hashtags auto-link** — Publora handles AT Protocol facets automatically
- **altTexts** — always provide for accessibility; maps by position to uploaded images
- **Up to 4 images** — each needs a separate `get-upload-url` call, all with same `postGroupId`
