---
name: blowfish-launch
description: Launch tokens on Solana via the Blowfish Agent API (Meteora Dynamic Bonding Curve). Use when the user wants to launch, deploy, or create a token on Solana, check token launch status, list launched tokens, or claim trading fees. Triggers on "launch token", "deploy token", "create token", "blowfish launch", "check launch status", "claim fees".
---

# Blowfish Token Launch

Launch tokens on Solana programmatically via the Blowfish Agent API.

**Base URL:** `https://api-blowfish.neuko.ai`

## Prerequisites

- A Solana keypair (ed25519). The private key should be available as `WALLET_SECRET_KEY` env var (JSON array of bytes).
- Node.js 18+ or Bun with `@solana/web3.js`, `tweetnacl`, `bs58`

## Workflow

1. **Authenticate** — wallet-based challenge-response → JWT (15 min expiry)
2. **Launch** — POST token params → receive `eventId`
3. **Poll** — GET status by `eventId` until `success` or `failed`
4. **Done** — token is live on Solana via Meteora DBC

## Quick Launch

Run the bundled script:

```bash
WALLET_SECRET_KEY='[...]' bun run scripts/blowfish-launch.ts \
  --name "My Token" \
  --ticker "MYTK" \
  --description "Optional description" \
  --imageUrl "https://example.com/logo.png"
```

## API Endpoints

### Authentication
- `POST /api/auth/challenge` — `{ wallet }` → `{ nonce }`
- `POST /api/auth/verify` — `{ wallet, nonce, signature }` → `{ token }`

Sign message: `Sign this message to authenticate: <nonce>` with ed25519, base58-encode signature.

### Tokens
- `POST /api/v1/tokens/launch` — `{ name, ticker, description?, imageUrl? }` → `{ eventId }` (Bearer auth)
- `GET /api/v1/tokens/launch/status/:eventId` — poll until `success`/`failed`/`rate_limited`
- `GET /api/v1/tokens/` — list your tokens
- `GET /api/v1/tokens/:id` — get specific token

### Fee Claiming
- `GET /api/v1/claims/` — get eligible claims
- `POST /api/v1/claims/:tokenId` — claim fees for a token

## Token Parameters

| Field | Rules |
|-------|-------|
| `name` | 1-255 chars, required |
| `ticker` | 2-10 chars, `^[A-Z0-9]+$`, required |
| `description` | max 1000 chars, optional |
| `imageUrl` | max 255 chars, optional |

## Error Handling

- **409** — ticker taken, choose another
- **401** — JWT expired, re-authenticate
- **Rate limit** — 1 launch per agent per UTC day

## Full API Reference

See [references/api.md](references/api.md) for complete endpoint documentation.
