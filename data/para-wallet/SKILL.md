---
name: para-wallet
description: Create blockchain wallets and sign transactions using Para's MPC infrastructure where the private key never exists in a single place. Supports EVM and Solana chains via three REST endpoints.
metadata:
  author: para
  version: "1.0"
  openclaw.requires.env: ["PARA_API_KEY"]
---

## Overview

Para provides MPC (Multi-Party Computation) wallets where the private key is split into shares and **never assembled in a single place**. This makes Para ideal for AI agents that need to create wallets and sign transactions without ever holding a full private key.

All operations use Para's REST API with a single API key for authentication.

- **Base URL (Beta):** `https://api.beta.getpara.com`
- **Base URL (Production):** `https://api.getpara.com`
- **Auth:** Pass your API key in the `X-API-Key` header on every request
- **Content-Type:** `application/json`
- **Request tracing:** Optionally pass `X-Request-Id` (UUID) for tracing; Para generates one if omitted

## Setup

1. Get an API key from [developer.getpara.com](https://developer.getpara.com)
2. Set the environment variable:
   ```
   export PARA_API_KEY="your-secret-api-key"
   ```
3. Use the **Beta** base URL (`https://api.beta.getpara.com`) during development. Switch to Production for mainnet.

## Create a Wallet

**`POST /v1/wallets`**

Creates a new MPC wallet for a user. Each combination of `type` + `scheme` + `userIdentifier` produces exactly one wallet. Attempting to create a duplicate returns a `409` with the existing `walletId`.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | `EVM`, `SOLANA`, or `COSMOS` |
| `userIdentifier` | string | Yes | User identifier (email, phone, or custom ID) |
| `userIdentifierType` | string | Yes | `EMAIL`, `PHONE`, `CUSTOM_ID`, `GUEST_ID`, `TELEGRAM`, `DISCORD`, or `TWITTER` |
| `scheme` | string | No | Signature scheme: `DKLS`, `CGGMP`, or `ED25519` (defaults based on wallet type) |

### EVM Example

```bash
curl -X POST https://api.beta.getpara.com/v1/wallets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PARA_API_KEY" \
  -d '{
    "type": "EVM",
    "userIdentifier": "alice@example.com",
    "userIdentifierType": "EMAIL"
  }'
```

### Solana Example

```bash
curl -X POST https://api.beta.getpara.com/v1/wallets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PARA_API_KEY" \
  -d '{
    "type": "SOLANA",
    "userIdentifier": "alice@example.com",
    "userIdentifierType": "EMAIL"
  }'
```

### Response (201 Created)

The wallet starts in `creating` status. You must poll until it reaches `ready`.

```json
{
  "id": "0a1b2c3d-4e5f-6789-abcd-ef0123456789",
  "type": "EVM",
  "scheme": "DKLS",
  "status": "creating",
  "createdAt": "2024-01-15T09:30:00Z"
}
```

The response includes a `Location` header with the wallet's URL:
```
Location: /v1/wallets/0a1b2c3d-4e5f-6789-abcd-ef0123456789
```

### Polling for Ready Status

After creating a wallet, poll `GET /v1/wallets/{walletId}` until `status` becomes `ready`:

```bash
# Poll every 1 second until the wallet is ready
WALLET_ID="0a1b2c3d-4e5f-6789-abcd-ef0123456789"
while true; do
  RESPONSE=$(curl -s https://api.beta.getpara.com/v1/wallets/$WALLET_ID \
    -H "X-API-Key: $PARA_API_KEY")
  STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
  if [ "$STATUS" = "ready" ]; then
    echo "$RESPONSE"
    break
  fi
  sleep 1
done
```

## Get Wallet Status

**`GET /v1/wallets/{walletId}`**

Retrieves the current status and details of a wallet.

### Request

```bash
curl https://api.beta.getpara.com/v1/wallets/0a1b2c3d-4e5f-6789-abcd-ef0123456789 \
  -H "X-API-Key: $PARA_API_KEY"
```

### Response (200 OK)

When the wallet is ready, the response includes the address and public key:

```json
{
  "id": "0a1b2c3d-4e5f-6789-abcd-ef0123456789",
  "type": "EVM",
  "scheme": "DKLS",
  "status": "ready",
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f...",
  "publicKey": "04a1b2c3d4e5f6...",
  "createdAt": "2024-01-15T09:30:00Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique wallet identifier (UUID) |
| `type` | string | Blockchain network: `EVM`, `SOLANA`, or `COSMOS` |
| `scheme` | string | Signature scheme: `DKLS`, `CGGMP`, or `ED25519` |
| `status` | string | `creating` or `ready` |
| `address` | string | Wallet address (present when `status` is `ready`) |
| `publicKey` | string | Public key (present when `status` is `ready`) |
| `createdAt` | string | ISO 8601 creation timestamp |

## Sign Data

**`POST /v1/wallets/{walletId}/sign-raw`**

Signs arbitrary data using the wallet's MPC key shares. The private key is never assembled — each share signs independently and the results are combined.

**Important:** The wallet must be in `ready` status before signing.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | string | Yes | Data to sign as a `0x`-prefixed hex string |

### EVM Example

Sign a message hash (e.g., a keccak256 hash of a transaction):

```bash
curl -X POST https://api.beta.getpara.com/v1/wallets/0a1b2c3d-4e5f-6789-abcd-ef0123456789/sign-raw \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PARA_API_KEY" \
  -d '{
    "data": "0x48656c6c6f20576f726c64"
  }'
```

### Solana Example

Sign a serialized Solana transaction:

```bash
curl -X POST https://api.beta.getpara.com/v1/wallets/aabbccdd-1122-3344-5566-778899aabbcc/sign-raw \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PARA_API_KEY" \
  -d '{
    "data": "0x01000103b5d..."
  }'
```

### Response (200 OK)

```json
{
  "signature": "a1b2c3d4e5f6..."
}
```

The `signature` is a hex string **without** the `0x` prefix.

## Key Concepts

### Wallet Uniqueness

Each combination of `type` + `scheme` + `userIdentifier` maps to exactly one wallet. If you try to create a duplicate, the API returns `409 Conflict` with the existing wallet's ID in the response body. Use this to safely retry or look up existing wallets.

### Async Wallet Creation

Wallet creation is asynchronous. The `POST /v1/wallets` call returns immediately with `status: "creating"`. You must poll `GET /v1/wallets/{walletId}` until `status` becomes `"ready"` before you can use the wallet to sign.

### MPC Security Model

Para uses Multi-Party Computation so the full private key never exists on any single machine. Key shares are distributed across independent parties. When you call `sign-raw`, each party signs with their share and the results are combined into a valid signature. This means:

- No single point of compromise can leak the private key
- Agents can sign transactions without ever having access to a full key
- Signing is functionally equivalent to a normal signature from the blockchain's perspective

## Error Reference

All error responses include a `message` field describing the issue.

| Status | Message | Cause | Action |
|--------|---------|-------|--------|
| 400 | `"type must be one of EVM, SOLANA, COSMOS"` | Invalid or missing request body fields | Check required fields and enum values |
| 401 | `"secret api key not provided"` | Missing `X-API-Key` header | Add the `X-API-Key` header with your API key |
| 403 | `"invalid secret api key"` | API key is wrong or revoked | Verify your API key at developer.getpara.com |
| 404 | `"wallet not found"` | Wallet ID doesn't exist or doesn't belong to your account | Check the wallet ID |
| 409 | `"a wallet for this identifier and type already exists"` | Duplicate wallet creation attempted | Use the returned `walletId` to access the existing wallet |
| 500 | `"Internal Server Error"` | Server-side issue | Retry with exponential backoff |

### 409 Conflict Response

The `409` response includes the existing wallet's ID so you can retrieve it:

```json
{
  "message": "a wallet for this identifier and type already exists",
  "walletId": "0a1b2c3d-4e5f-6789-abcd-ef0123456789"
}
```

## Complete Example: Create Wallet and Sign

```bash
# 1. Create an EVM wallet
RESPONSE=$(curl -s -X POST https://api.beta.getpara.com/v1/wallets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PARA_API_KEY" \
  -d '{
    "type": "EVM",
    "userIdentifier": "agent-1@myapp.com",
    "userIdentifierType": "EMAIL"
  }')

WALLET_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
echo "Created wallet: $WALLET_ID"

# 2. Poll until ready
while true; do
  WALLET=$(curl -s https://api.beta.getpara.com/v1/wallets/$WALLET_ID \
    -H "X-API-Key: $PARA_API_KEY")
  STATUS=$(echo "$WALLET" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
  if [ "$STATUS" = "ready" ]; then
    echo "Wallet is ready"
    echo "$WALLET"
    break
  fi
  echo "Status: $STATUS — waiting..."
  sleep 1
done

# 3. Sign data
SIGNATURE=$(curl -s -X POST https://api.beta.getpara.com/v1/wallets/$WALLET_ID/sign-raw \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PARA_API_KEY" \
  -d '{"data": "0x48656c6c6f"}')

echo "Signature: $SIGNATURE"
```
