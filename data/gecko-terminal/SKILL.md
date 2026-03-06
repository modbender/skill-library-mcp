---
name: geckoterminal
description: Query GeckoTerminal market data - networks, DEXes, pools, tokens, OHLCV, trades, and trending/new pools.
homepage: https://www.geckoterminal.com
user-invocable: true
disable-model-invocation: true
metadata:
  openclaw:
    emoji: "🦎"
    requires:
      bins: [node]
---

# GeckoTerminal

Query [GeckoTerminal](https://www.geckoterminal.com) via the local CLI script.

## Quick Start

```bash
# List networks
node {baseDir}/scripts/geckoterminal-cli.mjs get_networks

# Solana trending pools
node {baseDir}/scripts/geckoterminal-cli.mjs get_network_trending_pools --network solana --duration 1h --page 1

# Search pools
node {baseDir}/scripts/geckoterminal-cli.mjs search_pools --query "SOL USDC" --network solana --page 1
```

---

## After Install - Suggested Setup

### 1. Daily discovery scan
Use in your daily brief:
```
gecko trending pools + new pools + top pools
```

### 2. Track a token across pools
```bash
node {baseDir}/scripts/geckoterminal-cli.mjs get_token_pools --network solana --token "<token_address>" --page 1
node {baseDir}/scripts/geckoterminal-cli.mjs get_simple_token_prices --network solana --token-addresses "<token1>,<token2>"
```

### 3. Analyze a candidate pool
```bash
node {baseDir}/scripts/geckoterminal-cli.mjs get_pool_info --network solana --pool "<pool_address>"
node {baseDir}/scripts/geckoterminal-cli.mjs get_pool_trades --network solana --pool "<pool_address>" --page 1
```

---

## Commands

### Networks and DEXes

```bash
node {baseDir}/scripts/geckoterminal-cli.mjs get_networks
node {baseDir}/scripts/geckoterminal-cli.mjs get_dexes --network solana
node {baseDir}/scripts/geckoterminal-cli.mjs get_top_pools --network solana --page 1
node {baseDir}/scripts/geckoterminal-cli.mjs get_dex_pools --network solana --dex "raydium" --page 1
```

### Trending / New Pools

```bash
node {baseDir}/scripts/geckoterminal-cli.mjs get_global_trending_pools --duration 1h --page 1
node {baseDir}/scripts/geckoterminal-cli.mjs get_network_trending_pools --network solana --duration 24h --page 1
node {baseDir}/scripts/geckoterminal-cli.mjs get_global_new_pools --page 1
node {baseDir}/scripts/geckoterminal-cli.mjs get_network_new_pools --network base --page 1
```

### Pools and Search

```bash
node {baseDir}/scripts/geckoterminal-cli.mjs search_pools --query "SOL USDC" --network solana --page 1
node {baseDir}/scripts/geckoterminal-cli.mjs get_pool --network solana --pool "<pool_address>"
node {baseDir}/scripts/geckoterminal-cli.mjs get_multi_pools --network solana --pool-addresses "<pool1>,<pool2>"
node {baseDir}/scripts/geckoterminal-cli.mjs get_pool_info --network solana --pool "<pool_address>"
node {baseDir}/scripts/geckoterminal-cli.mjs get_pool_trades --network solana --pool "<pool_address>" --page 1
```

### Tokens

```bash
node {baseDir}/scripts/geckoterminal-cli.mjs get_token --network solana --token "<token_address>"
node {baseDir}/scripts/geckoterminal-cli.mjs get_multi_tokens --network solana --token-addresses "<token1>,<token2>"
node {baseDir}/scripts/geckoterminal-cli.mjs get_token_info --network solana --token "<token_address>"
node {baseDir}/scripts/geckoterminal-cli.mjs get_token_pools --network solana --token "<token_address>" --page 1
node {baseDir}/scripts/geckoterminal-cli.mjs get_simple_token_prices --network solana --token-addresses "<token1>,<token2>"
node {baseDir}/scripts/geckoterminal-cli.mjs get_recently_updated_token_info --page 1
```

### OHLCV

```bash
node {baseDir}/scripts/geckoterminal-cli.mjs get_pool_ohlcv --network solana --pool "<pool_address>" --timeframe hour --limit 100 --currency usd --token base
```

### Raw API fallback

```bash
node {baseDir}/scripts/geckoterminal-cli.mjs api_get --path /networks/trending_pools --query-json '{"duration":"5m","page":1}'
```

### Optional Query Params

Common optional flags supported by the CLI:

```bash
# Include related resources where supported
--include "base_token,quote_token,dex"

# Include extra pool/token breakdowns where supported
--include-volume-breakdown true
--include-composition true

# Include inactive-source rows where supported
--include-inactive-source true

# Sort/page where supported
--sort "h24_volume_usd_desc"
--page 1

# Community data toggle (trending/new/top/dex pools endpoints)
--include-gt-community-data false

# Simple token price extras
--include-market-cap true
--mcap-fdv-fallback true
--include-24hr-vol true
--include-24hr-price-change true
--include-total-reserve-in-usd true
```

---

## Output Features

Typical payloads include:
- Pool attributes (network, dex, addresses, links)
- Price, liquidity, volume, and transaction summaries
- Token metadata and linked pools
- OHLCV candles and recent trades

Default output is JSON for easy piping and automation.

---

## API

Uses GeckoTerminal public API v2 (read-only):
- Base URL: `https://api.geckoterminal.com/api/v2`
- `api_get --path` accepts API-relative paths only (absolute URLs are blocked)

---

## Security and Permissions

No API key required.

What this skill does:
- Makes HTTPS GET requests to GeckoTerminal API
- Reads public network/DEX/pool/token/market data

What this skill does not do:
- No wallet connections
- No transactions or trading
- No credential handling
- No autonomous invocation (`disable-model-invocation: true`)
