# Nova Net Worth Public API v1 — Reference

## Base URL
`https://api.novanetworth.com/api/v1/agent`

## Authentication
All requests require an API key in the Authorization header:
```
Authorization: Bearer nova_your_key_here
```

Generate API keys at: Settings → Integrations in your Nova dashboard.
Requires SuperNova ($19.99/mo) or Galaxy (enterprise) subscription.

## Endpoints

### GET /briefing ⭐ (Recommended)
Complete financial snapshot in a single call. Use for "how are my finances?" queries.

Response:
```json
{
  "success": true,
  "data": {
    "user": { "firstName": "Jesse", "subscriptionTier": "GALAXY", "currency": "USD" },
    "netWorth": { "current": 65063889, "previousMonth": 65272195, "change": -208306, "currency": "USD" },
    "spending": { "currentMonth": 14320857, "previousMonth": 7134804, "changePercent": 100.7, "currency": "USD" },
    "topAccounts": [
      { "id": "acct_1", "name": "Brokerage", "type": "INVESTMENT", "balance": 25400000, "currency": "USD", "mask": "****1234" }
    ],
    "goals": [
      { "id": "goal_1", "name": "Emergency Fund", "targetAmount": 2500000, "currentAmount": 1825000, "progressPercent": 73.0, "status": "on_track" }
    ],
    "healthScore": { "score": 69, "grade": "C" },
    "insights": [
      { "id": "ins_1", "type": "celebration", "title": "Amazing Savings Rate", "recommendation": "..." }
    ],
    "accountCount": 10
  },
  "meta": { "requestId": "req_abc123", "timestamp": "2026-02-25T18:31:41.138Z" }
}
```
Combines summary, top accounts, goals, spending, health, and insights. One call for a full briefing.

### GET /summary
Net worth headline numbers.

Response:
```json
{
  "success": true,
  "data": {
    "user": { "firstName": "Jesse" },
    "netWorth": { "amount": 65063889, "currency": "USD" },
    "monthOverMonthChange": { "amount": -208306, "currency": "USD" },
    "accountCount": 34,
    "subscriptionTier": "GALAXY",
    "financialHealthScore": 69,
    "lastSyncTime": "2026-02-25T12:00:00Z"
  },
  "meta": { "requestId": "req_abc123", "timestamp": "..." }
}
```

### GET /accounts
All financial accounts with balances, grouped by type.

Response:
```json
{
  "success": true,
  "data": {
    "accounts": [
      {
        "id": "acct_123",
        "name": "Checking Account",
        "type": "CHECKING",
        "institution": "Chase",
        "currentBalance": 1234500,
        "currency": "USD",
        "isActive": true,
        "mask": "****4567",
        "group": "depository"
      }
    ],
    "groupedByType": {
      "depository": [...],
      "investment": [...]
    }
  }
}
```
Groups: depository, investment, loan, credit, property, vehicle, crypto, other.

### GET /transactions
Recent transactions with filtering and delta polling.

Query params:
- `days` (1-90, default 30) — lookback window (ignored if `since` is set)
- `limit` (1-100, default 50) — max results
- `category` (string) — filter by Plaid category (e.g. FOOD_AND_DRINK)
- `account` (string) — filter by account ID
- `since` (ISO date) — delta polling: only transactions after this timestamp

Response:
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "txn_123",
        "name": "Starbucks",
        "merchant": "Starbucks",
        "amount": 575,
        "currency": "USD",
        "date": "2026-02-25T14:30:00.000Z",
        "pending": false,
        "category": "FOOD_AND_DRINK",
        "categoryDetail": "FOOD_AND_DRINK_COFFEE",
        "account": { "id": "acct_1", "name": "Checking", "type": "CHECKING" }
      }
    ],
    "count": 1,
    "filters": { "days": 30, "since": null, "limit": 50, "category": null, "account": null }
  }
}
```

### GET /goals
Financial goals with progress tracking.

Response:
```json
{
  "success": true,
  "data": {
    "goals": [
      {
        "id": "goal_123",
        "name": "Emergency Fund",
        "targetAmount": 2500000,
        "currentAmount": 1825000,
        "progressPercent": 73.0,
        "targetDate": "2026-08-01T00:00:00.000Z",
        "status": "on_track"
      }
    ]
  }
}
```
Status values: `on_track`, `overdue`, `completed`.

### GET /spending?months=1
Monthly spending by category.

Query params:
- `months` (1-12, default 1)

Response:
```json
{
  "success": true,
  "data": {
    "months": 1,
    "currency": "USD",
    "total": 485000,
    "byCategory": [
      { "category": "FOOD_AND_DRINK", "amount": 84700 },
      { "category": "RENT_AND_UTILITIES", "amount": 150000 }
    ],
    "comparisonToPreviousPeriod": {
      "previousTotal": 462000,
      "changeAmount": 23000,
      "changePercent": 4.98
    }
  }
}
```

### GET /insights
AI-generated financial insights.

Response:
```json
{
  "success": true,
  "data": {
    "insights": [
      {
        "id": "ins_123",
        "type": "celebration",
        "title": "Amazing Savings Rate",
        "recommendation": "Your savings rate is exceptional. Keep it up!",
        "createdAt": "2026-02-24T09:00:00.000Z"
      }
    ]
  }
}
```

### GET /net-worth/history?days=30
Net worth snapshots over time.

Query params:
- `days` (1-365, default 30)

Response:
```json
{
  "success": true,
  "data": {
    "days": 30,
    "history": [
      {
        "date": "2026-02-25T00:00:00.000Z",
        "netWorth": 65063889,
        "totalAssets": 79100000,
        "totalLiabilities": 14036111,
        "currency": "USD"
      }
    ]
  }
}
```

### GET /health-score
Financial health score with component breakdown.

Response:
```json
{
  "success": true,
  "data": {
    "totalScore": 69,
    "grade": "C",
    "breakdown": {
      "netWorthGrowth": { "score": 100, "weight": 0.25 },
      "debtToAssetRatio": { "score": 45, "weight": 0.2 },
      "creditUtilization": { "score": 78, "weight": 0.15 },
      "emergencyFund": { "score": 30, "weight": 0.2 },
      "savingsRate": { "score": 90, "weight": 0.2 }
    },
    "insights": ["Your net worth growth is excellent!"],
    "recommendations": ["Build emergency fund to cover 6 months"],
    "hasBureauCreditScore": false
  }
}
```

## Rate Limits

| Tier | Limit | Window |
|------|-------|--------|
| SuperNova ($19.99/mo) | 100 requests | per hour |
| Galaxy (Enterprise) | 1,000 requests | per hour |

Response headers:
- `X-RateLimit-Limit` — Max requests per window
- `X-RateLimit-Remaining` — Remaining requests
- `X-RateLimit-Reset` — Unix timestamp when window resets
- `Retry-After` — Seconds to wait (on 429 only)

## Error Codes

| HTTP Status | Code | Meaning |
|-------------|------|---------|
| 401 | UNAUTHORIZED | Invalid, expired, or missing API key |
| 403 | FORBIDDEN | Key lacks permission for this endpoint |
| 429 | RATE_LIMITED | Too many requests, check Retry-After |
| 500 | INTERNAL_SERVER_ERROR | Server error, try again later |

## Money Values

All monetary values are in **cents** (integer). Divide by 100 for dollars.
Example: `45840017` = `$458,400.17`

Always check the `currency` field (default: `USD`).

## Permissions

| Permission | Endpoints | Default |
|------------|-----------|---------|
| canReadNetWorth | summary, briefing, insights, net-worth/history, health-score | ✅ On |
| canReadAccounts | accounts | ✅ On |
| canReadGoals | goals | ✅ On |
| canReadBudgets | spending, transactions | ❌ Off |

## Transaction Categories

Common Plaid categories for filtering:
`FOOD_AND_DRINK`, `RENT_AND_UTILITIES`, `TRANSPORTATION`, `GENERAL_MERCHANDISE`,
`TRANSFER_OUT`, `TRANSFER_IN`, `LOAN_PAYMENTS`, `ENTERTAINMENT`, `PERSONAL_CARE`,
`MEDICAL`, `TRAVEL`, `INCOME`, `UNCATEGORIZED`
