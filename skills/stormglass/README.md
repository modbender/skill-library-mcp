# Stormglass Surf Skill

An OpenClaw-friendly surf data skill that fetches current and 1-3 day ocean forecasts from Stormglass, including:

- wave height
- swell height/period/direction
- wind speed/direction
- wind gusts
- water temperature
- high/low tide extremes

It supports querying by:

- surf spot name (`--location`, with geocoding), or
- direct coordinates (`--lat` + `--lon`).

## Project Layout

- `SKILL.md` - skill contract and agent handoff guidance
- `scripts/surf_report.py` - main CLI
- `scripts/test_surf_report.py` - CLI test runner
- `scripts/normalize_surf_data.py` - optional schema normalizer
- `examples.md` - practical command/pipeline examples
- `reference.md` - API mapping, schema, and behavior details

## Requirements

- Python 3.10+
- Stormglass API key for non-mock runs
- Google Geocoding key optional (if absent, location mode falls back to OpenStreetMap Nominatim)

## Environment Variables

- `STORMGLASS_API_KEY` - required for live Stormglass requests
- `GOOGLE_GEOCODING_API_KEY` - optional; used when present for `--location`

### Credential Matrix

| Mode | `STORMGLASS_API_KEY` | `GOOGLE_GEOCODING_API_KEY` |
|---|---|---|
| `--mock` (offline tests) | not required | not required |
| live with `--lat/--lon` | required | not required |
| live with `--location` + Google geocoder | required | optional (preferred when set) |
| live with `--location` + OSM fallback | required | not required |

Primary credential for this skill is `STORMGLASS_API_KEY`.

## Quick Start

From repository root:

```bash
# 1) Offline smoke test (no keys required)
python3 scripts/surf_report.py --location "Highcliffe Beach" --horizon now --mock --output pretty

# 2) Live request by coordinates (Stormglass key required)
export STORMGLASS_API_KEY="..."
python3 scripts/surf_report.py --lat 50.735 --lon -1.705 --horizon 24h --output json

# 3) Live request by location (Google optional; OSM fallback if missing)
python3 scripts/surf_report.py --location "Highcliffe Beach" --horizon 72h --output json
```

## CLI Usage

```bash
python3 scripts/surf_report.py \
  (--location "Spot Name" | --lat <LAT> --lon <LON>) \
  [--horizon now|24h|48h|72h] \
  [--output json|pretty] \
  [--source "sg,noaa"] \
  [--timeout 20] \
  [--mock]
```

### Output Modes

- `--output json` (default): stable machine-readable payload for cron/agent pipelines
- `--output pretty`: human-readable terminal summary

### Exit Codes

- `0` success
- `2` invalid CLI arguments
- `3` missing configuration (API keys)
- `4` external API failure
- `5` parsing/normalization error

## Testing

Run the test runner:

```bash
python3 scripts/test_surf_report.py
```

It validates valid/invalid argument combinations and JSON output shape (including gust and water temperature fields).

## Cron / Agent Pipeline

Recommended cron-style usage:

```bash
python3 scripts/surf_report.py --location "Highcliffe Beach" --horizon 72h --output json
```

Optional post-normalization for strict schema defaults:

```bash
python3 scripts/surf_report.py --lat 50.735 --lon -1.705 --horizon 72h --output json | \
python3 scripts/normalize_surf_data.py
```

## Best Practices

Use the skill responsibly and keep API usage sustainable:

- Cache responses and avoid rapid polling; keep request rates gentle to public endpoints.
- Persist fetched data locally where appropriate to reduce repeated lookups and duplicate requests.
- Validate and adapt to endpoint field changes by inspecting returned JSON before downstream assumptions.

## Further Documentation

- Detailed API behavior and schema: [reference.md](reference.md)
- Practical command and pipeline examples: [examples.md](examples.md)
- Skill contract for other agents: [SKILL.md](SKILL.md)
