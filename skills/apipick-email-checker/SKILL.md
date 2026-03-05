---
name: apipick-email-validation
description: Validate email addresses using the apipick Email Validator API. Performs syntax checking, MX record verification, and disposable/throwaway email detection. Use when the user wants to verify an email address, check if an email domain exists and can receive mail, detect disposable or temporary emails, or validate email format. Requires an apipick API key (x-api-key). Get a free key at https://www.apipick.com.
metadata:
  openclaw:
    requires:
      env:
        - APIPICK_API_KEY
    primaryEnv: APIPICK_API_KEY
---

# apipick Email Validator

Validate email addresses with syntax check, MX record lookup, and disposable email detection.

## Endpoint

```
POST https://www.apipick.com/api/check-email
```

**Authentication:** `x-api-key: YOUR_API_KEY` header required.
Get a free API key at https://www.apipick.com/dashboard/api-keys

## Request

```json
{"email": "user@example.com"}
```

## Response

```json
{
  "success": true,
  "code": 200,
  "message": "Email validation complete",
  "data": {
    "email": "user@example.com",
    "valid": true,
    "syntax_valid": true,
    "mx_valid": true,
    "disposable": false,
    "domain": "example.com",
    "normalized": "user@example.com",
    "reason": null
  },
  "credits_used": 1,
  "remaining_credits": 99
}
```

**Key fields:**
- `valid`: `true` only when both `syntax_valid` AND `mx_valid` are true
- `disposable`: `true` if the domain is a known throwaway email service
- `reason`: explanation when validation fails (null on success)
- `normalized`: canonical lowercase form of the email

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid request |
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |

**Cost:** 1 credit per request

## Usage Pattern

1. Use `$APIPICK_API_KEY` env var as the `x-api-key` header value; if not set, ask the user for their apipick API key
2. Make the POST request with the email address
3. Report the `valid` status and flag if `disposable` is true
4. Show `reason` when validation fails

See [references/api_reference.md](references/api_reference.md) for full response field descriptions.
