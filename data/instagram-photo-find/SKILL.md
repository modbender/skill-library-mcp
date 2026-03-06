---
name: instagram-photo-find
description: Find high-quality Instagram photos for any destination or place. Searches for Instagram posts via web search, downloads candidate images, vision-scores them for quality and iconic-ness, and returns the best matches with source URLs. Use when you need travel/destination photos from Instagram, hero images for a location, or Instagram post images for any place or attraction.
---

# Instagram Photo Find

Find the best Instagram photo for a given destination or place name.

## Workflow

### Step 1 — Search for Instagram post URLs

Search Brave for: `site:instagram.com/p/ {destination} popular photo`

- Request 10 results
- If the destination is a specific attraction/restaurant, use its name directly (e.g. `site:instagram.com/p/ "Barton Springs" Austin`)

### Step 2 — Filter candidates by title

From search results, pick the top 5-6 candidates based on titles that suggest scenic/visual content:

**Prefer titles with:**
- Visual/emotional language ("beautiful", "colors", "stunning", "golden hour", "aerial", "skyline")
- Specific landmark names
- Travel/photography language ("travel", "explore", "photography")

**Skip titles that suggest:**
- Brand/corporate posts (Nike, concerts, conferences)
- Personal diary posts ("photo dump", "my trip")
- Celebrity/influencer selfies
- Non-photo content (events, announcements)

### Step 3 — Download images

For each candidate, extract the image via:

```
https://www.instagram.com/p/{shortcode}/media/?size=l
```

- Use `curl -s -L` (follows the 302 redirect to CDN)
- Skip any that return non-200 or < 10KB (likely broken/removed)
- Save to `/tmp/` with descriptive names

### Step 4 — Vision-score each image

Run each downloaded image through the vision model with this prompt:

> Describe briefly. Rate 1-10 as a hero destination photo for {destination} (iconic, scenic, represents the place well). Description + score only.

### Step 5 — Return results

Return images ranked by score. For each result, provide:
- Score and brief description
- Instagram post URL (`instagram.com/p/{shortcode}/`)
- Local file path

## Parameters

- **destination** (required): Place name (e.g. "Mexico City", "Taormina Italy", "Barton Springs Austin")
- **count** (optional, default 2): How many top results to return
- **search_variant** (optional): Additional search terms to append (e.g. "photography", "travel guide")

## Tips

- For broad destinations (cities/countries), the generic search works well
- For specific attractions, quote the name: `"Palacio de Bellas Artes"`
- If first search yields low scores (< 6), retry with landmark-specific queries
- The `/media/?size=l` endpoint requires no authentication
- Carousel posts return only the first image
- Video posts may return a thumbnail
