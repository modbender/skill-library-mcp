# apipick Telegram Phone Checker - Full API Reference

**Base URL:** `https://www.apipick.com`
**Authentication:** All requests require `x-api-key: YOUR_API_KEY` header.
**Cost:** 1 credit per successful request.

---

## POST /api/check-phone-telegram

Checks whether a phone number is registered on Telegram and returns publicly available profile information.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phone_number` | string | Yes | Phone number in international format with country code |

**Supported formats:**
- With + prefix: `+1234567890` (recommended)
- With spaces: `+86 138 0013 8000`
- With 00 prefix: `001234567890`

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `code` | integer | HTTP status code |
| `registered` | boolean | `true` if the number is registered on Telegram |
| `user_id` | integer \| null | Telegram user identifier (null if not registered) |
| `username` | string \| null | Public @username if set and visible (null otherwise) |
| `first_name` | string \| null | User's first name if visible |
| `last_name` | string \| null | User's last name if visible |
| `dc_id` | integer \| null | Telegram data center ID |
| `message` | string | Response status message |

**Note:** Only publicly available Telegram profile information is returned. Private profiles may have null username/name fields even when registered.

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid phone number format (missing country code, etc.) |
| 401 | Missing or invalid `x-api-key` |
| 402 | Insufficient account credits |

### Example

```bash
curl -X POST https://www.apipick.com/api/check-phone-telegram \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"phone_number": "+1234567890"}'
```

**Registered user:**
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

**Not registered:**
```json
{
  "code": 200,
  "registered": false,
  "user_id": null,
  "username": null,
  "first_name": null,
  "last_name": null,
  "dc_id": null,
  "message": "Phone number not registered on Telegram"
}
```
