---
name: sectors-api
description: >
  Query financial market data from the Sectors API (api.sectors.app) for IDX
  (Indonesia Stock Exchange) and SGX (Singapore Exchange) markets. Use when the
  user asks about stock prices, company reports, financials, market indices, top
  movers, dividends, earnings, market cap, or any Indonesian or Singaporean
  equity market data. Only calls https://api.sectors.app. Python with requests.
license: MIT
compatibility: >
  Requires Python 3.8+ with the requests library. Requires the SECTORS_API_KEY
  environment variable to be set. Requires network access to https://api.sectors.app.
metadata:
  author: supertype
  version: "1.1"
allowed-tools: Bash(python:*) Bash(pip:*) Read
---

# Sectors API

Query IDX and SGX financial market data through the Sectors REST API.

**Full API docs**: https://sectors.app/api

## Constraints

- ONLY make HTTP requests to `https://api.sectors.app/v1`. Never call any other domain, database, or external service.
- All endpoints are `GET` requests returning JSON.
- Never hardcode or guess an API key. Always read it from the `SECTORS_API_KEY` environment variable.
- If `SECTORS_API_KEY` is not set, prompt the user to set it: `export SECTORS_API_KEY="your-api-key-here"` or run the setup check script at `scripts/check_setup.py`.

## Setup

### 1. Set the API key

The API key must be available as the `SECTORS_API_KEY` environment variable.

```bash
# Option A: Set in your current shell
export SECTORS_API_KEY="your-api-key-here"

# Option B: Add to your shell profile (~/.bashrc, ~/.zshrc) for persistence
echo 'export SECTORS_API_KEY="your-api-key-here"' >> ~/.bashrc

# Option C: Use a .env file in the project root (see .env.example)
```

For agent-specific configuration:
- **Claude Code**: `claude config set env SECTORS_API_KEY your-api-key-here`
- **OpenCode**: Set in `~/.config/opencode/config.json` under `env`
- **Cursor**: Settings > Features > Environment Variables

### 2. Install the dependency

```bash
pip install requests
```

### 3. Verify setup (optional)

```bash
python scripts/check_setup.py
```

### Making requests

```python
import os
import requests

API_KEY = os.environ["SECTORS_API_KEY"]
BASE_URL = "https://api.sectors.app/v1"

headers = {"Authorization": API_KEY}
response = requests.get(f"{BASE_URL}/subsectors/", headers=headers)
data = response.json()
```

The `Authorization` header takes the raw API key. Do NOT prefix it with `Bearer`.

## Endpoint decision table

Pick the right endpoint based on what the user needs:

### Market structure

| User wants | Endpoint | Required params |
|---|---|---|
| List all subsectors | `GET /subsectors/` | none |
| List all industries | `GET /industries/` | none |
| List all subindustries | `GET /subindustries/` | none |
| SGX sector list | `GET /sgx/sectors/` | none |

### Company discovery

| User wants | Endpoint | Required params |
|---|---|---|
| Companies in a subsector | `GET /companies/?sub_sector={sub_sector}` | `sub_sector` |
| Companies in a subindustry | `GET /companies/?sub_industry={sub_industry}` | `sub_industry` |
| Companies in a stock index | `GET /index/{index}/` | `index` |
| Companies with segment data | `GET /companies/list_companies_with_segments/` | none |
| SGX companies by sector | `GET /sgx/companies/?sector={sector}` | `sector` |

### Company details

| User wants | Endpoint | Required params |
|---|---|---|
| Full company report (IDX) | `GET /company/report/{ticker}/` | `ticker` |
| SGX company report | `GET /sgx/company/report/{ticker}` | `ticker` |
| Listing performance | `GET /listing-performance/{ticker}/` | `ticker` |
| Quarterly financial dates | `GET /company/get_quarterly_financial_dates/{ticker}/` | `ticker` |
| Quarterly financials | `GET /financials/quarterly/{ticker}/` | `ticker` |
| Company segments | `GET /company/get-segments/{ticker}/` | `ticker` |

### Market data

| User wants | Endpoint | Required params |
|---|---|---|
| Daily stock price | `GET /daily/{ticker}` | `ticker` |
| Index daily data | `GET /index-daily/{index_code}/` | `index_code` |
| Index summary | `GET /index/{index}/` | `index` |
| IDX total market cap | `GET /idx-total/` | none |

### Rankings and screening

| User wants | Endpoint | Required params |
|---|---|---|
| Top gainers/losers | `GET /companies/top-changes/` | none (all optional) |
| Top companies by metric | `GET /companies/top/` | none (all optional) |
| Top growth companies | `GET /companies/top-growth/` | none (all optional) |
| Most traded stocks | `GET /most-traded/` | none (all optional) |
| SGX top companies | `GET /sgx/companies/top/` | none (all optional) |

For full parameter lists and response schemas, see:
- [references/idx-endpoints.md](references/idx-endpoints.md) -- all 18 IDX endpoints
- [references/sgx-endpoints.md](references/sgx-endpoints.md) -- all 6 SGX endpoints
- [assets/endpoint-map.md](assets/endpoint-map.md) -- quick-lookup table

## Common patterns

### Fetch a company report

```python
import os
import requests

API_KEY = os.environ["SECTORS_API_KEY"]
BASE_URL = "https://api.sectors.app/v1"
headers = {"Authorization": API_KEY}

ticker = "BBCA"
params = {"sections": "overview,valuation,financials"}
resp = requests.get(f"{BASE_URL}/company/report/{ticker}/", headers=headers, params=params)
report = resp.json()

print(report["company_name"])
print(report["overview"]["market_cap"])
```

Available sections: `overview`, `valuation`, `future`, `peers`, `financials`, `dividend`, `management`, `ownership`. Use `all` or omit for everything.

### Get daily stock prices in a date range

```python
import os
import requests

API_KEY = os.environ["SECTORS_API_KEY"]
BASE_URL = "https://api.sectors.app/v1"
headers = {"Authorization": API_KEY}

ticker = "BBRI.JK"
# Normalize: uppercase, strip .JK
clean = ticker.upper().replace(".JK", "")

params = {"start": "2025-01-01", "end": "2025-01-31"}
resp = requests.get(f"{BASE_URL}/daily/{clean}", headers=headers, params=params)
prices = resp.json()

for day in prices:
    print(day["date"], day["close"], day["volume"])
```

### Find top gainers and losers

```python
import os
import requests

API_KEY = os.environ["SECTORS_API_KEY"]
BASE_URL = "https://api.sectors.app/v1"
headers = {"Authorization": API_KEY}

params = {
    "classifications": "top_gainers,top_losers",
    "periods": "7d,30d",
    "n_stock": 5,
    "min_mcap_billion": 5000,
}
resp = requests.get(f"{BASE_URL}/companies/top-changes/", headers=headers, params=params)
movers = resp.json()

for stock in movers["top_gainers"]["7d"]:
    print(stock["symbol"], stock["price_change"])
```

### List companies in an index

```python
import os
import requests

API_KEY = os.environ["SECTORS_API_KEY"]
BASE_URL = "https://api.sectors.app/v1"
headers = {"Authorization": API_KEY}

# Available: lq45, idx30, kompas100, jii70, idxhidiv20, srikehati, etc.
resp = requests.get(f"{BASE_URL}/index/lq45/", headers=headers)
companies = resp.json()

for c in companies:
    print(c["symbol"], c["company_name"])
```

### SGX company report

```python
import os
import requests

API_KEY = os.environ["SECTORS_API_KEY"]
BASE_URL = "https://api.sectors.app/v1"
headers = {"Authorization": API_KEY}

ticker = "D05"  # DBS Group
resp = requests.get(f"{BASE_URL}/sgx/company/report/{ticker}", headers=headers)
report = resp.json()

print(report["name"])
print(report["valuation"]["pe"])
print(report["financials"]["gross_margin"])
```

## Ticker normalization

| Market | Rule | Example |
|---|---|---|
| IDX | Uppercase, strip `.JK` suffix | `bbca.jk` -> `BBCA` |
| SGX | Uppercase, strip `.SI` suffix | `d05.si` -> `D05` |

Always normalize before passing to an endpoint.

## Gotchas

1. **Auth header format**: Use `Authorization: <raw_key>`. NOT `Bearer <key>`. NOT `Authorization: Bearer <key>`.

2. **Date format**: Always `YYYY-MM-DD`. Example: `2025-06-15`.

3. **Date range limit**: The `/most-traded/` endpoint requires start and end dates within 90 days of each other.

4. **Kebab-case for subsectors and sectors**: Use `banks`, `financing-service`, `consumer-defensive`. Not camelCase or snake_case.

5. **Nested response structure**: Ranking endpoints (`top-changes`, `top`, `top-growth`) return objects keyed by classification, then by period. Always navigate both levels.

   ```python
   # top-changes returns: { "top_gainers": { "7d": [...], "30d": [...] } }
   # top returns: { "dividend_yield": [...], "revenue": [...] }
   ```

6. **Market cap units**: IDX values are in billion IDR (`min_mcap_billion`). SGX values are in million SGD (`min_mcap_million`).

7. **Default values matter**: Many optional params default to `"all"` or specific values (e.g. `n_stock` defaults to 5, `min_mcap_billion` defaults to 5000). Be explicit when you need different behavior.

8. **Index codes**: IDX index daily data uses lowercase codes: `ihsg`, `lq45`, `idx30`. Company-by-index uses the same codes.

9. **Quarterly financials `approx` flag**: When `approx=true`, the API returns the closest available quarter if an exact match for `report_date` is not found.

10. **Company report sections param**: Only appended to the URL when not `"all"`. If you want all sections, omit the `sections` parameter entirely.

## Available IDX indices

`ftse`, `idx30`, `idxbumn20`, `idxesgl`, `idxg30`, `idxhidiv20`, `idxq30`, `idxv30`, `jii70`, `kompas100`, `lq45`, `sminfra18`, `srikehati`, `economic30`, `idxvesta28`

## Top companies classifications

**IDX** (`/companies/top/`): `dividend_yield`, `total_dividend`, `revenue`, `earnings`, `market_cap`, `pb`, `pe`, `ps`

**IDX growth** (`/companies/top-growth/`): `top_earnings_growth_gainers`, `top_earnings_growth_losers`, `top_revenue_growth_gainers`, `top_revenue_growth_losers`

**IDX movers** (`/companies/top-changes/`): `top_gainers`, `top_losers`

**SGX** (`/sgx/companies/top/`): `dividend_yield`, `revenue`, `earnings`, `market_cap`, `pe`

## Error handling

Always check the response status:

```python
resp = requests.get(url, headers=headers)
if resp.status_code == 403:
    raise ValueError("Invalid or missing API key. Ensure SECTORS_API_KEY is set correctly.")
if resp.status_code == 404:
    raise ValueError(f"Resource not found: {url}")
if not resp.ok:
    raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
data = resp.json()
```
