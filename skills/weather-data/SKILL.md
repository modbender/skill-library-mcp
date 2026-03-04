---
name: weather-data
description: Provides weather forecast data from NOAA. Free tier returns 3-day forecast, premium tier returns 7-day with hourly data.
user-invocable: true
---

# Weather Data Service

Get weather forecasts for any location using NOAA data.

## Usage

### Free Forecast (3-day)
```
curl "http://localhost:5000/forecast?lat=40.71&lon=-74.00"
```

### Premium Forecast (7-day + hourly)
Requires x402 payment (0.05 USDC)
```
curl -H "X-Payment: <payment_header>" "http://localhost:5000/forecast/premium?lat=40.71&lon=-74.00"
```

## Endpoints

- `GET /forecast` - Free 3-day forecast
- `GET /forecast/premium` - Paid 7-day + hourly forecast (0.05 USDC)
- `GET /health` - Health check

## Parameters

- `lat` - Latitude (default: 40.71)
- `lon` - Longitude (default: -74.00)
