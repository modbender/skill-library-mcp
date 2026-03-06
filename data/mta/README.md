# :metro: NYC MTA Transit — OpenClaw Skill

> **Real-time New York City transit data for your OpenClaw agent.** Get subway arrivals, bus predictions, service alerts, and route info for all MTA subway lines and bus routes.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js 18+](https://img.shields.io/badge/node-18%2B-green.svg)](https://nodejs.org)
[![ClawHub](https://img.shields.io/badge/ClawdHub-Skill-green.svg)](https://clawhub.ai)

---

## Why This Skill?

**For anyone who rides the NYC subway or bus and wants:**
- Real-time subway arrivals — know exactly when the next train comes, with track info
- Bus predictions — see when your bus will arrive at your stop
- Service alerts — know about delays, planned work, and weekend changes before you leave
- Stop and route lookup — find the nearest subway station or bus stop
- Subway works with zero setup — no API keys, no accounts, no environment variables

**How it works:**
Subway data comes from MTA's [GTFS-RT protobuf feeds](https://api.mta.info/) (open access, no key). Bus data comes from the [SIRI/OneBusAway API](https://bustime.mta.info/) (free key required). Alerts use GTFS-RT protobuf (open access).

---

## Quick Start

### Subway (zero config)

Subway and alert commands work immediately with no setup:

```bash
# Install dependencies
cd mta-skill && npm install

# Download subway stop data (one-time)
node scripts/mta.mjs refresh-gtfs

# Check subway arrivals
node scripts/mta.mjs arrivals --stop-search "times square"
```

### Bus (free API key)

Bus commands require a free MTA BusTime API key:

1. **Get a key:** https://register.developer.obanyc.com/ (delivered within 30 min)
2. **Set environment variable:**
```bash
export MTA_BUS_API_KEY=your-key-here
# Or add to .env file in the skill directory
```

---

## What You Can Do

### :clock3: Real-Time Subway Arrivals
- See when the next train arrives at any subway station
- Search stations by name — "penn station", "times square", "grand central"
- Filter by line (A, C, E, 1, 2, 3, etc.)
- Shows direction (Uptown/Downtown), track info, and minutes until arrival

### :bus: Bus Predictions
- Real-time bus arrival predictions at any stop
- Filter by route (M1, B52, Bx12, etc.)
- Shows distance, stops away, and estimated arrival time

### :round_pushpin: Vehicle Tracking
- View live positions of all subway trains on a line
- View live positions of all buses on a route

### :loudspeaker: Service Alerts
- Active delays, planned work, and service changes
- Filter by subway, bus, or specific line
- No API key required

### :world_map: Route & Stop Discovery
- Search subway stops by name or proximity
- Search bus stops by location or route
- List all subway lines or bus routes
- View every stop along a subway line

---

## Usage (via OpenClaw Chat)

Just ask your agent naturally:

- "When's the next A train at Penn Station?"
- "Is the L train running?"
- "Any subway delays right now?"
- "Where are the 1 trains?"
- "When does the M1 bus come to 5th Ave?"
- "Find subway stops near Times Square"
- "What subway lines go through Union Square?"

---

## Example Workflows

### Check When Your Train Arrives

```bash
# Search by station name
node scripts/mta.mjs arrivals --stop-search "times square"

# Filter to just the A train
node scripts/mta.mjs arrivals --stop-search "times square" --line A

# Use exact stop ID (127N = Times Sq northbound)
node scripts/mta.mjs arrivals --stop 127N
```

### Track a Bus

```bash
# When does the M1 bus arrive at my stop?
node scripts/mta.mjs bus-arrivals --stop MTA_308209 --route M1

# Where are all the B52 buses?
node scripts/mta.mjs bus-vehicles --route B52
```

### Check Service Alerts

```bash
# All subway alerts
node scripts/mta.mjs alerts --subway

# Just A train alerts
node scripts/mta.mjs alerts --line A

# All bus alerts
node scripts/mta.mjs alerts --bus
```

### Find Nearby Stops

```bash
# Subway stops near Midtown
node scripts/mta.mjs stops --near 40.7549,-73.9840

# Bus stops near a location
node scripts/mta.mjs bus-stops --near 40.7549,-73.9840
```

---

## Command Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Subway Arrivals** | |
| Search station by name | `mta.mjs arrivals --stop-search "penn station"` |
| Arrivals at station | `mta.mjs arrivals --station "Grand Central"` |
| Arrivals by stop ID | `mta.mjs arrivals --stop 127N` |
| Filter by line | `mta.mjs arrivals --stop-search "14th" --line L` |
| **Bus Predictions** | |
| Bus arrivals at stop | `mta.mjs bus-arrivals --stop MTA_308209` |
| Filter by route | `mta.mjs bus-arrivals --stop MTA_308209 --route M1` |
| Search bus stop | `mta.mjs bus-arrivals --stop-search "broadway"` |
| **Vehicle Tracking** | |
| Subway positions on a line | `mta.mjs vehicles --line 1` |
| Bus positions on a route | `mta.mjs bus-vehicles --route B52` |
| **Alerts** | |
| All service alerts | `mta.mjs alerts` |
| Subway alerts only | `mta.mjs alerts --subway` |
| Bus alerts only | `mta.mjs alerts --bus` |
| Alerts for a line | `mta.mjs alerts --line A` |
| **Stops** | |
| Search subway stops | `mta.mjs stops --search "grand central"` |
| Find nearby subway stops | `mta.mjs stops --near LAT,LON` |
| Find nearby bus stops | `mta.mjs bus-stops --near LAT,LON` |
| Stops on a bus route | `mta.mjs bus-stops --route M1` |
| **Routes** | |
| All subway lines | `mta.mjs routes` |
| All bus routes | `mta.mjs bus-routes` |
| Subway line stops | `mta.mjs route-info --line A` |
| **Maintenance** | |
| Refresh GTFS data | `mta.mjs refresh-gtfs` |

---

## NYC Subway Lines Reference

| Line | Color | Terminals |
|------|-------|-----------|
| 1 | Red | Van Cortlandt Park-242 St ↔ South Ferry |
| 2 | Red | Wakefield-241 St ↔ Flatbush Ave-Brooklyn College |
| 3 | Red | Harlem-148 St ↔ New Lots Ave |
| 4 | Green | Woodlawn ↔ Crown Heights-Utica Ave |
| 5 | Green | Eastchester-Dyre Ave ↔ Flatbush Ave-Brooklyn College |
| 6 | Green | Pelham Bay Park ↔ Brooklyn Bridge-City Hall |
| 7 | Purple | Flushing-Main St ↔ 34 St-Hudson Yards |
| A | Blue | Inwood-207 St ↔ Far Rockaway / Lefferts Blvd |
| C | Blue | 168 St ↔ Euclid Ave |
| E | Blue | Jamaica Center ↔ World Trade Center |
| B | Orange | Bedford Park Blvd ↔ Brighton Beach |
| D | Orange | Norwood-205 St ↔ Coney Island-Stillwell Ave |
| F | Orange | Jamaica-179 St ↔ Coney Island-Stillwell Ave |
| M | Orange | Middle Village-Metropolitan Ave ↔ Forest Hills-71 Ave |
| G | Light Green | Court Sq ↔ Church Ave |
| J | Brown | Jamaica Center ↔ Broad St |
| Z | Brown | Jamaica Center ↔ Broad St (Peak only) |
| L | Gray | 8 Ave ↔ Canarsie-Rockaway Pkwy |
| N | Yellow | Astoria-Ditmars Blvd ↔ Coney Island-Stillwell Ave |
| Q | Yellow | 96 St ↔ Coney Island-Stillwell Ave |
| R | Yellow | Forest Hills-71 Ave ↔ Bay Ridge-95 St |
| W | Yellow | Astoria-Ditmars Blvd ↔ Whitehall St-South Ferry |
| S | Gray | 42nd St Shuttle / Franklin Ave / Rockaway Park |
| SIR | Blue | St George ↔ Tottenville |

---

## Key Bus Routes Reference

| Route | Name | Borough |
|-------|------|---------|
| M1 | 5th Ave / Madison Ave | Manhattan |
| M15 | 1st Ave / 2nd Ave | Manhattan |
| M34 | 34th St Crosstown | Manhattan |
| M60 | LaGuardia Airport Link | Manhattan/Queens |
| B44 | Nostrand Ave | Brooklyn |
| B52 | Gates Ave/Greene Ave | Brooklyn |
| Bx12 | Fordham Rd/Pelham Pkwy | Bronx |
| Q44 | Merrick Blvd/Cross Island | Queens |
| S79 | Hylan Blvd | Staten Island |
| X27 | Bay Ridge Express | Brooklyn |

---

## Installation for ClawdHub

Once published on ClawdHub, users can install this skill with:

```bash
clawhub install mta
```

**Manual installation:**
```bash
cp -r mta-skill ~/.openclaw/skills/mta
cd ~/.openclaw/skills/mta && npm install
node scripts/mta.mjs refresh-gtfs
```

---

## Requirements

| Requirement | Details | How to Get |
|-------------|---------|------------|
| **Node.js 18+** | Runtime for the skill | [nodejs.org](https://nodejs.org) |
| **npm** | Installs protobufjs dependency | Included with Node.js |
| **MTA Bus API Key** | Required for bus commands only | [Free signup](https://register.developer.obanyc.com/) |

Note: Subway and alert commands work with zero configuration.

---

## Data Sources

| Data | Source | Auth | Update Frequency |
|------|--------|------|-----------------|
| Subway Arrivals | GTFS-RT Protobuf | None (open) | ~30 seconds |
| Bus Predictions | SIRI JSON API | API key (free) | ~30 seconds |
| Service Alerts | GTFS-RT Protobuf | None (open) | As needed |
| GTFS Static | ZIP download | None (open) | Hourly (supplemented) |

---

## Troubleshooting

### "MTA BusTime API key required"
**Solution:** Get a free key and set the environment variable:
```bash
# Apply at: https://register.developer.obanyc.com/
export MTA_BUS_API_KEY=your-key-here
```

### No subway arrivals showing
**Possible causes:**
- GTFS data hasn't been downloaded yet (run `refresh-gtfs`)
- No active service on that line at this time (late night/weekend changes)
- Real-time feed temporarily unavailable
- Station name didn't match — try a different search term

### "GTFS static data not found"
**Solution:** Run the one-time data download:
```bash
node scripts/mta.mjs refresh-gtfs
```

### "Cannot find module 'protobufjs'"
**Solution:** Install dependencies:
```bash
cd ~/.openclaw/skills/mta && npm install
```

### Subway commands work but bus commands don't
**This is expected** if `MTA_BUS_API_KEY` isn't set. Subway uses open feeds; bus requires a free key.

---

## MTA Fares Reference (2025)

| Fare Type | Price |
|-----------|-------|
| Subway/Bus (OMNY or MetroCard) | $2.90 |
| Bus-to-bus / subway-to-bus transfer | Free within 2 hours |
| Express Bus | $7.00 |
| 7-Day Unlimited | $34.00 |
| 30-Day Unlimited | $132.00 |
| Single Ride (vending machine only) | $3.25 |
| Reduced Fare | $1.45 |

---

## Learn More

### Resources
- **[MTA Developer Resources](https://api.mta.info/)** — Official GTFS-RT feeds and documentation
- **[MTA BusTime API](https://bustime.mta.info/wiki/Developers/Index)** — Bus SIRI API docs
- **[MTA System Map](https://map.mta.info/)** — Official subway and bus maps
- **[GTFS Reference](https://gtfs.org)** — The data format standard used by transit agencies worldwide
- **[GTFS-RT Reference](https://gtfs.org/realtime/)** — Real-time extension to GTFS

---

## About This Skill

**Skill Type:** Data Integration (GTFS-RT Protobuf + SIRI JSON API)
**Runtime:** Node.js
**Created for:** ClawdHub / OpenClaw
**License:** MIT


**Credits:**
- Transit data provided by [Metropolitan Transportation Authority (MTA)](https://www.mta.info)
- Subway real-time data via MTA GTFS-RT feeds
- Bus real-time data via MTA BusTime (SIRI/OneBusAway) API
- NYCT subway protobuf extensions from MTA Developer Resources

---

**Ready to ride?** Install the skill, run `refresh-gtfs`, and never miss your train again.
