# IDX Endpoints Reference

All endpoints use base URL `https://api.sectors.app/v1` and require the `Authorization: <api_key>` header.

---

## 1. Get subsectors

```
GET /subsectors/
```

**Parameters**: none

**Response**: Array of objects

| Field | Type |
|---|---|
| `sector` | string |
| `subsector` | string |

---

## 2. Fetch industries

```
GET /industries/
```

**Parameters**: none

**Response**: Array of objects

| Field | Type |
|---|---|
| `subsector` | string |
| `industry` | string |

---

## 3. Fetch subindustries

```
GET /subindustries/
```

**Parameters**: none

**Response**: Array of objects (key-value pairs, structure varies)

---

## 4. Fetch index data

```
GET /index/{index}/
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `index` | string | yes | Index code (e.g. `lq45`, `idx30`, `kompas100`) |

**Response**: Array of objects

| Field | Type |
|---|---|
| `symbol` | string |
| `company_name` | string |

**Available indices**: `ftse`, `idx30`, `idxbumn20`, `idxesgl`, `idxg30`, `idxhidiv20`, `idxq30`, `idxv30`, `jii70`, `kompas100`, `lq45`, `sminfra18`, `srikehati`, `economic30`, `idxvesta28`

---

## 5. Fetch companies by subsector

```
GET /companies/?sub_sector={subSector}
```

**Query parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `sub_sector` | string | yes | Subsector in kebab-case (e.g. `banks`, `financing-service`) |

**Response**: Array of company objects

---

## 6. Fetch companies by subindustry

```
GET /companies/?sub_industry={subIndustry}
```

**Query parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `sub_industry` | string | yes | Subindustry name |

**Response**: Array of company objects

---

## 7. Fetch companies with segments

```
GET /companies/list_companies_with_segments/
```

**Parameters**: none

**Response**: Array of company objects that have segment data available

---

## 8. Fetch listing performance

```
GET /listing-performance/{ticker}/
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | Company ticker (uppercase, no `.JK` suffix) |

**Response**:

| Field | Type | Description |
|---|---|---|
| `symbol` | string | Ticker symbol |
| `chg_7d` | number | 7-day price change (%) |
| `chg_30d` | number | 30-day price change (%) |
| `chg_90d` | number | 90-day price change (%) |
| `chg_365d` | number | 365-day price change (%) |

---

## 9. Fetch quarterly financial dates

```
GET /company/get_quarterly_financial_dates/{ticker}/
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | Company ticker (uppercase, no `.JK` suffix) |

**Response**: Object keyed by year, values are arrays of `[date, quarter]` tuples.

```json
{
  "2024": [["2024-04-30", "Q1"], ["2024-07-31", "Q2"]],
  "2023": [["2023-04-28", "Q1"], ["2023-07-31", "Q2"], ["2023-10-30", "Q3"], ["2024-01-31", "Q4"]]
}
```

---

## 10. Fetch quarterly financials

```
GET /financials/quarterly/{ticker}/
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | Company ticker (uppercase, no `.JK` suffix) |

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `report_date` | string | no | - | Specific report date (`YYYY-MM-DD`) |
| `approx` | boolean | no | - | If true, return closest quarter when exact date not found |
| `n_quarters` | integer | no | - | Number of quarters to return |

**Response**: Array of quarterly financial objects with fields including:

| Field | Type |
|---|---|
| `symbol` | string |
| `date` | string |
| `revenue` | number |
| `operating_expense` | number |
| `earnings` | number |
| `ebit` | number |
| `ebitda` | number |
| `total_assets` | number |
| `total_liabilities` | number |
| `total_equity` | number |
| `total_debt` | number |
| `operating_cash_flow` | number |
| `free_cash_flow` | number |
| `financials_sector_metrics` | object (nested) |

Plus additional balance sheet, income statement, and cash flow fields.

---

## 11. Fetch company segments

```
GET /company/get-segments/{ticker}/
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | Company ticker (uppercase, no `.JK` suffix) |

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `financial_year` | integer | no | latest | Financial year (e.g. `2023`) |

**Response**:

| Field | Type | Description |
|---|---|---|
| `symbol` | string | Ticker |
| `financial_year` | integer | Year |
| `revenue_breakdown` | array | Array of `{value, source, target}` objects |

---

## 12. Fetch company report

```
GET /company/report/{ticker}/
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | Company ticker |

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `sections` | string | no | `all` | Comma-separated list: `overview`, `valuation`, `future`, `peers`, `financials`, `dividend`, `management`, `ownership` |

Only append `sections` param when not requesting all sections.

**Response** (when `sections=all`):

| Field | Type | Description |
|---|---|---|
| `symbol` | string | Ticker |
| `company_name` | string | Full name |
| `overview` | object | Market cap, sector, listing date, employees, price data, ESG score |
| `overview.all_time_price` | object | Nested: `ytd_low`, `ytd_high`, `52_w_low`, `52_w_high`, `90_d_low`, `90_d_high`, `all_time_low`, `all_time_high` (each has `date` and `price`) |
| `valuation` | object | PE, PB, PS, PCF ratios |
| `future` | object | Forward estimates |
| `peers` | object | Peer comparison |
| `financials` | object | Revenue, earnings, margins |
| `dividend` | object | Yield, payout, history |
| `management` | object | Key personnel |
| `ownership` | object | Shareholder structure |

---

## 13. Fetch index daily data

```
GET /index-daily/{index_code}/
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `index_code` | string | yes | Index code (e.g. `ihsg`, `lq45`, `idx30`) |

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `start` | string | no | 30 days before end | Start date (`YYYY-MM-DD`) |
| `end` | string | no | today | End date (`YYYY-MM-DD`) |

**Response**: Array of objects

| Field | Type |
|---|---|
| `index_code` | string |
| `date` | string |
| `price` | number |

---

## 14. Fetch IDX market cap

```
GET /idx-total/
```

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `start` | string | no | 30 days before end | Start date (`YYYY-MM-DD`) |
| `end` | string | no | today | End date (`YYYY-MM-DD`) |

**Response**: Array of objects

| Field | Type |
|---|---|
| `date` | string |
| `idx_total_market_cap` | number |

---

## 15. Fetch top company movers

```
GET /companies/top-changes/
```

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `classifications` | string | no | `all` | Comma-separated: `top_gainers`, `top_losers` |
| `n_stock` | integer | no | `5` | Number of stocks (1-10) |
| `min_mcap_billion` | integer | no | `5000` | Minimum market cap in billion IDR |
| `periods` | string | no | `all` | Comma-separated: `1d`, `7d`, `14d`, `30d`, `365d` |
| `sub_sector` | string | no | `all` | Subsector filter (kebab-case) |

**Response**: Nested object

```json
{
  "top_gainers": {
    "7d": [
      {
        "name": "...",
        "symbol": "BBCA",
        "price_change": 5.2,
        "last_close_price": 9500,
        "latest_close_date": "2025-01-15"
      }
    ]
  },
  "top_losers": { ... }
}
```

---

## 16. Fetch most traded stocks

```
GET /most-traded/
```

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `start` | string | no | 30 days before end | Start date (`YYYY-MM-DD`). Must be within 90 days of end. |
| `end` | string | no | today | End date (`YYYY-MM-DD`). Must be within 90 days of start. |
| `n_stock` | integer | no | `5` | Number of stocks (1-10) |
| `adjusted` | boolean | no | `false` | If true, sort by volume x close price |
| `sub_sector` | string | no | `all` | Subsector filter |

**Response**: Object keyed by date

```json
{
  "2025-01-15": [
    {"symbol": "BBRI", "company_name": "...", "volume": 123456789, "price": 4500}
  ]
}
```

---

## 17. Fetch top growth companies

```
GET /companies/top-growth/
```

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `classifications` | string | no | `all` | Comma-separated: `top_earnings_growth_gainers`, `top_earnings_growth_losers`, `top_revenue_growth_gainers`, `top_revenue_growth_losers` |
| `n_stock` | integer | no | `5` | Number of companies (1-10) |
| `min_mcap_billion` | integer | no | `5000` | Minimum market cap in billion IDR |
| `sub_sector` | string | no | `all` | Subsector filter (kebab-case) |

**Response**:

```json
{
  "top_earnings_growth_gainers": [
    {"symbol": "...", "company_name": "...", "yoy_quarter_earnings_growth": 45.2}
  ],
  "top_earnings_growth_losers": [...],
  "top_revenue_growth_gainers": [...],
  "top_revenue_growth_losers": [...]
}
```

---

## 18. Fetch top companies by metrics

```
GET /companies/top/
```

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `classifications` | string | no | `all` | Comma-separated: `dividend_yield`, `total_dividend`, `revenue`, `earnings`, `market_cap`, `pb`, `pe`, `ps` |
| `filters` | string | no | - | Comma-separated conditions (e.g. `pe>20,revenue>1000`) |
| `logic` | string | no | `and` | Combine filters: `and` or `or` |
| `n_stock` | integer | no | `5` | Number of stocks (1-10) |
| `min_mcap_billion` | number | no | `5000` | Minimum market cap in billion IDR |
| `sub_sector` | string | no | `all` | Subsector filter (kebab-case) |
| `year` | integer | no | current year | Data year |

**Response**: Object keyed by classification

```json
{
  "dividend_yield": [{"symbol": "...", "company_name": "...", "dividend_yield": 7.5}],
  "revenue": [{"symbol": "...", "company_name": "...", "revenue": 50000000}],
  "pe": [{"symbol": "...", "company_name": "...", "pe": 8.2}]
}
```

---

## 19. Fetch daily transaction

```
GET /daily/{ticker}
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | Stock ticker (uppercase, `.JK` suffix will be normalized) |

Ticker validation: must be uppercase letters, optionally ending in `.JK`. Minimum 4 characters.

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `start` | string | no | - | Start date (`YYYY-MM-DD`) |
| `end` | string | no | today | End date (`YYYY-MM-DD`) |

**Response**: Array of objects

| Field | Type | Description |
|---|---|---|
| `symbol` | string | Ticker |
| `date` | string | Date |
| `close` | number | Closing price |
| `volume` | number | Trading volume |
| `market_cap` | number | Market capitalization |
