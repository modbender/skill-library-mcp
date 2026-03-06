---
name: Farseek — AI Job Search API
description: Find relevant job openings matched to your skills using AI-powered
  search across 22,700+ company boards and 20+ ATS platforms.
---

# Farseek — AI Job Search API

Find relevant job openings matched to your skills using AI-powered search across 22,700+ company boards and 20+ ATS platforms.

## What it does

Farseek searches a live database of job postings from Greenhouse, Lever, Ashby, Workday, SmartRecruiters, and more. It uses Claude to expand your skills into search terms, filter results by relevance, and rank matches into tiers.

## Endpoint

```
POST https://farseek.ai/api/v1/search
Content-Type: application/json
```

## Request

```json
{
  "skills": ["Python", "machine learning", "distributed systems"],
  "location": "San Francisco",
  "role": "Senior Software Engineer",
  "titles": ["Software Engineer", "Backend Developer"]
}
```

| Field      | Type       | Required | Description                          |
|------------|------------|----------|--------------------------------------|
| `skills`   | `string[]` | Yes      | Skills to match against (max 50)     |
| `location` | `string`   | No       | City or "Remote" (default: "Remote") |
| `role`     | `string`   | No       | Current/desired job title            |
| `titles`   | `string[]` | No       | Historical job titles for context    |

## Response

```json
{
  "jobs": [
    {
      "title": "ML Engineer",
      "company": "Anthropic",
      "location": "San Francisco, CA",
      "url": "https://boards.greenhouse.io/anthropic/jobs/123",
      "tier": 1,
      "tier_label": "Strong match",
      "haiku_score": 9,
      "broadened": false
    }
  ],
  "meta": {
    "total_results": 25,
    "location": "San Francisco",
    "tokens_used": 15000,
    "cost_usd": 0.003
  }
}
```

## Errors

| Code | Meaning             |
|------|---------------------|
| 400  | Missing/invalid skills array |
| 429  | Rate limited (10 req/min)    |
| 503  | Service unavailable          |

Errors return `{"error": {"code": "string", "message": "string"}}`.

## Notes

- CORS enabled (any origin)
- Returns up to 25 ranked results
- Tier 1 = best match, Tier 4 = broadest match
- Covers Greenhouse, Lever, Ashby, Workday, SmartRecruiters, BambooHR, Workable, JazzHR, Teamtailor, and more
