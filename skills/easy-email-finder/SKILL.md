---
name: easy-email-finder
description: Search for businesses by industry/location and enrich them with verified email addresses, tech stack detection, and social media links using the Easy Email Finder API.
metadata: {"openclaw":{"emoji":"📧","homepage":"https://easyemailfinder.com","primaryEnv":"EEF_API_KEY","requires":{"env":["EEF_API_KEY"]}}}
---

# Easy Email Finder API

Use this skill to find business leads and their email addresses. The Easy Email Finder API lets you search Google Places for businesses, then enrich them with verified emails scraped from their websites.

## Authentication

All requests require a Bearer token. The API key is available in the `EEF_API_KEY` environment variable.

```
Authorization: Bearer $EEF_API_KEY
```

Get an API key at https://easyemailfinder.com/developer

## Base URL

```
https://easyemailfinder.com/api/v1
```

## Endpoints

### Search for businesses (free — no credits)

```bash
curl -X POST https://easyemailfinder.com/api/v1/search \
  -H "Authorization: Bearer $EEF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "dentists in denver", "pageToken": null}'
```

Returns business names, addresses, phone numbers, websites, ratings, and Google Maps links. Use `pageToken` from the response to get the next page.

### Enrich a website with emails (1 credit per call)

```bash
curl -X POST https://easyemailfinder.com/api/v1/enrich \
  -H "Authorization: Bearer $EEF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"website": "https://example-business.com"}'
```

Returns: `emails`, `techStack` (wordpress/shopify/wix/squarespace/webflow/custom), `socialLinks` (facebook, instagram, linkedin, twitter, youtube, tiktok).

### Batch enrich (1 credit per website, max 20)

```bash
curl -X POST https://easyemailfinder.com/api/v1/enrich-batch \
  -H "Authorization: Bearer $EEF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"websites": ["https://site1.com", "https://site2.com"]}'
```

### Search + enrich in one call (1 credit per result)

```bash
curl -X POST https://easyemailfinder.com/api/v1/search-and-enrich \
  -H "Authorization: Bearer $EEF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "plumbers in austin", "limit": 20}'
```

Combines search and enrichment. `limit` defaults to 20, max 60.

### Check credit balance (free)

```bash
curl https://easyemailfinder.com/api/v1/balance \
  -H "Authorization: Bearer $EEF_API_KEY"
```

### View usage stats (free)

```bash
curl "https://easyemailfinder.com/api/v1/usage?days=7" \
  -H "Authorization: Bearer $EEF_API_KEY"
```

## Response Format

All responses follow this envelope:

```json
{
  "data": { ... },
  "meta": {
    "requestId": "req_abc123",
    "creditsUsed": 1,
    "remainingCredits": 94.75
  }
}
```

Errors:

```json
{
  "error": { "code": "INSUFFICIENT_CREDITS", "message": "..." },
  "meta": { "requestId": "req_abc123" }
}
```

## Rate Limits

- Standard endpoints (search, balance, usage): 60 requests/minute
- Enrich endpoints: 10 requests/minute
- When rate limited, check the `Retry-After` response header

## Credit Costs

| Endpoint | Cost |
|----------|------|
| /v1/search | Free |
| /v1/enrich | 1 credit ($0.25) |
| /v1/enrich-batch | 1 credit per website |
| /v1/search-and-enrich | 1 credit per result |
| /v1/balance | Free |
| /v1/usage | Free |

## Typical Workflow

1. Use `/v1/search` to find businesses in a specific industry and location
2. Use `/v1/enrich` or `/v1/enrich-batch` to get emails for businesses with websites
3. Or use `/v1/search-and-enrich` to do both in one call
4. Check `/v1/balance` to monitor credit usage
