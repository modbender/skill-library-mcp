---
name: openmeteo-sh-weather-advanced
description: "Advanced weather from free OpenMeteo API: historical data, detailed variable selection, model choice, past-days, and in-depth forecasts. Use when the user asks about historical weather, specific weather models, niche variables (pressure, dew point, snow depth, etc.), or needs fine-grained control beyond simple current/forecast queries."
metadata: {"openclaw":{"emoji":"🌦","requires":{"bins":["openmeteo"]}}}
homepage: https://github.com/lstpsche/openmeteo-sh
user-invocable: true
---

# OpenMeteo Weather — Advanced (openmeteo-sh)

Advanced weather queries via `openmeteo` CLI: historical data (from 1940), detailed variable selection, model choice, and fine-grained forecast control. No API key required.

CLI: `openmeteo <command> [options]`

## Output format

Always use `--llm` — compact TSV output designed for LLMs. Weather codes are auto-resolved to text. Pass `--raw` only if the user explicitly asks for JSON.

## Quick reference

```
# Current weather
openmeteo weather --current --city=Berlin --llm

# Current + 2-day forecast
openmeteo weather --current --forecast-days=2 --city=London --llm

# Only precipitation data
openmeteo weather --forecast-days=2 --city=Vienna \
  --hourly-params=precipitation,precipitation_probability,weather_code --llm

# Coordinates instead of city
openmeteo weather --current --lat=48.8566 --lon=2.3522 --llm

# Disambiguate city with country
openmeteo weather --current --city=Portland --country=US --llm

# Forecast starting from day 3 (skip today and tomorrow)
openmeteo weather --forecast-days=7 --forecast-since=3 --city=London --llm

# Historical weather
openmeteo history --city=Paris --start-date=2024-01-01 --end-date=2024-01-31 --llm
```

## Location (pick one, required)

- `--city=NAME` — city name, auto-geocoded; usually sufficient on its own
- `--country=CODE` — optional country hint to disambiguate (e.g. US, GB). Only needed when city name is ambiguous. Pass whatever you have or omit.
- `--lat=NUM --lon=NUM` — direct WGS84 coordinates, skips geocoding

## Commands

### weather — forecast up to 16 days + current conditions

**Mode (at least one required):**
- `--current` — fetch current conditions
- `--forecast-days=N` — days of forecast, 0–16 (default 7)
- `--forecast-since=N` — start from day N of the forecast (1=today, 2=tomorrow, etc.). Trims the window server-side. Must be <= forecast-days.

**Param overrides (comma-separated variable names):**
- `--current-params=LIST` — override current variables
- `--hourly-params=LIST` — override hourly variables
- `--daily-params=LIST` — override daily variables

**Units:**
- `--temperature-unit=UNIT` — celsius (default) / fahrenheit
- `--wind-speed-unit=UNIT` — kmh (default) / ms / mph / kn
- `--precipitation-unit=UNIT` — mm (default) / inch

**Other:**
- `--past-days=N` — include past days, 0–92 (default 0)
- `--timezone=TZ` — IANA timezone or auto (default auto)
- `--model=MODEL` — weather model (default best_match)

### history — historical weather from 1940

Requires `--start-date=YYYY-MM-DD` and `--end-date=YYYY-MM-DD`.
Supports `--hourly-params`, `--daily-params`, `--model` (era5, era5_land, cerra, ecmwf_ifs, etc.).

## Common weather variables

Override defaults via `--current-params`, `--hourly-params`, `--daily-params`. For the full variable list with descriptions, run `openmeteo weather help --daily-params` (or `--hourly-params`, `--current-params`).

### Current & hourly (most used)
- `temperature_2m` — air temp at 2m, C
- `apparent_temperature` — feels-like temp, C
- `relative_humidity_2m` — humidity, %
- `precipitation` — total precipitation (rain+showers+snow), mm
- `precipitation_probability` (hourly only) — chance of precipitation, %
- `weather_code` — condition code, auto-resolved to text (e.g. "Light rain")
- `wind_speed_10m` — wind at 10m, km/h
- `wind_gusts_10m` — gusts at 10m, km/h
- `cloud_cover` — total cloud cover, %
- `is_day` (current only) — daytime flag, 0/1
- `uv_index` (hourly only) — UV index
- `snowfall` — snowfall, cm
- `visibility` — visibility, m
- `pressure_msl` — sea-level pressure, hPa

### Daily (most used)
- `temperature_2m_max` / `temperature_2m_min` — daily max/min temp, C
- `precipitation_sum` — total daily precipitation, mm
- `precipitation_probability_max` — max precipitation chance, %
- `weather_code` — dominant condition for the day
- `wind_speed_10m_max` — max wind, km/h
- `sunrise` / `sunset` — ISO 8601 times
- `uv_index_max` — max UV index
- `snowfall_sum` — total daily snowfall, cm
- `apparent_temperature_max` / `apparent_temperature_min` — daily feels-like range, C

## Detailed variable help

Run `openmeteo weather help <flag>` to get a full list of available variables with descriptions:
```
openmeteo weather help --daily-params
openmeteo weather help --hourly-params
openmeteo weather help --current-params
openmeteo history help --daily-params
```
Add `--llm` for compact TSV output: `openmeteo weather help --daily-params --llm`

Use this when you need a variable beyond the common ones listed above.

## Rules

1. Always use `--llm` output format — most token-efficient, designed for agents.
2. **Quote all user-provided values** in shell commands. City names, dates, and any free-text input must be quoted to prevent shell interpretation: `--city="New York"`, `--city="St. Petersburg"`. Only known-safe tokens (numbers, single ASCII words) may be unquoted.
3. When the user asks about weather without specifying a location, use the user's default city/country if known from session context.
4. Present results as a natural-language summary — do not paste raw CLI output to the user.
5. Use `--forecast-days=1` or `--forecast-days=2` for today/tomorrow — don't waste tokens on 7-day fetches.
6. For targeted questions (e.g. "when will the rain stop?"), override params via `--hourly-params` or `--daily-params` to fetch only what's needed, analyze the output and give answer.
7. Use `--forecast-since=N` when the user asks about a specific future day (e.g. "weather on Friday") to avoid fetching unnecessary earlier days.
8. When the user switches cities ("and what about London?"), carry over all params used in prior weather queries this conversation — including any added in follow-ups. The new city gets the union of all previously requested params.

## Conversational examples

**User:** "What's the weather like?"
- Location not specified -> use city/country from session context.
- General overview -> `--current`.
```
openmeteo weather --current --city=Berlin --llm
```
- Summarize naturally: "Clear sky, -12C (feels like -17C), wind 9 km/h."

**User:** "When will the rain stop?"
- Needs hourly precipitation timeline.
```
openmeteo weather --forecast-days=2 --city=Berlin \
  --hourly-params=precipitation,precipitation_probability,weather_code --llm
```
- Scan output, find when precipitation drops to 0. Answer: "Rain should stop around 14:00 today."

**User:** "Do I need an umbrella?"
```
openmeteo weather --forecast-days=1 --city=Berlin \
  --hourly-params=precipitation,precipitation_probability,weather_code --llm
```
- Yes/no with reasoning: "Yes — 70% chance of rain between 11:00-15:00, up to 2mm."

**User:** "What's the weather this weekend in Rome?"
- Calculate `--forecast-since` to skip to Saturday, `--forecast-days` to cover through Sunday.
```
openmeteo weather --forecast-days=7 --forecast-since=5 --city=Rome \
  --daily-params=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum --llm
```
- Present only weekend days: "Saturday: 14/8C, partly cloudy. Sunday: 16/9C, clear."

**User:** "What's the temperature outside?"
- Only wants temperature -> narrow params.
```
openmeteo weather --current --city=Berlin \
  --current-params=temperature_2m,apparent_temperature --llm
```
- Short answer: "-5C, feels like -9C."

**User:** "How much rain fell in Tokyo last June?"
```
openmeteo history --city=Tokyo --start-date=2025-06-01 --end-date=2025-06-30 \
  --daily-params=precipitation_sum,rain_sum --llm
```
- Summarize total and notable days.
