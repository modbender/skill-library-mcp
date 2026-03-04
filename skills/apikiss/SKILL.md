---
name: apikiss
description: Access weather, IP geolocation, SMS, crypto prices, Danish CVR, Whois, phone lookup, UUID, stock data, and more via the API KISS unified gateway (apikiss.com).
homepage: https://www.apikiss.com
metadata: {"openclaw": {"emoji": "💋", "requires": {"env": ["APIKISS_API_KEY"]}, "primaryEnv": "APIKISS_API_KEY"}}
---

# API KISS

Use the [API KISS](https://www.apikiss.com) unified gateway to call dozens of services through one consistent API with Bearer token auth.

## Setup

Set your API key as an environment variable:

```
APIKISS_API_KEY=your_token_here
```

All requests use:
- Base URL: `https://apikiss.com/v1/`
- Auth header: `Authorization: Bearer $APIKISS_API_KEY`

## Available Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/weather` | GET | Current weather + forecast by location |
| `/ip` | GET | IP geolocation, ISP, timezone, connection type |
| `/sms` | POST | Send SMS worldwide with delivery tracking |
| `/flash-sms` | POST | Send flash SMS (appears on screen instantly) |
| `/crypto` | GET | Real-time crypto prices (BTC, ETH, etc.) |
| `/cvr` | GET | Danish Business Registry lookup by name or CVR number |
| `/whois` | GET | Domain registration info (registrar, dates, nameservers) |
| `/phone-lookup` | GET | Validate phone numbers, carrier, type, country |
| `/uuid` | GET | Generate a cryptographically secure UUID v4 |
| `/stock` | GET | Real-time and historical stock market data |
| `/time` | GET | Accurate time + timezone for any location |
| `/password` | POST | Hash or verify a password securely |
| `/photo` | GET/POST | Image metadata extraction and format conversion |
| `/chuck-norris-facts` | GET | Random Chuck Norris fact |

## Usage Examples

### Weather
```sh
curl "https://apikiss.com/v1/weather?location=Copenhagen" \
  -H "Authorization: Bearer $APIKISS_API_KEY"
```

### IP Lookup
```sh
curl "https://apikiss.com/v1/ip?ip=8.8.8.8" \
  -H "Authorization: Bearer $APIKISS_API_KEY"
```

### Danish CVR Lookup
```sh
curl "https://apikiss.com/v1/cvr?query=Novo+Nordisk" \
  -H "Authorization: Bearer $APIKISS_API_KEY"
```

### Send SMS
```sh
curl -X POST "https://apikiss.com/v1/sms" \
  -H "Authorization: Bearer $APIKISS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"to": "+4512345678", "message": "Hello from OpenClaw!"}'
```

### Crypto Price
```sh
curl "https://apikiss.com/v1/crypto?symbol=BTC" \
  -H "Authorization: Bearer $APIKISS_API_KEY"
```

### UUID
```sh
curl "https://apikiss.com/v1/uuid" \
  -H "Authorization: Bearer $APIKISS_API_KEY"
```

## External Endpoints

All requests go to: `https://apikiss.com/v1/*`

Data sent includes only the query parameters you provide (e.g. location, IP, phone number, symbol). Your `APIKISS_API_KEY` is sent as a Bearer token in the Authorization header and never logged locally.

## Security & Privacy

- Your API key stays in your environment — never in prompts or logs.
- Only the data you explicitly pass as parameters leaves your machine.
- API KISS does not store request payloads.

## Trust Statement

By using this skill, queries are sent to `https://apikiss.com`. Only install if you trust apikiss.com with the data you pass to it.
