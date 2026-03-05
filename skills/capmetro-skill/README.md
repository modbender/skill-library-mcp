# :bus: CapMetro Austin Transit — OpenClaw Skill

> **Real-time Austin public transit data for your OpenClaw agent.** Get vehicle positions, next arrivals, service alerts, and route info for MetroBus, MetroRapid, and MetroRail.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js 18+](https://img.shields.io/badge/node-18%2B-green.svg)](https://nodejs.org)
[![ClawdHub](https://img.shields.io/badge/ClawdHub-Skill-green.svg)](https://clawhub.ai)

---

## Why This Skill?

**For anyone who rides CapMetro and wants:**
- Real-time arrival predictions — no more guessing when the bus comes
- Live vehicle tracking — see exactly where your bus or train is
- Service alerts — know about detours and disruptions before you leave
- Stop and route lookup — find the nearest stop or explore a route's path
- Zero setup friction — no API keys, no accounts, no credentials

**How it works:**
All data comes from the [Texas Open Data Portal](https://data.texas.gov), which publishes CapMetro's GTFS and GTFS-RT feeds as open-access public data. This skill fetches, parses, and presents that data — updated every 15 seconds.

---

## Quick Start (2 Minutes)

### Step 1: Install the Skill

```bash
# Copy to your skills directory
cp -r capmetro-skill ~/.openclaw/skills/capmetro

# Or for a workspace-specific install:
cp -r capmetro-skill <workspace>/skills/capmetro
```

### Step 2: Install Dependencies

```bash
cd ~/.openclaw/skills/capmetro && npm install
```

### Step 3: Download Transit Data

```bash
# One-time download of routes, stops, and schedules
node scripts/capmetro.mjs refresh-gtfs

# You're ready! 🎉
```

No API keys. No accounts. No environment variables. Just install and go.

---

## What You Can Do

### :clock3: Real-Time Arrivals
- See when the next bus or train arrives at any stop
- Filter by route or direction (headsign)
- Search for stops by name instead of memorizing IDs
- Falls back to scheduled times when real-time data is unavailable

### :round_pushpin: Vehicle Tracking
- View live positions of every active CapMetro vehicle
- Filter by route to track a specific bus or train
- Positions update every ~15 seconds

### :loudspeaker: Service Alerts
- Active detours, delays, and service disruptions
- See which routes are affected
- Alert periods and descriptions

### :world_map: Route & Stop Discovery
- Search for stops by name or proximity to a location
- List all CapMetro routes
- View every stop along a route in order

---

## Usage (via OpenClaw Chat)

Just ask your agent naturally:

- "When's the next 801 at the Domain?"
- "Any CapMetro service alerts right now?"
- "Where are the MetroRail trains?"
- "Find bus stops near 30.267, -97.743"
- "What routes does CapMetro run?"
- "Show me the stops on route 803"

---

## Example Workflows

### Check When Your Bus Arrives

```bash
# 1. Find your stop
node scripts/capmetro.mjs stops --search "congress"

# 2. Get arrivals at that stop
node scripts/capmetro.mjs arrivals --stop 1234

# 3. Or skip the lookup — search by name directly
node scripts/capmetro.mjs arrivals --stop-search "congress" --route 801
```

**What just happened?**
- You searched for stops with "congress" in the name
- You got real-time arrival predictions for that stop
- The `--stop-search` shortcut found the best matching stop automatically

### Track the MetroRail

```bash
# Where are the trains right now?
node scripts/capmetro.mjs vehicles --route 550

# Next train heading to Lakeline?
node scripts/capmetro.mjs arrivals --stop-search "downtown" --route 550 --headsign "lakeline"
```

### Find Nearby Stops

```bash
# What stops are within 0.3 miles of me?
node scripts/capmetro.mjs stops --near 30.267,-97.743 --radius 0.3
```

---

## Command Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Arrivals** | |
| Next arrivals at a stop | `capmetro.mjs arrivals --stop STOP_ID` |
| Search stop by name | `capmetro.mjs arrivals --stop-search "name"` |
| Filter by route | `capmetro.mjs arrivals --stop STOP_ID --route 801` |
| Filter by direction | `capmetro.mjs arrivals --stop-search "name" --headsign "lakeline"` |
| **Vehicles** | |
| All active vehicles | `capmetro.mjs vehicles` |
| Vehicles on a route | `capmetro.mjs vehicles --route 550` |
| **Alerts** | |
| Current service alerts | `capmetro.mjs alerts` |
| **Stops** | |
| Search by name | `capmetro.mjs stops --search "domain"` |
| Find nearby stops | `capmetro.mjs stops --near LAT,LON` |
| Set search radius | `capmetro.mjs stops --near LAT,LON --radius 0.5` |
| **Routes** | |
| List all routes | `capmetro.mjs routes` |
| Route details + stops | `capmetro.mjs route-info --route 801` |
| **Maintenance** | |
| Refresh GTFS data | `capmetro.mjs refresh-gtfs` |

---

## Key Routes Reference

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
| 985 | Night Owl | Late Night Service |

---

## Installation for ClawdHub

Once published on ClawdHub, users can install this skill with:

```bash
# Install the skill
clawhub install capmetro
```

**Manual installation:**
```bash
# Clone or copy to your skills directory
cp -r capmetro-skill ~/.openclaw/skills/capmetro
cd ~/.openclaw/skills/capmetro && npm install
node scripts/capmetro.mjs refresh-gtfs
```

---

## Requirements

| Requirement | Details | How to Get |
|-------------|---------|------------|
| **Node.js 18+** | Runtime for the skill | [nodejs.org](https://nodejs.org) |
| **npm** | Installs protobufjs dependency | Included with Node.js |
| **API keys** | None required | Open-access data feeds |

---

## Data Sources

All feeds are open access from the [Texas Open Data Portal](https://data.texas.gov) — no API key, no authentication, no rate limits.

| Feed | Format | Update Frequency |
|------|--------|-----------------|
| Vehicle Positions | JSON / Protobuf | Every 15 seconds |
| Trip Updates | Protobuf | Every 15 seconds |
| Service Alerts | Protobuf | As needed |
| GTFS Static | ZIP | Quarterly / service changes |

---

## Troubleshooting

### "GTFS static data not found"
**Solution:** Run the one-time data download:
```bash
node scripts/capmetro.mjs refresh-gtfs
```

### No arrivals showing up
**Possible causes:**
- GTFS data hasn't been downloaded yet (run `refresh-gtfs`)
- No active service on that route at this time
- Real-time feed temporarily unavailable (scheduled times will show instead)

### Stale route or stop data
**Solution:** CapMetro updates their GTFS data quarterly or during service changes. Re-run:
```bash
node scripts/capmetro.mjs refresh-gtfs
```

### "Cannot find module 'protobufjs'"
**Solution:** Install dependencies:
```bash
cd ~/.openclaw/skills/capmetro && npm install
```

---

## Learn More

### Resources
- **[CapMetro Developer Tools](https://www.capmetro.org/developertools)** — Official developer portal and data license
- **[Texas Open Data Portal](https://data.texas.gov)** — Where all transit feeds are hosted
- **[GTFS Reference](https://gtfs.org)** — The data format standard used by transit agencies worldwide
- **[GTFS-RT Reference](https://gtfs.org/realtime/)** — Real-time extension to GTFS

---

## About This Skill

**Skill Type:** Data Integration (GTFS / GTFS-RT)
**Runtime:** Node.js
**Created for:** ClawdHub / OpenClaw
**License:** MIT

**Built by:** [Brian Leach](https://www.linkedin.com/in/bleach/) (bleach@gmail.com)

**Credits:**
- Transit data provided by [Capital Metropolitan Transportation Authority (CapMetro)](https://www.capmetro.org)
- Hosted on the [Texas Open Data Portal](https://data.texas.gov)
- Data provided under CMTA's Open Data License

---

**Ready to ride?** Install the skill, run `refresh-gtfs`, and never miss your bus again.
