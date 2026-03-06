# Recreation.gov Availability Checker

A Python CLI for checking campsite availability on [recreation.gov](https://www.recreation.gov) — National Parks, National Forests, BLM, and other federal campgrounds.

## Overview

This tool queries the recreation.gov public API to find available campsites for specific dates. It supports:

- **Multi-campground queries** — Check several campgrounds at once
- **Consecutive night searches** — Find sites available for your entire stay
- **Type filtering** — Tent, RV, electric, cabin, group sites
- **Amenity filtering** — Pets allowed, shade, fire pits, vehicle length
- **Smart status detection** — Distinguishes sold out, not yet released, and first-come-first-served

### Covered Campgrounds

Recreation.gov handles reservations for:

- National Park Service (NPS) campgrounds
- USDA Forest Service (USFS) campgrounds
- Bureau of Land Management (BLM) sites
- Army Corps of Engineers recreation areas
- Bureau of Reclamation facilities

For **state parks** and private campgrounds, use the companion `reserveamerica` skill.

## Prerequisites

- Python 3.8+
- No API key needed (uses public endpoints)

## Installation

```bash
cd /Users/doop/moltbot/skills/recgov-availability
# No dependencies to install — uses only stdlib
```

## Quick Start

```bash
# Check availability for Tillicum Beach (ID: 233965)
python3 scripts/check.py --campground 233965 --start 2026-07-10 --nights 2

# Check multiple campgrounds
python3 scripts/check.py -c 233965 233900 --start 2026-07-10 --nights 2

# Filter to tent sites only
python3 scripts/check.py -c 233965 --start 2026-07-10 --nights 2 --type tent

# JSON output
python3 scripts/check.py -c 233965 --start 2026-07-10 --nights 2 --json
```

## Finding Campground IDs

Campground IDs are in recreation.gov URLs:

```
https://www.recreation.gov/camping/campgrounds/233965
                                              ^^^^^^
                                              This is the ID
```

Or use the `ridb-search` skill to find campgrounds near a location:

```bash
python3 ../ridb-search/scripts/search.py -l "Newport, Oregon" --camping-only
```

## CLI Options

```bash
python3 scripts/check.py [options]
```

### Required

| Option | Description |
|--------|-------------|
| `-c, --campground` | Campground ID(s) to check (space-separated) |
| `-s, --start` | Start date (YYYY-MM-DD) |

### Filtering

| Option | Description |
|--------|-------------|
| `-n, --nights` | Consecutive nights needed (default: 1) |
| `-t, --type` | Site type: tent, rv, standard, cabin, group |
| `--electric` | Electric hookup sites only |
| `--nonelectric` | Non-electric sites only |
| `--include-group` | Include group sites (excluded by default) |

### Amenity Filters

These require additional API calls per site (slower):

| Option | Description |
|--------|-------------|
| `--pets` | Pet-friendly sites only |
| `--shade` | Shaded sites only |
| `--fire-pit` | Sites with fire pits |
| `--vehicle-length N` | Minimum vehicle length (feet) |

### Output

| Option | Description |
|--------|-------------|
| `--show-sites` | Show individual available sites |
| `--json` | JSON output for programmatic use |

## Examples

### Basic availability check

```bash
python3 scripts/check.py -c 233965 --start 2026-07-10 --nights 2
```

Output:
```
🏕️  TILLICUM (233965)
   ✅ 5 site(s) available out of 58
   🔗 https://www.recreation.gov/camping/campgrounds/233965

   📍 Site 04 (STANDARD NONELECTRIC)
      ✅ 2026-07-12 → 2026-07-14

   📍 Site 08 (STANDARD NONELECTRIC)
      ✅ 2026-07-12 → 2026-07-14
      ✅ 2026-07-13 → 2026-07-15
```

### Check multiple campgrounds

```bash
python3 scripts/check.py \
  -c 233965 233900 234502 \
  --start 2026-07-10 \
  --nights 2 \
  --type tent
```

### Pet-friendly RV sites with electric

```bash
python3 scripts/check.py \
  -c 232448 \
  --start 2026-08-01 \
  --nights 3 \
  --type rv \
  --electric \
  --pets \
  --vehicle-length 30
```

### JSON output for scripts

```bash
python3 scripts/check.py -c 233965 --start 2026-07-10 --nights 2 --json
```

```json
[
  {
    "campground_id": "233965",
    "campground_name": "TILLICUM",
    "url": "https://www.recreation.gov/camping/campgrounds/233965",
    "total_count": 58,
    "available_count": 5,
    "status": {
      "available": 0,
      "reserved": 37,
      "nyr": 0,
      "fcfs": 0,
      "not_yet_bookable": 21,
      "other": 0
    },
    "sites": [
      {
        "id": "80504",
        "name": "04",
        "type": "STANDARD NONELECTRIC",
        "loop": "Loop 1",
        "available_ranges": [
          ["2026-07-12", "2026-07-14"]
        ]
      }
    ]
  }
]
```

## Understanding Availability Status

The tool distinguishes several booking scenarios:

| Status | Meaning |
|--------|---------|
| ✅ Available | Sites bookable right now |
| ❌ Reserved | Already booked by someone |
| ⏳ Not Yet Released (NYR) | Reservations haven't opened for these dates |
| ⏳ Not Yet Bookable | Reservable campground, but outside 6-month window |
| 🚗 First-Come-First-Served | No reservations — show up and claim a site |

### Booking Windows

Recreation.gov uses a rolling 6-month booking window for most campgrounds:
- You can book **up to 6 months** in advance
- Dates beyond the window show as "NYR" or "Not Yet Bookable"
- Some popular campgrounds release reservations at specific times

Example output:
```
🏕️  Popular Campground (123456)
   ⏳ NOT YET BOOKABLE — Check back when 6-month window opens
```

## Campsite Types

Common `campsite_type` values:

| Type | Description |
|------|-------------|
| `TENT ONLY NONELECTRIC` | Tent camping, no hookups |
| `STANDARD NONELECTRIC` | Tent or RV, no hookups |
| `STANDARD ELECTRIC` | Tent or RV with electric |
| `RV NONELECTRIC` | RV only, no hookups |
| `RV ELECTRIC` | RV with electric hookup |
| `CABIN NONELECTRIC` | Rustic cabin |
| `GROUP STANDARD NONELECTRIC` | Large group sites |

Use `--type` to filter:
- `tent` → matches TENT
- `rv` → matches RV, TRAILER
- `standard` → matches STANDARD
- `electric` → matches ELECTRIC
- `nonelectric` → matches NONELECTRIC

Combine with flags: `--type rv --electric`

## Architecture

```
scripts/
└── check.py       # Single-file CLI (stdlib only)

references/
└── api-docs.md    # Recreation.gov API documentation
```

### API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `/api/camps/availability/campground/{id}/month` | Monthly availability calendar |
| `/api/camps/campgrounds/{id}` | Campground metadata |
| `/api/camps/campsites/{id}` | Individual site details (for amenity filters) |

### How It Works

1. **Fetch monthly availability** — Gets the availability calendar for each month in the search range
2. **Check consecutive nights** — Finds sites where ALL requested nights are "Available"
3. **Apply filters** — Type filtering is fast (from calendar data); amenity filtering requires additional API calls
4. **Analyze status** — Determines why sites aren't available (sold out vs not yet released vs FCFS)

## Technical Notes

### No Dependencies

Uses only Python standard library (`urllib`, `json`, `argparse`). No pip install needed.

### Rate Limiting

Recreation.gov doesn't strictly rate limit, but:
- Be reasonable (~1-2 requests/second)
- Amenity filters (`--pets`, `--shade`) require one extra API call per matching site
- Uses a browser-like User-Agent

### Caveats

1. **Availability changes constantly** — Popular sites book up fast. Check again before booking.

2. **Some campgrounds are seasonal** — They may show 0 sites outside their operating dates.

3. **Group sites excluded by default** — Use `--include-group` to see them.

## Workflow: Finding and Booking

```bash
# 1. Find campgrounds near your destination
python3 ../ridb-search/scripts/search.py -l "Yosemite Valley" --camping-only

# 2. Check availability for your dates
python3 scripts/check.py \
  -c 232447 232448 232449 \
  --start 2026-07-15 \
  --nights 2 \
  --type tent

# 3. Open the booking URL in your browser
open "https://www.recreation.gov/camping/campgrounds/232448"
```

## Combining with Reserve America

For comprehensive availability, check both recreation.gov and Reserve America:

```bash
# Recreation.gov (federal)
recgov=$(python3 scripts/check.py -c 233965 233900 --start 2026-07-10 -n 2 --json)

# Reserve America (state parks)
ra=$(node ../reserveamerica/dist/cli.js availability -l "Newport, OR" -d 2026-07-10 -n 2 --json)

# Both results in one view
echo "=== Recreation.gov ===" && echo "$recgov" | python3 -m json.tool
echo "=== Reserve America ===" && echo "$ra" | python3 -m json.tool
```

## License

MIT
