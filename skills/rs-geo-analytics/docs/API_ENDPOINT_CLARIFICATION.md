# API Endpoint Clarification

## Canonical Base URL

**Base:** `https://rankscale.ai`

All Rankscale Metrics API endpoints are served from `https://rankscale.ai` under the `/v1/metrics/` path prefix.

---

## Endpoint Reference

### JSON Reporting (POST Endpoints)

| Resource | Method | Path | Requires |
|---|---|---|---|
| GEO Report | POST | `v1/metrics/report` | brandId |
| Search Terms Report | POST | `v1/metrics/search-terms-report` | brandId |
| Sentiment | POST | `v1/metrics/sentiment` | brandId |
| Citations | POST | `v1/metrics/citations` | brandId |

### Utility (GET Endpoints)

| Resource | Method | Path | Requires |
|---|---|---|---|
| Brands | GET | `v1/metrics/brands` | — |
| Search Terms | GET | `v1/metrics/search-terms?brandId=<id>` | brandId (query param) |

---

## Authentication

All requests require:
```
Authorization: Bearer <RANKSCALE_API_KEY>
```

All responses are JSON.

---

## Examples

### GET Brands
```bash
curl -H "Authorization: Bearer $RANKSCALE_API_KEY" \
  https://rankscale.ai/v1/metrics/brands
```

### GET Search Terms
```bash
curl -H "Authorization: Bearer $RANKSCALE_API_KEY" \
  "https://rankscale.ai/v1/metrics/search-terms?brandId=YOUR_BRAND_ID"
```

### POST GEO Report
```bash
curl -X POST \
  -H "Authorization: Bearer $RANKSCALE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"brandId": "YOUR_BRAND_ID"}' \
  https://rankscale.ai/v1/metrics/report
```

### JavaScript (Fetch)

**GET:**
```js
const API_BASE = 'https://rankscale.ai';
const res = await fetch(`${API_BASE}/v1/metrics/brands`, {
  headers: { Authorization: `Bearer ${process.env.RANKSCALE_API_KEY}` }
});
```

**POST:**
```js
const API_BASE = 'https://rankscale.ai';
const res = await fetch(`${API_BASE}/v1/metrics/report`, {
  method: 'POST',
  headers: { 
    Authorization: `Bearer ${process.env.RANKSCALE_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ brandId: 'YOUR_BRAND_ID' })
});
```
