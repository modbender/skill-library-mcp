# Error Reference

All DECK-0 Agent API errors follow a standard response envelope.

## Response Format

### Success

```json
{
  "success": true,
  "data": { ... },
  "share": {
    "url": "https://app.deck-0.com/collection/0x...",
    "imageUrl": "https://..."
  }
}
```

The `share` field is optional and contains a shareable URL and optional image for the resource.

### Error

```json
{
  "success": false,
  "error": {
    "code": "AGENT_VALIDATION_ERROR",
    "message": "Invalid album address",
    "details": { ... }
  }
}
```

The `details` field is optional and provides additional context (e.g., validation field errors).

## Error Codes

### Authentication Errors (401)

| Code | Message | Cause |
|------|---------|-------|
| `AGENT_AUTH_MISSING_HEADER` | Missing one or more required headers | One or more `X-Agent-*` headers are absent or empty |
| `AGENT_AUTH_INVALID_CHAIN` | Missing required header: X-Agent-Chain-Id / Invalid chain ID format / Unsupported authentication chain | `X-Agent-Chain-Id` is missing, malformed, or not supported by DECK-0 |
| `AGENT_AUTH_INVALID_WALLET` | Invalid wallet address | `X-Agent-Wallet-Address` is not a valid EVM address |
| `AGENT_AUTH_INVALID_TIMESTAMP` | Invalid timestamp format / Timestamp outside allowed window | `X-Agent-Timestamp` is not a number or is more than 5 minutes from server time |
| `AGENT_AUTH_INVALID_NONCE` | Invalid nonce length | `X-Agent-Nonce` is shorter than 8 or longer than 128 characters |
| `AGENT_AUTH_INVALID_SIGNATURE` | Invalid signature format / Signature does not match wallet | `X-Agent-Signature` is malformed or the recovered address doesn't match the wallet header |
| `AGENT_AUTH_REPLAY_DETECTED` | Replay detected | The nonce has already been used within the 5-minute TTL window |

### Forbidden Errors (403)

| Code | Message | Cause |
|------|---------|-------|
| `AGENT_FORBIDDEN` | User address does not match pack opener | Pack-opening recap (`GET /api/agents/v1/me/pack-opening/{hash}`) is only for the wallet that opened the packs; see [endpoints.md](./endpoints.md) for the pack-opening endpoint. |

### Rate Limiting Errors (429)

| Code | Message | Cause |
|------|---------|-------|
| `AGENT_RATE_LIMITED_WALLET` | Rate limit exceeded | Wallet exceeded 60 requests per minute |
| `AGENT_RATE_LIMITED_IP` | Rate limit exceeded | IP address exceeded 120 requests per minute |

### Validation Errors (400)

| Code | Message | Cause |
|------|---------|-------|
| `AGENT_VALIDATION_ERROR` | Invalid album address | Path parameter (collection contract address) is not a valid EVM address |
| `AGENT_VALIDATION_ERROR` | Invalid JSON body | POST body could not be parsed as JSON |
| `AGENT_VALIDATION_ERROR` | Validation failed | Request body failed Zod schema validation (see `details.errors`) |
| `AGENT_VALIDATION_ERROR` | Application already submitted and pending review | Publisher application is already pending |
| `AGENT_VALIDATION_ERROR` | Application already approved | Publisher application was already approved |

### Not Found Errors (404)

| Code | Message | Cause |
|------|---------|-------|
| `AGENT_NOT_FOUND` | Collection not found | No collection exists at the given contract address |
| `AGENT_NOT_FOUND` | Album not found for this wallet and collection address | Wallet has no data for the specified collection |
| `AGENT_NOT_FOUND` | No application found | No publisher application exists for this wallet |

For `GET /api/agents/v1/me/pack-opening/{hash}`: `AGENT_NOT_FOUND` can indicate transaction not found, collection not found, packs not found, cards not found, or wallet not registered. See [endpoints.md](./endpoints.md) for the full list of 404 cases for that endpoint.

### Service Errors (503)

| Code | Message | Cause |
|------|---------|-------|
| `AGENT_SERVICE_UNAVAILABLE` | Shop is in maintenance, please try again later | The shop is in maintenance mode |

### Internal Errors (500)

| Code | Message | Cause |
|------|---------|-------|
| `AGENT_INTERNAL_ERROR` | Failed to fetch shop albums | Server error fetching shop data |
| `AGENT_INTERNAL_ERROR` | Failed to fetch collection | Server error fetching collection details |
| `AGENT_INTERNAL_ERROR` | Failed to fetch collection leaderboard | Server error fetching leaderboard |
| `AGENT_INTERNAL_ERROR` | Failed to get collection price | Server error getting signed price |
| `AGENT_INTERNAL_ERROR` | Failed to fetch wallet albums | Server error fetching user's albums |
| `AGENT_INTERNAL_ERROR` | Failed to fetch wallet album | Server error fetching user's specific album |
| `AGENT_INTERNAL_ERROR` | Failed to submit application | Server error submitting publisher application |
| `AGENT_INTERNAL_ERROR` | Failed to fetch application | Server error fetching publisher application |
| `AGENT_INTERNAL_ERROR` | Internal server error | Unhandled exception in middleware |

## Rate Limiting

### Limits

| Scope | Limit | Window |
|-------|-------|--------|
| Per wallet address | 60 requests | 1 minute |
| Per IP address | 120 requests | 1 minute |

Wallet-level limits are checked first. If both are exceeded, the wallet scope takes precedence in the error response.

### Response Headers (on 429)

| Header | Description | Example |
|--------|-------------|---------|
| `Retry-After` | Seconds to wait before retrying | `15` |
| `X-RateLimit-Limit` | Maximum requests allowed in the window | `60` |
| `X-RateLimit-Remaining` | Requests remaining in the current window | `0` |
| `X-RateLimit-Reset` | Unix timestamp when the window resets | `1706200000` |
| `X-RateLimit-Scope` | Which limit was hit: `wallet` or `ip` | `wallet` |

### Handling Rate Limits

The `X-Agent-*` headers in the example below should be produced via the same auth flow as in [auth.md](./auth.md) (e.g. `sign_request` and the authenticated request helpers).

```bash
HTTP_CODE=$(curl -s -o /tmp/response.json -w "%{http_code}" "$url" \
  -H "X-Agent-Wallet-Address: $HEADER_WALLET" \
  -H "X-Agent-Chain-Id: $HEADER_CHAIN_ID" \
  -H "X-Agent-Timestamp: $HEADER_TIMESTAMP" \
  -H "X-Agent-Nonce: $HEADER_NONCE" \
  -H "X-Agent-Signature: $HEADER_SIGNATURE" \
  -D /tmp/response_headers.txt)

if [ "$HTTP_CODE" = "429" ]; then
  RETRY_AFTER=$(grep -i "Retry-After:" /tmp/response_headers.txt | tr -d '\r' | awk '{print $2}')
  RETRY_AFTER="${RETRY_AFTER:-60}"
  SCOPE=$(grep -i "X-RateLimit-Scope:" /tmp/response_headers.txt | tr -d '\r' | awk '{print $2}')
  echo "Rate limited (${SCOPE}). Retrying in ${RETRY_AFTER}s..."
  sleep "$RETRY_AFTER"
  # Retry the request
fi
```

## Troubleshooting

### "Missing one or more required headers"

Ensure required headers are present and non-empty:

- `X-Agent-Wallet-Address`
- `X-Agent-Chain-Id`
- `X-Agent-Timestamp`
- `X-Agent-Nonce`
- `X-Agent-Signature`

### "Timestamp outside allowed window"

Your system clock may be out of sync. The timestamp must be within 5 minutes of the server's time. Use current time in milliseconds (e.g., `$(date +%s)000` in shell).

### "Signature does not match wallet"

Common causes:

1. **Wrong payload format** — ensure the canonical payload matches exactly (field order, newline separators, no trailing newline)
2. **Wrong signing method** — must use EIP-191 `personal_sign` (not EIP-712 typed data)
3. **Wallet mismatch** — the signing key must correspond to the `X-Agent-Wallet-Address`
4. **Body hash mismatch** — for POST requests, the SHA-256 must be computed on the raw body bytes, not a re-serialized version

### "Replay detected"

Each nonce can only be used once within 5 minutes. Generate a fresh random nonce for every request. Do not retry failed requests with the same nonce.

### "Invalid album address" / invalid collection address

Collection (album) contract addresses must be valid 42-character hex strings starting with `0x`. The API normalizes addresses to lowercase.

### Smart Contract Transaction Errors

- **Insufficient balance** — wallet needs enough native tokens (APE/ETH) to cover `(packPrice * priceInNative * quantity) / 100` plus gas
- **Price expired** — the signed price expires after 2 minutes; fetch a new one
- **Pack not owned** — `openPacks` requires the caller to own the pack token IDs
- **Already opened** — packs can only be opened once
