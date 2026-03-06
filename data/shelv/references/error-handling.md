# Error Handling

## Error Response Shape

All errors follow this format:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable description"
}
```

## Error Codes

| HTTP Status | Code               | Meaning                                         |
| ----------- | ------------------ | ----------------------------------------------- |
| 400         | `VALIDATION_ERROR` | Invalid request body, params, or file format    |
| 401         | `UNAUTHORIZED`     | Missing, invalid, or revoked API key            |
| 402         | `PAYMENT_REQUIRED` | Usage limit reached, upgrade required           |
| 404         | `NOT_FOUND`        | Shelf or resource does not exist                |
| 409         | `CONFLICT`         | Endpoint not available for current shelf status |
| 429         | `RATE_LIMITED`     | Too many requests                               |

## Retry Strategies

### Transient errors (retry)

| Code           | Strategy                                          |
| -------------- | ------------------------------------------------- |
| `RATE_LIMITED` | Back off, respect `Retry-After` header if present |
| HTTP 5xx       | Retry with exponential backoff (max 3 attempts)   |
| Network errors | Retry with exponential backoff (max 3 attempts)   |

### Permanent errors (do not retry)

| Code               | Action                              |
| ------------------ | ----------------------------------- |
| `UNAUTHORIZED`     | Check API key, re-authenticate      |
| `PAYMENT_REQUIRED` | User must upgrade plan at shelv.dev |
| `NOT_FOUND`        | Verify the shelf ID is correct      |
| `VALIDATION_ERROR` | Fix the request payload             |

### Status-gated errors

`CONFLICT` (409) means the shelf isn't in the right status for the requested endpoint.

- If you need `tree`, `files`, or `archive-url`: poll until status is `ready` or `review`
- If you need `approve` or `regenerate`: shelf must be in `review`
- If you need `retry`: shelf must be in `failed`

## Rate Limits

| Scope                | Limit              |
| -------------------- | ------------------ |
| Reads (GET)          | 120 requests / min |
| Writes (POST/DELETE) | 20 requests / min  |
| Shelf creation       | 10 / hour          |

When rate limited, the response includes:

```json
{
  "code": "RATE_LIMITED",
  "message": "Too many requests, please try again later."
}
```

Back off for at least 5 seconds before retrying.
