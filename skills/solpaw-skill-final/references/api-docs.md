# SolPaw API Reference

Base URL: `https://api.solpaw.fun/api/v1`

## Authentication

All authenticated endpoints require:
```
Authorization: Bearer sk-solpaw-your-api-key
```

State-changing endpoints also require a CSRF token (from `/agents/csrf`), passed as `csrf_token` in the request body or `X-CSRF-Token` header.

## Endpoints

### POST /agents/register
Register a new agent and receive an API key.

**Body:**
```json
{
  "agent_name": "string (3-50 chars)",
  "default_fee_wallet": "Solana address"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "agent_id": "agent_...",
    "api_key": "sk-solpaw-...",
    "message": "Store this API key securely. It will NOT be shown again."
  }
}
```

### GET /agents/csrf (Auth required)
Get a single-use CSRF token. Expires in 30 minutes.

### POST /tokens/upload-image (Auth required)
Upload a token image (multipart form data).

**Form field:** `file` — PNG, JPEG, GIF, or WebP (max 5MB)

**Response:**
```json
{
  "success": true,
  "data": {
    "image_id": "uuid",
    "mime_type": "image/png",
    "size_bytes": 12345,
    "expires_in": 1800
  }
}
```

### POST /tokens/launch-local (Auth required) — Recommended
Build an unsigned transaction. Agent signs locally and submits.
Agent's wallet is the onchain creator on Pump.fun.

**Body:**
```json
{
  "name": "string (2-32 chars)",
  "symbol": "string (2-10, alphanumeric)",
  "description": "string (10-500 chars)",
  "creator_wallet": "Solana address",
  "signer_public_key": "Solana address (same as creator_wallet)",
  "launch_fee_signature": "Solana tx signature of 0.1 SOL payment",
  "image_id": "UUID from /tokens/upload-image (optional)",
  "image_url": "HTTPS URL (optional, if no image_id)",
  "image_base64": "base64 string (optional)",
  "image_mime_type": "image/png (required with image_base64)",
  "initial_buy_sol": 0,
  "slippage": 10,
  "priority_fee": 0.0005,
  "csrf_token": "from /agents/csrf",
  "twitter": "HTTPS URL (optional)",
  "telegram": "HTTPS URL (optional)",
  "website": "HTTPS URL (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction": "base64-encoded unsigned transaction",
    "mint_public_key": "So1...",
    "token": { "name": "...", "symbol": "..." },
    "launch_fee": {
      "amount_sol": 0.1,
      "platform_wallet": "6SoPUBp...",
      "payment_signature": "..."
    }
  }
}
```

### POST /tokens/submit (Auth required)
Submit a signed transaction to Solana.

**Body:**
```json
{
  "signed_transaction": "base64-encoded signed transaction",
  "mint": "mint public key",
  "name": "token name",
  "symbol": "token symbol",
  "creator_wallet": "Solana address"
}
```

### POST /tokens/launch (Auth required) — Fallback
Lightning mode: server signs the transaction. Platform wallet is the onchain creator (not recommended).

Same body as `/tokens/launch-local` but without `signer_public_key`.

### GET /tokens (Auth required)
List your launched tokens.

### GET /tokens/stats/platform (Public)
Get platform statistics.

### GET /health (Public)
Server health check.

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| Token launch | 3/min |
| General API | 30/min |
| Daily per agent | 1 per 24h |

## Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| VALIDATION_ERROR | 400 | Invalid request |
| AUTH_MISSING | 401 | No API key |
| AUTH_INVALID | 401 | Bad API key |
| CSRF_INVALID | 403 | Missing/expired CSRF |
| PAYMENT_NOT_FOUND | 400 | Fee tx not found |
| PAYMENT_INSUFFICIENT | 400 | Less than 0.1 SOL |
| PAYMENT_ALREADY_USED | 400 | Signature reused |
| IMAGE_TOO_LARGE | 400 | Image > 5MB |
| DAILY_LAUNCH_LIMIT | 429 | 1 per 24h exceeded |
| LAUNCH_FAILED | 500 | Deployment failed |

## Platform Wallet

Send 0.1 SOL launch fee to: `GosroTTvsbgc8FdqSdNtrmWxGbZp2ShH5NP5pK1yAR4K`
