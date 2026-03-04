# apipick China Phone Checker - Full API Reference

**Base URL:** `https://www.apipick.com`
**Authentication:** All requests require `x-api-key: YOUR_API_KEY` header.
**Cost:** 1 credit per successful request.

---

## POST /api/check-china-phone

Validates a Chinese mobile phone number and returns carrier and geographic information.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phone_number` | string | Yes | Chinese phone number in any supported format |

**Supported formats:**
- 11-digit domestic: `13800138000`
- With +86 prefix: `+8613800138000`
- With 0086 prefix: `008613800138000`

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | `true` if the request succeeded |
| `code` | integer | HTTP status code |
| `message` | string | Human-readable status message |
| `data.phone` | string | The normalized phone number |
| `data.phone_type` | string | Carrier name: `China Mobile`, `China Telecom`, or `China Unicom` |
| `data.province` | string | Province associated with the number |
| `data.city` | string | City associated with the number |
| `data.zip_code` | string | Postal code for the area |
| `data.area_code` | string | Regional telephone area code prefix |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid phone number format |
| 401 | Missing or invalid `x-api-key` |
| 402 | Insufficient account credits |
| 500 | Internal server error |

### Example

```bash
curl -X POST https://www.apipick.com/api/check-china-phone \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"phone_number": "13800138000"}'
```

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
