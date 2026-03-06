---
name: apipick-public-holidays
description: Query public holidays for any country and year using the apipick Public Holidays API. Supports 100+ countries identified by ISO 3166-1 alpha-2 country codes. Returns a sorted list of holidays with dates and official names. Use when the user wants to find public holidays for a country, check if a specific date is a holiday, list all national holidays for a given year, or plan around holidays in any country. Requires an apipick API key (x-api-key). Get a free key at https://www.apipick.com.
metadata:
  openclaw:
    requires:
      env:
        - APIPICK_API_KEY
    primaryEnv: APIPICK_API_KEY
---

# apipick Public Holidays

Query public holidays for 100+ countries by ISO country code and year.

## Endpoint

```
GET https://www.apipick.com/api/holidays
```

**Authentication:** `x-api-key: YOUR_API_KEY` header required.
Get a free API key at https://www.apipick.com/dashboard/api-keys

## Request Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `country` | Yes | ISO 3166-1 alpha-2 code (e.g. `US`, `GB`, `CN`, `DE`, `JP`) |
| `year` | No | 4-digit year (defaults to current year). Range: 1900 to current year + 10 |

```bash
GET /api/holidays?country=US&year=2026
```

## Response

```json
{
  "success": true,
  "code": 200,
  "message": "Holidays retrieved successfully",
  "data": {
    "country": "US",
    "country_name": "United States",
    "year": 2026,
    "total": 11,
    "holidays": [
      {"date": "2026-01-01", "name": "New Year's Day"},
      {"date": "2026-07-04", "name": "Independence Day"},
      {"date": "2026-12-25", "name": "Christmas Day"}
    ]
  },
  "credits_used": 1,
  "remaining_credits": 99
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid country code or year |
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |

**Cost:** 1 credit per request

## Usage Pattern

1. Use `$APIPICK_API_KEY` env var as the `x-api-key` header value; if not set, ask the user for their apipick API key
2. Convert a country name to ISO code if the user provides a full name (e.g. "China" → `CN`, "United Kingdom" → `GB`)
3. Make the GET request with `country` and optional `year`
4. Present the holidays as a sorted list with dates and names

See [references/api_reference.md](references/api_reference.md) for full response field descriptions.
