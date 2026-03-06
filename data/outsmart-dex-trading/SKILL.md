---
name: outsmart-dex-trading
description: "Trade tokens on Solana via the outsmart CLI: buy, sell, quote, find pools, add/remove liquidity, claim fees, snipe, create pools. Use when: user asks about Solana trading, swaps, DEX, liquidity, pool, buy token, sell token, check price, wallet balance. NOT for: Ethereum/EVM trading, CEX orders, cross-chain bridging."
homepage: https://github.com/outsmartchad/outsmart-cli
metadata: { "openclaw": { "requires": { "bins": ["outsmart"], "env": ["PRIVATE_KEY", "MAINNET_ENDPOINT"] }, "install": [{ "id": "node", "kind": "node", "package": "outsmart", "bins": ["outsmart"], "label": "Install outsmart CLI (npm)" }] } }
---

# Solana DEX Trading

Trade across 18 Solana DEX protocols with a single CLI.

## When to Use

- "Buy SOL token"
- "Sell my tokens"
- "Check price of X"
- "Add liquidity to a pool"
- "Find the pool for token X"
- "What's my wallet balance?"
- "Snipe this token"
- "Create a new pool"

## When NOT to Use

- Ethereum/EVM/BSC trading — this is Solana only
- CEX orders (Binance, Coinbase) — this is on-chain DEX
- Cross-chain bridges — use dedicated bridge tools
- Historical price data — use DexScreener or charting tools

## Setup

```bash
npm i -g outsmart
outsmart init
# Enter your PRIVATE_KEY and MAINNET_ENDPOINT when prompted
# Config saved to ~/.outsmart/config.env
```

## Commands

### Buy Tokens

```bash
# Best price via Jupiter aggregator (just need token mint)
outsmart buy --dex jupiter-ultra --token MINT_ADDRESS --amount 0.1

# Direct on-chain (need pool address)
outsmart buy --dex raydium-cpmm --pool POOL_ADDRESS --amount 0.1

# With Jito MEV tip for priority execution
outsmart buy --dex meteora-dlmm --pool POOL --amount 0.05 --tip 0.005

# Dry run (simulate only)
outsmart buy --dex jupiter-ultra --token MINT --amount 0.1 --dry-run
```

### Sell Tokens

```bash
# Sell 100% of a token
outsmart sell --dex jupiter-ultra --token MINT_ADDRESS --pct 100

# Sell 50% from a specific pool
outsmart sell --dex raydium-cpmm --pool POOL_ADDRESS --pct 50
```

### Check Price

```bash
outsmart quote --dex raydium-cpmm --pool POOL_ADDRESS
```

### Find a Pool

```bash
outsmart find-pool --dex meteora-damm-v2 --token TOKEN_MINT
```

### Token Info (DexScreener)

```bash
outsmart info --token MINT_ADDRESS
# Returns: name, price, mcap, volume, buyers, liquidity, age, socials
```

### Wallet Balance

```bash
outsmart balance
outsmart balance --token MINT_ADDRESS
```

### Add Liquidity

```bash
# DLMM concentrated bins
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy spot --bins 50

# DAMM v2 full range
outsmart add-liq --dex meteora-damm-v2 --pool POOL --sol 0.5
```

### Remove Liquidity

```bash
outsmart remove-liq --dex meteora-dlmm --pool POOL --pct 100
```

### Claim Fees

```bash
outsmart claim-fees --dex meteora-dlmm --pool POOL
```

### List Positions

```bash
outsmart list-pos --dex meteora-dlmm --pool POOL
```

### Create Pool (DAMM v2)

```bash
outsmart create-pool --dex meteora-damm-v2 --token TOKEN_MINT \
  --base-amount 1000000 --quote-amount 0.5 \
  --max-fee 9900 --min-fee 200 --duration 86400 --periods 100
```

### List All DEXes

```bash
outsmart list-dex
outsmart list-dex --cap canBuy
```

## Picking the Right DEX

**Best price, don't care which pool:** `jupiter-ultra` — aggregates all DEXes.

**Specific pool (LP, on-chain execution):** Use the adapter that matches the pool's protocol.

| Situation | Use | Why |
|-----------|-----|-----|
| General trading | `jupiter-ultra` | Routes across everything |
| Meteora concentrated LP | `meteora-dlmm` | Bin-based positions |
| Meteora full-range LP | `meteora-damm-v2` | Full LP lifecycle |
| Raydium pools | `raydium-cpmm` / `raydium-clmm` / `raydium-amm-v4` | Match the pool type |
| PumpFun graduated | `pumpfun-amm` | PumpSwap AMM pools |
| PumpFun bonding curve | `pumpfun` | Pre-graduation |
| Unknown token | Check `outsmart info --token` first | Know what you're buying |

**Aggregators** (jupiter-ultra, dflow) need `--token` only.
**On-chain adapters** need `--pool`, token is auto-detected.

## Common Patterns

**Buy safely:**
```bash
outsmart info --token MINT          # check liquidity, age, volume
outsmart buy --dex jupiter-ultra --token MINT --amount 0.1 --dry-run  # simulate
outsmart buy --dex jupiter-ultra --token MINT --amount 0.1            # execute
```

**Provide liquidity:**
```bash
outsmart quote --dex meteora-dlmm --pool POOL        # current price
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy spot --bins 50
outsmart list-pos --dex meteora-dlmm --pool POOL      # verify
```

**Create DAMM v2 pool (first LP alpha):**
```bash
outsmart find-pool --dex meteora-damm-v2 --token MINT   # check if exists
outsmart create-pool --dex meteora-damm-v2 --token MINT --base-amount 1000000 --quote-amount 0.5 --max-fee 9900 --min-fee 200
```

**Exit LP:**
```bash
outsmart claim-fees --dex meteora-dlmm --pool POOL
outsmart remove-liq --dex meteora-dlmm --pool POOL --pct 100
```

## Safety

- Always check `outsmart info --token` before buying anything unfamiliar
- Use `--dry-run` for large trades
- Start small: 0.01 SOL test buy on unknown tokens
- Use jupiter-ultra for best price unless you specifically need a pool
- Watch for wash trading: high volume + low buyer count = fake activity
- Most memecoins go to zero. Size accordingly.

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `PRIVATE_KEY` | Yes | Base58 Solana private key |
| `MAINNET_ENDPOINT` | Yes | Solana RPC endpoint |
| `JUPITER_API_KEY` | No | Jupiter Ultra, Shield |
| `DFLOW_API_KEY` | No | DFlow adapter |

Config file: `~/.outsmart/config.env`

## 18 Supported DEXes

**Aggregators:** jupiter-ultra, dflow
**Raydium:** amm-v4, cpmm, clmm, launchlab
**Meteora:** damm-v2, dlmm, damm-v1, dbc
**PumpFun:** pumpswap amm, bonding curve
**Others:** orca, pancakeswap-clmm, byreal-clmm, fusion-amm, futarchy-amm, futarchy-launchpad
