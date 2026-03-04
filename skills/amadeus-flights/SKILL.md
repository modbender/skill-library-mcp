---
name: flights
description: Query flight offers (price, schedule, availability) via Amadeus API. Use when user asks about flight/机票/航班 prices, schedules, or availability.
metadata: {"openclaw":{"emoji":"✈️","requires":{"bins":["node"],"env":["AMADEUS_API_KEY","AMADEUS_API_SECRET"]}}}
---

# Flight Query (Amadeus)

Query real-time flight offers including price, schedule, stops, and seat availability.

## Setup

Set environment variables (or hardcoded defaults are used):

```bash
export AMADEUS_API_KEY=your_key
export AMADEUS_API_SECRET=your_secret
# For production (real data):
export AMADEUS_BASE_URL=https://api.amadeus.com
```

## Query Flights

```bash
node {baseDir}/scripts/query.mjs <FROM_IATA> <TO_IATA> [-d YYYY-MM-DD] [options]
```

### Examples

```bash
# Hong Kong to Shanghai
node {baseDir}/scripts/query.mjs HKG PVG -d 2026-02-25

# Direct flights only
node {baseDir}/scripts/query.mjs SWA HGH -d 2026-02-24 --direct

# Business class
node {baseDir}/scripts/query.mjs HKG PVG -d 2026-02-25 -c BUSINESS

# JSON output
node {baseDir}/scripts/query.mjs HKG PVG -d 2026-02-25 --json
```

### Options

- `-d, --date <YYYY-MM-DD>`: Departure date (default: today)
- `-a, --adults <n>`: Number of adults (default: 1)
- `-c, --class <class>`: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
- `--direct`: Non-stop flights only
- `-n, --max <n>`: Max results (default: 20)
- `--currency <code>`: Currency code (default: CNY)
- `--json`: Raw JSON output

## Airport Lookup

```bash
node {baseDir}/scripts/airports.mjs 揭阳    # → SWA
node {baseDir}/scripts/airports.mjs 杭州    # → HGH
node {baseDir}/scripts/airports.mjs tokyo   # API lookup
```

Built-in mappings for 40+ Chinese cities. Falls back to Amadeus API for others.

## Notes

- Test environment returns simulated data; production returns real prices
- Switch to production: set `AMADEUS_BASE_URL=https://api.amadeus.com`
- Free tier: 2000 calls/month (production)
