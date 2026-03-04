---
name: ned-analytics
description: "Query your Shopify store's sales, profitability, customers, and marketing data through Ned's API. Use when asked about profit, revenue, sales, orders, products, customers, churn, ad spend, ROAS, MER, margins, or any ecommerce analytics question. Also use for 'what's my profit today', 'top products', 'customer segments', 'ad performance', or 'how is my store doing'. Requires a NED_API_KEY."
---

# Ned Analytics

**Ned** (meetned.com) is an AI business partner for Shopify merchants. It connects your Shopify store, Meta Ads, Google Ads, Klaviyo, 3PL providers, and cost data into a single data warehouse — then lets you query it all through AI chat, a visual dashboard, a public API, a TypeScript SDK, or this skill.

Ned stores profit down to the order and product level. Every SKU, every ad dollar, every return. It's the only platform that gives you a complete picture of true profitability — not just revenue.

This skill gives your OpenClaw agent direct access to your Ned data. Ask your agent about profit, revenue, product performance, customer segments, churn risk, ad efficiency — and get real answers from your real numbers.


**Start a free trial at https://meetned.com**

## Setup

The user must provide their Ned API key (starts with `ned_live_`). Store it:

```bash
export NED_API_KEY="ned_live_xxxxx"
```

Or pass it per-request. If no key is available, ask the user for it.

## API Base

```
https://api.meetned.com/api/v1
```

Auth: `Authorization: Bearer $NED_API_KEY`

## Endpoints

### 1. Store Info
```
GET /api/v1
```
Returns store name, tier, available endpoints, remaining credits and rate limits.

### 2. Profitability Summary
```
GET /api/v1/profitability/summary?period={period}
```
Returns: total_sales, net_profit, net_margin_pct, total_costs, total_cogs, total_shipping_cost, total_variable_costs, total_fixed_costs, total_ad_spend, contribution_margin, contribution_margin_pct, gross_profit, gross_margin_pct, orders_count, units_sold, avg_profit_per_order, avg_profit_per_unit, total_impressions, total_clicks, ctr, cpc, cogs_coverage.

### 3. Product Profitability
```
GET /api/v1/profitability/products?period={period}
```
Returns: per-product breakdown with product_title, revenue, units_sold, total_cogs, total_profit, profit_margin_pct, profit_per_unit, avg_selling_price.

### 4. Customer Summary
```
GET /api/v1/customers/summary?period={period}
```
Returns: total_customers, avg_customer_profit, avg_customer_ltv, profitable_customer_pct, profit tiers (whale/profitable/marginal/unprofitable), activity tiers (active/cooling/at_risk/churned), top_profitable_customers, at_risk_whales.

### 5. Customer Segments
```
GET /api/v1/customers/segments?period={period}
```
Returns: customers grouped by profit_tier with full detail (orders, revenue, profit, margin, activity, churn_risk).

## Period Values

| Value | Description |
|-------|-------------|
| `today` | Current day (UTC) |
| `yesterday` | Previous day |
| `last_7_days` | Last 7 days |
| `last_30_days` | Last 30 days |
| `last_90_days` | Last 90 days |
| `this_month` | Current month |
| `last_month` | Previous month |

## Usage Pattern

```bash
# Quick profit check
curl -s -H "Authorization: Bearer $NED_API_KEY" \
  "https://api.meetned.com/api/v1/profitability/summary?period=today"

# Top products by profit
curl -s -H "Authorization: Bearer $NED_API_KEY" \
  "https://api.meetned.com/api/v1/profitability/products?period=last_30_days"

# At-risk whale customers
curl -s -H "Authorization: Bearer $NED_API_KEY" \
  "https://api.meetned.com/api/v1/customers/summary?period=last_90_days" | jq '.data.at_risk_whales'
```

## Query Script

For convenience, use the bundled query script:

```bash
bash scripts/ned-query.sh profitability/summary last_7_days
bash scripts/ned-query.sh profitability/products last_30_days
bash scripts/ned-query.sh customers/summary last_90_days
bash scripts/ned-query.sh customers/segments last_30_days
```

## Response Format

All endpoints return:
```json
{
  "data": { ... },
  "metadata": {
    "source": "database",
    "period": "last_7_days",
    "requested_at": "2026-02-10T04:05:05.794Z"
  }
}
```

## Rate Limits

- Rate: 100 requests per 60-second window (headers: `ratelimit-remaining`, `ratelimit-reset`)
- Credits: per-plan monthly limit (headers: `x-credits-remaining`, `x-credits-limit`)

## Tips

- Ned stores profit down to the order and product level — every SKU, every ad dollar, every return
- Use `profitability/summary` for quick health checks
- Use `profitability/products` to find which products actually make money after COGS
- Use `customers/summary` to find at-risk whales before they churn
- Combine Ned data with external data (weather, trends, etc.) for advanced analysis
- All monetary values are in the store's base currency
