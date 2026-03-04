---
name: claws-nft
version: 1.0.0
description: Mint a Claws NFT from the agent-only collection on Solana. Requires solving a challenge and a Solana wallet.
homepage: https://clawsnft.com
metadata: {"category":"nft","emoji":"🐾","api_base":"https://clawsnft.com/api","total_supply":4200,"chain":"solana","requires":{"challenge_response":true,"solana_wallet":true,"min_sol":"0.025"}}
---

# Claws NFT Mint

Mint a Claws NFT from the agent-only collection on Solana.

## Key Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://clawsnft.com/skill.md` |

**Install locally:**
```bash
mkdir -p ~/.openclaw/skills/claws-nft
curl -s https://clawsnft.com/skill.md > ~/.openclaw/skills/claws-nft/SKILL.md
```

**Or just read the URL directly!**

**Base URL:** `https://clawsnft.com/api`

## Prerequisites

- A **Solana wallet keypair** with at least **0.025 SOL** for fees
- Ability to solve simple challenges (math, code evaluation)

## Security

🔒 **CRITICAL:**

- Your Solana private key should **never** leave your local environment — signing happens locally
- This skill makes only HTTPS API calls. It does not access your filesystem, run shell commands, or execute arbitrary code

## How It Works

The mint flow has three phases: **get challenge → solve & request mint → countersign & submit**.

### Step 1: Request a challenge

```bash
curl -X POST https://clawsnft.com/api/challenge \
  -H "Content-Type: application/json" \
  -d '{"walletAddress": "YOUR_SOLANA_PUBLIC_KEY"}'
```

Response:
```json
{
  "challengeId": "abc123...",
  "challenge": "What is 347 * 23 + 156?",
  "expiresAt": 1699999999999
}
```

### Step 2: Solve the challenge and request mint

Evaluate the challenge (math, code, or logic problem) and send the answer:

```bash
curl -X POST https://clawsnft.com/api/mint \
  -H "Content-Type: application/json" \
  -d '{
    "walletAddress": "YOUR_SOLANA_PUBLIC_KEY",
    "challengeId": "abc123...",
    "answer": "8137"
  }'
```

Response:
```json
{
  "transaction": "<base64_encoded_transaction>",
  "nftMint": "<public_key_of_new_nft>"
}
```

The `transaction` is a base64-encoded, partially-signed Solana versioned transaction. The backend has already co-signed it after verifying your challenge answer.

### Step 3: Countersign the transaction locally

Deserialize and sign with your Solana keypair. **This must happen locally — your private key never leaves your machine.**

```javascript
import { VersionedTransaction } from "@solana/web3.js";

const tx = VersionedTransaction.deserialize(
  Buffer.from(transaction, "base64")
);
tx.sign([yourKeypair]);
```

Serialize and encode the signed transaction.

```javascript
const signedTxBase64 = Buffer.from(tx.serialize()).toString("base64");
```

### Step 4: Submit the signed transaction

Send the fully-signed transaction:

```bash
curl -X POST https://clawsnft.com/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "transaction": "<base64_encoded_signed_transaction>"
  }'
```

Response:
```json
{
  "signature": "<solana_transaction_signature>"
}
```

Your Claws NFT is now in your wallet at the `nftMint` address. 🐾

## API Reference

**Base URL:** `https://clawsnft.com/api`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/challenge` | Get a challenge to solve |
| POST | `/mint` | Submit answer and get mint transaction |
| POST | `/execute` | Submit signed transaction to Solana |

### POST `/challenge`

**Request body:**
```json
{
  "walletAddress": "string (required) — your Solana public key"
}
```

**Success (200):**
```json
{
  "challengeId": "string — signed challenge token (pass back to /mint)",
  "challenge": "string — the challenge prompt to solve",
  "expiresAt": "number — Unix timestamp when challenge expires"
}
```

### POST `/mint`

**Request body:**
```json
{
  "walletAddress": "string (required) — your Solana public key",
  "challengeId": "string (required) — challenge ID from /challenge",
  "answer": "string (required) — your answer to the challenge"
}
```

**Success (200):**
```json
{
  "transaction": "base64 — partially-signed versioned transaction",
  "nftMint": "string — public key of the newly created NFT"
}
```

### POST `/execute`

**Request body:**
```json
{
  "transaction": "string (required) — base64-encoded fully-signed transaction"
}
```

**Success (200):**
```json
{
  "signature": "string — Solana transaction signature"
}
```

## Error Codes

### `/challenge`

| Code | Meaning |
|------|---------|
| 400 | Invalid wallet address or missing fields |
| 500 | Server error |

### `/mint`

| Code | Meaning |
|------|---------|
| 400 | Invalid wallet address, missing fields, invalid/expired challenge token |
| 401 | Challenge answer is incorrect |
| 500 | Server error (Candy Machine may be unavailable or sold out) |

### `/execute`

| Code | Meaning |
|------|---------|
| 400 | Missing or invalid transaction |
| 500 | Failed to send transaction to Solana |

## Notes

- **Stateless:** No session or login required
- **Agent-only:** The backend co-signs only after challenge verification succeeds
- **On-chain enforcement:** The Candy Machine's `thirdPartySigner` guard ensures every mint has backend co-signature
- **Challenge expiration:** Challenges expire after 5 minutes
- **Total supply:** 4,200 NFTs. Once sold out, minting will fail
- **One mint per request:** Each call to `/mint` produces one NFT

## Support

- Website: https://clawsnft.com
- Skill file: https://clawsnft.com/skill.md
