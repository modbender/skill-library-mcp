---
name: itinerary-carousel-post
description: Create and publish an Instagram carousel post from a tabiji.ai itinerary. Given an itinerary URL, finds Instagram-worthy photos for the destination + top attractions, applies text overlays, and publishes as a carousel. Use when asked to create an Instagram post, carousel, or social content for a tabiji destination or itinerary.
---

# Create Instagram Carousel Post

End-to-end pipeline: itinerary URL → photo sourcing → text overlays → Instagram carousel publish.

## Parameters

- **itinerary_url** (required): tabiji.ai itinerary URL (e.g. `https://tabiji.ai/i/thaw-dome/`)
- **destination** (required): City/region name (e.g. "Kuala Lumpur")
- **attractions** (required): List of 5 attraction names + short descriptions
- **caption** (optional): Custom caption. If omitted, generate one with destination name, attraction list, CTA to link in bio, and relevant hashtags.

## Pipeline (3 chained sub-agents recommended)

Split into 3 sub-agents for reliability. Each writes outputs to `/tmp/ig-carousel/`.

### Sub-agent 1: Photo Finding

Use the `instagram-photo-find` skill workflow for each subject (1 destination + 5 attractions = 6 total).

For each subject:
1. `web_search`: `site:instagram.com/p/ "{subject}" photo` (10 results)
2. Download top 5 candidates: `curl -s -L -o /tmp/ig-carousel/raw-{slug}-{n}.jpg "https://www.instagram.com/p/{shortcode}/media/?size=l"`
3. Vision-score each with: "Rate 1-10 as hero destination photo for {subject}. Description + score only."
4. Keep best per subject → `/tmp/ig-carousel/{slug}-best.jpg`

Output: 6 best images + JSON manifest at `/tmp/ig-carousel/manifest.json`:
```json
[{"slug": "kuala-lumpur", "subject": "Kuala Lumpur", "score": 7, "path": "/tmp/ig-carousel/kuala-lumpur-best.jpg", "source": "instagram.com/p/XXX/"}]
```

### Sub-agent 2: Text Overlays

Read manifest from sub-agent 1. Run overlay script for each image.

**Slide 1 (cover)** — clean style:
```bash
python3 skills/instagram-photo-text-overlay/scripts/overlay.py \
  --input /tmp/ig-carousel/{dest-slug}-best.jpg \
  --output /tmp/ig-carousel/slide-1.jpg \
  --title "{N} Day {DESTINATION} Itinerary Highlights" \
  --style clean --watermark "tabiji.ai"
```

**Slides 2–6** — quote style per attraction with insider tip:
```bash
python3 skills/instagram-photo-text-overlay/scripts/overlay.py \
  --input /tmp/ig-carousel/{slug}-best.jpg \
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
