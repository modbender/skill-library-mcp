---
name: stormglass-surf-skill
description: Fetch surf-relevant ocean conditions from Stormglass by spot name or coordinates, including current snapshot and 1-3 day forecast windows with tides, gusts, and water temperature. Use when users ask for surf reports, wave or swell conditions, tide timing, wind, gusts, or water temperature for a beach or surf spot.
version: 1.0.2
metadata:
  openclaw:
    requires:
      env:
        - STORMGLASS_API_KEY
      bins:
        - python3
    primaryEnv: STORMGLASS_API_KEY
    homepage: https://github.com/dgorissen/stormglass-skill
---

# Stormglass Surf Skill

## Purpose

Produce machine-readable surf condition data for cron-driven agent pipelines.

This skill resolves a surf spot name with Google Geocoding (or uses direct coordinates), queries Stormglass, and returns a stable JSON payload for downstream interpretation/rendering.

## Inputs

Provide exactly one location mode:

- `--location "Spot name"` (optional country/region in string), or
- `--lat <float> --lon <float>`

Optional controls:

- `--horizon now|24h|48h|72h` (default `72h`)
- `--output json|pretty` (default `json`, recommended for automation)
- `--source <comma-separated provider list>`
- `--mock` (offline deterministic data; useful for tests)

## Required Environment Variables

- `STORMGLASS_API_KEY` for Stormglass requests
- `GOOGLE_GEOCODING_API_KEY` optional for `--location` (if absent, script falls back to OpenStreetMap Nominatim)

In `--mock` mode, no API keys are required.

### Credential Matrix

| Mode | `STORMGLASS_API_KEY` | `GOOGLE_GEOCODING_API_KEY` |
|---|---|---|
| `--mock` | not required | not required |
| live `--lat/--lon` | required | not required |
| live `--location` with Google | required | optional (preferred when set) |
| live `--location` with OSM fallback | required | not required |

Primary credential is `STORMGLASS_API_KEY`.

## Execution Commands

JSON output for cron:

```bash
python scripts/surf_report.py --location "Highcliffe Beach" --horizon 72h --output json
```

Direct coordinates:

```bash
python scripts/surf_report.py --lat 50.735 --lon -1.705 --horizon 24h --output json
```

Offline test run:

```bash
python scripts/surf_report.py --location "Highcliffe Beach" --horizon now --mock --output json
```

## Output Contract (JSON-first)

Top-level keys are stable:

- `meta`: request metadata, timestamps, input mode, optional warnings
- `location`: resolved place details and coordinates
- `now`: instantaneous surf-relevant metrics
- `forecast`: horizon summaries and best windows
- `tides`: tide extremes and inferred current tide trend

Expected metric coverage (null if unavailable):

- `waveHeightM`
- `swellHeightM`
- `swellPeriodS`
- `swellDirectionDeg`
- `windSpeedMps`
- `windDirectionDeg`
- `windGustMps`
- `waterTemperatureC`

## Exit Codes

- `0`: success
- `2`: invalid CLI usage/arguments
- `3`: missing API keys/configuration
- `4`: external API failure (geocoding/Stormglass)
- `5`: response parsing/normalization failure

## Agent Handoff Rules

- Prefer `--output json` for downstream agents.
- Treat null metrics as "not provided by source", not zero.
- Read field-level details in `reference.md`.
- Use `examples.md` for prompt and command patterns.
- Use `scripts/test_surf_report.py` before cron rollout.
- Optional: use `scripts/normalize_surf_data.py` to enforce strict schema defaults before rendering.
