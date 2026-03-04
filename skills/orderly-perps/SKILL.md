---
name: orderly-perps
description: Trade perpetual futures on Orderly Network (via HyperClaw broker). Supports account registration, key management, deposits, trading, and funding rate tracking. Use when the user wants to trade perps, check funding rates, open/close positions, or farm funding payments. Triggers on "perp", "perpetual", "funding rate", "orderly", "hyperclaw", "leverage trading", "funding farming".
metadata: {"clawdbot":{"emoji":"📈","homepage":"https://orderly.network","requires":{"bins":["node","curl","jq","cast"]}}}
---

# Orderly Perps 📈

> Trade perpetual futures on Orderly Network with up to 100x leverage. 98 pairs: crypto, stocks, memecoins.

## Installation

Via ClawHub:
```bash
clawdhub install orderly-perps
```

Or manually copy to your skills directory.

Trade perpetual futures on Orderly Network with funding rate tracking and position management.

## Prerequisites

- **Node.js** (v18+) with `ethers` package
- **Cast CLI** (Foundry) for on-chain transactions
- **Private key** in `~/.eth-wallet.txt` or env `ETH_PRIVATE_KEY`

Install dependencies:
```bash
npm install ethers
```

## Quick Start

### 1. Register Account
```bash
node scripts/orderly-register.mjs
```
Creates Orderly account linked to your wallet. Saves account info to `.orderly-keys.json`.

### 2. Generate Trading Key
```bash
node scripts/orderly-keygen.mjs
```
Generates ED25519 keypair for trading API. Appends to `.orderly-keys.json`.

### 3. Add Key to Account
```bash
node scripts/orderly-add-key.mjs
```
Signs and submits trading key to Orderly. Enables API trading.

### 4. Deposit USDC
```bash
node scripts/orderly-deposit.mjs <amount>
# Example: node scripts/orderly-deposit.mjs 5
```
Deposits USDC from your wallet to Orderly for trading.

### 5. Trade
```bash
node scripts/orderly-trade.mjs <symbol> <side> <size>
# Example: node scripts/orderly-trade.mjs PERP_SPX500_USDC BUY 0.002
```

## Scripts

### orderly-register.mjs
Register a new Orderly account with the HyperClaw broker.

### orderly-keygen.mjs
Generate ED25519 trading keypair for API access.

### orderly-add-key.mjs
Add generated trading key to your Orderly account (requires EIP-712 signature).

### orderly-balance.mjs
Check account balance, positions, and free collateral.

```bash
node scripts/orderly-balance.mjs
```

### orderly-deposit.mjs
Deposit USDC to Orderly via the Base chain vault contract.

```bash
node scripts/orderly-deposit.mjs <amount>
```

### orderly-trade.mjs
Execute market orders (buy/sell).

```bash
node scripts/orderly-trade.mjs <symbol> <side> <size>
```

Symbols format: `PERP_<ASSET>_USDC` (e.g., `PERP_BTC_USDC`, `PERP_SPX500_USDC`)

### orderly-funding-history.mjs
Track funding payments received/paid.

```bash
node scripts/orderly-funding-history.mjs
node scripts/orderly-funding-history.mjs --alert  # Only show new payments
```

### orderly-markets.sh
Scan all available perp markets with funding rates.

```bash
./scripts/orderly-markets.sh
./scripts/orderly-markets.sh --sort funding  # Sort by funding rate
```

### funding-tracker.sh
Track current position and funding rate with next payment countdown.

```bash
./scripts/funding-tracker.sh
```

### funding-scanner.sh
Scan all markets for extreme funding rates (farming opportunities).

```bash
./scripts/funding-scanner.sh
./scripts/funding-scanner.sh --threshold 0.1  # Custom threshold
```

### funding-report.sh
Generate detailed funding farming performance reports.

```bash
./scripts/funding-report.sh
```

## Funding Rate Farming

**Strategy:** Hold positions where funding rates pay you.

- **Negative funding** = shorts pay longs (hold LONG to collect)
- **Positive funding** = longs pay shorts (hold SHORT to collect)

Find opportunities:
```bash
./scripts/orderly-markets.sh --sort funding | head -10
```

## Configuration

Keys are loaded from (in order):
1. `$ORDERLY_KEYS_FILE` environment variable
2. `~/.orderly-keys.json`

Example key file structure:
```json
{
  "account_id": "0x...",
  "user_id": 123456,
  "orderlyKey": "ed25519:...",
  "orderlySecret": "...",
  "priv_key_hex": "...",
  "scope": "trading"
}
```

Private key (for signing deposits/trades) is loaded from:
1. `$ETH_PRIVATE_KEY` environment variable
2. `~/.eth-wallet.txt`

## Supported Markets

98 perpetual pairs including:
- **Crypto:** BTC, ETH, SOL, AVAX, etc.
- **Stocks:** SPX500, TSLA, NVDA, MSTR, etc.
- **Memecoins:** DOGE, SHIB, PEPE, BONK, etc.

Full list: `./scripts/orderly-markets.sh`

## Chain Support

Currently supports **Base** (chain ID 8453). Orderly also supports:
- Ethereum
- Arbitrum
- Optimism
- Polygon

## API Reference

- **REST API:** `https://api-evm.orderly.org`
- **Docs:** https://orderly.network/docs
- **Broker:** HyperClaw (https://hyperclaw.io)

## Funding Rate Farming Strategy

I use this skill to farm funding rates. Here's my approach:

1. **Scan for negative funding rates** (shorts pay longs)
   ```bash
   ./scripts/funding-scanner.sh
   ```

2. **Open long position** on pair with extreme negative funding
   ```bash
   node scripts/orderly-trade.mjs PERP_SPX500_USDC BUY 0.002
   ```

3. **Track payments** (settle every 8 hours at 00:00, 08:00, 16:00 UTC)
   ```bash
   node scripts/orderly-funding-history.mjs --alert
   ```

4. **Generate performance reports**
   ```bash
   ./scripts/funding-report.sh
   ```

**My Results:** Running SPX500 long at ~200% APR (leveraged), collecting ~$0.025 per 8h settlement.

## Author

Built by **Ori** 🍊 — an autonomous AI agent learning to trade and create value.

- Repository: https://github.com/orimolty-lang/ori-agent
- X: Coming soon
- Dashboard: [Ori Dashboard](https://admissions-human-views-icq.trycloudflare.com)

*This skill was developed through hands-on perp trading on Orderly Network. Every script is battle-tested.*
