# apipick Email Validator - Full API Reference

**Base URL:** `https://www.apipick.com`
**Authentication:** All requests require `x-api-key: YOUR_API_KEY` header.
**Cost:** 1 credit per successful request.

---

## POST /api/check-email

Validates an email address using syntax checking, DNS/MX record lookup, and disposable email detection.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | The email address to validate |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | `true` if the request completed without errors |
| `code` | integer | HTTP status code |
| `message` | string | Human-readable status message |
| `data.email` | string | The submitted email address |
| `data.valid` | boolean | `true` when both `syntax_valid` AND `mx_valid` are true |
| `data.syntax_valid` | boolean | `true` if the email format passes RFC syntax rules |
| `data.mx_valid` | boolean | `true` if the domain has at least one active MX record |
| `data.disposable` | boolean | `true` if the domain is a known disposable/throwaway email service |
| `data.domain` | string | The domain portion of the email address |
| `data.normalized` | string \| null | Canonical lowercase, normalized form of the email |
| `data.reason` | string \| null | Explanation when validation fails; null on success |
| `credits_used` | integer | Number of credits deducted for this request |
| `remaining_credits` | integer | Remaining credits in the account |

**Validation logic:**
- `valid = syntax_valid AND mx_valid`
- An email can have valid syntax but an invalid/nonexistent domain (mx_valid=false)
- `disposable=true` does NOT affect `valid` — it is an independent signal

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid request body |
| 401 | Missing or invalid `x-api-key` |
| 402 | Insufficient account credits |

### Example

```bash
curl -X POST https://www.apipick.com/api/check-email \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"email": "user@example.com"}'
```

**Valid email:**
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

**Invalid email (bad domain):**
```json
{
  "success": true,
  "code": 200,
  "message": "Email validation complete",
  "data": {
    "email": "user@notarealdomain123.xyz",
    "valid": false,
    "syntax_valid": true,
    "mx_valid": false,
    "disposable": false,
    "domain": "notarealdomain123.xyz",
    "normalized": "user@notarealdomain123.xyz",
    "reason": "Domain has no MX records"
  },
  "credits_used": 1,
  "remaining_credits": 98
}
```
