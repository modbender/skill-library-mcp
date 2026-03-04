# SGX Endpoints Reference

All endpoints use base URL `https://api.sectors.app/v1` and require the `Authorization: <api_key>` header.

---

## 1. Fetch SGX sectors

```
GET /sgx/sectors/
```

**Parameters**: none

**Response**: Array of strings (sector names)

```json
["consumer-defensive", "industrials", "technology", "financial-services", ...]
```

---

## 2. Fetch SGX companies by sector

```
GET /sgx/companies/?sector={sector}
```

**Query parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `sector` | string | yes | Sector in kebab-case (e.g. `consumer-defensive`, `industrials`, `financial-services`) |

**Response**: Array of objects

| Field | Type |
|---|---|
| `symbol` | string |
| `company_name` | string |

---

## 3. Fetch SGX company report

```
GET /sgx/company/report/{ticker}
```

**Path parameters**:

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | SGX ticker (e.g. `D05`, `U11`). Strip `.SI` suffix if present. |

**Response**:

| Field | Type | Description |
|---|---|---|
| `symbol` | string | Ticker |
| `name` | string | Company name |
| `overview` | object | See below |
| `valuation` | object | See below |
| `financials` | object | See below |
| `dividend` | object | See below |

### overview

| Field | Type | Description |
|---|---|---|
| `market_cap` | number | Market capitalization |
| `volume` | number | Trading volume |
| `employee_num` | number | Number of employees |
| `sector` | string | Sector |
| `sub_sector` | string | Sub-sector |
| `change_1d` | number | 1-day price change (%) |
| `change_7d` | number | 7-day price change (%) |
| `change_1m` | number | 1-month price change (%) |
| `change_1y` | number | 1-year price change (%) |
| `change_3y` | number | 3-year price change (%) |
| `change_ytd` | number | Year-to-date price change (%) |
| `all_time_price` | object | Nested price extremes |

### overview.all_time_price

Each sub-field is `{date: string, price: number}`:

`ytd_low`, `ytd_high`, `52_w_low`, `52_w_high`, `90_d_low`, `90_d_high`, `all_time_low`, `all_time_high`

### valuation

| Field | Type |
|---|---|
| `pe` | number |
| `ps` | number |
| `pcf` | number |
| `pb` | number |

### financials

| Field | Type | Description |
|---|---|---|
| `historical_earnings` | object | Keyed by year (e.g. `"2023": 5000000`), plus `"ttm"` |
| `historical_revenue` | object | Same structure as earnings |
| `eps` | number | Earnings per share |
| `gross_margin` | number | Gross margin (%) |
| `operating_margin` | number | Operating margin (%) |
| `net_profit_margin` | number | Net profit margin (%) |
| `one_year_eps_growth` | number | YoY EPS growth (%) |
| `one_year_sales_growth` | number | YoY sales growth (%) |
| `quick_ratio` | number or null | Quick ratio |
| `current_ratio` | number or null | Current ratio |
| `debt_to_equity` | number or null | Debt-to-equity ratio |

### dividend

| Field | Type | Description |
|---|---|---|
| `dividend_yield_5y_avg` | number | 5-year average yield |
| `dividend_growth_rate` | number | Growth rate |
| `payout_ratio` | number | Payout ratio |
| `forward_dividend` | number | Forward dividend |
| `forward_dividend_yield` | number | Forward yield |
| `dividend_ttm` | number | Trailing 12-month dividend |
| `historical_dividends` | array | Array of yearly dividend objects |

Each `historical_dividends` entry:

| Field | Type | Description |
|---|---|---|
| `year` | integer | Year |
| `breakdown` | array | Array of `{date, total, yield}` |
| `total_yield` | number | Total yield for the year |
| `total_dividend` | number | Total dividend for the year |

---

## 4. Fetch SGX top companies

```
GET /sgx/companies/top/
```

**Query parameters**:

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `sector` | string | no | `all` | Sector filter (kebab-case) |
| `classifications` | string | no | `all` | Comma-separated: `dividend_yield`, `revenue`, `earnings`, `market_cap`, `pe` |
| `min_mcap_million` | number | no | `1000` | Minimum market cap in **million SGD** |

**Response**: Object keyed by classification

```json
{
  "dividend_yield": [{"symbol": "...", "company_name": "...", "dividend_yield": 5.2}],
  "revenue": [{"symbol": "...", "company_name": "...", "revenue": 12000000}],
  "earnings": [...],
  "market_cap": [...],
  "pe": [...]
}
```

---

## 5. Fetch SGX companies by sector (duplicate note)

This is the same as endpoint #2 above. Listed here for completeness as it appears in the MCP tool registry under a separate name.

```
GET /sgx/companies/?sector={sector}
```

---

## 6. SGX company report (duplicate note)

This is the same as endpoint #3 above. The MCP registers it from two separate source files. The endpoint and response schema are identical.
