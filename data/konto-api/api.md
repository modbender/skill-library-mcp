# Konto API Reference

Base URL: `$KONTO_URL` (default: `http://localhost:5004`)  
Auth: `Authorization: Bearer konto_xxx`  
Scopes: `personal` (default) | `analytics`

---

## Personal Endpoints

### GET /api/v1/accounts
List bank accounts with balances.

**Response:**
```json
{
  "accounts": [
    { "id": 1, "name": "Compte Courant", "bank_name": "BNP", "balance": 2345.67, "type": "checking", "usage": "personal" }
  ]
}
```

Account types: `checking`, `savings`, `loan`, `investment`

---

### GET /api/v1/transactions
List transactions with auto-categorization.

**Query params:**
| Param | Default | Description |
|-------|---------|-------------|
| `months` | `3` | How many months back |
| `category` | — | Filter by category name |
| `min_amount` | — | Min amount filter |
| `max_amount` | — | Max amount filter |

**Response:**
```json
{
  "transactions": [
    { "id": 1, "date": "2026-02-01", "amount": -45.00, "label": "NETFLIX", "category": "subscriptions", "icon": "📺", "account": "Compte Courant" }
  ],
  "total": 120
}
```

**Categories:** food, transport, subscriptions, health, shopping, entertainment, utilities, salary, other

---

### GET /api/v1/investments
List investment portfolio.

**Response:**
```json
{
  "investments": [
    { "label": "World ETF", "code": "IE00B4L5Y983", "quantity": 10, "unit_value": 95.50, "current_value": 955.00, "type": "etf" }
  ],
  "total_value": 15432.00
}
```

Investment types: `etf`, `stock`, `crypto`, `bond`, `other`

---

### GET /api/v1/assets
List physical/real assets (real estate, vehicles, etc).

**Response:**
```json
{
  "assets": [
    { "name": "Appartement Paris", "type": "real_estate", "current_value": 350000, "purchase_value": 300000, "monthly_rent": 1200 }
  ]
}
```

---

### GET /api/v1/loans
List loan accounts with remaining balances.

**Response:**
```json
{
  "loans": [
    { "name": "Crédit Immobilier", "remaining_amount": -180000, "monthly_payment": null, "rate": null, "start_date": null, "end_date": null }
  ]
}
```

Note: `remaining_amount` is negative (liability). `monthly_payment`, `rate`, `start_date`, `end_date` are null if not tracked by the bank integration.

---

### GET /api/v1/summary
Full financial snapshot — the most useful endpoint.

**Response:**
```json
{
  "patrimoine_net": 125000.00,
  "accounts": { "count": 4, "total_balance": 8500.00 },
  "investments": { "count": 12, "total_value": 45000.00 },
  "assets": { "count": 1, "total_value": 350000.00 },
  "loans": { "count": 1, "total_remaining": -180000.00 },
  "monthly": { "income": 3200.00, "expenses": -1850.00, "savings": 1350.00 },
  "subscriptions": { "count": 8, "monthly": -87.50 },
  "top_expense_categories": [
    { "name": "food", "icon": "🍔", "pct": 32 }
  ],
  "crypto_holdings": [
    { "code": "BTC", "value": 1200.00 },
    { "code": "ETH", "value": 450.00 }
  ]
}
```

---

## Analytics Endpoints

> **Requires `analytics` scope API key.**  
> Returns anonymized aggregate data across all users.

### GET /api/v1/analytics/demographics
Platform-wide user stats.

**Response:**
```json
{
  "total_users": 42,
  "avg_patrimoine": 87500.00,
  "crypto_holders_pct": 64,
  "real_estate_holders_pct": 38,
  "avg_accounts_per_user": 3.2
}
```

---

### GET /api/v1/analytics/categories
Spending category breakdown across all users (last 3 months).

**Response:**
```json
{
  "categories": [
    { "name": "food", "icon": "🍔", "avg_pct": 28, "median_monthly": -420.00 }
  ]
}
```

---

### GET /api/v1/analytics/investments
Portfolio composition stats across all users.

**Response:**
```json
{
  "crypto_holders_pct": 64,
  "top_cryptos": [
    { "code": "BTC", "holders_pct": 58 },
    { "code": "ETH", "holders_pct": 42 }
  ],
  "avg_portfolio_size": 28000.00,
  "etf_vs_stocks_ratio": 0.73
}
```

---

### GET /api/v1/analytics/subscriptions
Top recurring merchants detected across all users (last 3 months).

**Response:**
```json
{
  "top_subscriptions": [
    { "merchant": "NETFLIX", "users_pct": 71, "avg_amount": -15.99 }
  ],
  "avg_monthly_subscriptions": -124.50
}
```

---

## Error Responses

| Code | Body | Meaning |
|------|------|---------|
| 401 | `{"error":"Unauthorized"}` | Missing or invalid API key |
| 403 | `{"error":"Analytics scope required"}` | Personal key used on analytics endpoint |

---

## Quick Reference

```bash
# Load secrets
source ~/.openclaw/secrets/konto.env

# Summary (most useful)
curl -s "$KONTO_URL/api/v1/summary" -H "Authorization: Bearer $KONTO_API_KEY" | jq .

# All endpoints
GET /api/v1/accounts
GET /api/v1/transactions?months=3&category=food&min_amount=-100&max_amount=0
GET /api/v1/investments
GET /api/v1/assets
GET /api/v1/loans
GET /api/v1/summary

# Analytics (analytics scope)
GET /api/v1/analytics/demographics
GET /api/v1/analytics/categories
GET /api/v1/analytics/investments
GET /api/v1/analytics/subscriptions
```
