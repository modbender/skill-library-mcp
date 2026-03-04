# apipick Company Facts - Full API Reference

**Base URL:** `https://www.apipick.com`
**Authentication:** All requests require `x-api-key: YOUR_API_KEY` header.
**Cost:** 1 credit per successful request.

---

## GET /api/company/facts

Retrieves public company data by stock ticker symbol or SEC CIK number.

### Query Parameters

Use **either** `ticker` or `cik`, not both.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | Optional* | Stock ticker symbol (case-insensitive, e.g. `AAPL`, `MSFT`, `GOOGL`, `TSLA`) |
| `cik` | string | Optional* | SEC Central Index Key, zero-padded to 10 digits (e.g. `0000320193`) |

*At least one of `ticker` or `cik` must be provided.

**Common tickers for reference:**

| Company | Ticker | Company | Ticker |
|---------|--------|---------|--------|
| Apple | `AAPL` | Microsoft | `MSFT` |
| Google/Alphabet | `GOOGL` | Amazon | `AMZN` |
| Tesla | `TSLA` | Meta | `META` |
| NVIDIA | `NVDA` | Netflix | `NFLX` |

### Response Fields

The response wraps data in a `company_facts` object.

| Field | Type | Description |
|-------|------|-------------|
| `company_facts.ticker` | string | Stock ticker symbol |
| `company_facts.name` | string | Official legal company name |
| `company_facts.cik` | string | SEC Central Index Key |
| `company_facts.industry` | string | Industry classification |
| `company_facts.sector` | string | Business sector |
| `company_facts.exchange` | string | Trading exchange (e.g. `NASDAQ`, `NYSE`) |
| `company_facts.market_cap` | number | Market capitalization in USD |
| `company_facts.number_of_employees` | number | Total employee headcount |
| `company_facts.website_url` | string | Official company website URL |
| `company_facts.sec_filings_url` | string | Link to SEC EDGAR filings page |

**Formatting `market_cap`:** When presenting to users, convert raw numbers to readable form:
- `3000000000000` → `$3T`
- `250000000000` → `$250B`
- `5000000000` → `$5B`

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Missing or invalid `ticker`/`cik` parameter |
| 401 | Missing or invalid `x-api-key` |
| 402 | Insufficient account credits |

### Example

```bash
curl "https://www.apipick.com/api/company/facts?ticker=AAPL" \
  -H "x-api-key: YOUR_API_KEY"
```

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
