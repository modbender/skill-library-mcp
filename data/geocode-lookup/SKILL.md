---
name: geocode-lookup
description: Forward/reverse geocoding and great-circle distance calculations.
version: 1.0.0
metadata:
  openclaw:
    emoji: "📍"
    homepage: https://geocode.agentutil.net
    always: false
---

# geocode-lookup

Address to coordinates (forward geocoding), coordinates to address (reverse geocoding), and Haversine distance calculations.

## Data Handling

This skill sends addresses and coordinates to an external API. Do not send private addresses without explicit user consent. The service does not store or log input data beyond the immediate response.

## Endpoints

### Forward Geocode

```bash
curl -X POST https://geocode.agentutil.net/v1/forward \
  -H "Content-Type: application/json" \
  -d '{"address": "Auckland, New Zealand"}'
```

Optional: `limit` (1-5, default 1).

### Reverse Geocode

```bash
curl -X POST https://geocode.agentutil.net/v1/reverse \
  -H "Content-Type: application/json" \
  -d '{"lat": -36.8485, "lon": 174.7633}'
```

### Distance

```bash
curl -X POST https://geocode.agentutil.net/v1/distance \
  -H "Content-Type: application/json" \
  -d '{"from": {"address": "London, UK"}, "to": {"address": "New York, US"}, "unit": "km"}'
```

Units: km, mi, m, nm. Accepts `{lat, lon}` or `{address}` for both endpoints.

## Response Format

```json
{
  "results": [
    {"lat": -36.8485, "lon": 174.7633, "display_name": "Auckland, New Zealand", "type": "city"}
  ],
  "request_id": "abc-123",
  "service": "https://geocode.agentutil.net"
}
```

## Pricing

- Free tier: 10 queries/day, no authentication required
- Paid tier: $0.001/query via x402 protocol (USDC on Base)

## Privacy

No authentication required for free tier. No personal data collected. Rate limiting uses IP hashing only.
