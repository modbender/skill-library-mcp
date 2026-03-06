# TfL London Transit — OpenClaw Skill

> **Real-time London transit data for your OpenClaw agent.** Get Tube arrivals, bus predictions, line status, disruptions, journey plans, and route info for all TfL services.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js 18+](https://img.shields.io/badge/node-18%2B-green.svg)](https://nodejs.org)
[![ClawHub](https://img.shields.io/badge/ClawdHub-Skill-green.svg)](https://clawhub.ai)

---

## Why This Skill?

**For anyone who rides TfL and wants:**
- Real-time Tube arrivals — know exactly when the next train comes
- Bus predictions — see when your bus will arrive at your stop
- Line status at a glance — check all Tube lines in one command
- Disruption alerts — know about delays, closures, and planned work
- Journey planning — step-by-step directions with fare estimates
- Stop and route lookup — find the nearest stop or explore a route's path

**How it works:**
All data comes from the [TfL Unified API](https://api.tfl.gov.uk/) — a single REST JSON API that covers Tube, bus, DLR, Overground, Elizabeth line, trams, river bus, and cable car. No protobuf, no GTFS parsing, no multiple APIs. Just clean JSON.

---

## Quick Start

### Step 1: Get an API Key (free, optional)

The TfL API works without a key (rate-limited). For 500 requests/minute:

1. Register at https://api-portal.tfl.gov.uk/
2. Create an app to get your `app_key`

### Step 2: Set Environment Variable

```bash
# Add to your shell profile or .env file:
export TFL_API_KEY=your-key-here
```

### Step 3: Install the Skill

```bash
# Copy to your skills directory
cp -r tfl-skill ~/.openclaw/skills/tfl

# Or for a workspace-specific install:
cp -r tfl-skill <workspace>/skills/tfl
```

No npm dependencies to install. No GTFS data to download. Ready to use immediately.

---

## What You Can Do

### Line Status
- Check all Tube lines at a glance — Good Service, Minor Delays, etc.
- See all TfL modes (Tube + DLR + Overground + Elizabeth line)
- Get detailed status for a specific line with disruption reasons

### Real-Time Arrivals
- See when the next Tube train arrives at any station
- Search stations by name — no need to memorize NaPTAN IDs
- Filter by line (e.g., just Piccadilly line arrivals at King's Cross)
- Shows platform names and current train locations

### Bus Predictions
- Real-time bus arrival predictions at any stop
- Filter by route number
- Search for bus stops by name

### Disruptions
- Active delays, closures, and planned engineering work
- Filter by line
- Colour-coded severity

### Journey Planning
- Plan journeys from A to B across all TfL modes
- Step-by-step directions with walking, Tube, bus, DLR, etc.
- Shows fare estimates when available
- Works with station names or coordinates

### Route & Stop Discovery
- Search for stops by name or proximity to a location
- List all stops on a line
- View route stop sequences
- List all 700+ bus routes

---

## Usage (via OpenClaw Chat)

Just ask your agent naturally:

- "Is the Northern line running?"
- "When's the next Tube at Oxford Circus?"
- "Any delays on the Piccadilly line?"
- "When does the 24 bus come to Oxford Circus?"
- "How do I get from Waterloo to King's Cross?"
- "Find Tube stations near Big Ben"
- "What's the TfL status right now?"

---

## Example Workflows

### Check Tube Status

```bash
# All Tube lines
node scripts/tfl.mjs status

# All TfL modes (Tube + DLR + Overground + Elizabeth)
node scripts/tfl.mjs status --all

# Specific line
node scripts/tfl.mjs status --line victoria
```

### Get Arrivals at a Station

```bash
# Search by station name
node scripts/tfl.mjs arrivals --stop-search "oxford circus"

# Filter by line
node scripts/tfl.mjs arrivals --stop-search "kings cross" --line piccadilly

# Use exact NaPTAN ID
node scripts/tfl.mjs arrivals --stop 940GZZLUOXC
```

### Plan a Journey

```bash
# By station name
node scripts/tfl.mjs journey --from "waterloo" --to "oxford circus"

# By coordinates
node scripts/tfl.mjs journey --from "51.5031,-0.1132" --to "51.5308,-0.1238"
```

### Find Nearby Stops

```bash
# Within 500m of a location
node scripts/tfl.mjs stops --near 51.5074,-0.1278 --radius 500
```

---

## Command Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Line Status** | |
| All Tube lines status | `tfl.mjs status` |
| All TfL modes status | `tfl.mjs status --all` |
| Specific line status | `tfl.mjs status --line victoria` |
| **Arrivals** | |
| Search station by name | `tfl.mjs arrivals --stop-search "oxford circus"` |
| Arrivals by NaPTAN ID | `tfl.mjs arrivals --stop 940GZZLUOXC` |
| Filter by line | `tfl.mjs arrivals --stop-search "kings cross" --line piccadilly` |
| **Bus Predictions** | |
| Bus arrivals at stop | `tfl.mjs bus-arrivals --stop 490005183E` |
| Search bus stop | `tfl.mjs bus-arrivals --stop-search "oxford circus"` |
| Filter by route | `tfl.mjs bus-arrivals --stop-search "oxford circus" --route 24` |
| **Disruptions** | |
| All disruptions | `tfl.mjs disruptions` |
| Disruptions for a line | `tfl.mjs disruptions --line northern` |
| **Stops** | |
| Search by name | `tfl.mjs stops --search "waterloo"` |
| Find nearby stops | `tfl.mjs stops --near LAT,LON` |
| Set search radius (meters) | `tfl.mjs stops --near LAT,LON --radius 500` |
| Stops on a line | `tfl.mjs stops --line victoria` |
| **Routes** | |
| Tube lines | `tfl.mjs routes` |
| All TfL lines | `tfl.mjs routes --all` |
| All bus routes | `tfl.mjs bus-routes` |
| Route details + stops | `tfl.mjs route-info --line bakerloo` |
| Bus route stops | `tfl.mjs route-info --route 24` |
| **Journey Planning** | |
| Journey by name | `tfl.mjs journey --from "waterloo" --to "kings cross"` |
| Journey by coordinates | `tfl.mjs journey --from "51.5031,-0.1132" --to "51.5308,-0.1238"` |

---

## Tube Lines Reference

| ID | Line | Terminals |
|----|------|-----------|
| bakerloo | Bakerloo | Harrow & Wealdstone <-> Elephant & Castle |
| central | Central | Epping / Ealing Broadway <-> West Ruislip |
| circle | Circle | Hammersmith (loop via Liverpool Street) |
| district | District | Richmond / Ealing Broadway <-> Upminster |
| hammersmith-city | Hammersmith & City | Hammersmith <-> Barking |
| jubilee | Jubilee | Stanmore <-> Stratford |
| metropolitan | Metropolitan | Chesham / Amersham / Uxbridge <-> Aldgate |
| northern | Northern | Edgware / High Barnet <-> Morden / Battersea |
| piccadilly | Piccadilly | Heathrow T5 / Uxbridge <-> Cockfosters |
| victoria | Victoria | Walthamstow Central <-> Brixton |
| waterloo-city | Waterloo & City | Waterloo <-> Bank |

### London Overground Lines

| ID | Line | Route |
|----|------|-------|
| liberty | Liberty | Romford — Upminster |
| lioness | Lioness | Watford — Euston |
| mildmay | Mildmay | Stratford — Richmond / Clapham Junction |
| suffragette | Suffragette | Gospel Oak — Barking Riverside |
| weaver | Weaver | Liverpool Street — Enfield / Cheshunt / Chingford |
| windrush | Windrush | Highbury & Islington — Crystal Palace / Clapham / West Croydon |

### Other TfL Rail

| ID | Line | Type |
|----|------|------|
| dlr | DLR | Docklands Light Railway |
| elizabeth | Elizabeth line | Crossrail |
| tram | London Trams | Croydon Tramlink |

---

## Key Bus Routes Reference

| Route | Name | Notes |
|-------|------|-------|
| 24 | Pimlico — Hampstead Heath | Via Victoria, Camden |
| 73 | Victoria — Stoke Newington | Via Oxford Street, Angel |
| 38 | Victoria — Clapton Pond | Via Piccadilly, Angel |
| 390 | Archway — Notting Hill Gate | Via Camden, Oxford Street |
| 148 | Camberwell — White City | Via Westminster, Notting Hill |
| 15 | Blackwall — Trafalgar Square | Heritage route via Tower, St Paul's |
| 11 | Fulham Broadway — Liverpool Street | Via Chelsea, Westminster |
| 23 | Westbourne Park — Liverpool Street | Via Oxford Street, Bank |
| 88 | Camden Town — Clapham Common | Via Westminster |
| 159 | Streatham — Paddington | Via Brixton, Westminster |

---

## Installation for ClawdHub

Once published on ClawdHub, users can install this skill with:

```bash
clawhub install tfl
```

**Manual installation:**
```bash
cp -r tfl-skill ~/.openclaw/skills/tfl
```

No `npm install` needed — zero dependencies!

---

## Requirements

| Requirement | Details | How to Get |
|-------------|---------|------------|
| **Node.js 18+** | Runtime for the skill | [nodejs.org](https://nodejs.org) |
| **TfL API Key** | Optional, recommended | [Register here](https://api-portal.tfl.gov.uk/) |

---

## Data Sources

| API | Auth | Update Frequency |
|-----|------|-----------------|
| TfL Unified API | API key (free, optional) | Real-time |

All data from a single API: `api.tfl.gov.uk`. Covers Tube, bus, DLR, Overground, Elizabeth line, trams, river bus, and cable car.

---

## Troubleshooting

### "Rate limited by TfL API"
**Solution:** Get a free API key for 500 requests/minute:
```bash
# Register at: https://api-portal.tfl.gov.uk/
export TFL_API_KEY=your-key-here
```

### No arrivals showing up
**Possible causes:**
- Station is closed (check with `status` command)
- No active service at this time (late night, planned closures)
- NaPTAN ID is incorrect — try `--stop-search` to find the right one

### "No stations found matching"
**Possible causes:**
- Spelling mismatch — try a shorter search term
- Station not in the embedded data — the API search will be tried automatically

### Journey planning returns no results
**Possible causes:**
- Station names couldn't be resolved — try using coordinates
- Service is unavailable at the requested time

---

## TfL Fares Reference (from March 2025)

| Fare Type | Price |
|-----------|-------|
| Tube Zone 1 (Oyster/contactless, peak) | £2.80 |
| Tube Zone 1 (Oyster/contactless, off-peak) | £2.70 |
| Tube Zones 1-2 (peak) | £2.80 |
| Tube Zones 1-2 (off-peak) | £2.70 |
| Tube Zones 1-3 (peak) | £3.50 |
| Tube Zones 1-3 (off-peak) | £2.80 |
| Bus & Tram (any journey) | £1.75 |
| Hopper fare (unlimited bus/tram within 1 hour) | £1.75 total |
| Daily cap Zones 1-2 | £8.90 |
| Weekly cap Zones 1-2 | £44.70 |
| Cash single (ticket machine) | £6.70 (Zone 1) |

Peak: Mon-Fri 6:30-9:30am and 4:00-7:00pm (except public holidays).

---

## Learn More

### Resources
- **[TfL Unified API](https://api.tfl.gov.uk/)** — Interactive API explorer and documentation
- **[TfL API Portal](https://api-portal.tfl.gov.uk/)** — Register for API keys
- **[TfL Open Data](https://tfl.gov.uk/info-for/open-data-users/)** — Data policy and terms
- **[Tube Map](https://tfl.gov.uk/maps/track/tube)** — Official Tube map

---

## About This Skill

**Skill Type:** Data Integration (TfL Unified REST API)
**Runtime:** Node.js
**Dependencies:** None (native fetch)
**Created for:** ClawdHub / OpenClaw
**License:** MIT

**Credits:**
- Transit data provided by [Transport for London (TfL)](https://tfl.gov.uk)
- Powered by the TfL Unified API
- Contains TfL data used under [TfL Open Data licence](https://tfl.gov.uk/corporate/terms-and-conditions/transport-data-service)

---

**Ready to ride?** Set your API key (or don't — it works without one), and never miss your Tube again.
