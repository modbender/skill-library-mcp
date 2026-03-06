---
name: lowkey-viral
description: >
  Create short-form social media videos and photo carousel slideshows using the
  lowkey viral API. Generate AI-powered TikTok videos, Instagram Reels, and
  carousel posts programmatically. Supports 2x2 grid videos (1080x1920, 5s,
  30fps) with background music and photo slideshows with text overlays. Use when
  the user wants to create social media content, short videos, viral clips,
  reels, TikToks, carousels, slideshows, or any vertical video for social
  platforms. Requires a lowkey viral API key (PRO or ULTIMATE plan) from
  https://lowkeyviral.com/dashboard/api-keys.
metadata:
  clawdbot:
    requires:
      env:
        - LOWKEY_VIRAL_API_KEY
      bins:
        - curl
    primaryEnv: LOWKEY_VIRAL_API_KEY
    homepage: https://github.com/tiotdev/lowkey-viral
    emoji: "🎬"
---

# lowkey viral — AI Social Media Video & Slideshow Creator

Create short-form vertical videos and photo carousel slideshows for TikTok, Instagram Reels, and other social platforms using the lowkey viral REST API.

## Prerequisites

**You need a lowkey viral API key to use this skill.**

1. Sign up at https://lowkeyviral.com and subscribe to a PRO or ULTIMATE plan.
2. Create an API key from the dashboard: https://lowkeyviral.com/dashboard/api-keys
3. Set the key as an environment variable:
   ```bash
   export LOWKEY_VIRAL_API_KEY="lkv_sk_your_key_here"
   ```

API keys are prefixed with `lkv_sk_` and are shown only once at creation time.

## What You Can Create

### Grid Videos (2x2 grid)
- 1080x1920 vertical MP4 video, 5 seconds, 30fps
- 4 images arranged in a 2x2 grid with a text hook overlay
- Optional background music from 20 CC0-licensed tracks
- 3 layout designs: `default`, `withCaptions`, `noSpaces`

### Photo Slideshows (carousel)
- 2-10 portrait slides (1080x1920) with text overlays
- 3 caption styles: `classic_bold`, `background_bar`, `neon_glow`
- Ready for Instagram carousel posts or TikTok photo mode

## Authentication

All API requests go to `https://lowkeyviral.com/api/v1/` and require the API key as a Bearer token:

```
Authorization: Bearer $LOWKEY_VIRAL_API_KEY
```

## Rate Limits

- PRO plan: 10 requests/minute
- ULTIMATE plan: 30 requests/minute
- Progress polling: 60 requests/minute (all plans)
- 429 responses include a `Retry-After` header

## Workflow: Create a Grid Video

### Step 1 — Generate AI Briefs (2 credits)

```bash
curl -s -X POST https://lowkeyviral.com/api/v1/briefs \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A travel app for Gen-Z backpackers"}'
```

Returns 5 briefs. Pick the best one and note its `id`.

### Step 2 — Generate Images (4-8 credits)

```bash
curl -s -X POST https://lowkeyviral.com/api/v1/briefs/BRIEF_ID/generate \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_model": "z_image_turbo"}'
```

Image models and costs per image:
- `z_image_turbo` — 1 credit/image (fastest)
- `p_image` — 2 credits/image (high quality)
- `flux_2_dev` — 2 credits/image (highly detailed)

Grid briefs always have 4 images.

### Step 3 — Render Video (1 credit)

```bash
curl -s -X POST https://lowkeyviral.com/api/v1/briefs/BRIEF_ID/render \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"design": "default", "soundtrack": "City Sunshine"}'
```

Returns `{"render_id": "..."}`.

### Step 4 — Poll Until Done (0 credits)

```bash
curl -s https://lowkeyviral.com/api/v1/briefs/BRIEF_ID/render/RENDER_ID/progress \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY"
```

Poll every 2-3 seconds. Responses:

- In progress: `{"type": "progress", "progress": 0.45, "stalled": false, ...}`
- Done: `{"type": "done", "url": "https://...out.mp4", "size": 1234567}`
- Error: `{"type": "error", "message": "..."}`

### Shortcut — One-Call Grid Video

Create a manual brief with `render: true` to do everything in one request:

```bash
curl -s -X POST https://lowkeyviral.com/api/v1/briefs/manual \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "hook": "these coffee shops are insane",
    "title": "Best Coffee Shops",
    "render": true,
    "design": "default",
    "soundtrack": "City Sunshine",
    "images": [
      {"title": "Cafe A", "description": "A cozy minimalist cafe with latte art"},
      {"title": "Cafe B", "description": "Industrial style coffee shop with exposed brick"},
      {"title": "Cafe C", "description": "Hidden garden cafe with hanging plants"},
      {"title": "Cafe D", "description": "Rooftop cafe with city skyline view"}
    ],
    "image_model": "z_image_turbo"
  }'
```

Images with `description` but no `url` are AI-generated. The response includes a `render_id` for polling.

## Workflow: Create a Photo Slideshow

### Step 1 — Generate AI Briefs (2 credits)

```bash
curl -s -X POST https://lowkeyviral.com/api/v1/briefs \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A skincare brand for 20-somethings", "type": "slideshow", "slide_count": 6}'
```

Parameters:
- `type`: must be `"slideshow"`
- `slide_count`: 4-10 (default 6)

### Step 2 — Generate Images (1-2 credits per slide)

```bash
curl -s -X POST https://lowkeyviral.com/api/v1/briefs/BRIEF_ID/generate \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_model": "z_image_turbo"}'
```

Images are generated in portrait 9:16 orientation automatically.

### Step 3 — Render Slides (1 credit, synchronous)

```bash
curl -s -X POST https://lowkeyviral.com/api/v1/briefs/BRIEF_ID/render \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"caption_style": "classic_bold"}'
```

Returns finished slides immediately (no polling needed):
```json
{
  "slides": [
    {"index": 0, "url": "https://...slide-0.jpg"},
    {"index": 1, "url": "https://...slide-1.jpg"}
  ]
}
```

### Shortcut — One-Call Slideshow

```bash
curl -s -X POST https://lowkeyviral.com/api/v1/briefs/manual \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "slideshow",
    "caption_style": "classic_bold",
    "render": true,
    "images": [
      {"title": "Step 1", "description": "Woman applying cleanser, soft morning light"},
      {"title": "Step 2", "description": "Serum dropper on clear skin, close-up"},
      {"title": "Step 3", "description": "Moisturizer application, dewy skin glow"}
    ],
    "image_model": "z_image_turbo"
  }'
```

Response includes `slides` array immediately. Note: `hook` is not accepted for slideshows — it is automatically set to the first slide's `title`.

## Uploading Custom Images

If you have your own images, upload them first:

```bash
# 1. Get presigned upload URL
curl -s -X POST https://lowkeyviral.com/api/v1/uploads \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content_type": "image/jpeg"}'

# Response: {"upload_url": "https://...", "file_url": "https://...", ...}

# 2. Upload the file (max 10 MB)
curl -X PUT "UPLOAD_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary @photo.jpg

# 3. Use file_url in your brief
```

Supported types: `image/jpeg`, `image/png`, `image/webp`.

## Checking Account & Credits

```bash
curl -s https://lowkeyviral.com/api/v1/account \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY"
```

Returns: `{"credits": 42, "plan_type": "PRO", "next_reset_date": "..."}`

## Listing & Managing Briefs

```bash
# List all briefs (paginated)
curl -s "https://lowkeyviral.com/api/v1/briefs?limit=20" \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY"

# Filter by type
curl -s "https://lowkeyviral.com/api/v1/briefs?type=slideshow" \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY"

# Get single brief
curl -s https://lowkeyviral.com/api/v1/briefs/BRIEF_ID \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY"

# Delete a brief
curl -s -X DELETE https://lowkeyviral.com/api/v1/briefs/BRIEF_ID \
  -H "Authorization: Bearer $LOWKEY_VIRAL_API_KEY"
```

## Credit Costs Summary

| Operation | Grid | Slideshow |
|-----------|------|-----------|
| AI briefs (5 returned) | 2 | 2 |
| Manual brief | 0 | 0 |
| Images (z_image_turbo) | 4 total | 1/image |
| Images (p_image) | 8 total | 2/image |
| Images (flux_2_dev) | 8 total | 2/image |
| Render | 1 | 1 |

**Full AI grid video:** 7-11 credits. **Full AI slideshow (6 slides):** 9-15 credits. **Bring your own images:** 1 credit to render.

## Valid Options

### Grid Designs
- `default` — standard 2x2 layout
- `withCaptions` — adds text captions on each image
- `noSpaces` — edge-to-edge compact grid

### Slideshow Caption Styles
- `classic_bold` — white text with black outline
- `background_bar` — white text on dark semi-transparent bar
- `neon_glow` — bright green (#00ff88) text with glow effect

### Soundtracks (Grid Only)
Advertime, And Just Like That, Blippy Trance, Brewing Potions, City Sunshine, Funshine, Happy Whistling Ukulele, I Guess What I'm Trying to Say, La Citadelle, Lukewarm Banjo, Magical Transition, Martini Sunset, Meditating Beat, Night in Venice, River Meditation, Soundtrack From the Starcourt Mall, Strength of the Titans, Study and Relax, Sun Up Gunned Down, The Celebrated Minuet

### Image Models
- `z_image_turbo` — fastest, 1 credit/image
- `p_image` — high quality, 2 credits/image
- `flux_2_dev` — highly detailed, 2 credits/image

## Error Handling

All errors return:
```json
{"error": {"code": "error_code", "message": "Human-readable description"}}
```

| Status | Code | Meaning |
|--------|------|---------|
| 401 | unauthorized | Invalid or missing API key |
| 403 | forbidden | PRO or ULTIMATE plan required |
| 402 | insufficient_credits | Not enough credits |
| 422 | validation_error | Bad parameters |
| 404 | not_found | Resource not found |
| 429 | rate_limited | Too many requests (check Retry-After header) |
| 500 | internal_error | Server error |

## Data & Trust

- All requests go to `https://lowkeyviral.com/api/v1/` only.
- Your API key is sent as a Bearer token in the Authorization header.
- Uploaded images are stored on AWS S3 (us-east-1).
- Generated videos and slides are hosted on S3 via CloudFront.
- No data is sent to any third-party service beyond lowkeyviral.com.
