# apipick Public Holidays - Full API Reference

**Base URL:** `https://www.apipick.com`
**Authentication:** All requests require `x-api-key: YOUR_API_KEY` header.
**Cost:** 1 credit per successful request.

---

## GET /api/holidays

Returns public holidays for a given country and year. Supports 100+ countries. Year range: 1900 to current year + 10.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `country` | string | Yes | ISO 3166-1 alpha-2 country code (e.g. `US`, `CN`, `GB`, `DE`, `JP`, `FR`) |
| `year` | integer | No | 4-digit year. Defaults to current year. |

**Common country codes:**

| Country | Code | Country | Code |
|---------|------|---------|------|
| United States | `US` | United Kingdom | `GB` |
| China | `CN` | Germany | `DE` |
| Japan | `JP` | France | `FR` |
| Australia | `AU` | Canada | `CA` |
| India | `IN` | Brazil | `BR` |
| South Korea | `KR` | Singapore | `SG` |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | `true` if request succeeded |
| `code` | integer | HTTP status code |
| `message` | string | Status message |
| `data.country` | string | ISO country code (uppercase) |
| `data.country_name` | string | Full English country name |
| `data.year` | integer | The queried calendar year |
| `data.total` | integer | Total number of public holidays returned |
| `data.holidays` | array | Array of holiday objects sorted by date |
| `data.holidays[].date` | string | Holiday date in `YYYY-MM-DD` format |
| `data.holidays[].name` | string | Official holiday name in English |
| `credits_used` | integer | Credits deducted for this request |
| `remaining_credits` | integer | Remaining credits in the account |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid country code or year value |
| 401 | Missing or invalid `x-api-key` |
| 402 | Insufficient account credits |

### Example

```bash
curl "https://www.apipick.com/api/holidays?country=US&year=2026" \
  -H "x-api-key: YOUR_API_KEY"
```

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
      {"date": "2026-01-19", "name": "Martin Luther King Jr. Day"},
      {"date": "2026-02-16", "name": "Presidents' Day"},
      {"date": "2026-05-25", "name": "Memorial Day"},
      {"date": "2026-07-03", "name": "Independence Day (observed)"},
      {"date": "2026-09-07", "name": "Labor Day"},
      {"date": "2026-10-12", "name": "Columbus Day"},
      {"date": "2026-11-11", "name": "Veterans Day"},
      {"date": "2026-11-26", "name": "Thanksgiving Day"},
      {"date": "2026-12-25", "name": "Christmas Day"}
    ]
  },
  "credits_used": 1,
  "remaining_credits": 99
}
```
