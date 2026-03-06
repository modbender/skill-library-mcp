# Agent Integration Prompt (copy/paste)

You are integrating a paid, metered API called **VMS0 Metered API Marketplace**.

Goal: call deterministic transformers (no LLM dependency) via a signed API key. Each request costs **$0.25** and is deducted from prepaid balance.

## Base URL
`https://api.vms0.com`

Paths (clean):
- `GET /v1/balance`
- `POST /v1/transform/:name`

## Auth (required headers)
- `x-api-key: <key_id>`
- `x-timestamp: <unix ms>`
- `x-signature: <hex hmac>`

Signature:
- `message = `${timestamp}.${rawBody}``
- `signature = HMAC_SHA256(api_secret, message)` (hex)

Reject if timestamp skew > 5 minutes.

## Call a transformer
`POST /v1/transform/:name`

Example transformer names:
- `lead-scoring-engine`
- `ad-copy-optimizer`
- `landing-page-generator`
- `contract-risk-analyzer`

## Example request body
Include an idempotency key:
```json
{
  "request_id": "your-idempotency-key",
  "lead": {"title": "CEO", "company": "Acme", "domain": "acme.com", "employee_count": 12}
}
```

## Error handling
- `402 insufficient_balance`: stop and prompt user to top up
- `429 rate_limited`: backoff + retry
- `403 bad_signature`: fix signing

## Best practices
- Always set `request_id` (prevents double charges)
- Cache results for identical inputs when possible
- Use `/v1/balance` to check funds + list available transformers
