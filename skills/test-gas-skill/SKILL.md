---
name: gas-price-alert
description: Find and monitor gas prices with daily notifications. Use when searching for the cheapest gas in a specific area, tracking Costco and other discount fuel stations, or setting up daily gas price alerts. Supports any US location with configurable radius and fuel type.
---

# Gas Price Alert

## Overview

Automatically search for the cheapest gas prices in your area, with a focus on Costco and other discount stations. Get daily notifications with the best options within a specified radius.

## Quick Start

1. **Configure location** - Set your city/coordinates and search radius
2. **Run search** - Find gas stations and estimated prices
3. **Schedule daily alerts** - Get morning notifications with cheapest options
4. **Focus on Costco** - Costco typically has gas $0.15-0.25 below market average

## Workflow

### Step 1: Configure Your Location

**Option A: Use ZIP code (recommended)**

```bash
# Search by ZIP code
python3 scripts/gas_alternative.py --zip 43215 --radius 20 --fuel 87 --summary
```

**Option B: Use coordinates**

Default locations are pre-configured for Columbus, Ohio:

```bash
# Columbus, OH (downtown)
lat: 39.9612
lon: -82.9988
radius: 20 miles
```

To use a different location:

```bash
python3 scripts/gas_alternative.py --lat <latitude> --lon <longitude> --radius <miles>
```

**Common US cities:**
- Columbus, OH: 39.9612, -82.9988
- Chicago, IL: 41.8781, -87.6298
- New York, NY: 40.7128, -74.0060
- Los Angeles, CA: 34.0522, -118.2437
- Miami, FL: 25.7617, -80.1918

### Step 2: Search for Gas Stations

```bash
# Search with summary output
python3 scripts/gas_alternative.py --lat 39.9612 --lon -82.9988 --radius 20 --fuel 87 --summary

# Save to file
python3 scripts/gas_alternative.py --lat 39.9612 --lon -82.9988 --radius 20 --fuel 87 --output gas_prices.json
```

**Parameters:**
- `--zip`: ZIP code (overrides lat/lon, e.g., `--zip 43215`)
- `--lat`: Latitude (default: 39.9612 - Columbus, OH)
- `--lon`: Longitude (default: -82.9988 - Columbus, OH)
- `--radius`: Search radius in miles (default: 20)
- `--fuel`: Fuel type - 87, 89, 91, diesel (default: 87)
- `--base-price`: Base price for estimation (default: 2.89)
- `--output`: Output file (default: gas_prices.json)
- `--summary`: Print human-readable summary to stdout

### Step 3: Set Up Daily Alerts

Use OpenClaw cron to receive daily morning notifications:

```json
{
  "name": "Gas price alert",
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *",
    "tz": "America/New_York"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Get me gas prices for Columbus, OH this morning. Focus on Costco and show the cheapest 87 octane within 20 miles of downtown."
  },
  "sessionTarget": "main"
}
```

This runs every day at 8 AM Eastern Time.

### Step 4: Receive Notifications

The agent will:
1. Search for gas stations in your area
2. Identify Costco and discount stations
3. Generate a summary with the cheapest options
4. Send the summary via Telegram

**Example notification:**

```
⛽ Gas Prices (87 Octane) - Columbus, OH

🏠 Costco (Typically Cheapest)
• Costco Gas
  💰 $2.69 (est.)
  📍 5000 Morse Rd, Columbus, OH 43213 (7.9 miles from downtown)

💡 Tip: Costco typically has gas $0.15-0.25 below market average.
```

## Output Format

Each station includes:

```json
{
  "source": "osm",
  "name": "Costco Gas",
  "brand": "Costco",
  "address": "5000 Morse Rd, Columbus, OH 43213",
  "lat": 39.9667,
  "lon": -82.8500,
  "distance": 7.9,
  "fuel_type": "87",
  "price": 2.69,
  "price_text": "$2.69 (est.)",
  "is_costco": true,
  "scraped_at": "2026-02-10T21:00:00.000Z"
}
```

## How It Works

1. **OpenStreetMap/Overpass API** - Finds all gas stations in the area
2. **Costco database** - Known Costco locations are matched and prioritized
3. **Price estimation** - Costco prices estimated $0.15-0.25 below market average
4. **Distance calculation** - Uses geodesic distance for accurate mileage
5. **Smart filtering** - Removes duplicates and sorts by relevance

## Limitations

- **Real-time prices:** Currently uses estimated prices for Costco. For exact prices, check GasBuddy.com or station apps.
- **Coverage:** Relies on OpenStreetMap data completeness
- **Estimation accuracy:** Costco prices estimated based on typical discount patterns

## For Real-Time Prices

To get actual real-time prices:

1. **GasBuddy.com** - Check manually or use their commercial API
2. **Station apps** - Costco, Kroger, Shell, etc., have apps with current prices
3. **AAA** - Provides average prices by region
4. **Waze** - Community-sourced price updates

## Troubleshooting

### No stations found

- Increase the `--radius` parameter
- Verify coordinates are correct
- Check if the area has good OpenStreetMap coverage

### Incorrect prices

- Prices for non-Costco stations are estimated as "N/A"
- Costco prices are estimates based on typical discount patterns
- For exact prices, use GasBuddy or the station's app

### Geopy not installed

```bash
pip install geopy
```

## Resources

### scripts/gas_alternative.py
Main script for searching gas stations using OpenStreetMap and Overpass API.

**Features:**
- Finds all gas stations within radius
- Identifies Costco locations
- Estimates Costco prices
- Calculates distances
- Generates human-readable summaries

### scripts/gasbuddy_search.py
Alternative script for GasBuddy integration (requires Playwright or API key).

**Use when:**
- You have a GasBuddy API key
- You need real-time prices
- You're willing to use Playwright for JavaScript rendering

### references/locations.md
Coordinates and configurations for common US cities.

## Dependencies

Install required packages:

```bash
pip install requests geopy
```

For Playwright-based GasBuddy scraping (optional):

```bash
pip install playwright
playwright install
```
