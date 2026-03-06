---
name: mfapi
description: Query Indian mutual fund NAV data, scheme info, and history via the free MFapi.in REST API.
homepage: https://www.mfapi.in
metadata:
  {
    "openclaw":
      { "emoji": "₹", "requires": { "bins": ["jq", "curl"] } },
  }
---

# MFapi Skill

Query Indian mutual fund data — NAV history, scheme info, search — using the free [MFapi.in](https://www.mfapi.in) API.

## Setup

No authentication or API keys required. The API is completely free and open.

Ensure `curl` and `jq` are installed:

```bash
# Debian/Ubuntu
sudo apt install -y curl jq

# macOS
brew install curl jq
```

## What is an ISIN Code?

ISIN (International Securities Identification Number) is a 12-character alphanumeric code that uniquely identifies a security globally (e.g. `INF200K01UT4`). Indian mutual fund schemes have up to two ISINs:

- **isinGrowth** — identifies the Growth option of the scheme
- **isinDivReinvestment** — identifies the IDCW (Dividend) Reinvestment option (may be `null`)

ISIN codes are printed on CAS (Consolidated Account Statements), broker/demat platforms, and AMFI's website. They are stable identifiers — unlike scheme names, they don't change when a fund house rebrands.

## Base URL

```
https://api.mfapi.in
```

Data is updated 6× daily (10:05 AM, 2:05 PM, 6:05 PM, 9:05 PM, 3:09 AM, 5:05 AM IST).

## Usage

### Search schemes by name

```bash
curl -s "https://api.mfapi.in/mf/search?q=HDFC" | jq '.[] | {schemeCode, schemeName}'
```

### List all schemes (paginated)

```bash
curl -s "https://api.mfapi.in/mf?limit=100&offset=0" | jq '.[] | {schemeCode, schemeName}'
```

### Get latest NAV for a scheme

```bash
curl -s "https://api.mfapi.in/mf/125497/latest" | jq '{scheme: .meta.scheme_name, nav: .data[0].nav, date: .data[0].date}'
```

### Get NAV history for a scheme

```bash
curl -s "https://api.mfapi.in/mf/125497" | jq '{scheme: .meta.scheme_name, records: (.data | length)}'
```

### Get NAV history with date range

```bash
curl -s "https://api.mfapi.in/mf/125497?startDate=2023-01-01&endDate=2023-12-31" | jq '.data'
```

### Get latest NAV for all schemes

```bash
curl -s "https://api.mfapi.in/mf/latest" | jq '.[:5]'
```

## Response Formats

### Latest NAV (`/mf/{scheme_code}/latest`)

```json
{
  "meta": {
    "fund_house": "HDFC Mutual Fund",
    "scheme_type": "Open Ended Schemes",
    "scheme_category": "Equity Scheme - Large Cap Fund",
    "scheme_code": 125497,
    "scheme_name": "HDFC Top 100 Fund - Direct Plan - Growth",
    "isin_growth": "INF179K01BB2",
    "isin_div_reinvestment": null
  },
  "data": [
    {
      "date": "26-10-2024",
      "nav": "892.45600"
    }
  ],
  "status": "SUCCESS"
}
```

### Search (`/mf/search?q=...`)

```json
[
  {
    "schemeCode": 125497,
    "schemeName": "HDFC Top 100 Fund - Direct Plan - Growth"
  }
]
```

### Scheme list (`/mf`)

```json
[
  {
    "schemeCode": 125497,
    "schemeName": "HDFC Top 100 Fund - Direct Plan - Growth",
    "isinGrowth": "INF179K01BB2",
    "isinDivReinvestment": "INF179K01BC0"
  }
]
```

## Endpoints Reference

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/mf/search` | Search schemes by name | `q` (required) |
| GET | `/mf` | List all schemes (paginated) | `limit` (1–1000), `offset` (default 0) |
| GET | `/mf/{scheme_code}` | NAV history for a scheme | `startDate`, `endDate` (ISO 8601) |
| GET | `/mf/{scheme_code}/latest` | Latest NAV for a scheme | — |
| GET | `/mf/latest` | Latest NAV for all schemes | — |

## Get Latest NAV by ISIN (Python)

The API doesn't support querying by ISIN directly. The `scripts/get_nav.py` script resolves ISIN → scheme code using a locally cached scheme list, then fetches the latest NAV.

### How it works

1. **Cache** — Downloads the full scheme list (`/mf`, ~37k schemes) to `/tmp/mfapi-schemes.json`. Refreshes automatically if the cache is missing or older than 24 hours.
2. **Lookup** — Searches `isinGrowth` and `isinDivReinvestment` fields in the cache. If no match, refreshes the cache and retries.
3. **Fetch** — Uses the resolved scheme code to call `/mf/{scheme_code}/latest`.

### Usage

```bash
# Single ISIN
python3 scripts/get_nav.py INF200K01UT4

# Multiple ISINs
python3 scripts/get_nav.py INF200K01UT4 INF846K01DP8
```

### Example output

```json
{
  "isin": "INF200K01UT4",
  "scheme_code": 119800,
  "scheme_name": "SBI Liquid Fund - DIRECT PLAN -Growth",
  "fund_house": "SBI Mutual Fund",
  "category": "Debt Scheme - Liquid Fund",
  "nav": "4277.67540",
  "date": "18-02-2026"
}
```

When multiple ISINs are passed, the output is a JSON array.

## Notes

- Dates in responses use `DD-MM-YYYY` format; query params use ISO 8601 (`YYYY-MM-DD`)
- NAV values are strings with 5-decimal precision
- Scheme codes can be found via the search or list endpoints, or from AMFI's website
- The `/mf` endpoint returns all ~37,000 schemes; the Python script caches it locally at `/tmp/mfapi-schemes.json` to avoid repeated large fetches
- Cache auto-refreshes on ISIN lookup miss or after 24 hours
- No rate-limit headers are published, but the API asks for fair usage

## Examples

```bash
# Find all SBI mutual fund schemes
curl -s "https://api.mfapi.in/mf/search?q=SBI" | jq '.[].schemeName'

# Get today's NAV for a known scheme
curl -s "https://api.mfapi.in/mf/119551/latest" | jq '.data[0]'

# Compare NAVs across a year
curl -s "https://api.mfapi.in/mf/125497?startDate=2025-01-01&endDate=2025-12-31" \
  | jq '[.data[0], .data[-1]] | {latest: .[0], oldest: .[1]}'

# Get fund house and category for a scheme
curl -s "https://api.mfapi.in/mf/125497/latest" | jq '.meta | {fund_house, scheme_category}'

# List first 10 Direct Plan Growth schemes matching "Axis"
curl -s "https://api.mfapi.in/mf/search?q=Axis" \
  | jq '[.[] | select(.schemeName | test("Direct.*Growth"))] | .[:10]'

# Get latest NAV by ISIN
python3 scripts/get_nav.py INF200K01UT4
```