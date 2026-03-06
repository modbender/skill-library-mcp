# subwayskill

NYC subway departure times CLI. Fetches realtime train arrivals from MTA GTFS-RT feeds, with automatic fallback to static schedule data for future times.

Designed to output LLM-friendly text — useful when you already know your route and just want to know when the next train is.

## Install

```
go install github.com/nyluke/subwayskill@latest
```

Or clone and build:

```
git clone https://github.com/nyluke/subwayskill.git
cd subwayskill
go build
```

## Usage

```
subwayskill [LINE] [STATION] [flags]
```

### No arguments — show default stations (realtime)

```
$ subwayskill

=== NYC Subway Departures (realtime) ===
Query time: 2026-02-16 14:35 EST

--- Clinton-Washington Avs (C) ---
  C northbound (Manhattan-bound): 2 min (14:37), 14 min (14:49), 26 min (15:01)
  C southbound (Euclid Av-bound):  5 min (14:40), 18 min (14:53)

--- Bergen St (2, 3) ---
  2 northbound: 3 min (14:38), 11 min (14:46)
  3 northbound: 7 min (14:42), 19 min (14:54)
  ...
```

Default stations: Clinton-Washington Avs (C), Bergen St (2,3), 7 Av (Q), Atlantic Av-Barclays Ctr (4,5).

### Specific line + station

```
$ subwayskill C clinton-washington
$ subwayskill 2 bergen
```

Station names are fuzzy-matched — lowercase, punctuation-insensitive, partial matches work.

### Direction filter

```
$ subwayskill 2 bergen -d N    # northbound only
$ subwayskill C clinton-washington -d S    # southbound only
```

### Future time — automatic schedule fallback

```
$ subwayskill 2 bergen -t 19:00

=== NYC Subway Departures (scheduled) ===
Target time: 2026-02-16 19:00 EST

--- Bergen St (2) ---
  2 northbound: 18:52, 19:04, 19:16, 19:28
  2 southbound: 18:55, 19:07, 19:19, 19:31
  Source: Supplemented GTFS
```

When the target time is beyond realtime feed coverage, the tool automatically downloads and caches static GTFS schedules (supplemented + regular) to `~/.cache/subwayskill/`.

### JSON output

```
$ subwayskill --json
$ subwayskill C clinton-washington --json
```

### Flags

| Flag | Description |
|------|-------------|
| `-d, --direction N\|S` | Filter northbound or southbound |
| `-t, --time HH:MM` | Target departure time (default: now) |
| `-w, --window INT` | Minutes of departures to show (default: 30 for schedule, all for realtime) |
| `--json` | JSON output |

## Data sources

- **Realtime**: MTA GTFS-RT feeds (no API key required)
- **Schedule**: [MTA static GTFS](https://api.mta.info/) — regular + supplemented (7-day lookahead with planned service changes)

## License

MIT
