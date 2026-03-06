# BudgetBakers Wallet API Reference

## Overview

The Wallet API provides programmatic access to personal finance data from the BudgetBakers Wallet app.

- **Base URL:** `https://rest.budgetbakers.com/wallet`
- **OpenAPI Spec:** `https://rest.budgetbakers.com/wallet/openapi/ui`
- **Authentication:** Bearer token (API key from web app settings)

## Authentication

All endpoints require an API token in the Authorization header:

```
Authorization: Bearer <your_api_token>
```

Tokens are generated in the [Web app](https://web.budgetbakers.com/settings/apiTokens). **Premium plan required.**

## Rate Limiting

Token Bucket algorithm:
- **Capacity:** 500 requests/hour per client
- **Exceeded:** Returns 429 Too Many Requests

**Headers:**
- `X-RateLimit-Limit`: 500
- `X-RateLimit-Remaining`: 487

## Pagination

Supported on all User Data endpoints:

| Parameter | Default | Max | Description |
|-----------|---------|-----|-------------|
| `limit`   | 30      | 100 | Items per page |
| `offset`  | 0       | -   | Items to skip |

Response includes `nextOffset` when more results available.

## Query Filters

### Text Filters

Format: `prefix.value`

| Prefix | Meaning | Example |
|--------|---------|---------|
| `eq.` | Exact match | `payee=eq.Amazon` |
| `contains.` | Contains (case-sensitive) | `note=contains.Bill` |
| `contains-i.` | Contains (case-insensitive) | `note=contains-i.grocery` |

Up to 2 filters for AND logic: `note=contains-i.grocery&note=contains-i.market`

### Range Filters

For numeric and datetime fields (`amount`, `recordDate`, `createdAt`):

| Prefix | Meaning | Example |
|--------|---------|---------|
| `eq.` | Equals | `amount=eq.100` |
| `gt.` | Greater than | `amount=gt.100` |
| `gte.` | Greater than or equal | `amount=gte.100` |
| `lt.` | Less than | `amount=lt.500` |
| `lte.` | Less than or equal | `amount=lte.500` |

**Date-only semantics:**
- `gt.2025-01-14` → `gte.2025-01-15T00:00:00Z`
- `eq.2025-01-13` → full day of Jan 13

**AND logic:** Up to 2 conditions or comma-separated: `amount=gte.100,lte.500`

## Data Synchronization

Data syncs from Wallet app to API. Changes may not appear immediately.

### Initial Sync

Returns 409 Conflict during first sync:
```json
{
  "error": "init_sync_in_progress",
  "message": "Data synchronization in progress. Please retry later.",
  "retry_after_minutes": 5
}
```

### Ongoing Sync Headers

| Header | Example | Description |
|--------|---------|-------------|
| `X-Last-Data-Change-At` | 2024-01-28T14:23:45Z | Last modification timestamp |
| `X-Last-Data-Change-Rev` | r1234 | Revision counter |
| `X-Sync-In-Progress` | false | More changes may follow |

## Agent Hints

Add `agentHints=true` to any request for advisory information:

| Type | Severity | When Generated |
|------|----------|----------------|
| `pagination.has_more` | instruction | More results available |
| `result.partial_match` | info | Some IDs not found |
| `result.empty` | info | No records match filters |
| `param.inferred` | info | Date bound auto-inferred |
| `rate_limit.warning` | warning | Approaching rate limit |
| `data.recency` | info | Data recently modified |

## Endpoints Overview

### User Data

- `GET /accounts` - List accounts
- `GET /categories` - List categories
- `GET /records` - List transactions
- `GET /budgets` - List budgets
- `GET /templates` - List templates

### User Info

- `GET /me` - Current user info

## Common Patterns

### Fetch Recent Transactions

```
GET /records?recordDate=gte.2025-01-01&limit=50&agentHints=true
```

### Filter by Amount Range

```
GET /records?amount=gte.100&amount=lte.500
```

### Filter by Category and Date

```
GET /records?categoryId=eq.<id>&recordDate=gte.2025-01-01
```
