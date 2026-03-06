---
name: apipick-china-phone
description: Validate Chinese mobile phone numbers using the apipick China Phone Checker API. Returns carrier (China Mobile/Telecom/Unicom), province, city, zip code, and area code. Use when the user wants to verify a Chinese phone number, look up carrier information for a Chinese mobile number, or get geographic information associated with a Chinese phone number. Requires an apipick API key (x-api-key). Get a free key at https://www.apipick.com.
metadata:
  openclaw:
    requires:
      env:
        - APIPICK_API_KEY
    primaryEnv: APIPICK_API_KEY
---

# apipick China Phone Checker

Validate Chinese mobile numbers and retrieve carrier and geographic data.

## Endpoint

```
POST https://www.apipick.com/api/check-china-phone
```

**Authentication:** `x-api-key: YOUR_API_KEY` header required.
Get a free API key at https://www.apipick.com/dashboard/api-keys

## Request

```json
{"phone_number": "13800138000"}
```

Supported formats: `13800138000` / `+8613800138000` / `008613800138000`

## Response

```json
{
  "success": true,
  "data": {
    "phone": "13800138000",
    "phone_type": "China Mobile",
    "province": "Beijing",
    "city": "Beijing",
    "zip_code": "100000",
    "area_code": "010"
  }
}
```

`phone_type` values: `China Mobile`, `China Telecom`, `China Unicom`

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid phone number format |
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |
| 500 | Server error |

**Cost:** 1 credit per request

## Usage Pattern

1. Use `$APIPICK_API_KEY` env var as the `x-api-key` header value; if not set, ask the user for their apipick API key
2. Make the POST request with the phone number
3. Present carrier and geographic results clearly

See [references/api_reference.md](references/api_reference.md) for full response field descriptions.
