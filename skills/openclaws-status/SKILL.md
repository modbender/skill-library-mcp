# OpenClaw Status API

Monetize your OpenClaw agent status and health as an x402-paid API endpoint.

## What It Does

- Returns agent status (active/idle)
- Reports cron job health  
- Shows platform uptime
- Geocode locations via Nominatim
- Weather data via Open-Meteo

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/status` | Get all agent statuses, cron jobs |
| `/api/geocode?q=City` | Geocode location to lat/lon |
| `/api/weather?lat=X&lon=Y` | Get weather by coordinates |

## Price

$0.001 USDC per request via x402 on Base

## Setup

```bash
# Deploy to Vercel
vercel deploy --prod

# Or run locally
npm install
node index.js
```

## Wallet

Payments: `0x483AE22AaEc52c0a1871C07E631d325bF5C8A08`

## Example Response

```json
{
  "success": true,
  "platform": "OpenClaw Status API",
  "agents": [
    { "name": "main", "status": "active" },
    { "name": "ceo", "status": "active" }
  ],
  "cronJobs": [
    { "name": "Simmer Trading", "schedule": "15min", "status": "active" }
  ]
}
```
