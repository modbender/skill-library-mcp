---
name: dc-weather
description: Check Washington DC weather using Open-Meteo API. Use when user asks about DC weather, current conditions, or needs a weather report for Washington DC.
---

# DC Weather Skill

Get Washington DC weather without API keys using Open-Meteo.

## Quick Check

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=38.9072&longitude=-77.0369&current_weather=true&temperature_unit=fahrenheit" | jq -r '"DC: \(.current_weather.temperature)°F, wind \(.current_weather.windspeed) mph, code \(.current_weather.weathercode)"'
```

## Weather Codes

| Code | Condition |
|------|-----------|
| 0 | Clear |
| 1-3 | Partly cloudy |
| 45-48 | Fog |
| 51-57 | Drizzle |
| 61-67 | Rain |
| 71-77 | Snow |
| 95-99 | Thunderstorm |

## Pretty Format

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=38.9072&longitude=-77.0369&current_weather=true&temperature_unit=fahrenheit" | jq -r '"\n🌤️ Washington, DC\n━━━━━━━━━━━━━━\n🌡️  \(.current_weather.temperature)°F\n💨  Wind: \(.current_weather.windspeed) mph\n🌪️  Code: \(.current_weather.weathercode)\n"'
```