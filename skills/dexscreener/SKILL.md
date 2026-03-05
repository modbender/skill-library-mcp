---
name: dexscreener
description: Query DexScreener market data - search pairs, inspect liquidity/volume, check boosted tokens, and fetch token orders.
homepage: https://dexscreener.com
user-invocable: true
disable-model-invocation: true
metadata:
  openclaw:
    emoji: "📈"
    requires:
      bins: [node]
---

# DexScreener

Query [DexScreener](https://dexscreener.com) using the local CLI script.

## Quick Start

```bash
# Search pairs
node {baseDir}/scripts/dexscreener-cli.mjs search_pairs --query "solana" --limit 5

# Get pair details
node {baseDir}/scripts/dexscreener-cli.mjs get_pair --chain "solana" --pair "<pair_address>"

# Top boosted tokens
node {baseDir}/scripts/dexscreener-cli.mjs top_boosted_tokens --limit 10
```

---

## After Install - Suggested Setup

### 1. Add to daily market scan
Use in morning/evening briefs:
```
dexscreener search_pairs + top_boosted_tokens
```

### 2. Track specific tokens
```bash
node {baseDir}/scripts/dexscreener-cli.mjs pairs_by_tokens --token-addresses "<token1>,<token2>" --limit 10
```

### 3. Check order/boost status for candidates
```bash
node {baseDir}/scripts/dexscreener-cli.mjs token_orders --chain "solana" --token "<token_address>" --limit 10
node {baseDir}/scripts/dexscreener-cli.mjs latest_boosted_tokens --limit 20
```

---

## Commands

### Search and Pair Lookup

```bash
node {baseDir}/scripts/dexscreener-cli.mjs search_pairs --query "SOL/USDC" --limit 10
node {baseDir}/scripts/dexscreener-cli.mjs get_pair --chain "solana" --pair "<pair_address>"
node {baseDir}/scripts/dexscreener-cli.mjs pairs_by_tokens --token-addresses "<token1>,<token2>" --limit 10
```

### Profiles and Boosts

```bash
node {baseDir}/scripts/dexscreener-cli.mjs latest_token_profiles --limit 10
node {baseDir}/scripts/dexscreener-cli.mjs latest_boosted_tokens --limit 10
node {baseDir}/scripts/dexscreener-cli.mjs top_boosted_tokens --limit 10
```

### Token Orders

```bash
node {baseDir}/scripts/dexscreener-cli.mjs token_orders --chain "solana" --token "<token_address>" --limit 10
```

---

## Output Features

Typical payloads include:
- Pair metadata (chain, dex, pair address, symbols)
- Price and price change fields
- Liquidity and volume fields
- Boost/profile/order metadata

Default output is JSON for easy piping and automation.

---

## API

Uses DexScreener public API endpoints (read-only):
- Base URL: `https://api.dexscreener.com`
- CLI supports override via `DEXSCREENER_BASE_URL`

---

## Security and Permissions

No API key required.

What this skill does:
- Makes HTTPS GET requests to DexScreener API
- Reads public market/pair/profile/boost/order data

What this skill does not do:
- No wallet connections
- No transactions or trading
- No credential handling
- No autonomous invocation (`disable-model-invocation: true`)
