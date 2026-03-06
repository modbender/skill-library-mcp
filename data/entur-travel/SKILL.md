---
name: entur-travel
description: "Plan public transit trips in Norway using the Entur API. Covers all operators (Vy, Ruter, Kolumbus, etc.), all modes (bus, rail, tram, metro, ferry, coach). Use when: (1) planning a journey between places in Norway, (2) checking departure boards/next departures, (3) finding stop IDs or place names, (4) looking up real-time transit info. Triggers on questions about trains, buses, ferries, trams in Norway, getting to airports (Gardermoen, Torp, Flesland), or how do I get to X."
---

# Entur Travel

Plan public transit journeys across Norway via the Entur Journey Planner API. Covers every operator and mode — bus, rail, tram, metro, ferry, coach, air — with real-time data.

**No API key required.** Free, open API under NLOD licence.

## Script

`scripts/entur.py` — standalone Python 3 CLI, no dependencies beyond stdlib.

### Commands

```bash
# Search for stops/places
python3 scripts/entur.py search "Oslo S"

# Plan a trip (place names auto-resolve via geocoder)
python3 scripts/entur.py trip "Porsgrunn" "Oslo lufthavn"

# Plan with specific departure time
python3 scripts/entur.py trip "Bergen" "Stavanger" --time "2025-03-01T08:00:00"

# Arrive by a specific time
python3 scripts/entur.py trip "Drammen" "Oslo S" --time "2025-03-01T09:00:00" --arrive

# Filter by mode
python3 scripts/entur.py trip "Tromsø" "Harstad" --modes water

# Departure board for a stop
python3 scripts/entur.py departures "NSR:StopPlace:58966" --limit 5

# Stop details (quays, platforms)
python3 scripts/entur.py stop "NSR:StopPlace:58966"
```

All output is JSON.

### Modes

Valid transport modes for `--modes`: `bus`, `rail`, `tram`, `metro`, `water`, `air`, `coach`

### Common Stop IDs

Use `search` to find IDs. Some common ones:
- Oslo S: `NSR:StopPlace:59872`
- Oslo lufthavn (Gardermoen): `NSR:StopPlace:269`
- Bergen stasjon: `NSR:StopPlace:585`
- Trondheim S: `NSR:StopPlace:41742`

## Presenting Results

When presenting trip results to users:
- Show times in local format (HH:MM), not ISO
- Summarize legs concisely: "🚆 RE11 Porsgrunn → Torp (10:17–10:50, platform 1)"
- Flag real-time delays: if aimed ≠ expected, mention the delay
- For departure boards, use a compact list format
- Include walk distances when significant (>200m)

## Limitations

- Norway only (Entur covers all Norwegian public transport)
- No ticket purchasing — planning and real-time info only
- Geocoder works best with Norwegian place names
- For international trips, only the Norwegian leg is covered
