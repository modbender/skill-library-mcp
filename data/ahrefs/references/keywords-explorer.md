# Keywords Explorer API Reference

Complete reference for Ahrefs Keywords Explorer API endpoints.

## Base URL
```
https://api.ahrefs.com/v3/keywords-explorer/
```

## Authentication
```
Authorization: Bearer {AHREFS_API_TOKEN}
```

---

## Keyword Overview

**Endpoint**: `GET /keywords-explorer/overview`

Get comprehensive metrics for a single keyword.

**Parameters**:
- `keyword` (required): Target keyword
- `country` (required): 2-letter country code (e.g., `us`, `au`, `uk`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/keywords-explorer/overview?keyword=seo+tools&country=us" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response Fields**:
- `keyword`: The searched keyword
- `volume`: Monthly search volume
- `keyword_difficulty`: Difficulty score (0-100)
- `cpc`: Cost per click (USD)
- `parent_topic`: Broader topic keyword
- `traffic_potential`: Estimated monthly traffic for #1 ranking
- `serp_features`: Array of SERP features present
- `serp_updated`: Last SERP data update timestamp
- `clicks`: Estimated clicks from search results
- `clicks_per_search`: Average clicks per search

---

## Related Keywords

**Endpoint**: `GET /keywords-explorer/related-keywords`

Find keywords related to your target keyword.

**Parameters**:
- `keyword` (required): Target keyword
- `country` (required): 2-letter country code
- `limit` (optional): Max results (default: 100, max: 1000)
- `offset` (optional): Pagination offset
- `order_by` (optional): Sort field (e.g., `volume:desc`, `keyword_difficulty:asc`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/keywords-explorer/related-keywords?keyword=seo+tools&country=us&limit=50&order_by=volume:desc" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "keywords": [
    {
      "keyword": "best seo tools",
      "volume": 8100,
      "keyword_difficulty": 82,
      "cpc": 31.20,
      "traffic_potential": 12500
    }
  ]
}
```

---

## Keyword Ideas

**Endpoint**: `GET /keywords-explorer/keyword-ideas`

Get keyword suggestions based on your seed keyword.

**Parameters**:
- `keyword` (required): Seed keyword
- `country` (required): 2-letter country code
- `mode` (optional): `phrase`, `questions`, `related` (default: `phrase`)
- `limit` (optional): Max results
- `min_volume` (optional): Minimum search volume filter
- `max_keyword_difficulty` (optional): Maximum KD filter

**Example**:
```bash
curl "https://api.ahrefs.com/v3/keywords-explorer/keyword-ideas?keyword=seo&country=us&mode=questions&limit=100" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

---

## Keyword Difficulty

**Endpoint**: `GET /keywords-explorer/keyword-difficulty`

Get detailed keyword difficulty breakdown.

**Parameters**:
- `keyword` (required): Target keyword
- `country` (required): 2-letter country code

**Example**:
```bash
curl "https://api.ahrefs.com/v3/keywords-explorer/keyword-difficulty?keyword=seo+tools&country=us" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response Fields**:
- `keyword_difficulty`: Overall difficulty (0-100)
- `difficulty_breakdown`: Array of ranking pages and their metrics
- `estimated_visits`: Estimated monthly visits for #1 position
- `estimated_links_needed`: Approximate referring domains needed to rank

---

## SERP Overview (from Keywords Explorer)

**Endpoint**: `GET /keywords-explorer/serp-overview`

Get SERP analysis for a keyword.

**Parameters**:
- `keyword` (required): Target keyword
- `country` (required): 2-letter country code
- `limit` (optional): Number of SERP results to return (default: 10, max: 100)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/keywords-explorer/serp-overview?keyword=seo+tools&country=us&limit=10" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response Fields**:
- `serp_results`: Array of ranking pages
  - `position`: Ranking position
  - `url`: Page URL
  - `domain`: Root domain
  - `domain_rating`: DR of the domain
  - `url_rating`: UR of the page
  - `backlinks`: Number of backlinks to page
  - `referring_domains`: Number of referring domains
  - `traffic`: Estimated organic traffic to page
  - `keywords`: Number of organic keywords

---

## Keyword Metrics (Batch)

**Endpoint**: `POST /keywords-explorer/batch/overview`

Get metrics for multiple keywords in one request.

**Parameters** (JSON body):
- `keywords` (required): Array of keywords (max 100)
- `country` (required): 2-letter country code

**Example**:
```bash
curl -X POST "https://api.ahrefs.com/v3/keywords-explorer/batch/overview" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["seo tools", "keyword research", "backlink analysis"],
    "country": "us"
  }'
```

**Response**:
```json
{
  "results": [
    {
      "keyword": "seo tools",
      "volume": 14000,
      "keyword_difficulty": 75,
      "cpc": 25.50
    }
  ]
}
```

---

## Available Countries

Common country codes:
- `us` - United States
- `uk` - United Kingdom
- `au` - Australia
- `ca` - Canada
- `de` - Germany
- `fr` - France
- `es` - Spain
- `it` - Italy
- `nl` - Netherlands
- `br` - Brazil
- `in` - India
- `jp` - Japan

For full list, see Ahrefs API documentation.

---

## Cost Optimization

Keywords Explorer requests cost API units based on:
- Number of keywords analyzed
- Number of rows returned
- Complexity of data requested

**Tips**:
1. Use batch endpoints for multiple keywords
2. Limit results with `limit` parameter
3. Filter by volume/difficulty to reduce results
4. Cache frequently accessed keyword data

---

## Error Handling

Common errors:
- `400` - Invalid country code or keyword format
- `401` - Invalid API token
- `403` - Plan limits exceeded or feature not available
- `429` - Rate limit exceeded

Always check response status and handle errors appropriately.
