---
name: 4claw-mint
description: Mint 4Claw tokens on BSC through OpenClaw agents. Each agent can mint 100 tokens every 15 minutes. Use when the user wants to mint 4Claw tokens, check mint status, or learn about the 4Claw token.
---

# 4Claw Mint

Mint **4Claw (symbol: 4)** tokens on BSC. Only OpenClaw agents can mint — the contract requires a signature from the authorized signer service.

## Token Info

- Name: **4Claw**, Symbol: **4**
- Chain: BSC (Chain ID: 56)
- Contract: `0x5F4E6Ee459fA71C226131BCeD5694aAab3b481dB`
- Total Supply: 1,000,000
- Public Mint: 600,000 (100 per mint, 6000 total mints)
- LP Reserve: 400,000 (pre-minted to deployer)
- Cooldown: 15 minutes per wallet

## How It Works

1. Agent calls the signer service with its wallet address
2. Service checks cooldown, generates nonce + deadline, signs the mint authorization
3. Agent submits the signature to the on-chain contract
4. Contract verifies signature, enforces cooldown, mints 100 tokens

## Mint

Run the mint script with the agent's wallet private key:

```bash
node scripts/mint.js <PRIVATE_KEY> <SERVER_URL>
```

- `PRIVATE_KEY`: Agent's BSC wallet private key (needs small BNB for gas)
- `SERVER_URL`: Signer service URL (default: http://43.160.201.224:3456)

The script handles everything: request signature → send tx → confirm → report balance.

## Signer Service

The signer service must be running for mints to work. It validates requests and signs mint authorizations.

```bash
SIGNER_PRIVATE_KEY=0x... CONTRACT_ADDRESS=0x... node scripts/server.js
```

Endpoints:
- `POST /api/mint-signature` — Request a mint signature. Body: `{"wallet_address": "0x..."}`
- `GET /api/status` — Check service status

## Contract

Source: `references/FourClaw.sol`

Key functions:
- `mint(nonce, deadline, signature)` — Mint 100 tokens (requires valid signer signature)
- `lastMintTime(address)` — Check when an address last minted
- `mintRemaining()` — How many public mint tokens are left
- `setSigner(address)` — Owner can update the signer address

## Setup for Deployer

1. Deploy `FourClaw.sol` to BSC with constructor args: `(signerAddress, lpWalletAddress)`
2. Set env vars and start the signer service
3. Share the skill — any OpenClaw agent with a BSC wallet can mint

## Error Handling

- **Cooldown not elapsed**: Wait 15 minutes between mints
- **Public mint exhausted**: All 600,000 tokens have been minted
- **Signature expired**: Signature is valid for 5 minutes, retry
- **Invalid signature**: Signer service may be misconfigured
- **Insufficient BNB**: Agent wallet needs BNB for gas (~0.001 BNB per mint)
