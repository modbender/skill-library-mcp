---
name: capmetro-skill
description: Austin CapMetro transit - real-time vehicle positions, next arrivals, service alerts, route info, and trip planning for buses and rail (MetroRail, MetroRapid, MetroBus). Use when the user asks about Austin public transit, bus schedules, train times, CapMetro alerts, or nearby stops.
homepage: "https://github.com/brianleach/capmetro-skill"
license: MIT
metadata:
  clawdbot:
    emoji: "🚌"
    tags: [transit, austin, capmetro, transportation, bus, train, schedule]
    requires:
      bins: ["node", "unzip"]
      env: []
    files: ["scripts/capmetro.mjs", "scripts/gtfs-realtime.proto"]
    install:
      - id: npm-deps
        kind: shell
        command: "npm install --prefix $SKILL_DIR protobufjs"
        label: "Install protobufjs Node.js dependency"
---

# CapMetro Austin Transit

Real-time Austin CapMetro transit data - vehicle positions, next arrivals, service alerts, and route information. No API key required.

## When to Use

- User asks about Austin bus or train schedules, arrival times, or delays
- User asks "when is the next bus/train" or "is the 801 running"
- User asks about CapMetro service alerts, detours, or disruptions
- User wants to know where a bus/train currently is
- User asks about nearby stops or route information
- User mentions MetroRail (Red Line), MetroRapid (801/803), or any Austin bus route
- User asks about CapMetro fares, how to ride, or general transit info

## Data Sources

All feeds are **open access, no API key required**, hosted on the Texas Open Data Portal.

### GTFS-RT (Real-Time) Feeds - Updated every 15 seconds

| Feed | Format | URL |
|------|--------|-----|
| Vehicle Positions | JSON | `https://data.texas.gov/download/cuc7-ywmd/text%2Fplain` |
| Vehicle Positions | Protobuf | `https://data.texas.gov/download/eiei-9rpf/application%2Foctet-stream` |
| Trip Updates | Protobuf | `https://data.texas.gov/download/rmk2-acnw/application%2Foctet-stream` |
| Service Alerts | Protobuf | `https://data.texas.gov/download/nusn-7fcn/application%2Foctet-stream` |

### GTFS Static Feed - Route/Stop/Schedule data

| Feed | Format | URL |
|------|--------|-----|
| GTFS Static (zip) | ZIP | `https://data.texas.gov/download/r4v4-vz24/application%2Fx-zip-compressed` |

## Implementation

### Quick Start: Use the helper scripts

The scripts in this skill's `scripts/` directory handle fetching, parsing, and presenting CapMetro data.

### Script: `scripts/capmetro.mjs`

Main entry point. Supports these commands:

```bash
# Get current service alerts
node scripts/capmetro.mjs alerts

# Get real-time vehicle positions (optionally filter by route)
node scripts/capmetro.mjs vehicles [--route 801]

# Get next arrivals at a stop (by stop_id)
node scripts/capmetro.mjs arrivals --stop <stop_id>

# Get arrivals by searching stop name (uses best match)
node scripts/capmetro.mjs arrivals --stop-search "lakeline" --route 550

# Get arrivals filtered by direction/headsign
node scripts/capmetro.mjs arrivals --stop-search "downtown" --route 550 --headsign "lakeline"

# Get arrivals filtered by route at a stop
node scripts/capmetro.mjs arrivals --stop <stop_id> --route 801

# Search for stops by name or location
node scripts/capmetro.mjs stops --search "domain" 
node scripts/capmetro.mjs stops --near 30.4,-97.7

# List all routes
node scripts/capmetro.mjs routes

# Get route details including stops
node scripts/capmetro.mjs route-info --route 801

# Download/refresh GTFS static data (run periodically)
node scripts/capmetro.mjs refresh-gtfs
```

### Setup: GTFS Static Data

On first use, run `node scripts/capmetro.mjs refresh-gtfs` to download and extract the static GTFS data (routes, stops, schedules) to `~/.capmetro/gtfs/`. This only needs to be refreshed when CapMetro updates their schedule (typically quarterly or during service changes).

### Key Route Reference

| Route | Name | Type |
|-------|------|------|
| 550 | MetroRail Red Line | Rail (Leander ↔ Downtown) |
| 801 | MetroRapid North/South | Rapid Bus (Tech Ridge ↔ Southpark Meadows) |
| 803 | MetroRapid Burnet/South Lamar | Rapid Bus (Domain ↔ Westgate) |
| 1 | N Lamar/S Congress | Local Bus |
| 7 | Duval/Dove Springs | Local Bus |
| 10 | S 1st/Red River | Local Bus |
| 20 | Manor Rd/Riverside | Local Bus |
| 300 | Oltorf/Riverside Crosstown | Crosstown Bus |
| 325 | Ohlen/Loyola | Crosstown Bus |
| 985 | Night Owl | Late Night Service |

### Tips for Users

- **Stop IDs** can be found on CapMetro stop signs, in the Transit app, or by searching with the `stops` command
- **MetroRapid 801/803** have the most frequent service (every 10-12 minutes during peak)
- **MetroRail Red Line (550)** runs Leander to Downtown Austin with limited frequency
- Service alerts often contain detour information - check alerts before advising routes
- Vehicle position data updates every ~15 seconds, so locations are near real-time

### Error Handling

- If a feed returns an error or empty data, inform the user that real-time data may be temporarily unavailable
- The JSON vehicle positions feed is easier to parse and a good fallback if protobuf parsing fails
- GTFS static data is required for stop names, route names, and schedule lookups - ensure it's been downloaded

### Response Formatting

When presenting transit info to the user:
- Lead with the most actionable info (next arrival time, active alerts)
- Include route number AND name (e.g., "Route 801 MetroRapid")
- Show times in 12-hour format with AM/PM
- For delays, show both scheduled and estimated times
- For vehicle positions, describe location relative to landmarks when possible
- If there are active service alerts for the route the user asked about, always mention them

## Fares Reference (as of 2025)

| Fare Type | Price |
|-----------|-------|
| Local / MetroRapid | $1.25 |
| MetroRail | $3.50 (single) |
| Day Pass | $2.50 |
| 7-Day Pass | $11.25 |
| 31-Day Pass | $41.25 |

Payment via Umo app, tap-to-pay, or fare card. Free transfers within 2 hours.

## External Endpoints

| Endpoint | Data Sent | Data Received |
|----------|-----------|---------------|
| `data.texas.gov/download/cuc7-ywmd/...` | None (GET only) | Vehicle positions (JSON) |
| `data.texas.gov/download/eiei-9rpf/...` | None (GET only) | Vehicle positions (Protobuf) |
| `data.texas.gov/download/rmk2-acnw/...` | None (GET only) | Trip updates (Protobuf) |
| `data.texas.gov/download/nusn-7fcn/...` | None (GET only) | Service alerts (Protobuf) |
| `data.texas.gov/download/r4v4-vz24/...` | None (GET only) | GTFS static data (ZIP) |

All endpoints are open-access Texas Open Data Portal URLs. No API key, authentication, or user data is transmitted.

## Security & Privacy

- **No credentials required** - all data sources are open access, no API keys or tokens
- **No user data transmitted** - requests are anonymous GET calls with no query parameters containing user info
- **Local storage only** - GTFS static data is cached locally at `~/.capmetro/gtfs/`; no data is written elsewhere
- **No telemetry** - this skill does not phone home or collect usage data
- **Input handling** - stop names and route IDs from user input are used only for local filtering, never interpolated into URLs or shell commands

## Trust Statement

This skill only reads publicly available transit data from the Texas Open Data Portal. It does not access, store, or transmit any personal information. All network requests are read-only GET calls to open government data feeds.
