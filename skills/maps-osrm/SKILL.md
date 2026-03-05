---
name: maps
description: Distance, routing, and geocoding using free APIs (OSRM + Nominatim/OSM). Use when the user asks about distance between places, travel time, directions, how far something is, or needs to convert a place name to coordinates. No API key required. Requires python3 (3.6+).
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# Maps

Free distance/routing (OSRM) and geocoding (Nominatim/OSM). No API keys needed.

## Geocoding (place name → coordinates)

```bash
bash scripts/geocode.sh "Times Square, New York"
```

Returns lat,lon and display name. Use this first when you have place names instead of coordinates.

## Distance & Route

```bash
bash scripts/distance.sh <origin_lat>,<origin_lon> <dest_lat>,<dest_lon> [mode]
```

Modes: `driving` (default), `foot`, `bicycle`

Examples:
```bash
# Manhattan to JFK Airport
bash scripts/distance.sh 40.7580,-73.9855 40.6413,-73.7781 driving

# Golden Gate Park to Fisherman's Wharf (walking)
bash scripts/distance.sh 37.7694,-122.4862 37.8080,-122.4177 foot
```

## Workflow

1. If user gives place names → geocode both with `geocode.sh`
2. Use returned lat,lon pairs with `distance.sh`
3. Report distance in km and duration in minutes

## Limits

- OSRM: free public demo server, no hard rate limit but be reasonable
- Nominatim: max 1 request/second (OSM policy), include User-Agent
- No live traffic data — durations are estimates based on road type/speed
- Routing is road-network only (no public transit)
