---
name: meta-business
description: |
  Meta Business Suite automation via Graph API. Use this skill when:
  (1) Publishing posts to Facebook Pages
  (2) Scheduling Facebook posts
  (3) Publishing to Instagram (photos, reels, carousels)
  (4) Reading insights/analytics from Facebook or Instagram
  (5) Managing comments on Facebook or Instagram
  (6) Uploading photos or videos to Facebook Pages
  (7) Deleting posts from Facebook or Instagram
homepage: https://developers.facebook.com/docs/graph-api
metadata:
  {
    "openclaw":
      {
        "emoji": "📱",
        "requires":
          {
            "bins": ["curl", "python3"],
            "env": ["META_PAGE_ACCESS_TOKEN", "META_PAGE_ID"],
          },
        "primaryEnv": "META_PAGE_ACCESS_TOKEN",
      },
  }
---

# Meta Business Suite — Facebook & Instagram API

## Configuration

**CRITICAL:** Never hardcode tokens or IDs in commands. Always use variables.

### Option A: Environment variables (recommended)

Set these environment variables before using the skill:

```bash
export META_PAGE_ACCESS_TOKEN="your-page-access-token"
export META_PAGE_ID="your-page-id"
```

Then use them directly:

```bash
PAGE_TOKEN="$META_PAGE_ACCESS_TOKEN"
PAGE_ID="$META_PAGE_ID"
```

The same Page Access Token works for both Facebook and Instagram (the IG Business account is linked to the Page).

### Option B: Token cache file (alternative)

If environment variables are not set, credentials can be read from `~/.meta_tokens_cache.json` (chmod 600):

```bash
PAGE_TOKEN=$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.meta_tokens_cache.json')))
page_id = list(d['pages'].keys())[0]
print(d['pages'][page_id]['access_token'])
")

PAGE_ID=$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.meta_tokens_cache.json')))
print(list(d['pages'].keys())[0])
")

IG_ID=$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.meta_tokens_cache.json')))
print(list(d['instagram'].keys())[0])
")
```

### API Version

Always use `v25.0` in all API calls.

---

## Facebook Page — Publish

### Text post

```bash
curl -X POST "https://graph.facebook.com/v25.0/$PAGE_ID/feed" \
  -d "message=Tu mensaje aquí" \
  -d "access_token=$PAGE_TOKEN"
```

### Post with image (URL)

```bash
curl -X POST "https://graph.facebook.com/v25.0/$PAGE_ID/photos" \
  -d "url=https://example.com/image.jpg" \
  -d "message=Texto del post" \
  -d "access_token=$PAGE_TOKEN"
```

### Post with image (local file)

```bash
curl -X POST "https://graph.facebook.com/v25.0/$PAGE_ID/photos" \
  -F "source=@/path/to/image.jpg" \
  -F "message=Texto del post" \
  -F "access_token=$PAGE_TOKEN"
```

### Post with video

```bash
curl -X POST "https://graph.facebook.com/v25.0/$PAGE_ID/videos" \
  -F "source=@/path/to/video.mp4" \
  -F "description=Descripción del vídeo" \
  -F "title=Título del vídeo" \
  -F "access_token=$PAGE_TOKEN"
```

### Post with link

```bash
curl -X POST "https://graph.facebook.com/v25.0/$PAGE_ID/feed" \
  -d "message=Mira este artículo" \
  -d "link=https://example.com/article" \
  -d "access_token=$PAGE_TOKEN"
```

---

## Facebook Page — Schedule

### Schedule a post

```bash
# Get Unix timestamp: python3 -c "from datetime import datetime; print(int(datetime(2026,3,1,9,0).timestamp()))"

curl -X POST "https://graph.facebook.com/v25.0/$PAGE_ID/feed" \
  -d "message=Post programado" \
  -d "published=false" \
  -d "scheduled_publish_time=UNIX_TIMESTAMP" \
  -d "access_token=$PAGE_TOKEN"
```

**Note:** Must be between 10 minutes and 75 days from now.

### List scheduled posts

```bash
curl -s "https://graph.facebook.com/v25.0/$PAGE_ID/scheduled_posts?access_token=$PAGE_TOKEN"
```

---

## Facebook Page — Read & Manage

### Page info

```bash
curl -s "https://graph.facebook.com/v25.0/$PAGE_ID?fields=name,fan_count,followers_count,about&access_token=$PAGE_TOKEN"
```

### Recent posts

```bash
curl -s "https://graph.facebook.com/v25.0/$PAGE_ID/feed?fields=message,created_time,id,shares,likes.summary(true),comments.summary(true)&limit=10&access_token=$PAGE_TOKEN"
```

### Page insights

```bash
curl -s "https://graph.facebook.com/v25.0/$PAGE_ID/insights?metric=page_views_total,page_fan_adds,page_engaged_users&period=day&access_token=$PAGE_TOKEN"
```

### Delete a post

```bash
curl -X DELETE "https://graph.facebook.com/v25.0/POST_ID?access_token=$PAGE_TOKEN"
```

### Comment on a post

```bash
curl -X POST "https://graph.facebook.com/v25.0/POST_ID/comments" \
  -d "message=Tu comentario" \
  -d "access_token=$PAGE_TOKEN"
```

---

## Instagram — Publish

Instagram uses a 2-step process: create media container → publish.

### Photo post

```bash
# Step 1: Create container
CONTAINER_ID=$(curl -s -X POST "https://graph.facebook.com/v25.0/$IG_ID/media" \
  -d "image_url=https://example.com/image.jpg" \
  -d "caption=Tu caption con #hashtags" \
  -d "access_token=$PAGE_TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 2: Publish
curl -X POST "https://graph.facebook.com/v25.0/$IG_ID/media_publish" \
  -d "creation_id=$CONTAINER_ID" \
  -d "access_token=$PAGE_TOKEN"
```

### Reel (video)

```bash
# Step 1: Create container
CONTAINER_ID=$(curl -s -X POST "https://graph.facebook.com/v25.0/$IG_ID/media" \
  -d "media_type=REELS" \
  -d "video_url=https://example.com/video.mp4" \
  -d "caption=Caption del reel #reels" \
  -d "access_token=$PAGE_TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 2: Wait for processing
curl -s "https://graph.facebook.com/v25.0/$CONTAINER_ID?fields=status_code&access_token=$PAGE_TOKEN"
# Poll until status_code = "FINISHED"

# Step 3: Publish
curl -X POST "https://graph.facebook.com/v25.0/$IG_ID/media_publish" \
  -d "creation_id=$CONTAINER_ID" \
  -d "access_token=$PAGE_TOKEN"
```

### Carousel (multiple images)

```bash
# Step 1: Create each item
IMG1=$(curl -s -X POST "https://graph.facebook.com/v25.0/$IG_ID/media" \
  -d "image_url=https://example.com/img1.jpg" \
  -d "is_carousel_item=true" \
  -d "access_token=$PAGE_TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

IMG2=$(curl -s -X POST "https://graph.facebook.com/v25.0/$IG_ID/media" \
  -d "image_url=https://example.com/img2.jpg" \
  -d "is_carousel_item=true" \
  -d "access_token=$PAGE_TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 2: Create carousel container
CAROUSEL=$(curl -s -X POST "https://graph.facebook.com/v25.0/$IG_ID/media" \
  -d "media_type=CAROUSEL" \
  -d "children=$IMG1,$IMG2" \
  -d "caption=Mi carrusel #carousel" \
  -d "access_token=$PAGE_TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 3: Publish
curl -X POST "https://graph.facebook.com/v25.0/$IG_ID/media_publish" \
  -d "creation_id=$CAROUSEL" \
  -d "access_token=$PAGE_TOKEN"
```

---

## Instagram — Read & Manage

### Account info

```bash
curl -s "https://graph.facebook.com/v25.0/$IG_ID?fields=username,followers_count,follows_count,media_count&access_token=$PAGE_TOKEN"
```

### Recent media

```bash
curl -s "https://graph.facebook.com/v25.0/$IG_ID/media?fields=id,caption,media_type,timestamp,like_count,comments_count,permalink&limit=10&access_token=$PAGE_TOKEN"
```

### Post insights

```bash
curl -s "https://graph.facebook.com/v25.0/MEDIA_ID/insights?metric=impressions,reach,engagement&access_token=$PAGE_TOKEN"
```

### Delete a post

```bash
curl -X DELETE "https://graph.facebook.com/v25.0/MEDIA_ID?access_token=$PAGE_TOKEN"
```

### Reply to a comment

```bash
curl -X POST "https://graph.facebook.com/v25.0/COMMENT_ID/replies" \
  -d "message=Tu respuesta" \
  -d "access_token=$PAGE_TOKEN"
```

---

## Token Management

### Page Token
- Stored in `~/.meta_tokens_cache.json` under `pages.<PAGE_ID>.access_token`
- **Never expires** (expires_at: 0)
- Data access expires ~60 days — renew before

### Renew tokens
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select app → Add permissions → Generate Access Token
3. Exchange for long-lived token via Graph API Explorer or the App Dashboard
4. Get new page token:
```bash
curl -s "https://graph.facebook.com/v25.0/me/accounts?access_token=LONG_LIVED_TOKEN"
```
5. Update `~/.meta_tokens_cache.json` with new tokens

---

## Tips

- **Never hardcode tokens or IDs** — always use environment variables or read from `~/.meta_tokens_cache.json`
- Instagram requires images/videos as **public URLs** (not local files)
- For local files on Instagram, upload to hosting first or use Facebook's photo upload
- Reels may take time to process — poll status before publishing
- Schedule Facebook posts at least 10 minutes in advance
- Instagram does NOT support native scheduling via API
- File permissions on cache: `chmod 600 ~/.meta_tokens_cache.json`
