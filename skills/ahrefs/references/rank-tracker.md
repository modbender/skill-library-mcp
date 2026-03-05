# Rank Tracker API Reference

Track keyword rankings and monitor SERP positions over time.

**⚠️ Important**: Rank Tracker requires pre-configured projects in the Ahrefs web interface. You must set up tracking projects before using these API endpoints.

## Base URL
```
https://api.ahrefs.com/v3/rank-tracker/
```

## Setup Requirements

1. Log in to https://app.ahrefs.com
2. Navigate to Rank Tracker
3. Create a project and add keywords to track
4. Note your `project_id` (visible in URL or project settings)
5. Wait for initial crawl to complete

---

## Get Project Overview

**Endpoint**: `GET /rank-tracker/project`

Get overview metrics for a tracking project.

**Parameters**:
- `project_id` (required): Your Rank Tracker project ID

**Example**:
```bash
curl "https://api.ahrefs.com/v3/rank-tracker/project?project_id=12345" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response Fields**:
- `project_id`: Project identifier
- `project_name`: Project display name
- `domain`: Target domain being tracked
- `keywords_count`: Total keywords tracked
- `avg_position`: Average ranking position
- `visibility`: Visibility score
- `traffic_estimate`: Estimated organic traffic
- `last_updated`: Last crawl timestamp

---

## Get Project Keywords

**Endpoint**: `GET /rank-tracker/keywords`

List all tracked keywords with current positions.

**Parameters**:
- `project_id` (required): Project ID
- `limit` (optional): Max results (default: 100)
- `offset` (optional): Pagination offset
- `order_by` (optional): Sort field (e.g., `position:asc`, `volume:desc`)
- `filter` (optional): Filter keywords (e.g., `position_changed:up`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/rank-tracker/keywords?project_id=12345&limit=50&order_by=position:asc" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "keywords": [
    {
      "keyword": "seo tools",
      "position": 5,
      "previous_position": 7,
      "position_change": -2,
      "volume": 14000,
      "url": "https://example.com/seo-tools",
      "serp_features": ["featured_snippet"],
      "traffic_estimate": 850
    }
  ]
}
```

---

## Get Position History

**Endpoint**: `GET /rank-tracker/position-history`

Get historical ranking data for a specific keyword.

**Parameters**:
- `project_id` (required): Project ID
- `keyword` (required): Target keyword
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/rank-tracker/position-history?project_id=12345&keyword=seo+tools&date_from=2026-01-01&date_to=2026-02-18" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "keyword": "seo tools",
  "history": [
    {
      "date": "2026-02-18",
      "position": 5,
      "url": "https://example.com/seo-tools"
    },
    {
      "date": "2026-02-11",
      "position": 7,
      "url": "https://example.com/seo-tools"
    }
  ]
}
```

---

## Get Competitor Rankings

**Endpoint**: `GET /rank-tracker/competitors`

Compare your rankings with competitors for tracked keywords.

**Parameters**:
- `project_id` (required): Project ID
- `competitor_domains` (optional): Comma-separated competitor domains
- `limit` (optional): Max keywords to return

**Example**:
```bash
curl "https://api.ahrefs.com/v3/rank-tracker/competitors?project_id=12345&competitor_domains=competitor1.com,competitor2.com" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "competitors": [
    {
      "domain": "competitor1.com",
      "shared_keywords": 87,
      "avg_position": 8.5,
      "visibility": 42.3
    }
  ],
  "keyword_comparison": [
    {
      "keyword": "seo tools",
      "your_position": 5,
      "competitor1_position": 3,
      "competitor2_position": 12
    }
  ]
}
```

---

## Get SERP Features

**Endpoint**: `GET /rank-tracker/serp-features`

Track SERP features for your tracked keywords.

**Parameters**:
- `project_id` (required): Project ID
- `feature` (optional): Filter by specific SERP feature

**Example**:
```bash
curl "https://api.ahrefs.com/v3/rank-tracker/serp-features?project_id=12345" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Available SERP Features**:
- `featured_snippet`
- `people_also_ask`
- `local_pack`
- `knowledge_graph`
- `image_pack`
- `video_carousel`
- `site_links`
- `reviews`

---

## Share of Voice

**Endpoint**: `GET /rank-tracker/share-of-voice`

Calculate share of voice vs competitors.

**Parameters**:
- `project_id` (required): Project ID

**Example**:
```bash
curl "https://api.ahrefs.com/v3/rank-tracker/share-of-voice?project_id=12345" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "your_domain": {
    "domain": "example.com",
    "share_of_voice": 32.5,
    "estimated_traffic": 12500
  },
  "competitors": [
    {
      "domain": "competitor1.com",
      "share_of_voice": 45.2,
      "estimated_traffic": 18900
    }
  ]
}
```

---

## Best Practices

1. **Project Setup**: Create projects in Ahrefs web interface first
2. **Keyword Selection**: Track high-value keywords relevant to your business
3. **Regular Monitoring**: Check rankings weekly or bi-weekly
4. **Historical Data**: Use date ranges to analyze trends
5. **Competitor Tracking**: Add 3-5 main competitors for comparison
6. **SERP Features**: Monitor opportunities for featured snippets and other SERP features

---

## Cost Notes

- Rank Tracker API requests consume API units
- Frequency of checks affects unit consumption
- Consider caching position data if checking frequently
- Use date ranges to limit historical data fetched

---

## Limitations

- Projects must be pre-configured in Ahrefs web interface
- Initial crawl required before API data is available
- Position updates depend on project crawl frequency
- Maximum keywords per project varies by plan tier
