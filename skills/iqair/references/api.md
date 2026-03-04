# IQAir API Reference

## API Key Setup

Users must get a free API key from IQAir:
1. Visit https://dashboard.iqair.com/personal/api-keys
2. Sign up or sign in
3. Subscribe to the free Community plan
4. Copy the API key

Store the key as an environment variable: `IQAIR_API_KEY`

## Endpoints

### Get City Air Quality (Nearest)

Finds the nearest city based on IP geolocation:

```bash
curl "https://api.airvisual.com/v2/nearest_city?key=YOUR_API_KEY"
```

### Get City Air Quality (By Name)

Get air quality for a specific city:

```bash
curl "https://api.airvisual.com/v2/city?city=Riga&state=Riga&country=Latvia&key=YOUR_API_KEY"
```

**Note**: City, state, and country names are case-sensitive and must match IQAir's database exactly.

### Get City Air Quality (By Coordinates)

Get air quality by GPS coordinates (most flexible):

```bash
curl "https://api.airvisual.com/v2/nearest_city?lat=56.9496&lon=24.1052&key=YOUR_API_KEY"
```

## Response Format

All endpoints return similar JSON:

```json
{
  "status": "success",
  "data": {
    "city": "Riga",
    "state": "Riga",
    "country": "Latvia",
    "location": {
      "type": "Point",
      "coordinates": [24.1052, 56.9496]
    },
    "current": {
      "pollution": {
        "ts": "2026-02-16T22:00:00.000Z",
        "aqius": 45,
        "mainus": "p2",
        "aqicn": 15,
        "maincn": "p2"
      },
      "weather": {
        "ts": "2026-02-16T22:00:00.000Z",
        "tp": -5,
        "pr": 1015,
        "hu": 85,
        "ws": 3.6,
        "wd": 270,
        "ic": "03n"
      }
    }
  }
}
```

### Key Fields

- `aqius`: US AQI (Air Quality Index) value
- `aqicn`: China AQI value
- `mainus`/`maincn`: Main pollutant (p2=PM2.5, p1=PM10, o3=Ozone, etc.)

## AQI Levels & Interpretation

| AQI Range | Level | Color | Emoji |
|-----------|-------|-------|-------|
| 0-50 | Good | Green | 🟢 |
| 51-100 | Moderate | Yellow | 🟡 |
| 101-150 | Unhealthy for Sensitive Groups | Orange | 🟠 |
| 151-200 | Unhealthy | Red | 🔴 |
| 201-300 | Very Unhealthy | Purple | 🟣 |
| 301+ | Hazardous | Maroon | 🟤 |

## Rate Limits (Community Plan)

- 5 calls per minute
- 500 calls per day
- 10,000 calls per month

## Error Handling

Common errors:

- `401`: Invalid API key
- `404`: City/location not found
- `429`: Rate limit exceeded
- `500`: Server error

Always check `status` field in response:
- `"success"`: Data retrieved successfully
- `"fail"`: Error occurred (check error message)
