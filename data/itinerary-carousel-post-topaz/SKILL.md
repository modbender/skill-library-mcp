---
name: itinerary-carousel-post-topaz
description: Create and publish an Instagram carousel post from a tabiji.ai itinerary, with Topaz Labs AI image enhancement. Same as itinerary-carousel-post but adds a Topaz upscale/enhance step after photo finding and before text overlays. Use when asked to create an Instagram carousel with Topaz enhancement.
---

# Create Instagram Carousel Post (Topaz Enhanced)

End-to-end pipeline: itinerary URL → photo sourcing → **Topaz AI enhance** → text overlays → Instagram carousel publish.

Identical to `itinerary-carousel-post` except Sub-agent 1 includes a Topaz enhancement step after selecting the best photo for each subject.

## Parameters

- **itinerary_url** (required): tabiji.ai itinerary URL (e.g. `https://tabiji.ai/i/thaw-dome/`)
- **destination** (required): City/region name (e.g. "Kuala Lumpur")
- **attractions** (required): List of 5 attraction names + short descriptions
- **caption** (optional): Custom caption. If omitted, generate one with destination name, attraction list, CTA to link in bio, and relevant hashtags.

## Pipeline (3 chained sub-agents recommended)

Split into 3 sub-agents for reliability. Each writes outputs to `/tmp/ig-carousel/`.

### Sub-agent 1: Photo Finding + Topaz Enhancement

Use the `instagram-photo-find` skill workflow for each subject (1 destination + 5 attractions = 6 total).

For each subject:
1. `web_search`: `site:instagram.com/p/ "{subject}" photo` (10 results)
2. Download top 5 candidates: `curl -s -L -o /tmp/ig-carousel/raw-{slug}-{n}.jpg "https://www.instagram.com/p/{shortcode}/media/?size=l"`
3. Vision-score each with: "Rate 1-10 as hero destination photo for {subject}. Description + score only."
4. Keep best per subject → `/tmp/ig-carousel/{slug}-best.jpg`

**5. Topaz Enhance each best image:**
```bash
TOPAZ_API_KEY=$(security find-generic-password -s "topaz-api-key" -w)

curl --request POST \
  --url https://api.topazlabs.com/image/v1/enhance \
  --header "X-API-Key: ${TOPAZ_API_KEY}" \
  --header 'accept: image/jpeg' \
  --header 'content-type: multipart/form-data' \
  --form 'model=Low Resolution V2' \
  --form 'output_scale_factor=2' \
  --form 'output_format=jpeg' \
  --form "image=@/tmp/ig-carousel/${slug}-best.jpg" \
  --output "/tmp/ig-carousel/${slug}-enhanced.jpg"
```

If the sync endpoint times out or returns a `process_id` instead of image bytes, use the async flow:

```bash
# Async: submit
RESPONSE=$(curl -s --request POST \
  --url https://api.topazlabs.com/image/v1/enhance/async \
  --header "X-API-Key: ${TOPAZ_API_KEY}" \
  --header 'content-type: multipart/form-data' \
  --form 'model=Low Resolution V2' \
  --form 'output_scale_factor=2' \
  --form 'output_format=jpeg' \
  --form "image=@/tmp/ig-carousel/${slug}-best.jpg")

PROCESS_ID=$(echo "$RESPONSE" | jq -r '.process_id')

# Poll status until Completed
while true; do
  STATUS=$(curl -s --header "X-API-Key: ${TOPAZ_API_KEY}" \
    "https://api.topazlabs.com/image/v1/status/${PROCESS_ID}" | jq -r '.status')
  [ "$STATUS" = "Completed" ] && break
  sleep 3
done

# Download result
curl -s --header "X-API-Key: ${TOPAZ_API_KEY}" \
  "https://api.topazlabs.com/image/v1/download/${PROCESS_ID}" \
  --output "/tmp/ig-carousel/${slug}-enhanced.jpg"
```

**Model choice:** `Low Resolution V2` — designed for web-sourced images (exactly our use case). Handles JPEG compression artifacts, low resolution, and general softness. Fast and cheap.

**Parameters explained:**
- `output_scale_factor=2` — doubles the input resolution (2x upscale). For typical IG-sourced images (~1080px), this produces ~2160px which gives the overlay step plenty of resolution to work with.
- `output_format=jpeg` — keeps file size reasonable for IG's 8MB limit

Output: 6 enhanced images at `/tmp/ig-carousel/{slug}-enhanced.jpg` + JSON manifest at `/tmp/ig-carousel/manifest.json`:
```json
[{"slug": "kuala-lumpur", "subject": "Kuala Lumpur", "score": 7, "path": "/tmp/ig-carousel/kuala-lumpur-enhanced.jpg", "original": "/tmp/ig-carousel/kuala-lumpur-best.jpg", "source": "instagram.com/p/XXX/", "topaz_enhanced": true}]
```

### Sub-agent 2: Text Overlays

Read manifest from sub-agent 1. Run overlay script for each **enhanced** image.

**Slide 1 (cover)** — clean style:
```bash
python3 skills/instagram-photo-text-overlay/scripts/overlay.py \
  --input /tmp/ig-carousel/{dest-slug}-enhanced.jpg \
  --output /tmp/ig-carousel/slide-1.jpg \
  --title "{N} Day {DESTINATION} Itinerary Highlights" \
  --style clean --watermark "tabiji.ai"
```

**Slides 2–6** — quote style per attraction with insider tip:
```bash
python3 skills/instagram-photo-text-overlay/scripts/overlay.py \
  --input /tmp/ig-carousel/{slug}-enhanced.jpg \
  --output /tmp/ig-carousel/slide-{N}.jpg \
  --title "{ATTRACTION}" \
  --quote "{Specific insider tip about THIS attraction — must directly reference the place in the title, not a generic travel tip}" \
  --author "tabiji.ai" \
  --style quote --watermark "tabiji.ai"
```

Output: 6 overlay images at `/tmp/ig-carousel/slide-{1-6}.jpg`

### Sub-agent 3: Publish to Instagram

1. **Host images publicly** — copy slides to tabiji repo (`img/instagram/`), git push, use raw GitHub URLs (`https://raw.githubusercontent.com/psyduckler/tabiji/main/img/instagram/slide-{N}.jpg`). Wait ~30s after push for GitHub CDN.

2. **Create carousel item containers** (one per slide):
```bash
curl -s -X POST "https://graph.facebook.com/v21.0/${IG_USER}/media" \
  -d "image_url=${PUBLIC_URL}" \
  -d "is_carousel_item=true" \
  -d "access_token=${IG_TOKEN}"
```

3. **Create carousel container** with all children + caption:
```bash
curl -s -X POST "https://graph.facebook.com/v21.0/${IG_USER}/media" \
  --data-urlencode "caption=${CAPTION}" \
  -d "media_type=CAROUSEL" \
  -d "children=${CHILD_IDS}" \
  -d "access_token=${IG_TOKEN}"
```

4. **Publish**:
```bash
curl -s -X POST "https://graph.facebook.com/v21.0/${IG_USER}/media_publish" \
  -d "creation_id=${CAROUSEL_ID}" \
  -d "access_token=${IG_TOKEN}"
```

5. **Get permalink** (or verify publish on rate-limit error):

If `media_publish` returns a `POST_ID`, get the permalink directly:
```bash
curl -s "https://graph.facebook.com/v21.0/${POST_ID}?fields=permalink&access_token=${IG_TOKEN}"
```

**If `media_publish` returns error 2207051 (rate limit / action blocked):** Instagram sometimes processes the request despite returning an error. Always verify by checking the account's recent media before declaring failure:
```bash
curl -s "https://graph.facebook.com/v21.0/${IG_USER}/media?fields=id,timestamp,permalink&limit=1&access_token=${IG_TOKEN}"
```
If the most recent post timestamp is within the last few minutes, the publish likely succeeded — grab that permalink.

6. **Cleanup hosted images** — after publish is confirmed, delete the images from the tabiji repo and push:
```bash
cd /path/to/tabiji/repo
git rm img/instagram/slide-*.jpg
git commit -m "cleanup: remove instagram carousel images after publish"
git push
```
Also clean up local temp files:
```bash
rm -rf /tmp/ig-carousel/
```

Output: Instagram post URL

## Instagram API Auth

Keys from macOS Keychain:
- `instagram-access-token` — Graph API token
- `instagram-account-id` — IG user ID (17841449394591017)

## Topaz API Auth

Key from macOS Keychain:
- `topaz-api-key` — Topaz Labs API key

## Caption Template

```
🇲🇾 {N} Nights in {Destination} — {Itinerary Subtitle}

{One-line hook about the trip}

📍 Swipe through our top 5 picks:
1. {Attraction 1} — {one-line reason}
2. {Attraction 2} — {one-line reason}
3. {Attraction 3} — {one-line reason}
4. {Attraction 4} — {one-line reason}
5. {Attraction 5} — {one-line reason}

Full free itinerary with tips, prices & Reddit recs 👉 {ITINERARY_URL}

💬 {PROVOCATIVE_QUESTION — e.g. "Is 5 nights enough for {Destination} or do you need more?" or "What's the one thing most tourists get wrong about {Destination}?"}

#{destination_hashtag} #{country} #travelitinerary #foodietravel #southeastasia #asiatravel #travelguide #tabiji
```

## Tips

- Raw GitHub URLs work for IG image_url; tabiji.ai Cloudflare CDN may trigger format validation errors.
- Add `sleep 1` between container creation calls to avoid rate limits.
- If a subject yields low photo scores (<5), broaden search: try Unsplash/Flickr or more specific landmark names.
- Islamic/cultural museums tend to have fewer quality IG photos — try searching the museum's official IG handle.
- **Topaz sync endpoint** may return image bytes directly (check Content-Type header). If it returns JSON with `process_id`, switch to async flow.
- **Topaz rate limits:** If you get HTTP 429, use exponential backoff. Processing 6 images sequentially should be fine.
- **Keep originals:** The manifest stores both `path` (enhanced) and `original` so you can compare quality or fall back if Topaz fails on a specific image.
