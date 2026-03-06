# Domain Trust Check — API Reference

**Base URL:** `https://app.outtake.ai/api/v1`

**Authentication:** Bearer token in the `Authorization` header.

```
Authorization: Bearer $OUTTAKE_API_KEY
```

## POST /trust/check

Check a single URL.

**Request:**

```json
{
  "url": "https://suspicious-site.com/login"
}
```

**Response (200):**

```json
{
  "data": {
    "url": "https://suspicious-site.com/login",
    "domain": "suspicious-site.com",
    "verdict": "malicious",
    "confidence": 0.92,
    "safe_to_visit": "unsafe",
    "recommended_action": "block",
    "checked_at": "2026-02-26T12:00:00.000Z"
  }
}
```

### Response Fields

| Field | Values | Description |
|---|---|---|
| `verdict` | `malicious`, `suspicious`, `safe`, `unknown` | Threat classification |
| `confidence` | `0.0` – `1.0` | `1.0` = human-reviewed, `0.7–0.99` = ML, `0.0` = no data |
| `safe_to_visit` | `safe`, `unsafe`, `unknown` | Binary browsing safety |
| `recommended_action` | `block`, `warn`, `proceed`, `use_caution` | Suggested action |

## POST /trust/check-batch

Check up to 50 URLs in one request.

**Request:**

```json
{
  "urls": [
    "https://suspicious-site.com",
    "https://google.com",
    "https://totally-legit-bank.xyz"
  ]
}
```

**Response (200):**

```json
{
  "data": {
    "results": [
      {
        "index": 0,
        "success": true,
        "data": {
          "url": "https://suspicious-site.com",
          "domain": "suspicious-site.com",
          "verdict": "malicious",
          "confidence": 0.92,
          "safe_to_visit": "unsafe",
          "recommended_action": "block",
          "checked_at": "2026-02-26T12:00:00.000Z"
        }
      }
    ],
    "success_count": 3,
    "failure_count": 0
  }
}
```

- Maximum 50 URLs per request — more than 50 returns `400`
- Results maintain the same order as input URLs
- Invalid URLs return per-item failures without consuming daily quota

## Rate Limits

| Limit | Window | Value |
|---|---|---|
| Burst | Per minute | 10 requests |
| Daily | Per 24 hours | 10,000 URL checks |

Batch requests count each valid URL toward the daily limit.

On rate limit, the API returns `429`:

```json
{
  "error": "Daily check limit exceeded (10000/day)",
  "code": "RATE_LIMIT_DAILY",
  "retry_after_seconds": 3600
}
```

## Error Codes

| Status | Code | Meaning |
|---|---|---|
| `400` | `INVALID_URL` | URL is malformed |
| `429` | `RATE_LIMIT_BURST` | Too many requests per minute |
| `429` | `RATE_LIMIT_DAILY` | Daily quota exhausted |

On 429, wait `retry_after_seconds` before retrying. Do not retry 400 errors.
