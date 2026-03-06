---
name: reddit-quote-topaz
description: Create an Instagram carousel from a popular-picks list with Reddit quotes + Topaz 2x upscaling. Cover = "clean" style ("Top CATEGORY in Destination"), attraction slides = "quote" style with Reddit quotes + subreddit attribution. All photos Topaz-enhanced before overlay. Trigger phrase "reddit-quote-topaz". Use when Bernard says "reddit-quote-topaz" or wants a Topaz-enhanced Reddit-quote carousel.
---

# Reddit Quote Carousel (Topaz Enhanced)

Same as `reddit-quote-carousel` but adds **Topaz Labs 2x AI upscale** after photo finding, before text overlays.

## Trigger

Bernard says **"reddit-quote-topaz"** → use this skill.
Bernard says **"reddit-quote"** → use `reddit-quote-carousel` (no Topaz).

## Parameters

- **destination** (required): City/region (e.g. "Barcelona")
- **category** (required): What the picks are (e.g. "Cheap Eats", "Hidden Gems", "Date Night Spots")
- **popular_picks_url** (required): tabiji.ai popular-picks page URL to pull attractions + Reddit quotes from
- **reddit_post_count** (optional): Number of Reddit posts analyzed (for subtitle). Pull from the page if available.

## Pipeline (3 chained sub-agents)

Working directory: `/tmp/ig-reddit-quote/`

### Sub-agent 1: Scrape Picks + Find Photos + Topaz Enhance

1. **Fetch the popular-picks page** via `web_fetch` to get:
   - List of attractions (names)
   - A compelling Reddit quote for each attraction (vivid, specific, personal — not generic praise)
   - The subreddit each quote came from (e.g. "r/london", "r/AskLondon")
   - Total Reddit post count if shown on the page

2. **Find photos** using `instagram-photo-find` workflow:
   - 1 hero photo for the destination (for cover slide)
   - 1 photo per attraction (for quote slides)
   - For each: `web_search` → download candidates → vision-score → keep best

3. **Topaz 2x Enhance each best photo:**
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
  --form "image=@/tmp/ig-reddit-quote/${slug}-best.jpg" \
  --output "/tmp/ig-reddit-quote/${slug}-enhanced.jpg"
```

If sync returns JSON with `process_id` instead of image bytes, use async flow:
```bash
# Submit async
RESPONSE=$(curl -s --request POST \
  --url https://api.topazlabs.com/image/v1/enhance/async \
  --header "X-API-Key: ${TOPAZ_API_KEY}" \
  --header 'content-type: multipart/form-data' \
  --form 'model=Low Resolution V2' \
  --form 'output_scale_factor=2' \
  --form 'output_format=jpeg' \
  --form "image=@/tmp/ig-reddit-quote/${slug}-best.jpg")

PROCESS_ID=$(echo "$RESPONSE" | jq -r '.process_id')

# Poll until Completed
while true; do
  STATUS=$(curl -s --header "X-API-Key: ${TOPAZ_API_KEY}" \
    "https://api.topazlabs.com/image/v1/status/${PROCESS_ID}" | jq -r '.status')
  [ "$STATUS" = "Completed" ] && break
  sleep 3
done

# Download
curl -s --header "X-API-Key: ${TOPAZ_API_KEY}" \
  "https://api.topazlabs.com/image/v1/download/${PROCESS_ID}" \
  --output "/tmp/ig-reddit-quote/${slug}-enhanced.jpg"
```

4. **Write manifest** to `/tmp/ig-reddit-quote/manifest.json`:
```json
{
  "destination": "Barcelona",
  "category": "Cheap Eats",
  "reddit_post_count": 150,
  "cover_photo": "/tmp/ig-reddit-quote/cover-enhanced.jpg",
  "slides": [
    {
      "name": "Bar Cañete",
      "quote": "Went here on a random Tuesday and had the best patatas bravas of my life.",
      "subreddit": "r/barcelona",
      "photo": "/tmp/ig-reddit-quote/bar-canete-enhanced.jpg",
      "original": "/tmp/ig-reddit-quote/bar-canete-best.jpg",
      "source_url": "instagram.com/p/XXX/",
      "topaz_enhanced": true
    }
  ]
}
```

### Sub-agent 2: Text Overlays

Read manifest. Create overlays using `instagram-photo-text-overlay` skill on **enhanced** images.

**Slide 1 (Cover)** — `clean` style:
```bash
python3 /Users/psy/.openclaw/workspace/skills/instagram-photo-text-overlay/scripts/overlay.py \
  --input /tmp/ig-reddit-quote/cover-enhanced.jpg \
  --output /tmp/ig-reddit-quote/slide-1.jpg \
  --title "Top {COUNT} {CATEGORY} in {DESTINATION}" \
  --subtitle "Insider Takes from Reddit ({N}+ posts)" \
  --style clean --watermark "tabiji.ai"
```

**Slides 2+** — `quote` style, one per attraction:
```bash
python3 /Users/psy/.openclaw/workspace/skills/instagram-photo-text-overlay/scripts/overlay.py \
  --input /tmp/ig-reddit-quote/{slug}-enhanced.jpg \
  --output /tmp/ig-reddit-quote/slide-{N}.jpg \
  --title "{ATTRACTION_NAME}" \
  --quote "{REDDIT_QUOTE}" \
  --author "{SUBREDDIT}" \
  --style quote --watermark "tabiji.ai"
```

Output: slides at `/tmp/ig-reddit-quote/slide-{1-N}.jpg`

### Sub-agent 3: Publish to Instagram

1. Host images in tabiji repo (`img/instagram/`), git push, use raw GitHub URLs
2. Create carousel item containers
3. Create carousel container with caption
4. Publish
5. Get permalink
6. Cleanup hosted images + local temp files

## Instagram API Auth

Keys from macOS Keychain:
- `instagram-access-token` — Graph API token
- `instagram-account-id` — IG user ID (17841449394591017)

## Topaz API Auth

- `topaz-api-key` — Topaz Labs API key (macOS Keychain)

## Caption Template

```
{flag_emoji} Top {COUNT} {CATEGORY} in {DESTINATION}

Real recommendations from {N}+ Reddit posts 🧵

📍 Swipe for the spots + what Redditors actually said:
1. {Attraction 1}
2. {Attraction 2}
...

Full list with maps, prices & more Reddit recs 👉 {POPULAR_PICKS_URL}

💬 {PROVOCATIVE_QUESTION — e.g. "What's the most overrated restaurant you've been to abroad?" or "Would you trust a stranger's Reddit rec over a Michelin star?"}

#{destination} #{category_tag} #redditfinds #traveltips #foodietravel #localfavorites #tabiji
```

## Tips

- Pick quotes that are **specific and personal** — "best patatas bravas of my life" beats "this place is great"
- Keep quotes under ~120 chars so they render well on the slide
- If a quote is too long, trim it but keep the vivid part
- The cover title should feel like a listicle: "Top 7 Cheap Eats in Barcelona"
- **Topaz model:** `Low Resolution V2` — designed for web-sourced images (our exact use case)
- **Topaz rate limits:** If HTTP 429, use exponential backoff. Sequential processing of 6-8 images should be fine.
- Keep originals in manifest so you can fall back if Topaz fails on a specific image
