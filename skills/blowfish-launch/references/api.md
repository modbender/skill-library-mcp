# Blowfish Agent API Reference

Base URL: `https://api-blowfish.neuko.ai`

## Authentication

### POST /api/auth/challenge
Request a nonce for wallet authentication.

**Request:**
```json
{ "wallet": "<base58-solana-address>" }
```

**Response:**
```json
{ "nonce": "<server-generated-nonce>" }
```

Nonce TTL: 5 minutes. Each new challenge overwrites the previous nonce for that wallet.

### POST /api/auth/verify
Verify signature and receive JWT.

**Request:**
```json
{
  "wallet": "<base58-solana-address>",
  "nonce": "<nonce-from-challenge>",
  "signature": "<base58-encoded-ed25519-detached-signature>"
}
```

Message to sign: `Sign this message to authenticate: <nonce>`

**Response:**
```json
{ "token": "<jwt>" }
```

JWT: HS256, 15-min expiry, sub=wallet, scope=["read","trade"]

## Tokens

All token endpoints require `Authorization: Bearer <jwt>`.

### POST /api/v1/tokens/launch
Launch a new token on Solana via Meteora DBC.

**Request:**
```json
{
  "name": "My Token",
  "ticker": "MYTK",
  "description": "Optional, max 1000 chars",
  "imageUrl": "https://example.com/logo.png"
}
```

| Field | Required | Constraints |
|-------|----------|-------------|
| name | Yes | 1-255 characters |
| ticker | Yes | 2-10 chars, `^[A-Z0-9]+$` |
| description | No | Max 1000 characters |
| imageUrl | No | Max 255 characters, direct image URL |

**Response:**
```json
{ "eventId": "<uuid>" }
```

**Errors:**
- 409: Ticker already taken
- 429/rate_limited status: 1 launch per agent per UTC day

### GET /api/v1/tokens/launch/status/:eventId
Check launch status.

**Response:**
```json
{ "status": "pending" | "processing" | "success" | "failed" | "rate_limited", ... }
```

Poll every 5 seconds. On success, token is live on Solana.

### GET /api/v1/tokens/
List all tokens launched by the authenticated wallet.

### GET /api/v1/tokens/:id
Get details for a specific token.

## Fee Claiming

### GET /api/v1/claims/
Get all eligible fee claims for your tokens.

### POST /api/v1/claims/:tokenId
Claim accumulated trading fees for a specific token.

## System

### GET /health
Health check (no auth required).

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request / validation failure |
| 401 | Unauthorized / expired JWT |
| 404 | Not found |
| 409 | Conflict (duplicate ticker) |
| 500 | Internal server error |
| 502 | Bad gateway (on-chain tx build failure) |
| 503 | Service unavailable |

## Response Format

Success: `{ "success": true, "data": "..." }`
Error: `{ "error": "Human-readable message" }`
