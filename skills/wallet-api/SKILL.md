---
name: wallet-api
description: Interact with the BudgetBakers Wallet API for personal finance data. Use when the user needs to query accounts, categories, transactions (records), budgets, or templates from their Wallet app via the REST API. Requires WALLET_API_TOKEN environment variable.
---

# Wallet API Skill

Interact with the BudgetBakers Wallet personal finance API.

## Prerequisites

1. **Premium Wallet plan** required for API access
2. **API Token** from [web.budgetbakers.com/settings/apiTokens](https://web.budgetbakers.com/settings/apiTokens)
3. Set `WALLET_API_TOKEN` environment variable

## Quick Start

```bash
export WALLET_API_TOKEN="your_token_here"
./scripts/wallet-api.sh me
```

## API Reference

See [references/api-reference.md](references/api-reference.md) for:
- Authentication details
- Rate limiting (500 req/hour)
- Query filter syntax (text and range filters)
- Pagination parameters
- Data synchronization behavior
- Agent hints

## Available Commands

| Command | Description |
|---------|-------------|
| `me` | Current user info |
| `accounts` | List accounts |
| `categories` | List categories |
| `records` | List transactions |
| `budgets` | List budgets |
| `templates` | List templates |

## Query Parameters

All list endpoints support:
- `limit` (default 30, max 100)
- `offset` (default 0)

### Filter Examples

**Recent transactions:**
```bash
./wallet-api.sh records "recordDate=gte.2025-02-01&limit=50"
```

**Amount range:**
```bash
./wallet-api.sh records "amount=gte.100&amount=lte.500"
```

**Text search:**
```bash
./wallet-api.sh records "note=contains-i.grocery"
```

**Category + date:**
```bash
./wallet-api.sh records "categoryId=eq.<id>&recordDate=gte.2025-01-01"
```

### Filter Prefixes

| Prefix | Meaning |
|--------|---------|
| `eq.` | Exact match |
| `contains.` | Contains (case-sensitive) |
| `contains-i.` | Contains (case-insensitive) |
| `gt.` | Greater than |
| `gte.` | Greater than or equal |
| `lt.` | Less than |
| `lte.` | Less than or equal |

## Common Workflows

### Get Account Balances
```bash
./wallet-api.sh accounts
```

### List Categories for Organization
```bash
./wallet-api.sh categories
```

### Recent Spending
```bash
./wallet-api.sh records "recordDate=gte.2025-02-01&limit=100"
```

### Filter by Payee
```bash
./wallet-api.sh records "payee=contains-i.amazon"
```

## Data Sync Considerations

- Initial sync returns 409 Conflict — wait and retry
- Recent app changes may not appear immediately
- Check `X-Last-Data-Change-At` header for freshness

## Rate Limit Handling

Watch for:
- `429 Too Many Requests` when exceeding 500/hour
- `X-RateLimit-Remaining` header
- Add `agentHints=true` for rate limit warnings
