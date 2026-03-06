---
name: db-travel
description: "Plan journeys across Germany and Europe using the Deutsche Bahn API (v6.db.transport.rest). Covers ICE, IC, regional trains, S-Bahn, U-Bahn, trams, buses, ferries. Use when: (1) planning trips in Germany or cross-border European rail, (2) checking departure/arrival boards at German/European stations, (3) finding station IDs, (4) navigating cities like Berlin, Munich, Hamburg. Triggers on questions about German trains, DB, BVG, getting around Berlin, European rail connections."
---

# DB Travel

Plan journeys across Germany and Europe via the Deutsche Bahn REST API. Covers ICE, IC/EC, regional trains, S-Bahn, U-Bahn, trams, buses, and ferries — with real-time delays.

**No API key required.** Free public API. Rate limit: 100 req/min.

## Script

`scripts/db-travel.py` — standalone Python 3 CLI, no dependencies beyond stdlib.

### Commands

```bash
# Search for stations/stops
python3 scripts/db-travel.py search "Berlin Hbf"

# Plan a trip (place names auto-resolve)
python3 scripts/db-travel.py trip "Berlin Hbf" "Munich Hbf"

# Depart at specific time
python3 scripts/db-travel.py trip "Berlin Hbf" "Flughafen BER" --time "2025-03-01T10:00:00+01:00"

# Arrive by a specific time
python3 scripts/db-travel.py trip "Hamburg" "Berlin" --time "2025-03-01T14:00:00" --arrive

# Departure board
python3 scripts/db-travel.py departures 8011160 --limit 10

# Arrival board
python3 scripts/db-travel.py arrivals 8011160 --duration 60

# Station details
python3 scripts/db-travel.py stop 8011160
```

All output is JSON.

### Common Station IDs

Use `search` to find IDs. Some common ones:
- Berlin Hbf: `8011160`
- München Hbf: `8000261`
- Hamburg Hbf: `8002549`
- Frankfurt (Main) Hbf: `8000105`
- Köln Hbf: `8000207`
- Flughafen BER: `8089110`

### Products

The API returns product types: `nationalExpress` (ICE), `national` (IC/EC), `regionalExpress`, `regional`, `suburban` (S-Bahn), `subway` (U-Bahn), `tram`, `bus`, `ferry`, `taxi`.

## Presenting Results

When presenting trip results to users:
- Show times in HH:MM local format, not ISO
- Summarize legs concisely: "🚄 ICE 507 Berlin Hbf → München Hbf (10:29–14:25, platform 3)"
- Flag delays: if delay_min > 0, mention it
- For departure boards, filter to relevant modes (skip trams if user asked about long-distance)
- Walking legs can usually be omitted unless distance is significant

## Limitations

- Primarily Germany, but includes international trains (IC/EC to neighboring countries)
- Rate limited to 100 req/min — don't hammer it
- No ticket purchasing
- For Norway, use the entur-travel skill instead
