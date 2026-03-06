# 🌤️ tempest-weather

An [OpenClaw](https://openclaw.ai) skill that fetches live weather data from a [WeatherFlow Tempest](https://weatherflow.com/tempest-weather-system/) station on demand and returns structured JSON.

## What it does

Ask your OpenClaw agent anything about current conditions and it will call the Tempest REST API and return clean, normalized JSON covering:

- **Conditions** — temperature (°C/°F), humidity, barometric pressure, pressure trend
- **Wind** — average, lull, gust (m/s and mph), direction (degrees + cardinal)
- **Precipitation** — rain last hour, daily total, precipitation type (rain/hail/none)
- **Lightning** — strike count, last strike distance, 1hr and 3hr totals
- **Solar** — UV index, solar radiation, illuminance

## Requirements

- Python 3
- `curl` or `requests` (`pip install requests`)
- A [Tempest Personal Access Token](https://tempestwx.com) and Station ID

## Setup

**1. Get your credentials**

Generate a token at tempestwx.com → Settings → Data Authorizations → Create Token.

Find your Station ID:
```bash
curl -s "https://swd.weatherflow.com/swd/rest/stations?token=YOUR_TOKEN" | python3 -m json.tool
```
Look for `"station_id"` in the response.

**2. Set environment variables**

Add these to your `~/.zshrc` (or `~/.bashrc`):
```bash
export TEMPEST_TOKEN="your_token_here"
export TEMPEST_STATION_ID="your_station_id_here"
```
Then reload: `source ~/.zshrc`

**3. Install the skill**

```bash
clawhub install tempest-weather
```

Or manually copy the skill folder to your OpenClaw workspace:
```bash
scp -r tempest-weather magpie@your-host.local:~/.openclaw/workspace/skills/
```

## Example interactions

> "What's the weather at my station?"

> "Is it raining?"

> "How windy is it right now?"

> "Any lightning nearby?"

> "What's the UV index?"

## Output schema

```json
{
  "station_id": 12345,
  "station_name": "My Backyard",
  "timestamp": "2024-01-15T14:32:00Z",
  "conditions": {
    "temperature_c": 18.5,
    "temperature_f": 65.3,
    "humidity_pct": 62,
    "pressure_mb": 1013.4,
    "pressure_trend": "steady"
  },
  "wind": {
    "speed_avg_ms": 3.2,
    "speed_avg_mph": 7.2,
    "speed_gust_ms": 5.8,
    "speed_gust_mph": 13.0,
    "direction_deg": 247,
    "direction_cardinal": "WSW"
  },
  "precipitation": {
    "rain_last_1hr_mm": 0.0,
    "rain_daily_mm": 2.4,
    "precip_type": "none"
  },
  "lightning": {
    "strike_count_interval": 0,
    "strike_count_last_1hr": 0,
    "last_strike_distance_km": null
  },
  "solar": {
    "uv_index": 3,
    "solar_radiation_wm2": 412,
    "illuminance_lux": 28500
  },
  "battery_volts": 2.42
}
```

## Files

```
tempest-weather/
├── SKILL.md                    # Skill instructions and frontmatter
├── scripts/
│   └── fetch_tempest.py        # Standalone fetch + normalize script
└── references/
    └── obs_fields.md           # Full field reference and unit conversions
```

## License

MIT
