---
name: openmeteo-weather
description: "Get current weather, hourly and daily forecasts for any city or coordinates worldwide. Use when the user asks about weather, temperature, rain, snow, wind, sunrise/sunset, UV, humidity, pressure, or wants to know if they need an umbrella."
metadata: {"openclaw":{"emoji":"🌤","requires":{"bins":["curl","jq"]}}}
user-invocable: true
---

# OpenMeteo Weather

Fetch current weather and forecasts via the free Open-Meteo API. No API key required. Supports any location worldwide.

CLI: `bash {baseDir}/scripts/weather.sh [options]`

## Quick reference

```
# Current weather (city name alone is enough)
bash {baseDir}/scripts/weather.sh --current --city=Berlin
bash {baseDir}/scripts/weather.sh --current --city=London

# Exact coordinates for precision if available
bash {baseDir}/scripts/weather.sh --current --lat=48.8566 --lon=2.3522

# Disambiguate with --country (any format: code, full name, partial)
bash {baseDir}/scripts/weather.sh --current --city=Portland --country=US

# Forecast (daily + hourly)
bash {baseDir}/scripts/weather.sh --forecast-days=3 --city=Paris

# Both current + forecast
bash {baseDir}/scripts/weather.sh --current --forecast-days=2 --city=Rome

# Custom params — fetch only precipitation data
bash {baseDir}/scripts/weather.sh --forecast-days=2 --city=Vienna \
  --hourly-params=precipitation,precipitation_probability,weather_code
```

## Options

**Location (required — pick one):**
- `--city=NAME` — city name; auto-geocoded, usually sufficient on its own
- `--country=…` — optional country hint, any format works (`GB`, `France`, `Ger`). Only needed to disambiguate (e.g. Portland US vs UK). Do not look up the "correct" code — pass whatever you have or omit entirely.
- `--lat=FLOAT --lon=FLOAT` — direct coordinates, skips geocoding

**Mode (at least one required):**
- `--current` — fetch current conditions
- `--forecast` — fetch hourly + daily forecast
- `--forecast-days=N` — forecast length 1–16 days (default: 7; implies `--forecast`)

**Param overrides (comma-separated variable names):**
- `--current-params=…` — override current weather variables
- `--hourly-params=…` — override hourly forecast variables
- `--daily-params=…` — override daily forecast variables

**Output:**
- `--human` — emoji-rich formatted output for humans (default is porcelain, optimized for agents)

## Rules

1. Default output is porcelain (compact, for agents). Never pass `--porcelain` — it's the default; saves tokens.
2. When the user asks about weather without specifying a location, check **USER.md** for their city/country.
3. Present results as a natural-language summary — do not paste raw CLI output to the user.
4. WMO weather codes are resolved to text labels automatically (e.g. "Slight rain", "Overcast").
5. Use `--forecast-days=1` or `--forecast-days=2` when the user only asks about today/tomorrow — don't waste tokens on a full 7-day fetch.
6. For targeted questions (e.g. "when will the rain stop?"), override params via `--hourly-params` or `--daily-params` to fetch only what's needed.

## Available API variables

Override defaults via `--current-params`, `--hourly-params`, `--daily-params`.

### Current & hourly variables

- `temperature_2m` (default) — air temperature at 2m, °C
- `apparent_temperature` (default) — feels-like temperature, °C
- `relative_humidity_2m` (default) — relative humidity at 2m, %
- `precipitation` (default) — total precipitation (rain + showers + snow), mm
- `precipitation_probability` (default, hourly only) — probability of precipitation, %
- `weather_code` (default) — weather condition, auto-resolved to text in output
- `wind_speed_10m` (default) — wind speed at 10m, km/h
- `wind_gusts_10m` — wind gust speed at 10m, km/h
- `wind_direction_10m` — wind direction, °
- `cloud_cover` (default, current only) — total cloud cover, %
- `is_day` (default, current only) — daytime flag, 0/1
- `pressure_msl` — sea-level atmospheric pressure, hPa
- `surface_pressure` — surface pressure, hPa
- `visibility` — visibility distance, m
- `rain` — rain only (no showers/snow), mm
- `showers` — shower rain only, mm
- `snowfall` — snowfall amount, cm
- `snow_depth` — snow depth on the ground, m
- `dew_point_2m` — dew point temperature at 2m, °C
- `uv_index` (hourly only) — UV index

### Daily variables

- `temperature_2m_max` (default) — daily max temperature, °C
- `temperature_2m_min` (default) — daily min temperature, °C
- `precipitation_sum` (default) — total daily precipitation, mm
- `precipitation_probability_max` (default) — max precipitation probability, %
- `weather_code` (default) — dominant weather condition for the day
- `wind_speed_10m_max` (default) — max wind speed, km/h
- `wind_gusts_10m_max` — max wind gust speed, km/h
- `wind_direction_10m_dominant` — dominant wind direction, °
- `sunrise` — sunrise time, ISO 8601
- `sunset` — sunset time, ISO 8601
- `daylight_duration` — daylight duration, seconds
- `sunshine_duration` — sunshine duration, seconds
- `precipitation_hours` — hours with precipitation
- `rain_sum` — total daily rain, mm
- `showers_sum` — total daily showers, mm
- `snowfall_sum` — total daily snowfall, cm
- `uv_index_max` — max UV index
- `apparent_temperature_max` — daily max feels-like, °C
- `apparent_temperature_min` — daily min feels-like, °C

## Conversational examples

**User:** "What's the weather like?"
- Location not specified → get city/country from USER.md.
- Wants a general overview → use `--current`.
```
bash {baseDir}/scripts/weather.sh --current --city=Berlin
```
- Summarize conditions naturally: "Clear sky, -12°C (feels like -17°C), wind 9 km/h."

**User:** "When will the rain stop?"
- Needs hourly precipitation timeline → use `--forecast-days=2` with only rain-related params.
```
bash {baseDir}/scripts/weather.sh --forecast-days=2 --city=Berlin \
  --hourly-params=precipitation,precipitation_probability,weather_code
```
- Scan the hourly output, find when precipitation drops to 0 and weather_code changes to non-rain. Answer concisely: "Rain should stop around 14:00 today."

**User:** "Do I need an umbrella?"
- Same approach as rain — check upcoming hours for precipitation.
```
bash {baseDir}/scripts/weather.sh --forecast-days=1 --city=Berlin \
  --hourly-params=precipitation,precipitation_probability,weather_code
```
- Analyze output and give a yes/no answer with reasoning: "Yes — 70% chance of rain between 11:00 and 15:00, up to 2mm."

**User:** "What's the weather this weekend in Rome?"
- Specific city + specific days → use `--forecast` with `--daily-params` only.
- Calculate the right `--forecast-days` to cover the weekend, then pick Saturday/Sunday from the daily output.
```
bash {baseDir}/scripts/weather.sh --forecast-days=7 --city=Rome \
  --daily-params=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,precipitation_probability_max
```
- Present only Saturday and Sunday from the output: "Saturday: 14°/8°C, partly cloudy. Sunday: 16°/9°C, clear sky."

**User:** "What's the temperature outside?"
- Only wants temperature → use `--current` with narrowed params.
```
bash {baseDir}/scripts/weather.sh --current --city=Berlin \
  --current-params=temperature_2m,apparent_temperature
```
- Short answer: "-5°C, feels like -9°C."
