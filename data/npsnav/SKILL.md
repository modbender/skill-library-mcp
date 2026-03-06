---
name: npsnav
description: Query Indian NPS (National Pension System) fund NAV data, scheme info, returns, and history via the free npsnav.in REST API.
homepage: https://npsnav.in
metadata:
  {
    "openclaw":
      { "emoji": "🏦", "requires": { "bins": ["jq", "curl"] } },
  }
---

# NPS NAV Skill

Query Indian NPS (National Pension System) fund data — NAV, scheme info, returns, history — using the free [npsnav.in](https://npsnav.in) API.

## Setup

No authentication or API keys required. The API is completely free for non-commercial use.

Ensure `curl` and `jq` are installed.

## What is an NPS Scheme Code?

NPS scheme codes follow the format `SM` followed by 6 digits (e.g. `SM001001`). Each code uniquely identifies an NPS fund managed by a Pension Fund Manager (PFM). Scheme codes can be discovered via the Schemes API or from the [full list of NPS funds](https://npsnav.in/nps-funds-list).

## Base URL

```
https://npsnav.in/api
```

## Usage

### Get latest NAV for a scheme (plain text)

The simplest endpoint — returns just the NAV number as plain text. Perfect for spreadsheets and quick lookups.

```bash
curl -s "https://npsnav.in/api/SM001001"
# → 46.7686
```

### List all scheme codes

```bash
curl -s "https://npsnav.in/api/schemes" | jq '.data[] | {code: .[0], name: .[1]}'
```

### Get latest NAV for all funds (detailed)

```bash
curl -s "https://npsnav.in/api/latest" | jq '.data[:5]'
```

### Get latest NAV for all funds (minimal)

```bash
curl -s "https://npsnav.in/api/latest-min" | jq '.data[:5]'
```

### Get detailed fund data with returns

```bash
curl -s "https://npsnav.in/api/detailed/SM001001" | jq '.'
```

### Get historical NAV data

```bash
curl -s "https://npsnav.in/api/historical/SM001001" | jq '.data[:5]'
```

## More Examples

```bash
# Get NAV for SBI Pension Fund (Central Govt)
curl -s "https://npsnav.in/api/SM001001"

# List all NPS scheme names
curl -s "https://npsnav.in/api/schemes" | jq '.data[] | .[1]'

# Get detailed data with returns for a scheme
curl -s "https://npsnav.in/api/detailed/SM001001" | jq '{name: .["Scheme Name"], nav: .NAV, "1Y": .["1Y"], "3Y": .["3Y"]}'

# Get latest NAV and date for all funds
curl -s "https://npsnav.in/api/latest" | jq '.data[] | {code: .["Scheme Code"], name: .["Scheme Name"], nav: .NAV}'

# Get historical NAV for a scheme
curl -s "https://npsnav.in/api/historical/SM001001" | jq '[.data[0], .data[-1]] | {latest: .[0], oldest: .[1]}'

# Find a scheme by name (filter from schemes list)
curl -s "https://npsnav.in/api/schemes" | jq '.data[] | select(.[1] | test("HDFC")) | {code: .[0], name: .[1]}'
```

## Endpoints Reference

| Method | Endpoint                       | Description                        | Response    |
|--------|--------------------------------|------------------------------------|-------------|
| GET    | `/api/schemes`                 | List all scheme codes and names    | JSON        |
| GET    | `/api/{scheme_code}`           | Latest NAV for a scheme            | Plain text  |
| GET    | `/api/latest`                  | Latest NAV for all funds (detailed)| JSON        |
| GET    | `/api/latest-min`              | Latest NAV for all funds (minimal) | JSON        |
| GET    | `/api/detailed/{scheme_code}`  | Fund data with returns             | JSON        |
| GET    | `/api/historical/{scheme_code}`| Historical NAV data                | JSON        |

## Notes

- Scheme codes follow the format `SM` + 6 digits (e.g. `SM001001`)
- Dates in responses use `DD-MM-YYYY` format
- The Simple API (`/api/{scheme_code}`) returns plain text, not JSON
- The `/api/schemes` endpoint returns all ~151 NPS schemes
- No API keys or rate limits; unlimited non-commercial usage
- Data is sourced from Protean eGov Technologies and NPS Trust
