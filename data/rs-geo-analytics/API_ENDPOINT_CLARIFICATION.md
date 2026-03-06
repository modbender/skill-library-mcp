# API Endpoint Clarification

## Canonical Base URL

**Base:** `https://rankscale.ai`

All Rankscale Metrics API endpoints are served from `https://rankscale.ai` under the `/v1/metrics/` path prefix.

> ⚠️ The Cloud Functions URL (`https://us-central1-rankscale-2e08e.cloudfunctions.net`) is **deprecated** and must not be used. It has been removed from this skill as of v1.0.4.

---

## Endpoint Reference

All endpoints are relative to the base `https://rankscale.ai`:

| Resource | Method | Path |
|---|---|---|
| Brands | GET | `/v1/metrics/brands` |
| GEO Report | GET | `/v1/metrics/report` |
| Citations | GET | `/v1/metrics/citations` |
| Sentiment | GET | `/v1/metrics/sentiment` |
| Search Terms | GET | `/v1/metrics/search-terms-report` |

### Authentication

All requests require: `Authorization: Bearer <RANKSCALE_API_KEY>`

---

## Example

```bash
curl -H "Authorization: Bearer $RANKSCALE_API_KEY" \
  https://rankscale.ai/v1/metrics/brands
```
