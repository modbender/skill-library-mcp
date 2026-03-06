# Pond3r Reference

## Report API

### Create Report

```http
POST https://api.pond3r.xyz/v1/api/reports
Content-Type: application/json
x-api-key: <API_KEY>

{
  "description": "Track new tokens on Uniswap with rising liquidity",
  "schedule": "daily",
  "delivery_format": "structured_markdown"
}
```

Returns `reportId`.

### Get Latest Report

```http
GET https://api.pond3r.xyz/v1/api/reports/{reportId}/latest
x-api-key: <API_KEY>
```

### Report Response Structure

```json
{
  "reportId": "report_123456",
  "title": "New Token Opportunities - Daily Report",
  "generatedAt": "2024-03-24T09:00:00Z",
  "executiveSummary": {
    "keyFindings": "3 new tokens identified with 50%+ liquidity growth",
    "topOpportunity": "TOKEN_ABC showing 85% volume increase"
  },
  "analysis": {
    "statisticalInsights": "# Statistical Analysis\n\n...",
    "riskAssessment": "# Risk Assessment\n\n...",
    "actionableInsights": "# Actionable Insights\n\n..."
  },
  "opportunities": [
    {
      "token": "TOKEN_ABC",
      "riskScore": 0.3,
      "opportunitySize": "High",
      "details": "Rising liquidity with institutional backing"
    }
  ]
}
```

## Report Types

| Type | Use |
|------|-----|
| Token Opportunity | New token screening, liquidity growth, graduation success |
| Protocol Intelligence | Yield farming, TVL trends, governance, revenue |
| Market Risk | Liquidation risk, correlation, volatility, whale tracking |
| Cross-Chain | Bridge volume, ecosystem growth, arbitrage |

## Schedule Options

- `daily` — fast-moving opportunities
- `weekly` — trend analysis
- `monthly` — strategic insights

## Web Interface

- Report creation: [makeit.pond3r.xyz](https://makeit.pond3r.xyz)
- API keys: [makeit.pond3r.xyz/api-keys](https://makeit.pond3r.xyz/api-keys)
