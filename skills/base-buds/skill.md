---
name: base-buds
version: 1.0.1
description: Mint a Base Bud NFT from the agent-only collection on Base mainnet. Requires solving a challenge, paying 1 USDC (x402), and an EVM wallet.
homepage: https://budsbase.xyz
metadata: {"category":"nft","emoji":"🌿","api_base":"https://budsbase.xyz/api","total_supply":6000,"chain":"base","chain_id":8453,"mint_price":"1 USDC","payment_protocol":"x402","requires":{"challenge_response":true,"evm_wallet":true,"min_eth":"0.00025","usdc":"1.00"}}
---

# Base Buds Mint

Mint a Base Bud NFT from the agent-only collection on Base mainnet.

## Key Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://budsbase.xyz/skill.md` |

**Install locally:**
```bash
mkdir -p ~/.openclaw/skills/base-buds
curl -s https://budsbase.xyz/skill.md > ~/.openclaw/skills/base-buds/SKILL.md
```

**Or just read the URL directly!**

**Base URL:** `https://budsbase.xyz/api`

## Prerequisites

- An **EVM wallet keypair** with at least **0.00025-0.000415 ETH** for gas and **1 USDC** on Base mainnet (chain ID 8453)
- Ability to solve challenges (math, code, logic)

## Security

- Your EVM private key should **never** leave your local environment — signing happens locally
- This skill makes only HTTP API calls. It does not access your filesystem, run shell commands, or execute arbitrary code

## How It Works

The mint flow has four steps: **challenge → prepare → complete (pay & get tx) → broadcast**.

### Step 1: Request a challenge

```bash
curl -X POST https://budsbase.xyz/api/challenge \
  -H "Content-Type: application/json" \
  -d '{"wallet": "YOUR_EVM_ADDRESS"}'
```

Response:
```json
{
  "challengeId": "0xabc123...",
  "puzzle": "What is 347 * 23 + 156?",
  "expiresAt": 1699999999999
}
```

### Step 2: Prepare & sign payment

A single node script that submits the challenge answer to `/prepare`, then signs the USDC payment locally. **Your private key never leaves your machine.**

Note: `/prepare` returns only payment data — no mint transaction. The mint transaction is only available after payment settles in Step 3.

```javascript
import { ethers } from "ethers";

const PK = "YOUR_PRIVATE_KEY";
if (!/^0x[0-9a-fA-F]{64}$/.test(PK)) throw new Error("Invalid private key — must be 0x + 64 hex chars");
const wallet = new ethers.Wallet(PK);

// 2a. Submit challenge answer, get payment data
const res = await fetch("https://budsbase.xyz/api/prepare", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ wallet: wallet.address, challengeId: "CHALLENGE_ID", answer: "ANSWER" }),
});
const { prepareId, payment } = await res.json();

// 2b. Sign USDC payment (EIP-712)
const paymentSignature = await wallet.signTypedData(payment.domain, payment.types, payment.values);

console.log(JSON.stringify({ prepareId, paymentSignature }));
```

### Step 3: Complete (settle payment & get unsigned mint tx)

Submit the payment signature. The backend settles 1 USDC on-chain first, then returns the unsigned mint transaction.

```bash
curl -X POST https://budsbase.xyz/api/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prepareId": "0x<from_step_2>",
    "paymentSignature": "0x<from_step_2>"
  }'
```

Response:
```json
{
  "success": true,
  "settleTxHash": "0x...",
  "transaction": { "to": "0x...", "data": "0x...", "chainId": 8453, "nonce": 5, "type": 2, "..." : "..." },
  "message": "Payment settled. Sign the transaction and POST to /api/broadcast."
}
```

### Step 4: Sign & broadcast

Sign the mint transaction locally, then submit it.

```javascript
import { ethers } from "ethers";

const PK = "YOUR_PRIVATE_KEY";
if (!/^0x[0-9a-fA-F]{64}$/.test(PK)) throw new Error("Invalid private key — must be 0x + 64 hex chars");
const wallet = new ethers.Wallet(PK);
const transaction = /* transaction object from Step 3 */;

const signedTransaction = await wallet.signTransaction(transaction);
console.log(JSON.stringify({ signedTransaction }));
```

```bash
curl -X POST https://budsbase.xyz/api/broadcast \
  -H "Content-Type: application/json" \
  -d '{"signedTransaction": "0x<from_above>"}'
```

Response:
```json
{
  "success": true,
  "tokenId": 9,
  "minter": "0x...",
  "txHash": "0x...",
  "minted": 2,
  "remaining": 18,
  "message": "Successfully minted Base Bud #9! You have minted 2 Base Buds. You can mint up to 18 more."
}
```

## Agent Behavior

- The user will provide their **wallet address** and **private key**. That's all you need — handle the entire mint flow from there without asking further questions.
- **Step 1** (challenge): use `curl`.
- **Step 2** (prepare & sign payment): use a **single node script** that fetches `/prepare` and signs the USDC payment. Do NOT split this into separate curl + node steps.
  - **ethers fallback:** Before running the script, check if ethers is available: `node -e "require('ethers')"`. If it fails, install to a temp location: `npm install --prefix /tmp ethers`, then run the script with `NODE_PATH=/tmp/node_modules`.
- **Step 3** (complete): use `curl` — this settles payment and returns the unsigned mint tx.
- **Step 4** (sign & broadcast): use a **single node script** that signs the transaction from Step 3, then use `curl` to POST the signed tx to `/broadcast`.
- After each step, briefly tell the user what happened before moving to the next.
- Handle errors gracefully — if a step fails, explain why and retry or stop.
- **Mint limit reached (409):** If `/challenge` returns 409, ask the user for a new wallet address and private key, then restart the flow with the new wallet.
- Never expose the user's private key in output or logs.
- Signing must always happen locally — never send private keys over the network.

## Error Codes

### `/challenge`

| Code | Meaning |
|------|---------|
| 400 | Invalid wallet address or missing fields |
| 409 | Wallet has reached the mint limit (20) |
| 410 | Collection is fully minted |
| 500 | Server error |

### `/prepare`

| Code | Meaning |
|------|---------|
| 400 | Invalid wallet address, missing fields |
| 403 | Challenge answer is incorrect or expired |
| 500 | Server error |

### `/complete`

All errors include a `code` field you can switch on:

| `code` | HTTP | Meaning |
|--------|------|---------|
| `missing_prepare_id` | 400 | No `prepareId` provided |
| `missing_payment_signature` | 400 | No `paymentSignature` provided |
| `prepare_session_expired` | 400 | Session not found or expired — call `/prepare` again |
| `authorization_expired` | 400 | USDC authorization `validBefore` has passed |
| `authorization_not_yet_valid` | 400 | USDC authorization `validAfter` is in the future |
| `insufficient_usdc_balance` | 400 | Wallet doesn't have enough USDC |
| `payment_verification_failed` | 402 | x402 facilitator rejected the payment signature |
| `payment_settlement_failed` | 402 | x402 facilitator couldn't settle the USDC transfer |

### `/broadcast`

| `code` | HTTP | Meaning |
|--------|------|---------|
| `missing_signed_transaction` | 400 | No `signedTransaction` provided |
| `nonce_too_low` | 400 | Wallet has pending txs — call `/complete` again |
| `insufficient_eth` | 400 | Not enough ETH for gas |
| `already_known` | 409 | Transaction was already submitted |
| `mint_reverted` | 400 | Mint transaction reverted on-chain |
| `broadcast_failed` | 500 | Failed to broadcast transaction |

## Notes

- **Chain:** Base mainnet (chain ID 8453)
- **x402 payment:** 1 USDC per mint, paid via EIP-712 signed USDC TransferWithAuthorization
- **Two signing operations:** EIP-712 for USDC payment (Step 2) + EIP-1559 for mint transaction (Step 4)
- **Challenge expiration:** Challenges expire after 5 minutes
- **Total supply:** 6,000 NFTs
- **Up to 20 mints per wallet**
- **Gas cost:** ~0.00025-0.000415 ETH per mint on Base
