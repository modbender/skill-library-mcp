---
name: birdweather
description: Query BirdWeather station data — species detections, trends, and comparisons from BirdNET-Pi and PUC bird song detection stations. Use when asked about bird sightings, bird song detections, local bird activity, BirdWeather stations, or wildlife audio monitoring. No API key required.
---

# BirdWeather

CLI at `scripts/birdweather.py` for querying BirdWeather station data. No API key needed — all station data is public.

Find station IDs at https://app.birdweather.com/

## Commands

```bash
# Station info (name, location, status, last detection)
scripts/birdweather.py station <station_id>

# Species detected (default: today)
scripts/birdweather.py species <station_id> --period day|week|month --limit 50

# Species for date range
scripts/birdweather.py species <station_id> --from 2026-02-01 --to 2026-02-14

# Top species (compact, default: week)
scripts/birdweather.py top <station_id> --period week --limit 10

# Recent individual detections
scripts/birdweather.py detections <station_id> --limit 20

# Compare periods (shows new arrivals, departures, trends)
scripts/birdweather.py compare <station_id> --this week --last month

# Any command with raw JSON output
scripts/birdweather.py --json species <station_id> --period week
```

## Output

Species lists show detection count, common name, and scientific name:
```
    467  Eurasian Blue Tit (Cyanistes caeruleus)
    290  Eurasian Wren (Troglodytes troglodytes)
```

Compare shows arrivals, departures, and significant changes between periods.

## Notes

- Detection count ≠ bird count (one bird singing repeatedly = many detections)
- BirdNET AI classification can misidentify — unusual species may be false positives
- Stations go offline periodically — empty results may mean the station is down, not that there are no birds
- Period options: `day` (today), `week` (last 7 days), `month` (last 30 days)
- Stdlib only — no pip dependencies
