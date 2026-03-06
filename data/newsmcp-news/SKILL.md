---
name: newsmcp
description: Real-time world news briefings with AI-clustered events, topic classification, and geographic filtering. No API key needed.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - curl
    emoji: "📰"
    homepage: https://newsmcp.io
---

# World News Skill

Get real-time world news from an AI-powered news aggregation service. Stories are clustered into **events** (deduplicated across multiple sources), summarized, classified by topic, and tagged by geography.

**No API key required. No authentication. Just call the API.**

## Why This Is Different

- **Events, not articles** — individual articles are clustered into stories, so you get one summary per story instead of 20 duplicates
- **Pre-summarized** — every event has an AI-generated summary, no need to read full articles
- **Classified** — 12 topic categories and 100+ geographic regions
- **Importance signals** — `sources_count` (how many outlets covered it) and `impact_score` (AI-assessed significance)
- **Multi-source** — each event lists all source articles with titles, URLs, and domains

## API Base URL

```
https://newsmcp.io/v1
```

## Endpoints

### 1. Get News Events

```bash
curl -s "https://newsmcp.io/v1/news/?hours=24&per_page=10&order_by=-sources_count"
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | int | 24 | Time window (1-168, i.e. up to 7 days) |
| `topics` | string | — | Comma-separated topic slugs (e.g. `politics,military`) |
| `geo` | string | — | Comma-separated geo slugs (e.g. `europe,united-states`) |
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Results per page (max 50) |
| `order_by` | string | `-sources_count` | Sort field. Options: `sources_count`, `entries_count`, `impact_score`, `first_seen_at`, `last_seen_at` (prefix `-` for descending) |

**Response shape:**
```json
{
  "events": [
    {
      "id": "uuid",
      "summary": "AI-generated event summary",
      "topics": ["politics", "military"],
      "geo": ["europe", "ukraine"],
      "entries_count": 15,
      "sources_count": 8,
      "first_seen_at": "2026-03-03T10:00:00Z",
      "last_seen_at": "2026-03-03T14:00:00Z",
      "impact_score": 4,
      "entries": [
        {
          "title": "Article headline",
          "url": "https://example.com/article",
          "domain": "example.com",
          "published_at": "2026-03-03T12:00:00Z"
        }
      ]
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 10
}
```

### 2. Get Event Detail

```bash
curl -s "https://newsmcp.io/v1/news/{event_id}/"
```

Returns the same fields as the list, plus `context` — extended background and analysis of the event.

### 3. List Available Topics

```bash
curl -s "https://newsmcp.io/v1/news/topics/"
```

Returns: `politics`, `economy`, `technology`, `science`, `health`, `environment`, `sports`, `culture`, `crime`, `military`, `education`, `society`

### 4. List Available Regions

```bash
curl -s "https://newsmcp.io/v1/news/regions/"
```

Returns continents (`europe`, `asia`, `africa`, `north-america`, `south-america`, `oceania`) and countries (e.g. `united-states`, `ukraine`, `china`, `lithuania`, etc.). Each region has a `type` field: `"continent"` or `"country"`.

## How to Use This Skill

When the user asks for news, headlines, or current events:

1. **Default briefing** — Fetch top events from the last 24 hours sorted by importance:
   ```bash
   curl -s "https://newsmcp.io/v1/news/?hours=24&per_page=10&order_by=-sources_count"
   ```

2. **Topic-specific** — If the user asks about a specific topic (e.g. "tech news", "sports"), use the `topics` parameter:
   ```bash
   curl -s "https://newsmcp.io/v1/news/?topics=technology&hours=24"
   ```

3. **Region-specific** — If the user asks about a region (e.g. "European news", "what's happening in Asia"), use the `geo` parameter:
   ```bash
   curl -s "https://newsmcp.io/v1/news/?geo=europe&hours=24"
   ```

4. **Combined filters** — Topics and geo can be combined:
   ```bash
   curl -s "https://newsmcp.io/v1/news/?topics=politics,military&geo=europe&hours=48"
   ```

5. **Deep dive** — For more detail on a specific event, fetch the event detail:
   ```bash
   curl -s "https://newsmcp.io/v1/news/{event_id}/"
   ```

## Formatting the Briefing

Present results as a clean news briefing:

- Lead with the most important events (highest `sources_count` or `impact_score`)
- For each event, show the summary and note how many sources covered it
- Include 1-2 source links for each event so the user can read more
- Group by topic or region if the user asked for a broad overview
- Mention the time window and number of events found
- If `topics` or `geo` arrays are present, use them to add context tags

## Topic Slugs Reference

`politics` `economy` `technology` `science` `health` `environment` `sports` `culture` `crime` `military` `education` `society`

## Example Interaction

**User:** "What's happening in the world today?"

**Action:** Fetch `https://newsmcp.io/v1/news/?hours=24&per_page=10&order_by=-sources_count`

**User:** "Give me the latest on Ukraine"

**Action:** Fetch `https://newsmcp.io/v1/news/?geo=ukraine&hours=48&order_by=-last_seen_at`

**User:** "Any tech news this week?"

**Action:** Fetch `https://newsmcp.io/v1/news/?topics=technology&hours=168&order_by=-sources_count`
