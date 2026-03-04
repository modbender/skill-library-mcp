# CTA Skill — Development Guide

## Architecture

Single-file Node.js CLI (`scripts/cta.mjs`) with zero npm dependencies. Uses only Node.js built-in modules (`node:util`, `node:fs`, `node:path`, `node:os`, `node:child_process`) and the built-in `fetch` API (Node 18+).

## Project Structure

```
scripts/cta.mjs    Main entry point — CLI, API calls, data parsing, output formatting
SKILL.md           OpenClaw skill manifest (read by the agent runtime)
.env.example       Template for API keys
```

## Key Design Decisions

- **Zero dependencies**: Keeps the skill lightweight and avoids supply chain risk. CSV parsing, .env loading, and timestamp parsing are all hand-rolled.
- **Central Time handling**: CTA APIs return timestamps in Central Time with no timezone suffix. We store these in a Date's UTC slots so `getUTCHours()`/`getUTCMinutes()` returns the Central Time values directly. See `parseCTATimestamp()`.
- **Embedded station data**: The `STATIONS` array provides fuzzy matching for ~50 key stations without requiring GTFS data. GTFS extends this when available.
- **GTFS cached locally**: Static schedule data downloads to `~/.cta/gtfs/` and is read on demand. Not bundled with the skill.

## Running

```bash
node scripts/cta.mjs --help              # Show all commands
node scripts/cta.mjs arrivals --station "Clark/Lake"
node scripts/cta.mjs alerts
```

Requires `CTA_TRAIN_API_KEY` and `CTA_BUS_API_KEY` environment variables (or `.env` file) for train/bus commands. Alerts work without keys.

## Testing

```bash
npm test
```

Tests are in `tests/` using Node.js built-in test runner (`node --test`).

## APIs

| API | Base URL | Auth |
|-----|----------|------|
| Train Tracker | `https://lapi.transitchicago.com/api/1.0` | API key (query param) |
| Bus Tracker v2 | `https://www.ctabustracker.com/bustime/api/v2` | API key (query param) |
| Customer Alerts | `https://www.transitchicago.com/api/1.0` | None |
| GTFS Static | `https://www.transitchicago.com/downloads/sch_data/google_transit.zip` | None |

## Station IDs

- Parent station IDs (mapid): 4xxxx range — used for Train Tracker arrivals
- Directional stop IDs: 3xxxx range — platform-specific
- Source of truth: [CTA L Stops dataset](https://data.cityofchicago.org/Transportation/CTA-System-Information-List-of-L-Stops/8pix-ypme)
