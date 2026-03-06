---
name: solana-whale-alert
description: Monitor Solana wallets and tokens for large transactions. Get alerts when whales move. No API keys required.
---

# Solana Whale Alert

Monitor Solana wallets and tokens for large transactions. Detect whale movements in real-time using free public APIs.

## Usage

- "Watch this wallet for large transactions: [address]"
- "Alert me when someone moves more than $10K of SOL"  
- "Monitor top holders of [token] for sells"
- "Check recent large SOL transfers"

## Commands

### Check recent large transfers
```bash
bash scripts/whale-check.sh [min_amount_sol]
```

### Monitor a specific wallet
```bash
bash scripts/watch-wallet.sh <wallet_address> [check_interval_seconds]
```

### Scan token top holders for movements
```bash
bash scripts/scan-holders.sh <token_mint>
```

## What It Detects

| Signal | Description | Interpretation |
|--------|-------------|----------------|
| Large SOL transfer | >1000 SOL moved | Whale repositioning |
| CEX deposit | Large transfer to known exchange | Potential sell pressure |
| CEX withdrawal | Large transfer from exchange | Accumulation signal |
| Token dump | Top holder selling large % | Rug/exit risk |
| New whale | Unknown wallet accumulating | Smart money signal |

## APIs Used (all free)
- Solana RPC (getSignaturesForAddress, getTransaction)
- Helius Enhanced API (if key available, much richer data)
- DexScreener (token context)

## Limitations
- Public RPC rate limits (~40 req/10s)
- Set SOLANA_RPC_URL or HELIUS_API_KEY for better throughput
- Historical lookback limited without indexed data
