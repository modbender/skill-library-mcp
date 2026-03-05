---
name: metra
description: Chicago Metra commuter rail — real-time train arrivals, vehicle tracking, service alerts, and schedule info for all 11 Metra lines serving the Chicago metropolitan area. Use when the user asks about Metra trains, Chicago commuter rail, or specific Metra lines and stations.
homepage: "https://github.com/brianleach/metra-skill"
license: MIT
metadata:
  clawhub:
    emoji: "🚂"
    tags: [transit, chicago, metra, transportation, commuter-rail, train, schedule]
    requires:
      bins: ["node", "unzip"]
      env: ["METRA_API_KEY"]
    files: ["scripts/metra.mjs", "scripts/gtfs-realtime.proto"]
    install:
      - id: npm-deps
        kind: shell
        command: "npm install --prefix $SKILL_DIR"
        label: "Install Node.js dependencies (protobufjs)"
---

# Chicago Metra Commuter Rail

Real-time Chicago Metra commuter rail data — train arrivals (GTFS-RT protobuf), vehicle positions, service alerts, schedule info, and fare calculation for all 11 Metra lines serving the six-county northeastern Illinois region. Requires a free API key for all feeds.

## When to Use

- User asks about Metra, Chicago commuter rail, or commuter trains in Chicago
- User asks "when is the next train" in a Chicago suburban context
- User mentions specific Metra lines: BNSF, UP-N, UP-NW, UP-W, MD-N, MD-W, ME (Metra Electric), RI (Rock Island), NCS, HC (Heritage Corridor), SWS (SouthWest Service)
- User mentions specific Metra stations: Union Station, Ogilvie, Millennium Station, LaSalle Street, Naperville, Aurora, Downers Grove, Evanston, Highland Park, etc.
- User asks about Metra service alerts, delays, or construction
- User asks about Metra fares, zones, monthly passes, Ventra
- User asks about Chicago train schedules (distinguish from CTA "L" trains — Metra is commuter rail)

### When NOT to Use

- User asks about CTA trains (the "L"), CTA buses, or Pace buses — those are separate systems
- User asks about Amtrak long-distance trains at Union Station

## Data Sources

Metra uses standard GTFS-RT protobuf feeds served from a single base URL with Bearer token authentication. No proprietary extensions — clean standard GTFS-RT.

### GTFS Realtime Feeds (Protobuf, requires `METRA_API_KEY`)

Get a free key at: https://metra.com/developers

| Feed | Endpoint | Description |
|------|----------|-------------|
| Trip Updates | `GET /gtfs/public/tripupdates` | Real-time arrival/departure predictions |
| Vehicle Positions | `GET /gtfs/public/positions` | GPS locations of active trains |
| Alerts | `GET /gtfs/public/alerts` | Service alerts, delays, construction notices |

Base URL: `https://gtfspublic.metrarr.com`

Authentication: `Authorization: Bearer {METRA_API_KEY}` header.

Data updates every 30 seconds. No need to poll more frequently.

### GTFS Static Feed

| Feed | URL |
|------|-----|
| GTFS Static (zip) | `https://schedules.metrarail.com/gtfs/schedule.zip` |
| Published timestamp | `https://schedules.metrarail.com/gtfs/published.txt` |

Static schedule updates regularly (sometimes within 24 hours). New scheduled updates publish at 3:00 AM.

### Important Notes from Metra

- If realtime data is unavailable for a trip, assume the static schedule is correct
- Vehicle positions may drop when trains are underground or at terminals (GPS loss)
- Trip updates may be provided hours in advance for annulled or added trains
- If an alert is in the feed, it's active; if it's not, it's no longer active (regardless of active_period)

## Implementation

### Script: `scripts/metra.mjs`

Main entry point. Supports these commands:

```bash
# Train arrivals
node scripts/metra.mjs arrivals --station "Union Station"
node scripts/metra.mjs arrivals --station "Naperville" --line BNSF
node scripts/metra.mjs arrivals --station "Ogilvie"
node scripts/metra.mjs arrivals --station "Millennium Station" --line ME

# Vehicle tracking
node scripts/metra.mjs vehicles --line BNSF
node scripts/metra.mjs vehicles --line UP-N
node scripts/metra.mjs vehicles --line ME

# Service alerts
node scripts/metra.mjs alerts
node scripts/metra.mjs alerts --line BNSF
node scripts/metra.mjs alerts --line RI

# Routes and stops
node scripts/metra.mjs routes
node scripts/metra.mjs stops --search "downers grove"
node scripts/metra.mjs stops --line BNSF
node scripts/metra.mjs stops --near 41.8781,-87.6298
node scripts/metra.mjs route-info --line UP-NW

# Fares
node scripts/metra.mjs fares
node scripts/metra.mjs fares --from "Union Station" --to "Naperville"

# Schedule
node scripts/metra.mjs schedule --station "Naperville"
node scripts/metra.mjs schedule --station "Ogilvie" --line UP-N

# Maintenance
node scripts/metra.mjs refresh-gtfs
```

### Setup: API Key

All Metra feeds require authentication:

1. Register for a free key at https://metra.com/developers
2. Set environment variable: `METRA_API_KEY`

### Setup: GTFS Static Data

On first use, run `node scripts/metra.mjs refresh-gtfs` to download and extract the static GTFS data (routes, stops, schedules) to `~/.metra/gtfs/`. Refresh periodically or when Metra updates their schedule.

### Metra Lines Reference

| Line Code | Line Name | Color | Downtown Terminal | Outer Terminal |
|-----------|-----------|-------|-------------------|----------------|
| BNSF | BNSF Railway | Orange | Union Station (CUS) | Aurora |
| ME | Metra Electric | Teal | Millennium Station | University Park / South Chicago / Blue Island |
| HC | Heritage Corridor | Purple | Union Station (CUS) | Joliet |
| MD-N | Milwaukee District North | Light Green | Union Station (CUS) | Fox Lake |
| MD-W | Milwaukee District West | Light Green | Union Station (CUS) | Elburn / Big Timber |
| NCS | North Central Service | Gold | Union Station (CUS) | Antioch |
| RI | Rock Island | Red | LaSalle Street Station | Joliet |
| SWS | SouthWest Service | Dark Purple | Union Station (CUS) | Manhattan |
| UP-N | Union Pacific North | Dark Green | Ogilvie Transportation Center (OTC) | Kenosha |
| UP-NW | Union Pacific Northwest | Blue | Ogilvie Transportation Center (OTC) | Harvard / McHenry |
| UP-W | Union Pacific West | Blue | Ogilvie Transportation Center (OTC) | Elburn |

### Downtown Terminal Stations

- **Chicago Union Station (CUS)** — Zone 1 — BNSF, HC, MD-N, MD-W, NCS, SWS
- **Ogilvie Transportation Center (OTC)** — Zone 1 — UP-N, UP-NW, UP-W
- **LaSalle Street Station** — Zone 1 — RI
- **Millennium Station** — Zone 1 — ME

### Metra Fares Reference (4-Zone System, effective Feb 2024)

| Ticket Type | Zones 1-2 | Zones 1-2-3 | Zones 1-2-3-4 | Zones 2-3-4 (no downtown) |
|-------------|-----------|-------------|---------------|---------------------------|
| One-Way | $3.75 | $5.50 | $6.75 | $3.75 |
| Day Pass | $7.50 | $11.00 | $13.50 | $7.50 |
| Day Pass 5-Pack | $35.75 | $52.25 | $64.25 | $35.75 |
| Monthly Pass | $75.00 | $110.00 | $135.00 | $75.00 |

Special Passes:
- Saturday/Sunday/Holiday Day Pass: $7.00 (systemwide)
- Weekend Pass (Ventra app only): $10.00 (systemwide)
- Regional Connect Pass (with Monthly): $30.00 (adds CTA + Pace)
- Onboard Surcharge (cash on train): $5.00

Monthly Passes are valid for unlimited rides on weekdays between selected zones and systemwide on weekends.

### Tips for Users

- Metra uses **inbound** (toward downtown Chicago) and **outbound** (away from downtown) for directions
- Train numbers matter — Metra riders often know their train by number (e.g., "the 7:42 BNSF" or "Train 1252")
- Different lines use different downtown terminals — always note which terminal
- Peak trains run during rush hours; off-peak and weekend service is less frequent
- If real-time data is unavailable, the schedule command shows static times
- Use `--line` to filter by specific Metra line code (BNSF, UP-N, etc.)

### Error Handling

- If `METRA_API_KEY` is not set, all commands print a helpful message with the signup URL
- Invalid station names show "No matching station found" with a suggestion to use stops --search
- No real-time data available → fall back to static schedule with a note
- Network errors produce friendly messages
- GPS dropout for vehicle positions → note that train may be underground or at terminal

### Response Formatting

When presenting transit info to the user:
- Lead with the most actionable info (next arrival time, active alerts)
- Show line name AND train number (e.g., "BNSF Train 1252 inbound")
- Show times in 12-hour format with AM/PM
- For arrivals: show both real-time ETA and scheduled time when available
- Always note the downtown terminal for the line
- If there are active service alerts for the line being queried, mention them

## External Endpoints

| Endpoint | Data Sent | Data Received |
|----------|-----------|---------------|
| `gtfspublic.metrarr.com/gtfs/public/tripupdates` | API key (Bearer header, HTTPS) | Trip updates (Protobuf) |
| `gtfspublic.metrarr.com/gtfs/public/positions` | API key (Bearer header, HTTPS) | Vehicle positions (Protobuf) |
| `gtfspublic.metrarr.com/gtfs/public/alerts` | API key (Bearer header, HTTPS) | Service alerts (Protobuf) |
| `schedules.metrarail.com/gtfs/schedule.zip` | None (GET only) | GTFS static data (ZIP) |
| `schedules.metrarail.com/gtfs/published.txt` | None (GET only) | Schedule publish timestamp (text) |

All API calls use HTTPS. The API key is passed as a Bearer token in the Authorization header. No other user data is transmitted.

## Security & Privacy

- **API key required** — All GTFS-RT feeds require a free developer key passed as a Bearer token in the Authorization header
- **No user data transmitted** — Requests contain only the API key; no personal information
- **Local storage only** — GTFS static data is cached locally at `~/.metra/gtfs/`; no data is written elsewhere
- **No telemetry** — This skill does not phone home or collect usage data
- **Input handling** — Stop names and route IDs from user input are used only for local filtering, never interpolated into shell commands

## Trust Statement

This skill reads publicly available transit data from Metra's official GTFS-RT feeds. The API key is used only for Metra API authentication. The skill does not access, store, or transmit any personal information beyond the API key configured by the user.
