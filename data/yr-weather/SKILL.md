---
name: yr-weather
description: Fetch weather forecasts from the Norwegian Meteorological Institute (MET) using the yr.no API. Use when the user asks for weather information, forecasts, temperature, precipitation, wind conditions, or any weather-related queries for specific locations. Supports coordinates-based lookups and returns current conditions plus forecasts. REQUIRES latitude/longitude - no defaults. See common locations table.
---

# Yr.no Weather

Get weather forecasts from MET Norway via yr.no API (free, no key).

## Quick Start

```bash
# Current weather + forecast (requires lat/lon)
python3 {baseDir}/scripts/weather.py &lt;lat&gt; &lt;lon&gt; [altitude]

# Examples from common locations:
python3 {baseDir}/scripts/weather.py -33.9288 18.4174   # Cape Town
python3 {baseDir}/scripts/weather.py -33.8688 151.2093  # Sydney
python3 {baseDir}/scripts/weather.py 51.5074 -0.1278    # London

# Tomorrow&#x27;s summary (requires lat/lon)
python3 {baseDir}/scripts/tomorrow.py &lt;lat&gt; &lt;lon&gt;

# Run tests
python3 -m unittest discover {baseDir}/tests
```

## Tests

- Unit tests mock API calls (no network).
- Sample data in `scripts/tests/data/`.
- Run: `cd {baseDir}/scripts &amp;&amp; python3 ../tests/test_*.py`

## Common Locations

| City          | Lat       | Lon       |
|---------------|-----------|-----------|
| Cape Town     | -33.9288 | 18.4174  |
| Johannesburg  | -26.2041 | 28.0473  |
| Durban        | -29.8587 | 31.0218  |
| Sydney        | -33.8688 | 151.2093 |
| London        | 51.5074  | -0.1278  |
| New York      | 40.7128  | -74.0060 |
| Tokyo         | 35.6762  | 139.6503 |

## Structure

```
scripts/
├── yr_service.py    # API calls (tested/mocked)
├── utils.py         # Emoji/symbol helpers
├── weather.py       # Current + forecast CLI
├── tomorrow.py      # Tomorrow summary CLI
└── tests/data/      # Sample JSON
tests/
├── test_weather.py
└── test_service.py
```

## Standalone Repo

Install via pip: `pip install git+https://github.com/brandoncrabpi/yr-weather.git`
- `yr-weather -33.9288 18.4174`
- Tagged: v1.0.0

## Usage Terms

- User-Agent required (included).
- Cache 10min+ per location.
- Credit: "Data from MET Norway".

Refactored for production: no defaults, tests, modular service.
