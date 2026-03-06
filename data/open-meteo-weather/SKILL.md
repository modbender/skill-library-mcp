---
name: open-meteo-weather
description: >-
  Fetch current weather conditions and 7-day daily forecasts for any location
  using the Open-Meteo API. Includes geocoding to resolve city names to
  coordinates. Free, no API key required.
---

# Open-Meteo Weather

Current weather conditions and 7-day daily forecasts for any location. Uses the free Open-Meteo API with built-in geocoding. No API key, no authentication, no rate limits for non-commercial use.

## Quick Reference

| Action | Endpoint |
|--------|----------|
| Geocode city to lat/lon | `GET https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en` |
| Current + 7-day forecast | `GET https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,wind_speed_10m_max,weather_code&timezone=auto` |

## Units

Default to metric. On the first weather request in a session, ask the user: "Do you prefer Celsius or Fahrenheit?" Remember their answer for the rest of the session.

For metric (default), no extra parameters needed.

For imperial, append these parameters to the forecast URL:

```
&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch
```

The response `current_units` and `daily_units` objects reflect the chosen system.

## Geocoding

Resolve a city name to latitude/longitude before calling the forecast API.

**Endpoint:** `GET https://geocoding-api.open-meteo.com/v1/search`

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | City name (minimum 2 characters) |
| `count` | No | Number of results (default 10, max 100). Use `1` for best match. |
| `language` | No | Response language (default `en`) |

**Example:**

```bash
curl "https://geocoding-api.open-meteo.com/v1/search?name=Berlin&count=1&language=en"
```

**Extract from the response:**

| Field | Description |
|-------|-------------|
| `results[0].latitude` | Latitude (WGS84) |
| `results[0].longitude` | Longitude (WGS84) |
| `results[0].name` | Resolved city name |
| `results[0].country` | Country name |
| `results[0].admin1` | State/province |

If `results` is empty or missing, tell the user the location was not found and ask them to be more specific.

If multiple cities share the same name, use `count=5` and present the options (name, admin1, country) so the user can pick the right one.

## Current Conditions

Include the `current` parameter in the forecast call.

**Parameters to request:**

```
current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,precipitation
```

**Response fields:**

| Field | Description |
|-------|-------------|
| `current.temperature_2m` | Temperature at 2m height |
| `current.apparent_temperature` | Feels-like temperature (wind chill / heat index) |
| `current.relative_humidity_2m` | Relative humidity percentage |
| `current.weather_code` | WMO code (see Weather Codes below) |
| `current.wind_speed_10m` | Wind speed at 10m height |
| `current.wind_direction_10m` | Wind direction in degrees |
| `current.precipitation` | Precipitation in the last hour |

Units are in the `current_units` object. Always include the unit when presenting values.

Convert `wind_direction_10m` degrees to the nearest compass direction: N (338-22), NE (23-67), E (68-112), SE (113-157), S (158-202), SW (203-247), W (248-292), NW (293-337).

## Daily Forecast

Include the `daily` parameter. Always add `timezone=auto` so times are in the location's local timezone.

**Parameters to request:**

```
daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,wind_speed_10m_max,weather_code&timezone=auto
```

All `daily` fields are arrays indexed by day. `daily.time` contains date strings (YYYY-MM-DD).

| Field | Description |
|-------|-------------|
| `daily.time[i]` | Date |
| `daily.weather_code[i]` | WMO code for the day |
| `daily.temperature_2m_max[i]` | High temperature |
| `daily.temperature_2m_min[i]` | Low temperature |
| `daily.precipitation_sum[i]` | Total precipitation |
| `daily.precipitation_probability_max[i]` | Max precipitation probability (%) |
| `daily.sunrise[i]` | Sunrise time (ISO 8601, local) |
| `daily.sunset[i]` | Sunset time (ISO 8601, local) |
| `daily.wind_speed_10m_max[i]` | Max wind speed |

## Weather Codes

WMO weather interpretation codes returned in `weather_code` fields:

| Code | Description |
|------|-------------|
| 0 | Clear sky |
| 1 | Mainly clear |
| 2 | Partly cloudy |
| 3 | Overcast |
| 45 | Fog |
| 48 | Depositing rime fog |
| 51 | Light drizzle |
| 53 | Moderate drizzle |
| 55 | Dense drizzle |
| 56 | Light freezing drizzle |
| 57 | Dense freezing drizzle |
| 61 | Slight rain |
| 63 | Moderate rain |
| 65 | Heavy rain |
| 66 | Light freezing rain |
| 67 | Heavy freezing rain |
| 71 | Slight snow |
| 73 | Moderate snow |
| 75 | Heavy snow |
| 77 | Snow grains |
| 80 | Slight rain showers |
| 81 | Moderate rain showers |
| 82 | Violent rain showers |
| 85 | Slight snow showers |
| 86 | Heavy snow showers |
| 95 | Thunderstorm |
| 96 | Thunderstorm with slight hail |
| 99 | Thunderstorm with heavy hail |

Use the description when presenting weather to the user. Do NOT show the numeric code.

## Response Formatting

Present a concise summary. Do NOT show raw JSON, API URLs, or technical details.

**Current conditions format:**

```
Weather in {city}, {country}
{weather description}, {temperature} (feels like {apparent_temperature})
Humidity: {humidity}%
Wind: {speed} from the {compass_direction}
Precipitation: {amount}
```

**Forecast format:**

After current conditions, show the 7-day outlook as a compact list with one line per day:

```
Mon Feb 24: Partly cloudy, 8/3C, 10% rain, wind 15 km/h
Tue Feb 25: Rain, 6/2C, 80% rain, 4.2mm, wind 25 km/h
```

If the user asks a specific question ("Will it rain tomorrow?", "What's the temperature on Friday?"), answer directly instead of showing the full forecast.

## Error Handling

If any API call returns a non-200 status or the response cannot be parsed, inform the user that the weather service is temporarily unavailable and suggest trying again in a few minutes. Do NOT show raw error messages or status codes.
