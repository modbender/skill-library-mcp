---
name: apipick-ip-geolocation
description: Look up geographic location and network information for any IPv4 or IPv6 address using the apipick IP Geolocation API. Returns country, continent, city, latitude/longitude, timezone, currency, ISP, and ASN. Use when the user wants to geolocate an IP address, find the country or city for an IP, identify the ISP or ASN of an IP, look up timezone or currency for an IP, or check their own public IP location. Omit the IP parameter to look up the caller's own IP. Requires an apipick API key (x-api-key). Get a free key at https://www.apipick.com.
metadata:
  openclaw:
    requires:
      env:
        - APIPICK_API_KEY
    primaryEnv: APIPICK_API_KEY
---

# apipick IP Geolocation

Look up location and network information for any public IPv4 or IPv6 address.

## Endpoint

```
GET https://www.apipick.com/api/ip-geolocation
```

**Authentication:** `x-api-key: YOUR_API_KEY` header required.
Get a free API key at https://www.apipick.com/dashboard/api-keys

## Request

```bash
# Look up a specific IP
GET /api/ip-geolocation?ip=8.8.8.8

# Look up caller's own IP (omit parameter)
GET /api/ip-geolocation
```

## Response

```json
{
  "success": true,
  "code": 200,
  "message": "ok",
  "data": {
    "ip": "8.8.8.8",
    "country_code": "US",
    "country_name": "United States",
    "continent": "North America",
    "continent_code": "NA",
    "city": "Mountain View",
    "latitude": 37.4056,
    "longitude": -122.0775,
    "timezone": "America/Los_Angeles",
    "currency": "USD",
    "isp": "Google LLC",
    "asn": 15169
  },
  "credits_used": 1,
  "remaining_credits": 99
}
```

`city`, `latitude`, `longitude` may be empty or null for some IPs.

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid or private/reserved IP address |
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |
| 404 | No geolocation data available for this IP |
| 503 | Geolocation database temporarily unavailable |

**Cost:** 1 credit per request

## Usage Pattern

1. Use `$APIPICK_API_KEY` env var as the `x-api-key` header value; if not set, ask the user for their apipick API key
2. Make the GET request (with or without `ip` query parameter)
3. Present location data in a readable format

See [references/api_reference.md](references/api_reference.md) for full response field descriptions.
