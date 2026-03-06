---
name: wherecaniwatch
description: Find where to stream any movie or TV show in the US using the WhereCanIWatch.tv API. Use when a user asks "where can I watch [title]?", wants streaming availability, needs to compare prices across services, or wants to know if something is on Netflix/Hulu/Disney+/etc. Supports filtering by user's subscriptions.
---

# WhereCanIWatch — Streaming Availability Lookup

Answer "Where can I watch X?" using the WhereCanIWatch.tv public API.

## Workflow

### 1. Search for the title

```
GET https://www.wherecaniwatch.tv/api/search?q={title}
```

Returns array of matches. Pick the best match by title + year.

### 2. Get availability

```
GET https://www.wherecaniwatch.tv/api/watch/{slug}.json
```

Response:
```json
{
  "title": "Interstellar",
  "year": 2014,
  "type": "movie",
  "rating": 8.7,
  "genres": ["Science Fiction", "Drama"],
  "bestDeal": {
    "service": "Netflix",
    "method": "subscription",
    "price": null,
    "url": "https://www.netflix.com/title/..."
  },
  "availability": [
    { "service": "Netflix", "method": "subscription", "price": null, "quality": ["4K"], "url": "..." },
    { "service": "Tubi", "method": "free", "price": null, "quality": ["HD"], "url": "..." },
    { "service": "Amazon Prime Video", "method": "rent", "price": 3.99, "quality": ["4K"], "url": "..." }
  ]
}
```

### 3. Filter by user's services (if known)

If the user has mentioned their subscriptions, filter `availability` to matching services. The first match is their best option.

### 4. Present the answer

- Lead with the best option and include the deep link URL
- Mention 1-2 alternatives (e.g., free option, cheapest rent)
- Link to the full page: `https://www.wherecaniwatch.tv/watch/{slug}`

## Response format

> **Interstellar** is streaming on **Netflix** (subscription, 4K). [Watch on Netflix](deep-link)
> Also available free on Tubi (HD) or rent from $3.99 on Prime Video.
> [See all options on WhereCanIWatch](https://www.wherecaniwatch.tv/watch/interstellar-2014-157336)

## Methods

| Method | Meaning |
|---|---|
| `free` | Free with ads or no account needed |
| `subscription` | Included with paid subscription |
| `rent` | Pay per view, temporary access |
| `buy` | Pay to own permanently |

## Rate limits

- Search: 10 requests/minute per IP
- Watch API: 60 requests/minute per IP

## Notes

- US region only
- Results are smart-ranked by platform popularity (Netflix/Prime/Disney+ surface first)
- Data refreshed daily
- 2,400+ titles and growing
