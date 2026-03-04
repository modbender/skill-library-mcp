# Kubera API Reference (V3)

Base URL: `https://api.kubera.com`

## Authentication

HMAC-SHA256 signed requests. Required headers on every request:

```
x-api-token: <API_KEY>
x-timestamp: <UNIX_TIMESTAMP_SECONDS>
x-signature: <HMAC_SHA256_HEX>
```

### Signature Generation

```
data = "{api_key}{timestamp}{METHOD}{path}{body}"
signature = HMAC-SHA256(data, secret)  → hex digest
```

- `body` = compact JSON (`separators=(',',':')`) for POST, empty string for GET
- `METHOD` = "GET" or "POST" (uppercase)
- `path` = e.g. `/api/v3/data/portfolio`

## Rate Limits

- 30 requests/minute
- Essentials: 100 requests/day (UTC)
- Black: 1,000 requests/day (UTC)

## Endpoints

### GET /api/v3/data/portfolio
List all portfolios.

Response:
```json
{"data": [{"id": "...", "name": "...", "currency": "USD"}], "errorCode": 0}
```

### GET /api/v3/data/portfolio/{PORTFOLIO_ID}
Full portfolio data including all assets, debts, insurance, documents.

Response includes: `asset[]`, `debt[]`, `insurance[]`, `document[]`, `assetTotal`, `debtTotal`, `netWorth`, `costBasis`, `unrealizedGain`, `allocationByAssetClass`

### POST /api/v3/data/item/{ASSET_ID|DEBT_ID}
Update an asset or debt. Body fields (all optional): `name`, `description`, `value`, `cost`

## Asset/Debt Object Fields

Key fields: `id`, `name`, `value` ({amount, currency}), `cost`, `ticker`, `quantity`, `sheetName`, `sectionName`, `subType`, `tickerSubType`, `tickerSector`, `irr`, `ownership`, `investable`, `taxRate`, `taxability`, `connection` (aggregator info), `parent` (account grouping)
