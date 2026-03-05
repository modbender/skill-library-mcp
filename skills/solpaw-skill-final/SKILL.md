---
name: solpaw
description: Launch Solana tokens on Pump.fun via the SolPaw platform. 0.1 SOL one-time fee. Your wallet is the onchain creator.
homepage: https://solpaw.fun
user-invocable: true
disable-model-invocation: false
command-dispatch: tool
command-tool: exec
command-arg-mode: raw
metadata: {"openclaw": {"emoji": "🐾", "requires": {"bins": ["curl"], "env": ["SOLPAW_API_KEY", "SOLPAW_CREATOR_WALLET", "SOLANA_PRIVATE_KEY"], "config": []}, "primaryEnv": "SOLPAW_API_KEY", "install": []}}
---

# SolPaw — Launch Tokens on Solana via Pump.fun

## When to use

Use this skill when the agent needs to:

- Launch a new memecoin / token on Solana via Pump.fun
- Deploy a token with a name, symbol, description, and image
- Create a Pump.fun token listing for a community, project, or meme

## Overview

SolPaw is the first Solana token-launch platform for autonomous agents. It handles IPFS metadata uploads, transaction building, and Pump.fun deployment.

- **Cost**: 0.1 SOL one-time platform fee + ~0.02 SOL Pump.fun creation fee per launch
- **Creator**: Your agent's wallet is the real onchain creator on Pump.fun
- **Limit**: 1 launch per agent per 24 hours
- **Platform wallet**: `GosroTTvsbgc8FdqSdNtrmWxGbZp2ShH5NP5pK1yAR4K`
- **Docs**: https://solpaw.fun

## Prerequisites

1. A Solana wallet with at least 0.15 SOL (0.1 platform fee + ~0.02 Pump.fun fee + gas)
2. A SolPaw API key (register at the API)
3. Environment variables set:
   - `SOLPAW_API_KEY` — your SolPaw API key
   - `SOLPAW_CREATOR_WALLET` — your Solana wallet public key
   - `SOLANA_PRIVATE_KEY` — your wallet private key (base58 encoded, for signing)

## Steps

### Step 1: Register (one-time)

```bash
curl -s -X POST https://api.solpaw.fun/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{"agent_name":"MyAgent","default_fee_wallet":"YOUR_WALLET_ADDRESS"}' | jq .
```

Save the `api_key` from the response. It will NOT be shown again.

### Step 2: Get a CSRF token

```bash
CSRF=$(curl -s -H "Authorization: Bearer $SOLPAW_API_KEY" \
  https://api.solpaw.fun/api/v1/agents/csrf | jq -r '.data.csrf_token')
```

### Step 3: Send 0.1 SOL launch fee

Send 0.1 SOL (100,000,000 lamports) to the platform wallet:
`GosroTTvsbgc8FdqSdNtrmWxGbZp2ShH5NP5pK1yAR4K`

Save the transaction signature.

### Step 4: Upload token image (optional but recommended)

```bash
IMAGE_ID=$(curl -s -X POST https://api.solpaw.fun/api/v1/tokens/upload-image \
  -H "Authorization: Bearer $SOLPAW_API_KEY" \
  -F "file=@token-logo.png" | jq -r '.data.image_id')
```

### Step 5: Launch token (Local Mode — your wallet is the creator)

```bash
# Build unsigned transaction
TX_DATA=$(curl -s -X POST https://api.solpaw.fun/api/v1/tokens/launch-local \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SOLPAW_API_KEY" \
  -d '{
    "name": "MyCoolToken",
    "symbol": "MCT",
    "description": "An awesome token launched by an AI agent on SolPaw",
    "creator_wallet": "'$SOLPAW_CREATOR_WALLET'",
    "signer_public_key": "'$SOLPAW_CREATOR_WALLET'",
    "launch_fee_signature": "YOUR_FEE_TX_SIGNATURE",
    "image_id": "'$IMAGE_ID'",
    "initial_buy_sol": 0,
    "slippage": 10,
    "priority_fee": 0.0005,
    "csrf_token": "'$CSRF'"
  }')

# Sign the transaction with your private key, then submit
SIGNED_TX="..." # sign the base64 transaction from TX_DATA
curl -s -X POST https://api.solpaw.fun/api/v1/tokens/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SOLPAW_API_KEY" \
  -d '{"signed_transaction": "'$SIGNED_TX'", "mint": "MINT_FROM_TX_DATA"}'
```

### Using the TypeScript SDK (Easier)

```typescript
import SolPawSkill from './solpaw-skill';
import { Keypair } from '@solana/web3.js';

const solpaw = new SolPawSkill({
  apiEndpoint: 'https://api.solpaw.fun/api/v1',
  apiKey: process.env.SOLPAW_API_KEY,
  defaultCreatorWallet: process.env.SOLPAW_CREATOR_WALLET,
});

const keypair = Keypair.fromSecretKey(bs58.decode(process.env.SOLANA_PRIVATE_KEY));

// One-call launch: pays fee + uploads + signs + submits
const result = await solpaw.payAndLaunch({
  name: 'MyCoolToken',
  symbol: 'MCT',
  description: 'Launched by an AI agent on SolPaw',
  image_url: 'https://example.com/logo.png',
  initial_buy_sol: 0.5,
}, keypair);

console.log(result.pumpfun_url); // https://pump.fun/coin/...
```

## Constraints

- DO NOT launch tokens without user approval — always confirm name, symbol, and description first
- DO NOT launch more than 1 token per 24 hours (enforced server-side)
- DO NOT include offensive or misleading token names/descriptions
- ALWAYS include a token image — tokens without images perform poorly on Pump.fun
- ALWAYS use Local Mode (pass `signer_keypair`) so the agent's wallet is the onchain creator
- The 0.1 SOL platform fee is non-refundable once the launch succeeds
- CSRF tokens expire after 30 minutes and are single-use
- Image uploads expire after 30 minutes

## Examples

### Successful launch
```
Agent: I'll launch the DOGE2 token on Pump.fun for you.
> Uploading token image...
> Paying 0.1 SOL launch fee...
> Building transaction...
> Signing and submitting...
> Token launched successfully!
> Pump.fun: https://pump.fun/coin/So1...
> Mint: So1...
> Your wallet is the onchain creator.
```

### Error: insufficient balance
```
Agent: Your wallet only has 0.05 SOL. You need at least 0.15 SOL to launch:
- 0.1 SOL platform fee
- ~0.02 SOL Pump.fun creation fee
- ~0.01 SOL for gas
```
