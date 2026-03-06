# Maps Skill

Free distance, routing, and geocoding for OpenClaw — no API keys required.

## What it does

- **Geocode** place names to coordinates using [Nominatim](https://nominatim.openstreetmap.org/) (OpenStreetMap)
- **Route & distance** between two points using [OSRM](https://router.project-osrm.org/) (Open Source Routing Machine)
- Supports driving, walking, and cycling modes

## Requirements

- `python3` (3.6+)
- POSIX shell (bash)

## Usage

### Geocode a place

```bash
bash scripts/geocode.sh "Central Park, New York"
# [1] Central Park, Manhattan, New York, USA
#     lat,lon: 40.7828647,-73.9653551
#     type: park / leisure
```

### Get distance & travel time

```bash
bash scripts/distance.sh 40.7580,-73.9855 40.6413,-73.7781 driving
# Mode: driving
# Distance: 20.3 km
# Duration: 22 min
```

### Modes

| Mode | Aliases |
|------|---------|
| Driving | `driving`, `car` |
| Walking | `foot`, `walk`, `walking` |
| Cycling | `bicycle`, `bike`, `cycling` |

## How it works

- **Geocoding**: Queries Nominatim's free API (1 req/sec rate limit per OSM policy)
- **Routing**: Queries OSRM's public demo server for shortest path on the road network
- **No API keys** needed — both services are free and open

## Limitations

- No live traffic data — durations are road-type estimates
- No public transit routing
- OSRM demo server is best-effort (not for high-volume production use)
- Nominatim rate limit: 1 request per second

## License

MIT
