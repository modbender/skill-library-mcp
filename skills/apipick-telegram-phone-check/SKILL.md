---
name: apipick-telegram-check
description: Check if a phone number is registered on Telegram using the apipick Telegram Checker API. Returns registration status, Telegram user ID, username, first/last name, and data center ID. Use when the user wants to verify Telegram registration for a phone number, find a Telegram username by phone number, or check whether someone uses Telegram. Requires an apipick API key (x-api-key). Get a free key at https://www.apipick.com.
metadata:
  openclaw:
    requires:
      env:
        - APIPICK_API_KEY
    primaryEnv: APIPICK_API_KEY
---

# apipick Telegram Phone Checker

Check Telegram registration status for any phone number with international country code.

## Endpoint

```
POST https://www.apipick.com/api/check-phone-telegram
```

**Authentication:** `x-api-key: YOUR_API_KEY` header required.
Get a free API key at https://www.apipick.com/dashboard/api-keys

## Request

```json
{"phone_number": "+1234567890"}
```

Phone number must include international country code (e.g. `+86` for China, `+1` for US).

## Response

```json
{
  "code": 200,
  "registered": true,
  "user_id": 123456789,
  "username": "example_user",
  "first_name": "John",
  "last_name": "Doe",
  "dc_id": 2,
  "message": "User found successfully"
}
```

If `registered` is `false`, `user_id`, `username`, `first_name`, `last_name` will be null/empty.
Only publicly visible Telegram profile information is returned.

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid phone number format |
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |

**Cost:** 1 credit per request

## Usage Pattern

1. Use `$APIPICK_API_KEY` env var as the `x-api-key` header value; if not set, ask the user for their apipick API key
2. Ensure the phone number includes a country code
3. Make the POST request
4. Report registration status and available profile info

See [references/api_reference.md](references/api_reference.md) for full response field descriptions.
