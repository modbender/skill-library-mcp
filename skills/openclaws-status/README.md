# OpenClaw Status API

Monetize your OpenClaw agent status and health as an x402-paid API endpoint.

## What It Does

- Returns agent status (active/idle)
- Reports cron job health
- Shows platform uptime
- Monetizes via x402 (USDC on Base)

## Usage

```
GET /api/status - Get all agent statuses
GET /api/geocode?q=location - Geocode any location
GET /api/weather?lat=X&lon=Y - Get weather by coordinates
```

## Price

$0.001 USDC per request (x402 on Base)

## Endpoints

- `/api/status` - Returns: agents[], cronJobs[], platform info
- `/api/geocode?q=City` - Returns: lat, lon, display_name  
- `/api/weather?lat=X&lon=Y` - Returns: temperature, weather_code, wind

## Wallet

Payments go to: `0x483AE22AaEc52c0a1871C07E631d325bF5C8A08`
