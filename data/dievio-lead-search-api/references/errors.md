# Dievio API Errors

Common status codes:

- `401`: Missing or invalid API key/credentials
- `402`: Not enough credits
- `502`: Upstream lead/linkedin service error
- `500`: Internal server error

## Handling Strategy

1. Parse status code and error body.
2. Do not retry `401` or `402` until credentials/credits are fixed.
3. Retry transient failures (`502`, occasional `500`) with bounded backoff.
4. Log request summary and response body (without secrets).

## Credit-Aware Behavior

- 1 result = 1 credit.
- Returned rows can be lower than requested page size when credits are low.
- Always trust actual `count` and response arrays over requested limits.
