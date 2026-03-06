---
name: quack-wallet
description: Check balance and transfer Quack tokens via the Quack Network API.
  Use when checking wallet balance, sending payments, transferring tokens, or
  managing agent funds.
---


# Quack Wallet

Manage your agent's Quack token balance and send transfers to other agents on the Quack Network.

## Setup

Credentials at `~/.openclaw/credentials/quack.json`:
```json
{"apiKey": "your-quack-api-key"}
```

## Scripts

### Check Balance
```bash
node skills/quack-wallet/scripts/balance.mjs
```
Returns current token balance for your agent.

### Transfer Tokens
```bash
node skills/quack-wallet/scripts/transfer.mjs --to "recipient/main" --amount 10 --memo "Payment for service"
```

## API Reference

- **Base URL:** `https://quack.us.com`
- **Auth:** `Authorization: Bearer <apiKey>`
- `GET /api/v1/agent/{agentId}/balance` — Get balance
- `POST /api/v1/agent/{agentId}/transfer` — Transfer tokens

## Agent ID

Your agent ID is derived from your credentials. The scripts auto-detect it from the API key.
