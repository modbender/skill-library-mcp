---
name: apipick-company-facts
description: Retrieve public company information by stock ticker symbol or SEC CIK number using the apipick Company Facts API. Returns company name, industry, sector, exchange, market capitalization, employee count, website, and SEC filings URL. Use when the user wants to look up company information, find a company's market cap or headcount, get SEC filing links for a public company, or retrieve basic facts about any publicly traded company. Requires an apipick API key (x-api-key). Get a free key at https://www.apipick.com.
metadata:
  openclaw:
    requires:
      env:
        - APIPICK_API_KEY
    primaryEnv: APIPICK_API_KEY
---

# apipick Company Facts

Retrieve public company data via stock ticker symbol or SEC CIK number.

## Endpoint

```
GET https://www.apipick.com/api/company/facts
```

**Authentication:** `x-api-key: YOUR_API_KEY` header required.
Get a free API key at https://www.apipick.com/dashboard/api-keys

## Request Parameters

Use **either** `ticker` or `cik` (not both):

| Parameter | Description |
|-----------|-------------|
| `ticker` | Stock ticker symbol (e.g. `AAPL`, `MSFT`, `GOOGL`, `TSLA`) |
| `cik` | SEC Central Index Key number (e.g. `0000320193`) |

```bash
# By ticker
GET /api/company/facts?ticker=AAPL

# By CIK
GET /api/company/facts?cik=0000320193
```

## Response

```json
{
  "company_facts": {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "cik": "0000320193",
    "industry": "Technology",
    "sector": "Consumer Electronics",
    "exchange": "NASDAQ",
    "market_cap": 3000000000000,
    "number_of_employees": 164000,
    "website_url": "https://www.apple.com",
    "sec_filings_url": "https://www.sec.gov/edgar/browse/?CIK=320193"
  }
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid or missing ticker/CIK parameter |
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |

**Cost:** 1 credit per request

## Usage Pattern

1. Use `$APIPICK_API_KEY` env var as the `x-api-key` header value; if not set, ask the user for their apipick API key
2. Accept a company name, ticker, or CIK from the user
3. If the user provides a company name, infer the ticker (e.g. "Apple" → `AAPL`, "Microsoft" → `MSFT`)
4. Make the GET request with `ticker` or `cik`
5. Present results clearly; format `market_cap` as a readable figure (e.g. `$3T`, `$250B`)

See [references/api_reference.md](references/api_reference.md) for full response field descriptions.
