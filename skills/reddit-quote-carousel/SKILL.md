---
name: reddit-quote-carousel
description: Create an Instagram carousel from a popular-picks list with Reddit quotes. Cover slide uses "clean" style with "Top CATEGORY in Destination" title. Each attraction slide uses "quote" style with a real Reddit quote. Trigger phrase "reddit-quote". Use when Bernard says "reddit-quote" or asks for a Reddit-quote carousel.
---

# Reddit Quote Carousel

Instagram carousel: cover + attraction slides with Reddit quotes, sourced from a popular-picks list.

## Trigger

Bernard says **"reddit-quote"** → use this skill.

## Parameters

- **destination** (required): City/region (e.g. "Barcelona")
- **category** (required): What the picks are (e.g. "Cheap Eats", "Hidden Gems", "Date Night Spots")
- **popular_picks_url** (required): tabiji.ai popular-picks page URL to pull attractions + Reddit quotes from
- **reddit_post_count** (optional): Number of Reddit posts analyzed (for subtitle, e.g. "150+ posts"). Pull from the popular-picks page if available.

## Pipeline (3 chained sub-agents)

Working directory: `/tmp/ig-reddit-quote/`

### Sub-agent 1: Scrape Picks + Find Photos

1. **Fetch the popular-picks page** via `web_fetch` to get:
   - List of attractions (names)
   - A compelling Reddit quote for each attraction (look for vivid, specific, personal quotes — not generic praise)
   - The subreddit each quote came from (e.g. "r/london", "r/AskLondon")
   - Total Reddit post count if shown on the page

2. **Find photos** using `instagram-photo-find` workflow:
   - 1 hero photo for the destination (for cover slide)
   - 1 photo per attraction (for quote slides)
   - For each: `web_search` → download candidates → vision-score → keep best

3. **Write manifest** to `/tmp/ig-reddit-quote/manifest.json`:
```json
{
  "destination": "Barcelona",
  "category": "Cheap Eats",
  "reddit_post_count": 150,
  "cover_photo": "/tmp/ig-reddit-quote/cover-best.jpg",
  "slides": [
    {
      "name": "Bar Cañete",
      "quote": "Went here on a random Tuesday and had the best patatas bravas of my life. The old guy next to me ordered for me and everything was incredible.",
      "subreddit": "r/barcelona",
      "photo": "/tmp/ig-reddit-quote/bar-canete-best.jpg",
      "source_url": "instagram.com/p/XXX/"
    }
  ]
}
```

### Sub-agent 2: Text Overlays

Read manifest. Create overlays using `instagram-photo-text-overlay` skill.

**Slide 1 (Cover)** — `clean` style:
```bash
python3 /Users/psy/.openclaw/workspace/skills/instagram-photo-text-overlay/scripts/overlay.py \
  --input /tmp/ig-reddit-quote/cover-best.jpg \
  --output /tmp/ig-reddit-quote/slide-1.jpg \
  --title "Top {COUNT} {CATEGORY} in {DESTINATION}" \
  --subtitle "Insider Takes from Reddit ({N}+ posts)" \
  --style clean --watermark "tabiji.ai"
```

Where:
- `{COUNT}` = number of attractions
- `{CATEGORY}` = category (e.g. "Cheap Eats")
- `{DESTINATION}` = destination name
- `{N}` = reddit_post_count from manifest

**Slides 2+** — `quote` style, one per attraction:
```bash
python3 /Users/psy/.openclaw/workspace/skills/instagram-photo-text-overlay/scripts/overlay.py \
  --input /tmp/ig-reddit-quote/{slug}-best.jpg \
  --output /tmp/ig-reddit-quote/slide-{N}.jpg \
  --title "{ATTRACTION_NAME}" \
  --quote "{REDDIT_QUOTE}" \
  --author "{SUBREDDIT}" \
  --style quote --watermark "tabiji.ai"
```

Output: slides at `/tmp/ig-reddit-quote/slide-{1-N}.jpg`

### Sub-agent 3: Publish to Instagram

Same as `create-instagram-carousel-post` Sub-agent 3:
1. Host images in tabiji repo (`img/instagram/`)
2. Create carousel item containers
3. Create carousel container with caption
4. Publish
5. Cleanup hosted images + local temp files

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
