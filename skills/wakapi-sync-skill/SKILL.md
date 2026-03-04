---
name: wakapi-sync
description: Daily Wakapi (WakaTime-compatible) summary → local CSV files. Fetch today stats and append/update CSVs for totals, top projects, and top languages.
metadata: {"openclaw": {"requires": {"env": ["WAKAPI_URL", "WAKAPI_API_KEY", "WAKAPI_OUT_DIR"]}, "primaryEnv": "WAKAPI_OUT_DIR"}}
---

# wakapi-sync

Daily Wakapi (WakaTime-compatible) summary → local CSV files.

## What it does
- Fetches **today** stats from Wakapi and appends/updates CSVs:
  - `daily-total.csv` (1 row/day)
  - `daily-top-projects.csv` (N rows/day)
  - `daily-top-languages.csv` (N rows/day)

## Requirements
- Node.js 18+

## Configuration (env vars)
- `WAKAPI_URL` (required)
  - Example: `https://wakapi.example.com`
- `WAKAPI_API_KEY` (required)
  - Your Wakapi API key.
- `WAKAPI_OUT_DIR` (required)
  - Output directory for CSVs.
  - Example: `~/wakapi-data`

Optional:
- `WAKAPI_TOP_N_PROJECTS` (default: `10`)
- `WAKAPI_TOP_N_LANGUAGES` (default: `10`)

Auth:
- Uses `Authorization: Basic base64(<api_key>)` (matches our current Wakapi setup).

## Usage
Run:

```bash
node scripts/wakapi-daily-summary.mjs
```

## Output CSV schemas
### daily-total.csv
Columns:
- `date` (YYYY-MM-DD)
- `total_seconds`
- `total_hours`
- `projects_count`
- `languages_count`

### daily-top-projects.csv
Columns:
- `date`
- `rank`
- `project`
- `seconds`
- `hours`
- `percent`

### daily-top-languages.csv
Columns:
- `date`
- `rank`
- `language`
- `seconds`
- `hours`
- `percent`
