# 🚂 Metra Chicago Commuter Rail — OpenClaw Skill

> **Real-time Chicago Metra commuter rail data for your OpenClaw agent.** Get train arrivals, vehicle tracking, service alerts, schedules, and fare info for all 11 Metra lines.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js 18+](https://img.shields.io/badge/node-18%2B-green.svg)](https://nodejs.org)
[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-green.svg)](https://clawhub.ai)

---

## Why This Skill?

**For anyone who rides Metra and wants:**
- Real-time train arrivals — know exactly when the next train arrives at your station
- Live vehicle tracking — see where trains are on the line right now
- Service alerts — know about delays, construction, and service changes before you leave
- Today's schedule — see all remaining trains with inbound/outbound grouping
- Fare calculation — know exactly how much a trip costs between any two stations
- Stop and route lookup — find stations, explore line stops, locate nearby stations

**How it works:**
Data comes from Metra's official [GTFS-RT feeds](https://metra.com/developers) — standard protobuf format updated every 30 seconds. Static schedule data from Metra's published GTFS feed.

---

## Quick Start

### Step 1: Get Your API Key (free)

Register at **https://metra.com/developers** to get a free API key.

### Step 2: Set Environment Variable

```bash
cp .env.example .env
# Edit .env and add your key:
# METRA_API_KEY=your-key-here
```

### Step 3: Install the Skill

```bash
# Copy to your skills directory
cp -r metra-skill ~/.openclaw/skills/metra

# Or for a workspace-specific install:
cp -r metra-skill <workspace>/skills/metra
```

### Step 4: Install Dependencies & Download Data

```bash
cd ~/.openclaw/skills/metra && npm install
node scripts/metra.mjs refresh-gtfs
```

---

## What You Can Do

### 🕐 Real-Time Train Arrivals
- See when the next train arrives at any Metra station
- Filter by specific line (BNSF, UP-N, etc.)
- Shows train numbers — know which specific train is coming
- Falls back to scheduled times when real-time data is unavailable

### 📍 Vehicle Tracking
- View live GPS positions of all active trains on a line
- See which station each train is approaching or stopped at
- Speed and bearing data when available

### 📢 Service Alerts
- Active delays, construction, and service changes
- Filter by line to see only relevant alerts
- If an alert is in the feed, it's active — no complex period checking needed

### 📅 Schedule
- Today's full timetable for any station
- Grouped by direction: Inbound (toward downtown) and Outbound (away)
- Shows train numbers — find "your train" easily
- Knows about weekday/weekend/holiday schedules

### 💰 Fare Calculation
- Calculate exact fare between any two stations
- Zone-based system with all ticket types (one-way, day pass, monthly)
- Shows special passes (weekend, regional connect)

### 🗺️ Route & Stop Discovery
- Search for stations by name or proximity to GPS coordinates
- List all stops along a line in sequence
- View detailed line info including terminals and zones

---

## Usage (via OpenClaw Chat)

Just ask your agent naturally:

- "When's the next BNSF train from Naperville?"
- "What time does the UP-N leave Ogilvie?"
- "Any Metra service alerts right now?"
- "Where are the trains on the Rock Island line?"
- "How much is a ticket from Union Station to Aurora?"
- "Show me today's schedule for Downers Grove"
- "Find Metra stations near Wrigley Field"
- "What lines run out of Ogilvie?"

---

## Example Workflows

### Check Your Morning Train

```bash
# Next arrivals at your station
node scripts/metra.mjs arrivals --station "Naperville" --line BNSF

# Full schedule for the morning
node scripts/metra.mjs schedule --station "Naperville" --line BNSF
```

### Track Your Train Home

```bash
# Where are the BNSF trains right now?
node scripts/metra.mjs vehicles --line BNSF

# What's leaving Union Station?
node scripts/metra.mjs arrivals --station "Union Station" --line BNSF
```

### Check Before You Go

```bash
# Any delays on your line?
node scripts/metra.mjs alerts --line UP-N

# All current alerts
node scripts/metra.mjs alerts
```

### Plan a Trip

```bash
# How much is the fare?
node scripts/metra.mjs fares --from "Union Station" --to "Naperville"

# What line serves a station?
node scripts/metra.mjs stops --search "highland park"
```

---

## Command Cheat Sheet

| What You Want | Command |
|---------------|---------|
| **Arrivals** | |
| Next trains at a station | `metra.mjs arrivals --station "Naperville"` |
| Filter by line | `metra.mjs arrivals --station "Ogilvie" --line UP-N` |
| **Vehicles** | |
| Train positions on a line | `metra.mjs vehicles --line BNSF` |
| **Alerts** | |
| All service alerts | `metra.mjs alerts` |
| Alerts for a line | `metra.mjs alerts --line RI` |
| **Routes** | |
| List all 11 lines | `metra.mjs routes` |
| Line details + stops | `metra.mjs route-info --line UP-NW` |
| **Stops** | |
| Search by name | `metra.mjs stops --search "downers grove"` |
| List stops on a line | `metra.mjs stops --line BNSF` |
| Find nearby stations | `metra.mjs stops --near 41.8781,-87.6298` |
| **Fares** | |
| Full fare table | `metra.mjs fares` |
| Calculate a trip | `metra.mjs fares --from "Union Station" --to "Aurora"` |
| **Schedule** | |
| Today's schedule | `metra.mjs schedule --station "Naperville"` |
| Filter by line | `metra.mjs schedule --station "Ogilvie" --line UP-N` |
| **Maintenance** | |
| Refresh GTFS data | `metra.mjs refresh-gtfs` |

---

## Metra Lines Reference

| Code | Line Name | Color | Downtown Terminal | Outer Terminal |
|------|-----------|-------|-------------------|----------------|
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

### Downtown Terminals

- **Chicago Union Station (CUS)** — BNSF, HC, MD-N, MD-W, NCS, SWS
- **Ogilvie Transportation Center (OTC)** — UP-N, UP-NW, UP-W
- **LaSalle Street Station** — RI
- **Millennium Station** — ME

---

## Metra Fares (4-Zone System)

| Ticket Type | Zones 1-2 | Zones 1-3 | Zones 1-4 | Zones 2-4 |
|-------------|-----------|-----------|-----------|-----------|
| One-Way | $3.75 | $5.50 | $6.75 | $3.75 |
| Day Pass | $7.50 | $11.00 | $13.50 | $7.50 |
| Monthly | $75.00 | $110.00 | $135.00 | $75.00 |

- Weekend Day Pass: $7.00 (systemwide)
- Onboard Surcharge: $5.00

---

## Installation for ClawHub

Once published on ClawHub, users can install this skill with:

```bash
clawhub install metra
```

**Manual installation:**
```bash
cp -r metra-skill ~/.openclaw/skills/metra
cd ~/.openclaw/skills/metra && npm install
node scripts/metra.mjs refresh-gtfs
```

---

## Requirements

| Requirement | Details | How to Get |
|-------------|---------|------------|
| **Node.js 18+** | Runtime for the skill | [nodejs.org](https://nodejs.org) |
| **npm** | Installs protobufjs dependency | Included with Node.js |
| **unzip** | Required for GTFS data extraction | Pre-installed on most systems |
| **METRA_API_KEY** | Required for all real-time data | [metra.com/developers](https://metra.com/developers) |

---

## Data Sources

| Feed | Auth | Update Frequency |
|------|------|-----------------|
| Trip Updates (Protobuf) | Bearer token (free) | Every 30 seconds |
| Vehicle Positions (Protobuf) | Bearer token (free) | Every 30 seconds |
| Service Alerts (Protobuf) | Bearer token (free) | As needed |
| GTFS Static (ZIP) | None (open) | Schedule changes (check published.txt) |

---

## Troubleshooting

### "Metra API key required"
**Solution:** Get a free key at https://metra.com/developers and set `METRA_API_KEY`:
```bash
METRA_API_KEY=your-key-here
```

### "Authentication failed"
**Possible causes:**
- Key was copy-pasted incorrectly (check for extra spaces)
- Key may have expired or been revoked

### "GTFS static data not found"
**Solution:** Run the one-time data download:
```bash
node scripts/metra.mjs refresh-gtfs
```

### No arrivals showing up
**Possible causes:**
- No active service at this time (late night, weekends have limited service)
- Station name didn't match — try `stops --search` to find the right name
- Real-time data temporarily unavailable — schedule command shows static times

### "Cannot find module 'protobufjs'"
**Solution:** Install dependencies:
```bash
cd /path/to/metra-skill && npm install
```

### Vehicle positions missing for a train
This is expected — GPS signals drop when trains are underground or at terminals. The position will reappear when GPS is reacquired.

---

## Learn More

### Resources
- **[Metra Developer Portal](https://metra.com/developers)** — API key signup and documentation
- **[Metra Schedules](https://metra.com/schedules)** — Official timetables
- **[Metra System Map](https://metra.com/maps)** — Route maps
- **[GTFS Reference](https://gtfs.org)** — The data format standard
- **[GTFS-RT Reference](https://gtfs.org/realtime/)** — Real-time extension

---

## About This Skill

**Skill Type:** Data Integration (GTFS-RT Protobuf + GTFS Static)
**Runtime:** Node.js
**Created for:** ClawHub / OpenClaw
**License:** MIT

**Credits:**
- Transit data provided by [Metra](https://metra.com)
- GTFS-RT feeds from gtfspublic.metrarr.com
- Static schedule data from schedules.metrarail.com

---

**Ready to ride?** Get your free API key, set it up, and never miss your train again.
