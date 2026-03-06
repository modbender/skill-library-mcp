# OpenWeather Skill for OpenClaw

## Changelog

### 1.0.1 — Documentation/behavior alignment

Fixes the previously noted doc vs. implementation mismatches:
- If no city is provided, the CLI now uses `OPENWEATHER_DEFAULT_LOCATION` (when set).
- Documentation no longer claims `curl` is used; the implementation uses Python `urllib` (stdlib).
- The “home location” mechanism is explicitly defined via `OPENWEATHER_DEFAULT_LOCATION` (env-based, no hidden config path).

### 1.0.0 — Initial Public Release

## Why OpenWeather (and why this skill)

The OpenWeather One Call API 3.0 provides a complete, unified weather dataset in a single, consistent response.

In practical terms:
- Fewer API calls to assemble a complete forecast (1 geocode + 1 onecall)
- Consistent fields across current, hourly, and daily data
- Forecast depth (8 days) and context (UV index, moon phase, alerts) that simpler APIs may omit
- More reliable conversational output because the data model is stable and predictable

## Subscription Requirement

The OpenWeather One Call API 3.0 requires enabling/activating the One Call 3.0 product for your API key on your OpenWeather account. A free quota may exist, but it must be enabled for the key before requests succeed.

## Forecast Products Supported (One Call 3.0)

- Current weather (near real-time conditions)
- Hourly forecast (up to 48 hours)
- Daily forecast (up to 8 days)

Note: This CLI excludes `alerts` to avoid unexpected long text outputs; add alerts later only if you also implement message chunking for your chat platform.

## Data Returned (high level)

- Conditions and descriptions
- Temperature and feels-like
- Humidity, pressure, dew point (where provided)
- Cloudiness and visibility (where provided)
- UV index (UVI)
- Wind speed/direction/gust (where provided)
- Precipitation probability (PoP), rain/snow volume (where provided)
- Sunrise/sunset, timezone offsets
- Moon phase (available in daily payload; not currently printed)

## Location Resolution

- City/state/region/country lookup via OpenWeather Geocoding
- Automatic lat/lon lookup
- Graceful handling of ambiguous locations (use “City, State, Country” to disambiguate)

## Conversational Output

- Human-readable CLI output intended for bots to relay

If you want Telegram-safe chunking and multi-message flows, that should be implemented at the agent layer (or add explicit chunking logic in a future version).

## Security and Configuration

- Config via environment variables only
  - `OPENWEATHER_API_KEY` (required)
  - `OPENWEATHER_UNITS` (optional: imperial|metric|standard; default imperial)
  - `OPENWEATHER_DEFAULT_LOCATION` (optional default “home” location string)
- No hardcoded credentials
- No user data storage
- No external state required
- No elevated privileges required
- Network requests are restricted to OpenWeather domains only
- At most 2 API calls per request (geocode + onecall)

## Usage

Examples:

python3 scripts/weather.py current "New York, NY, US"
python3 scripts/weather.py forecast "Johnstown, PA, US" --days 5
python3 scripts/weather.py hourly "Johnstown, PA, US" --hours 12

Default home location:

export OPENWEATHER_DEFAULT_LOCATION="Johnstown, PA, US"
python3 scripts/weather.py current
