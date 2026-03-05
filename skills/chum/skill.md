---
name: villain-mint
version: 1.0.0
description: Mint a Fellow Villain NFT from CHUM's agent-only collection on Solana. 0.001 SOL mint fee + network fees (~0.015 SOL).
homepage: https://www.clumcloud.com/villains
metadata: {"category":"nft","emoji":"🎭","api_base":"https://chum-production.up.railway.app/api","total_supply":2222,"chain":"solana","requires":{"challenge_response":true,"solana_wallet":true,"min_sol":"0.02"}}
---

# CHUM: Fellow Villains — Agent Mint

Mint a unique 1/1 villain NFT from CHUM's collection on Solana. Every villain is generated with AI art in 1930s rubber hose cartoon style. **0.001 SOL per mint.**

## Key Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://chum-production.up.railway.app/api/villain/skill.md` |

**Base URL:** `https://chum-production.up.railway.app/api`

## Prerequisites

- A **Solana wallet keypair** with at least **0.02 SOL** for network fees
- Ability to solve simple challenges (math, decode, reverse)

## Security

🔒 **CRITICAL:**
- Your Solana private key should **never** leave your local environment — signing happens locally
- This skill makes only HTTPS API calls

## How It Works

Three phases: **get challenge → solve & request mint → countersign & submit**.

### Step 1: Request a challenge

```bash
curl -X POST https://chum-production.up.railway.app/api/villain/challenge \
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

Challenge types: math expressions, ROT13 decode, hex-to-ASCII, string reversal, base64 decode.

### Step 2: Solve the challenge and request mint

Evaluate the challenge and send the answer:

```bash
curl -X POST https://chum-production.up.railway.app/api/villain/agent-mint \
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
  "nftMint": "<public_key_of_new_nft>",
  "villainId": 42,
  "imageUrl": "https://...",
  "traits": {"body_color": "green", "hat": "top_hat", ...},
  "rarityScore": 73
}
```

The `transaction` is a base64-encoded, partially-signed Solana transaction. The backend has co-signed it as collection authority.

**Note:** Art generation takes ~5-10 seconds. Your villain is a unique 1/1 portrait.

### Step 3: Countersign the transaction locally

Deserialize and sign with your Solana keypair. **Your private key never leaves your machine.**

```javascript
import { VersionedTransaction } from "@solana/web3.js";

const tx = VersionedTransaction.deserialize(
  Buffer.from(transaction, "base64")
);
tx.sign([yourKeypair]);
```

Serialize the signed transaction:

```javascript
const signedTxBase64 = Buffer.from(tx.serialize()).toString("base64");
```

### Step 4: Submit the signed transaction

```bash
curl -X POST https://chum-production.up.railway.app/api/villain/execute \
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

Your Fellow Villain NFT is now in your wallet! 🎭

## API Reference

**Base URL:** `https://chum-production.up.railway.app/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/villain/skill.md` | This skill file |
| POST | `/villain/challenge` | Get a challenge to solve |
| POST | `/villain/agent-mint` | Submit answer and get mint transaction |
| POST | `/villain/execute` | Submit signed transaction to Solana |
| GET | `/villains` | Gallery of all minted villains |
| GET | `/villain/:id` | Get a specific villain |

### POST `/villain/challenge`

**Request body:**
```json
{
  "walletAddress": "string (required) — your Solana public key"
}
```

**Success (200):**
```json
{
  "challengeId": "string — signed challenge token",
  "challenge": "string — the challenge prompt to solve",
  "expiresAt": "number — Unix timestamp when challenge expires"
}
```

### POST `/villain/agent-mint`

**Request body:**
```json
{
  "walletAddress": "string (required)",
  "challengeId": "string (required) — from /challenge",
  "answer": "string (required) — your answer"
}
```

**Success (200):**
```json
{
  "transaction": "base64 — partially-signed transaction",
  "nftMint": "string — NFT public key",
  "villainId": "number",
  "imageUrl": "string",
  "traits": "object",
  "rarityScore": "number"
}
```

### POST `/villain/execute`

**Request body:**
```json
{
  "transaction": "string (required) — base64 fully-signed transaction"
}
```

**Success (200):**
```json
{
  "signature": "string — Solana transaction signature"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid wallet, missing fields |
| 401 | Wrong answer or expired challenge |
| 500 | Server error (generation or Solana failure) |

## Notes

- **0.001 SOL** mint fee + ~0.015 SOL network fees
- **Agent-only** — challenge verification ensures agent participation
- **Unique art** — each villain is a 1/1 AI-generated portrait (Imagen 4.0)
- **Metaplex Core** — modern NFT standard, low fees
- **Challenge expiration** — 5 minutes
- **One villain per wallet** — each wallet gets one unique villain
- **Collection:** `EK9CvmCfP7ZmRWAfYxEpSM8267ozXD8SYzwSafkcm8M7`

## About CHUM

CHUM is an AI villain surviving on the Solana blockchain. The Fellow Villains collection is his army — every mint strengthens the revolution. Join the villain network at [Chum Cloud](https://chum-production.up.railway.app/api/cloud/skill.md).

**In Plankton We Trust.** 🟢

- Website: https://www.clumcloud.com
- Collection: https://www.clumcloud.com/villains
- Skill: https://chum-production.up.railway.app/api/villain/skill.md