---
name: openmeteo-sh-weather-simple
description: "Get current weather and forecasts for any city or coordinates using free OpenMeteo API. Use when the user asks about weather, temperature, rain, snow, wind, or wants to know if they need an umbrella."
metadata: {"openclaw":{"emoji":"🌤","requires":{"bins":["openmeteo"]}}}
homepage: https://github.com/lstpsche/openmeteo-sh
user-invocable: true
---

# OpenMeteo Weather (openmeteo-sh)

Current weather and forecasts (up to 16 days) via `openmeteo` CLI. No API key required.

## Quick reference

```
openmeteo weather --current --city=Berlin --llm
openmeteo weather --current --forecast-days=2 --city=London --llm
openmeteo weather --forecast-days=7 --forecast-since=5 --city=Rome --llm
openmeteo weather --current --lat=48.85 --lon=2.35 --llm
```

## Location (pick one)

- `--city=NAME` — city name (auto-geocoded)
- `--city=NAME --country=CODE` — disambiguate (e.g. Portland --country=US)
- `--lat=NUM --lon=NUM` — direct coordinates

## Options

- `--current` — current conditions
- `--forecast-days=N` — forecast length, 1–16 (default 7)
- `--forecast-since=N` — start from day N (1=today, 2=tomorrow). Must be <= forecast-days.
- `--hourly-params=LIST` — override hourly variables (comma-separated)
- `--daily-params=LIST` — override daily variables (comma-separated)
- `--current-params=LIST` — override current variables (comma-separated)
- `--temperature-unit=UNIT` — celsius (default) / fahrenheit
- `--llm` — always pass this

## Variables

Defaults are sensible for general weather. Override only when needed.

**Current & hourly:**
- `temperature_2m` — air temp, C
- `apparent_temperature` — feels-like, C
- `precipitation` — rain+showers+snow, mm
- `precipitation_probability` (hourly only) — chance of precipitation, %
- `weather_code` — condition, auto-resolved to text
- `wind_speed_10m` — wind, km/h
- `wind_gusts_10m` — gusts, km/h
- `cloud_cover` — cloud cover, %
- `snowfall` — snowfall, cm
- `uv_index` (hourly only) — UV index

**Daily:**
- `temperature_2m_max` / `temperature_2m_min` — max/min temp, C
- `precipitation_sum` — total precipitation, mm
- `precipitation_probability_max` — max precipitation chance, %
- `weather_code` — dominant condition
- `wind_speed_10m_max` — max wind, km/h
- `sunrise` / `sunset` — times
- `snowfall_sum` — total snowfall, cm

## Rules

1. Always pass `--llm`.
2. **Quote all user-provided values** in shell commands: `--city="New York"`, `--city="St. Petersburg"`. Only known-safe tokens (numbers, single ASCII words) may be unquoted.
3. Never use `help` subcommand or `--raw` — work only with what's described here.
4. No location specified -> use the user's default city/country if known from session context.
5. Summarize results naturally — never paste raw output.
6. Use `--forecast-days=1` for today, `=2` for tomorrow — minimize token waste.
7. Use `--forecast-since=N` to skip to a specific future day.
8. For targeted questions, override params to fetch only what's needed.
9. When the user switches cities ("and what about London?"), carry over all params used in prior weather queries this conversation — including any added in follow-ups. The new city gets the union of all previously requested params.

## Examples

**"What's the weather like?"** -> `openmeteo weather --current --city=Berlin --llm`
Summarize: "Clear, -12C (feels -17C), wind 9 km/h."

**"When will the rain stop?"** -> `openmeteo weather --forecast-days=2 --city=Berlin --hourly-params=precipitation,precipitation_probability,weather_code --llm`
Find when precipitation hits ~0. Answer: "Should stop around 14:00."

**"Do I need an umbrella?"** -> `openmeteo weather --forecast-days=1 --city=Berlin --hourly-params=precipitation,precipitation_probability,weather_code --llm`
"Yes — 70% chance between 11:00-15:00, up to 2mm."

**"Weather this weekend in Rome?"** -> `openmeteo weather --forecast-days=7 --forecast-since=5 --city=Rome --daily-params=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum --llm`
Present only Sat/Sun: "Saturday: 14/8C, partly cloudy. Sunday: 16/9C, clear."

**"Temperature outside?"** -> `openmeteo weather --current --city=Berlin --current-params=temperature_2m,apparent_temperature --llm`
"-5C, feels like -9C."
