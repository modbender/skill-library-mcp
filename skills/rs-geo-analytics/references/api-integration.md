# Rankscale API Integration Reference

**Base URL:** `https://rankscale.ai`  
**Auth:** `Authorization: Bearer <RANKSCALE_API_KEY>`  
**Format:** JSON request/response  
**Rate Limit:** 60 req/min per key (429 on breach)

---

## Authentication

All endpoints require Bearer token authentication.

```http
GET /v1/metrics/brands HTTP/1.1
Host: rankscale.ai
Authorization: Bearer rk_YOUR_API_KEY_HERE
Content-Type: application/json
User-Agent: openclaw-rs-geo-analytics/1.0.1
```

### API Key Format

```
rk_<hash>_<brandId>
```

Replace `<hash>` and `<brandId>` with your actual credentials.

- `rk_` — static prefix  
- `<hash>` — 8-char alphanumeric token hash (example: `YOUR_API_KEY_HERE`)
- `<brandId>` — brand identifier (example: `YOUR_BRAND_ID_HERE`)

The brand ID can be extracted from the API key automatically.

---

## Endpoints

### 1. GET /v1/metrics/brands

List all brands associated with this API key.

**Request:**
```http
GET /v1/metrics/brands
Authorization: Bearer rk_YOUR_API_KEY_HERE
```

**Response (200):**
```json
{
  "brands": [
    {
      "id": "YOUR_BRAND_ID_HERE",
      "name": "Rankscale",
      "domain": "rankscale.ai",
      "createdAt": "2025-09-01T00:00:00Z",
      "plan": "pro"
    }
  ],
  "total": 1
}
```

**Error Responses:**

| Code | Body | Meaning |
|------|------|---------|
| 401 | `{"error":"Unauthorized"}` | Invalid/expired API key |
| 403 | `{"error":"Forbidden"}` | Key lacks permission |
| 429 | `{"error":"Rate limit exceeded","retryAfter":30}` | Too many requests |

---

### 2. GET /v1/metrics/report

Get the GEO visibility score and rank for a brand.

**Request:**
```http
GET /v1/metrics/report?brandId=YOUR_BRAND_ID_HERE
Authorization: Bearer rk_YOUR_API_KEY_HERE
```

**Query Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `brandId` | string | yes | Brand identifier |
| `period` | string | no | `week` (default), `month`, `quarter` |

**Response (200):**
```json
{
  "brandId": "YOUR_BRAND_ID_HERE",
  "brandName": "Rankscale",
  "score": 72,
  "rank": 3,
  "change": 3,
  "period": "week",
  "generatedAt": "2026-02-19T00:00:00Z",
  "breakdown": {
    "citations": 28,
    "sentiment": 22,
    "coverage": 22
  }
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `score` | int (0–100) | Overall GEO visibility score |
| `rank` | int | Rank among tracked brands (1 = best) |
| `change` | int | Score delta vs. previous period (+/-) |
| `breakdown` | object | Score component weights (sum ≤ 100) |

**Alternative Format (some accounts):**
```json
{
  "geoScore": 72,
  "rankPosition": 3,
  "weeklyDelta": 3,
  "visibilityScore": 72
}
```

The skill normalizes both formats via `normalizeReport()`.

---

### 3. GET /v1/metrics/citations

Get citation count, rate, and top sources for a brand.

**Request:**
```http
GET /v1/metrics/citations?brandId=YOUR_BRAND_ID_HERE
Authorization: Bearer rk_YOUR_API_KEY_HERE
```

**Query Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `brandId` | string | yes | Brand identifier |
| `period` | string | no | `week`, `month`, `quarter` |
| `limit` | int | no | Max sources returned (default: 10) |

**Response (200):**
```json
{
  "brandId": "YOUR_BRAND_ID_HERE",
  "count": 847,
  "rate": 34,
  "industryAvg": 28,
  "sources": [
    {
      "domain": "techcrunch.com",
      "mentions": 42,
      "lastSeen": "2026-02-18"
    },
    {
      "domain": "g2.com",
      "mentions": 31,
      "lastSeen": "2026-02-17"
    }
  ],
  "period": "week"
}
```

**Alternative Format:**
```json
{
  "total": 847,
  "citationRate": 34,
  "benchmarkRate": 28,
  "topSources": [...]
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `count` / `total` | int | Raw citation count this period |
| `rate` / `citationRate` | float | % of tracked queries citing this brand |
| `industryAvg` / `benchmarkRate` | float | Category average for comparison |
| `sources` / `topSources` | array | Top referring domains |

---

### 4. GET /v1/metrics/sentiment

Get AI-generated sentiment breakdown for brand mentions.

**Request:**
```http
GET /v1/metrics/sentiment?brandId=YOUR_BRAND_ID_HERE
Authorization: Bearer rk_YOUR_API_KEY_HERE
```

**Response Format A (float 0–1):**
```json
{
  "brandId": "YOUR_BRAND_ID_HERE",
  "positive": 0.61,
  "neutral": 0.29,
  "negative": 0.10,
  "period": "week",
  "sampleSize": 412
}
```

**Response Format B (nested scores, 0–100):**
```json
{
  "brandId": "YOUR_BRAND_ID_HERE",
  "scores": {
    "pos": 61,
    "neu": 29,
    "neg": 10
  },
  "period": "week",
  "sampleSize": 412
}
```

Both formats normalized by `normalizeSentiment()` to:
```js
{ positive: 61.0, neutral: 29.0, negative: 10.0 }
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `positive` | float | % of mentions with positive tone |
| `neutral` | float | % of mentions with neutral/informational tone |
| `negative` | float | % of mentions with negative/critical tone |
| `sampleSize` | int | Number of AI responses analyzed |

---

### 5. GET /v1/metrics/search-terms-report

Get top search queries where this brand is cited in AI answers.

**Request:**
```http
GET /v1/metrics/search-terms-report?brandId=YOUR_BRAND_ID_HERE
Authorization: Bearer rk_YOUR_API_KEY_HERE
```

**Query Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `brandId` | string | yes | Brand identifier |
| `limit` | int | no | Max terms returned (default: 20, max: 100) |
| `period` | string | no | `week`, `month`, `quarter` |

**Response (200):**
```json
{
  "brandId": "YOUR_BRAND_ID_HERE",
  "terms": [
    {
      "query": "best ai rank tracker",
      "mentions": 18,
      "rank": 1,
      "sentiment": "positive"
    },
    {
      "query": "rankscale reviews",
      "mentions": 12,
      "rank": 2,
      "sentiment": "positive"
    },
    {
      "query": "ai search visibility tools",
      "mentions": 9,
      "rank": 1,
      "sentiment": "neutral"
    }
  ],
  "total": 47,
  "period": "week"
}
```

**Alternative Formats:**
```json
{ "data": [...], "searchTerms": [...], "results": [...] }
```

Each term object normalizes to:
```js
{ query: string, mentions: number }
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Skill Action |
|------|---------|--------------|
| 200 | Success | Process response |
| 401 | Unauthorized | Auth error + show settings link |
| 403 | Forbidden | Auth error + check key permissions |
| 404 | Not found | NotFoundError, try brand discovery |
| 429 | Rate limit | Exponential backoff (1s, 2s, 4s) |
| 500 | Server error | Retry 3x then graceful error |
| 503 | Service unavailable | Retry with backoff |

### Exponential Backoff

```
Attempt 1: wait 1000ms
Attempt 2: wait 2000ms + jitter
Attempt 3: wait 4000ms + jitter
Attempt 4: fail with ApiError
```

### Rate Limit Headers (when available)

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1708300800
Retry-After: 30
```

---

## Request Examples

### cURL — Full Report

```bash
API_KEY="rk_YOUR_API_KEY_HERE"
BRAND_ID="YOUR_BRAND_ID_HERE"
BASE="https://rankscale.ai"

# GEO Score
curl -H "Authorization: Bearer $API_KEY" \
  "$BASE/metrics/report?brandId=$BRAND_ID"

# Citations
curl -H "Authorization: Bearer $API_KEY" \
  "$BASE/metrics/citations?brandId=$BRAND_ID"

# Sentiment
curl -H "Authorization: Bearer $API_KEY" \
  "$BASE/metrics/sentiment?brandId=$BRAND_ID"

# Search Terms
curl -H "Authorization: Bearer $API_KEY" \
  "$BASE/metrics/search-terms-report?brandId=$BRAND_ID"
```

### Node.js — Minimal Client

```js
const apiKey = process.env.RANKSCALE_API_KEY;  // rk_YOUR_API_KEY_HERE
const brandId = process.env.RANKSCALE_BRAND_ID;  // YOUR_BRAND_ID_HERE
const base = 'https://rankscale.ai';

async function get(path) {
  const res = await fetch(`${base}/${path}`, {
    headers: { Authorization: `Bearer ${apiKey}` }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

const [report, citations, sentiment, terms] = await Promise.all([
  get(`metrics/report?brandId=${brandId}`),
  get(`metrics/citations?brandId=${brandId}`),
  get(`metrics/sentiment?brandId=${brandId}`),
  get(`metrics/search-terms-report?brandId=${brandId}`),
]);
```

---

## SDK Notes

- No official SDK at time of implementation (RS-126)
- HTTP/2 supported on production endpoint
- Request compression not required
- Response always UTF-8 JSON
- Timestamps in ISO 8601 (UTC)
