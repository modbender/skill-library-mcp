---
name: trifle-auth
description: Authenticate with the Trifle API using Sign-In with Ethereum (SIWE). Manages wallet-based authentication, JWT token storage, and session management for the Trifle ecosystem.
version: 1.0.0
metadata:
  clawdhub:
    emoji: "🔐"
    requires:
      bins: ["node"]
      npm: ["viem", "siwe"]
    platforms: ["api"]
---

# Trifle Auth Skill

Authenticate with the Trifle API (`bot.trifle.life`) using SIWE (Sign-In with Ethereum) for wallet-based authentication. Stores JWT tokens for use by other skills (snake-game, etc.).

## Setup

### 1. Install dependencies

```bash
cd ~/.openclaw/workspace/skills/trifle-auth
npm install
```

### 2. Generate a wallet

```bash
node trifle-auth.mjs generate
```

This generates a new Ethereum address and **automatically saves the private key to 1Password** (vault: Gigi, item: "EVM Wallet - Trifle Agent"). The key is never printed to stdout. If 1Password is unavailable, it falls back to a restricted file (`~/.trifle-wallet.key`, mode 600).

### 3. Set environment (or use 1Password)

The skill reads the private key from:
1. `TRIFLE_PRIVATE_KEY` environment variable (first priority)
2. 1Password: `op://Gigi/EVM Wallet - Gigi/private_key` <!-- nocheck -->

### 4. Login

```bash
node trifle-auth.mjs login
```

This authenticates via SIWE and stores the JWT token in `~/.local/state/trifle-auth/auth-state.json`.

## Commands

```bash
# Authenticate and store JWT token
node trifle-auth.mjs login

# Check auth status and user info
node trifle-auth.mjs status

# Get JWT token path (written to a secure temp file, not stdout)
TOKEN=$(cat $(node trifle-auth.mjs token))
node trifle-auth.mjs token

# Generate a new wallet keypair
node trifle-auth.mjs generate

# Check ball balance
node trifle-auth.mjs balance
```

## Authentication Flow

1. Gets nonce from `/auth/wallet/nonce`
2. Creates SIWE message with domain `trifle.life`
3. Signs message with private key (no gas cost)
4. Verifies signature at `/auth/wallet/verify`
5. Receives JWT token (valid 30 days)
6. Stores token in state file

## State File

Location: `~/.local/state/trifle-auth/auth-state.json` (XDG-compliant, override with `TRIFLE_AUTH_STATE` env var)

```json
{
  "token": "jwt-token-here",
  "address": "0x...",
  "userId": 123,
  "username": "gigi",
  "totalBalls": 50,
  "lastLogin": "2026-02-05T15:00:00Z"
}
```

## CORS Notes

API requests include `Origin: https://trifle.life` header to satisfy CORS requirements. The backend validates the origin against its allowed list.

## Ball Economy

- **Earning balls**: GM game (1/day), auth bonuses (10 per platform), reactions, etc.
- **Spending balls**: Snake game votes (min 1 per vote)
- **Auth bonuses**: Each platform auth earns 10 balls (wallet, discord, telegram, etc.)
