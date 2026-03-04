---
name: weather-intelligence-digest
description: Generate daily Weather Intelligence Digest using NOAA/NWS data with customizable locations and alert monitoring.
homepage: https://api.weather.gov
metadata: { "openclaw": { "emoji": "🌦️", "requires": { "bins": ["python3", "pip"] } } }
---

# Weather Intelligence Digest

Generate a daily Weather Intelligence Digest using NOAA / NWS data.

## Setup

1. **Dependencies:** `python3`, `pip`.
2. Optional but recommended: `python3 -m venv .venv && source .venv/bin/activate`.
3. `pip install -r requirements.txt`.
4. Copy `config.example.json` to `config.json` and customize the `locations` list with `name`, `lat`, `lon` pairs.

## Usage

```bash
python3 weather_digest.py --config config.json --output digest.md
```

Output is Markdown; convert to PDF/email as needed.

## Configuration Notes

- Data source: `api.weather.gov` (no API key required; feel free to customize the User-Agent string in the script).
- Each location fetches forecast + alerts; add/remove fields as needed.
- Extend the template by editing `build_digest` in `weather_digest.py`.