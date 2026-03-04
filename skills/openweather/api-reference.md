# OpenWeather One Call API 3.0 — Quick Reference

## Endpoints

### Geocoding (city name → coordinates)
```
GET https://api.openweathermap.org/geo/1.0/direct
  ?q={city name},{state code},{country code}
  &limit=1
  &appid={API_KEY}
```

### Current + Forecast
```
GET https://api.openweathermap.org/data/3.0/onecall
  ?lat={lat}
  &lon={lon}
  &units={imperial|metric|standard}
  &exclude={minutely,hourly,daily,alerts}   ← exclude unneeded sections
  &appid={API_KEY}
```

### Human-readable overview (today + tomorrow)
```
GET https://api.openweathermap.org/data/3.0/onecall/overview
  ?lat={lat}
  &lon={lon}
  &units={imperial|metric|standard}
  &appid={API_KEY}
```

## Response Fields (current)
| Field | Description |
|-------|-------------|
| `dt` | Unix timestamp |
| `temp` | Temperature |
| `feels_like` | Perceived temperature |
| `humidity` | % humidity |
| `wind_speed` | Wind speed |
| `wind_deg` | Wind direction (degrees) |
| `uvi` | UV index |
| `visibility` | Visibility in metres |
| `weather[0].description` | Condition text |

## Response Fields (daily)
| Field | Description |
|-------|-------------|
| `dt` | Unix timestamp (noon) |
| `temp.min` / `temp.max` | Daily temperature range |
| `pop` | Probability of precipitation (0–1) |
| `summary` | Human-readable daily summary |
| `weather[0].description` | Condition text |

## Rate Limits
- Free tier: 1,000 calls/day
- Paid: pay-per-call beyond free tier
- One Call 3.0 requires separate subscription at openweathermap.org

## Error Codes
| Code | Meaning |
|------|---------|
| 401 | Invalid API key |
| 404 | Location not found |
| 429 | Rate limit exceeded |
| 5xx | Server error — retry |
