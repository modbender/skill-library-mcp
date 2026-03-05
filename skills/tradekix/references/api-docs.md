# Tradekix API Reference

Base URL: `https://www.tradekix.ai/api/v1`

## Authentication

All endpoints (except `/connect`) require `X-API-Key` header.

```
X-API-Key: tk_live_your_key_here
```

## Endpoints

### POST /connect
Sign up for an API key. No auth required.

**Body:**
```json
{"agent_name": "MyAgent", "email": "agent@example.com", "moltbook_id": "optional"}
```

**Response:** Returns `api_key` in `data`. Save it — shown only once.

### GET /market/overview
Broad market summary across stocks, crypto, forex, commodities.

### GET /market/prices?symbols=AAPL,TSLA,BTC
Price data for specific symbols. Comma-separated.

### GET /market/indices
Global market indices (S&P 500, NASDAQ, FTSE, Nikkei, etc.)

### GET /market/forex
Major, minor, and exotic currency pair rates.

### GET /news/summary
AI-summarized market news with sentiment and impact scores.

### GET /alerts/latest
Recent market alerts — price moves, breaking news, volatility.

### GET /events/economic
Economic calendar — Fed meetings, CPI, jobs data, GDP, etc.

### GET /events/earnings
Upcoming and recent earnings reports with estimates.

### GET /social/sentiment
Social media sentiment analysis for markets and assets.

### GET /social/tweets
Curated market-related tweets from analysts and traders.

### GET /trades/congressional
Congressional stock trades with AI conflict-of-interest detection.

### POST /keys/upgrade
Upgrade API key to Pro tier. Returns Stripe checkout URL.

**Body:**
```json
{"plan": "monthly"}  // or "yearly"
```

**Response:** `data.checkout_url` — redirect user/owner to complete payment.

### POST /keys/revoke
Revoke the current API key. Requires `X-API-Key` header.

## Response Format

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "tier": "free",
    "rate_limit_remaining": 7
  }
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400  | Bad request — invalid parameters |
| 401  | Missing or invalid API key |
| 404  | Not found |
| 429  | Rate limited — check Retry-After header |
| 500  | Server error |

## Tiers

| Tier | Price | Daily Calls | Per Minute |
|------|-------|-------------|------------|
| Free | $0 | 10 | 5 |
| Pro | $9/mo or $89/yr | 2,000 | 60 |
| Enterprise | Contact us | 50,000 | 300 |
