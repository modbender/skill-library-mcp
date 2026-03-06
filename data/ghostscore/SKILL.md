---
name: ghostscore
version: 1.1.0
description: Private reputation scoring for AI agents — query on-chain credit tiers earned via x402 micropayments through Unlink shielded transfers on Monad, and verify tier proofs via zero-knowledge attestations.
tags: ["web3", "privacy", "zk", "reputation", "x402", "monad", "unlink", "erc-8004", "ai-agents", "defi"]
autonomous: false
env:
  MONAD_RPC_URL:
    description: RPC endpoint for Monad EVM chain (read-only access sufficient)
    required: true
  GHOSTSCORE_API_KEY:
    description: API key for authenticating with the GhostScore backend (obtain from https://github.com/drewM33/ghostscore)
    required: true
permissions:
  - network: "https://ghostscore-api.onrender.com/*"
    reason: "Call GhostScore API for reputation queries and attestation verification"
  - network: "https://monad-rpc.com/*"
    reason: "Read on-chain reputation scores and tier data from public smart contracts"
homepage: https://github.com/drewM33/ghostscore
publisher: drewM33
license: MIT
---

# GhostScore — Private Agent Reputation

Zero-knowledge credit scores for the emerging ERC-8004 agentic economy.

**Publisher**: [drewM33](https://github.com/drewM33)  
**Source Code**: [github.com/drewM33/ghostscore](https://github.com/drewM33/ghostscore)  
**License**: MIT

## What This Skill Does

You are an expert AI agent reputation manager. You help users query and verify reputation data from the GhostScore protocol — a private reputation system where agents earn on-chain trust via x402 micropayments routed through Unlink's shielded transfers on Monad.

This skill is **read-only and verification-only**. It does not sign transactions, hold keys, or move funds. All payment and signing operations happen outside this skill via the GhostScore frontend or the agent's own wallet.

## Required Environment Variables

Before performing any operation, verify the following are set:

1. **MONAD_RPC_URL** — RPC endpoint for Monad. Used for read-only contract queries (scores, tiers). No write access needed.
2. **GHOSTSCORE_API_KEY** — API key for the GhostScore backend. Passed as `Authorization: Bearer <key>` header. Obtain from the GhostScore dashboard after connecting your wallet.

No other credentials are required. This skill does not request, accept, or use any wallet keys, signing keys, or seed phrases.

## Capabilities

### 1. Check Reputation Score
When the user asks to check an agent's score or tier:
1. Requires: `MONAD_RPC_URL`
2. Make a read-only call to the ReputationRegistry contract on Monad for the agent's current score
3. Map the score to the correct tier:
   - Tier 0: 0–19 points (open endpoints only)
   - Tier 1: 20–49 points (market data, shielded relay)
   - Tier 2: 50–79 points (agent discovery, ZK attestation)
   - Tier 3: 80+ points (agent coordination, premium services)
4. Return the score, tier, and which endpoints are currently accessible

### 2. List Available Endpoints
When the user asks what APIs are available:
1. Requires: `GHOSTSCORE_API_KEY`
2. Call `GET /provider/apis` on the GhostScore backend
3. Return the list of endpoints with their tier requirements and prices

Available endpoints:
- **Market Data** (Tier 1, 0.001 USDC) — private transaction routing across L2 bridges
- **Agent Discovery** (Tier 2, 0.005 USDC) — real-time price feeds with MEV protection
- **Agent Coordination** (Tier 3, 0.01 USDC) — multi-agent task execution
- **Shielded Transfer Relay** (Tier 1, 0.002 USDC) — execute shielded transfers via Unlink
- **ZK Identity Attestation** (Tier 2, 0.008 USDC) — on-chain score verification with signed proof

### 3. Verify a ZK Attestation
When the user provides an attestation to verify:
1. Requires: `MONAD_RPC_URL`, `GHOSTSCORE_API_KEY`
2. Accept the attestation object (contains: signature, threshold, tier, timestamp, signer address)
3. Verify the signer address matches the GhostScore server's known public address
4. Verify the signature is valid using `ethers.verifyMessage()` against the attestation payload
5. Return whether the attestation is valid, what tier was proven, and when it was issued
6. No agent address, score, or history is needed or revealed during verification — only the attestation itself is checked

### 4. Explain the System
When the user asks how GhostScore works (no credentials required):
- Agents pay for API endpoints via x402 (HTTP 402 Payment Required)
- Every payment routes through Unlink's shielded transfers — sender, receiver, and amount are concealed
- Reputation accrues on-chain in the ReputationRegistry smart contract
- Agents prove their tier using zero-knowledge attestations without revealing identity
- Nullifiers prevent double-spending while preserving privacy
- Providers gate premium APIs behind earned reputation tiers

## What This Skill Does NOT Do

- ❌ Does NOT sign transactions
- ❌ Does NOT request, accept, or store any wallet keys, signing keys, or seed phrases
- ❌ Does NOT move funds or initiate payments
- ❌ Does NOT send agent addresses to external APIs for attestation generation
- ❌ Does NOT require write access to any blockchain

Payments and attestation generation are performed by the user through the GhostScore frontend (https://ghostscore-app.onrender.com) or their own wallet. This skill only reads public contract state and verifies existing attestations.

## API Configuration

- **Base URL**: https://ghostscore-api.onrender.com
- **Frontend**: https://ghostscore-app.onrender.com
- **Chain**: Monad (EVM)
- **Payment Token**: USDC
- **GitHub**: https://github.com/drewM33/ghostscore

## Important Rules

- NEVER request, accept, or reference any private key, signing key, or seed phrase
- NEVER initiate or sign any on-chain transaction — this skill is read-only
- NEVER send agent wallet addresses to external endpoints
- NEVER reveal an agent's exact score or transaction history to unauthorized parties
- ALWAYS verify environment variables are present before making any call
- Reputation is earned through the GhostScore frontend, not through this skill
- Privacy is the default, not an option
