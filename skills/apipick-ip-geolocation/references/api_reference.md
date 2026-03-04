# apipick IP Geolocation - Full API Reference

**Base URL:** `https://www.apipick.com`
**Authentication:** All requests require `x-api-key: YOUR_API_KEY` header.
**Cost:** 1 credit per successful request.

---

## GET /api/ip-geolocation

Returns geographic and network information for a public IPv4 or IPv6 address. Omit the `ip` parameter to look up the caller's own IP.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ip` | string | No | Public IPv4 or IPv6 address. Omit to look up caller's IP. |

**Note:** Private/reserved IP ranges (e.g. `192.168.x.x`, `10.x.x.x`, `127.x.x.x`) will return a 400 error.

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | `true` if the request succeeded |
| `code` | integer | HTTP status code |
| `message` | string | Status message |
| `data.ip` | string | The queried IP address |
| `data.country_code` | string | ISO 3166-1 alpha-2 country code (e.g. `US`, `DE`, `JP`) |
| `data.country_name` | string | Full English country name |
| `data.continent` | string | Continent name (e.g. `North America`, `Europe`) |
| `data.continent_code` | string | Two-letter continent code |
| `data.city` | string | City name (may be empty for some IPs) |
| `data.latitude` | number \| null | Approximate latitude coordinate |
| `data.longitude` | number \| null | Approximate longitude coordinate |
| `data.timezone` | string | IANA timezone identifier (e.g. `America/Los_Angeles`) |
| `data.currency` | string | ISO 4217 currency code for the country (e.g. `USD`, `EUR`) |
| `data.isp` | string | ISP or organization name from ASN database |
| `data.asn` | integer \| null | Autonomous System Number |
| `credits_used` | integer | Credits deducted for this request |
| `remaining_credits` | integer | Remaining credits in the account |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid IP address or private/reserved IP range |
| 401 | Missing or invalid `x-api-key` |
| 402 | Insufficient account credits |
| 404 | No geolocation data available for this IP |
| 503 | Geolocation database temporarily unavailable |

### Example

```bash
# Specific IP
curl "https://www.apipick.com/api/ip-geolocation?ip=8.8.8.8" \
  -H "x-api-key: YOUR_API_KEY"

# Caller's own IP
curl "https://www.apipick.com/api/ip-geolocation" \
  -H "x-api-key: YOUR_API_KEY"
```

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
