# Weather Intelligence Digest Skill

This skill builds a daily briefing that highlights forecasts and severe-weather alerts for a list of locations. It relies entirely on NOAA/NWS public APIs, so there are no keys to manage.

## Features

- Pulls the latest gridpoint forecast (today + tonight) for each configured city
- Surfaces active alerts with severity badges, local expiration times, and trimmed instructions
- Produces Markdown, HTML (with selectable color themes), and JSON so you can publish, embed, or automate the digest anywhere

## Quick Start

```bash
cd skills/weather-digest
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json  # customize locations
python weather_digest.py \
  --config config.json \
  --output digest.md \
  --html digest.html \
  --json digest.json \
  --theme daybreak  # midnight (dark) by default
```

## Sample Output

```
# Weather Intelligence Digest
*Generated Tuesday, February 10 2026*

## New York City
**Nearest location:** New York, NY
### Outlook
- **Today**: 42°F, Light Rain (winds 10 mph S)
- **Tonight**: 35°F, Chance Rain/Snow (winds 5 mph NW)

### Active Alerts
- No active alerts
```

Customize the template by editing `build_digest` in `weather_digest.py`. Ship-ready marketing copy lives in `landing-page.md`, pricing guidance in `pricing.md`, automation recipes in `automation.md`, and theme notes in `themes.md`.
