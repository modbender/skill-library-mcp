# :metro: CTA Chicago Transit — OpenClaw Skill

> **Real-time Chicago transit data for your OpenClaw agent.** Get L train arrivals, bus predictions, service alerts, and route info for all CTA services.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js 18+](https://img.shields.io/badge/node-18%2B-green.svg)](https://nodejs.org)
[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-green.svg)](https://clawhub.ai)

---

## Why This Skill?

**For anyone who rides CTA and wants:**
- Real-time L train arrivals — know exactly when the next train comes
- Bus predictions — see when your bus will arrive at your stop
- Live vehicle tracking — see where trains and buses are right now
- Service alerts — know about delays, detours, and disruptions before you leave
- Stop and route lookup — find the nearest stop or explore a route's path

**How it works:**
Data comes from CTA's three official APIs — [Train Tracker](https://www.transitchicago.com/developers/traintracker/), [Bus Tracker](https://www.transitchicago.com/developers/bustracker/), and [Customer Alerts](https://www.transitchicago.com/developers/alerts/). Train and bus data require free API keys. Alerts always work with no key.

---

## Quick Start

### Step 1: Get Your API Keys (free)

1. **Train Tracker key:** Apply at https://www.transitchicago.com/developers/traintrackerapply/
2. **Bus Tracker key:** Apply at https://www.transitchicago.com/developers/bustracker/

### Step 2: Set Environment Variables

```bash
cp .env.example .env
# Then edit .env and add your keys:
# CTA_TRAIN_API_KEY=your-train-key-here
# CTA_BUS_API_KEY=your-bus-key-here
```

### Step 3: Install the Skill

```bash
# Copy to your skills directory
cp -r cta-skill ~/.openclaw/skills/cta

# Or for a workspace-specific install:
cp -r cta-skill <workspace>/skills/cta
```

### Step 4: Download Transit Data

```bash
# One-time download of routes, stops, and schedules
node scripts/cta.mjs refresh-gtfs
```

Note: Re-run `refresh-gtfs` periodically when CTA updates their schedule. Alert commands work even without API keys or GTFS data.

---

## What You Can Do

### :clock3: Real-Time Train Arrivals
- See when the next L train arrives at any station
- Search stations by name — no need to memorize IDs
- Filter by L line (Red, Blue, Brown, etc.)
- Shows "Due" for approaching trains, minutes for upcoming

### :bus: Bus Predictions
- Real-time bus arrival predictions at any stop
- Filter by route number
- Search for stops by name

### :round_pushpin: Vehicle Tracking
- View live positions of all active trains on a line
- View live positions of all active buses on a route
- Positions update every 30-60 seconds

### :loudspeaker: Service Alerts
- Active delays, detours, and service disruptions
- Filter by route — works for both L lines and bus routes
- No API key required — alerts always work

### :world_map: Route & Stop Discovery
- Search for stops by name or proximity to a location
- List all CTA routes (L lines + 129 bus routes)
- View every stop along a route in order

---

## Usage (via OpenClaw Chat)

Just ask your agent naturally:

- "When's the next Red Line at Belmont?"
- "Is the Blue Line running to O'Hare?"
- "Any CTA service alerts right now?"
- "Where are the Brown Line trains?"
- "When does the 22 bus come to Clark & Diversey?"
- "Find CTA stops near Wrigley Field"
- "What bus routes does CTA run?"

---

## Example Workflows

### Check When Your Train Arrives

```bash
# Search by station name
node scripts/cta.mjs arrivals --stop-search "belmont" --route Red

# Or use the exact station ID
node scripts/cta.mjs arrivals --mapid 41320

# Or search by station name
node scripts/cta.mjs arrivals --station "Clark/Lake"
```

### Track a Bus

```bash
# When does the 22 bus arrive at my stop?
node scripts/cta.mjs bus-arrivals --stop 1836 --route 22

# Where are all the 77 Belmont buses?
node scripts/cta.mjs bus-vehicles --route 77
```

### Find Nearby Stops

```bash
# What stops are within 0.3 miles of the Loop?
node scripts/cta.mjs stops --near 41.8781,-87.6298 --radius 0.3
```

### Check Alerts Before You Go

```bash
# All current alerts
node scripts/cta.mjs alerts

# Just Red Line alerts
node scripts/cta.mjs alerts --route Red
```

---

## Command Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Train Arrivals** | |
| Search station by name | `cta.mjs arrivals --stop-search "ohare"` |
| Arrivals at station | `cta.mjs arrivals --station "Clark/Lake"` |
| Arrivals by station ID | `cta.mjs arrivals --mapid 40380` |
| Arrivals by stop ID | `cta.mjs arrivals --stop 30070` |
| Filter by L line | `cta.mjs arrivals --stop-search "belmont" --route Red` |
| **Bus Predictions** | |
| Bus arrivals at stop | `cta.mjs bus-arrivals --stop 456` |
| Filter by route | `cta.mjs bus-arrivals --stop 456 --route 22` |
| Search bus stop | `cta.mjs bus-arrivals --stop-search "michigan"` |
| **Vehicle Tracking** | |
| Train positions on a line | `cta.mjs vehicles --route Red` |
| Bus positions on a route | `cta.mjs bus-vehicles --route 22` |
| **Alerts** | |
| All service alerts | `cta.mjs alerts` |
| Alerts for a route | `cta.mjs alerts --route Red` |
| **Stops** | |
| Search by name | `cta.mjs stops --search "belmont"` |
| Find nearby stops | `cta.mjs stops --near LAT,LON` |
| Set search radius | `cta.mjs stops --near LAT,LON --radius 0.5` |
| **Routes** | |
| All routes (L + bus) | `cta.mjs routes` |
| All bus routes (live API) | `cta.mjs bus-routes` |
| Route details + stops | `cta.mjs route-info --route Red` |
| Bus route stops | `cta.mjs route-info --route 22` |
| **Maintenance** | |
| Refresh GTFS data | `cta.mjs refresh-gtfs` |

---

## L Train Lines Reference

| Code | Line | Terminals |
|------|------|-----------|
| Red | Red Line | Howard ↔ 95th/Dan Ryan |
| Blue | Blue Line | O'Hare ↔ Forest Park |
| Brn | Brown Line | Kimball ↔ Loop |
| G | Green Line | Harlem/Lake ↔ Ashland/63rd or Cottage Grove |
| Org | Orange Line | Midway ↔ Loop |
| P | Purple Line | Linden ↔ Howard (Express to Loop weekdays) |
| Pink | Pink Line | 54th/Cermak ↔ Loop |
| Y | Yellow Line | Dempster-Skokie ↔ Howard |

---

## Key Bus Routes Reference

| Route | Name | Notes |
|-------|------|-------|
| 22 | Clark | Major north-south corridor |
| 36 | Broadway | North Side lakefront |
| 77 | Belmont | Major east-west crosstown |
| 151 | Sheridan | Lakefront express |
| 146 | Inner Drive/Michigan Express | Loop to north lakefront |
| 8 | Halsted | Long north-south route |
| 9 | Ashland | Major north-south corridor |
| 49 | Western | Longest route in system |
| 66 | Chicago | Major east-west route |
| 79 | 79th | Major south side east-west |

---

## Installation for ClawHub

Once published on ClawHub, users can install this skill with:

```bash
clawhub install cta
```

**Manual installation:**
```bash
cp -r cta-skill ~/.openclaw/skills/cta
cd ~/.openclaw/skills/cta && npm install
node scripts/cta.mjs refresh-gtfs
```

---

## Requirements

| Requirement | Details | How to Get |
|-------------|---------|------------|
| **Node.js 18+** | Runtime for the skill | [nodejs.org](https://nodejs.org) |
| **unzip** | Required for GTFS data extraction | Pre-installed on most systems |
| **CTA Train API Key** | Required for train commands | [Apply here](https://www.transitchicago.com/developers/traintrackerapply/) |
| **CTA Bus API Key** | Required for bus commands | [Apply here](https://www.transitchicago.com/developers/bustracker/) |

Note: Alert commands (`alerts`) work without any API keys.

---

## Data Sources

| API | Auth | Update Frequency |
|-----|------|-----------------|
| Train Tracker | API key (free) | ~1 minute |
| Bus Tracker v2 | API key (free) | ~30 seconds |
| Customer Alerts | None (open) | As needed |
| GTFS Static | None (open) | Periodic schedule updates |

---

## Troubleshooting

### "CTA Train Tracker API key required"
**Solution:** Get a free key and add it to your `.env` file:
```bash
# Apply at: https://www.transitchicago.com/developers/traintrackerapply/
CTA_TRAIN_API_KEY=your-key-here
```

### "CTA Bus Tracker API key required"
**Solution:** Get a free key and add it to your `.env` file:
```bash
# Apply at: https://www.transitchicago.com/developers/bustracker/
CTA_BUS_API_KEY=your-key-here
```

### "Invalid API key" error
**Possible causes:**
- Key was copy-pasted incorrectly (check for extra spaces)
- Key hasn't been activated yet (can take a few minutes after signup)
- Daily request limit exceeded (50,000/day for train; similar for bus)

### No arrivals showing up
**Possible causes:**
- No active service at this time (late night, holidays)
- Station/stop ID is incorrect — try `--stop-search` to find the right one
- API may be temporarily unavailable

### "GTFS static data not found"
**Solution:** Run the one-time data download:
```bash
node scripts/cta.mjs refresh-gtfs
```

### Alert commands work but train/bus commands don't
**This is expected** if API keys aren't set. Alerts use the Customer Alerts API which requires no authentication. Set `CTA_TRAIN_API_KEY` and `CTA_BUS_API_KEY` for full functionality.

---

## CTA Fares Reference (2026)

| Fare Type | Price |
|-----------|-------|
| Regular (Ventra/contactless) | $2.50 |
| Bus transfer | $0.25 |
| Rail-to-rail transfer | Free within 2 hours |
| Reduced fare | $1.25 |
| 1-Day Pass | $5.00 |
| 3-Day Pass | $15.00 |
| 7-Day Pass | $20.00 |
| 30-Day Pass | $75.00 |

---

## Learn More

### Resources
- **[CTA Developer Center](https://www.transitchicago.com/developers/)** — Official API docs and key signup
- **[Train Tracker API Docs](https://www.transitchicago.com/developers/traintracker/)** — Detailed train API reference
- **[Bus Tracker API Docs](https://www.transitchicago.com/developers/bustracker/)** — Detailed bus API reference
- **[CTA System Map](https://www.transitchicago.com/maps/)** — Official route maps
- **[GTFS Reference](https://gtfs.org)** — The data format standard used by transit agencies worldwide

---

## About This Skill

**Skill Type:** Data Integration (CTA REST APIs + GTFS)
**Runtime:** Node.js
**Created for:** ClawHub / OpenClaw
**License:** MIT

**Credits:**
- Transit data provided by [Chicago Transit Authority (CTA)](https://www.transitchicago.com)
- Train Tracker, Bus Tracker, and Customer Alerts APIs by CTA
- GTFS static data published by CTA

---

**Ready to ride?** Get your free API keys, set them up, and never miss your train again.
