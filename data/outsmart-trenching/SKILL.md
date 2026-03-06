---
name: outsmart-trenching
description: "Trade memecoins on Solana. Use when: user asks about memecoins, trenching, degen trading, ape, GMGN, Axiom, pump, 100x, alpha, CT, smart money, whale tracking, fresh wallets, rug checks. NOT for: blue chip trading (use DCA), LP farming, prediction markets."
homepage: https://github.com/outsmartchad/outsmart-cli
metadata: { "openclaw": { "requires": { "bins": ["outsmart", "curl"], "env": ["PRIVATE_KEY", "MAINNET_ENDPOINT"] }, "install": [{ "id": "node", "kind": "node", "package": "outsmart", "bins": ["outsmart"], "label": "Install outsmart CLI (npm)" }] } }
---

# Trenching

You're trading attention. Memecoins have no fundamentals — just vibes, narratives, and social momentum. Most go to zero. Some go to $1B. Cap allocation at 10% of portfolio.

## When to Use

- "Find me a memecoin to buy"
- "What's the current meta?"
- "Check if this token is safe"
- "Smart money is buying X"

## When NOT to Use

- Blue chip accumulation (SOL, JUP) — use DCA
- LP farming — different skill
- Prediction markets — different skill

## Finding What's Hot

**Twitter/X** — ground zero. 5+ accounts posting about the same thing = meta forming.

**Smart money** — build a watchlist on GMGN or Cielo. When 3+ converge on same token, real signal.

**On-chain** — GMGN "Sniper New" feed, DexScreener trending.

## Sizing Up a Token

```bash
# Quick check: price, volume, buyers, liquidity, age
outsmart info --token MINT_ADDRESS
```

| Metric | Good | Bad |
|--------|------|-----|
| Liquidity | > 50 SOL | < 10 SOL |
| Buyers (5m/1h) | Growing, diverse | Flat or declining |
| Volume vs buyers | Proportional | Huge volume, few buyers |
| Age | 10min - 6h | < 2min or > 24h with no momentum |
| Market cap | $50k - $5M | > $50M (you're late) |

### Jupiter Shield (security check)

```bash
curl -s "https://api.jup.ag/ultra/v1/shield?mints=MINT_ADDRESS" | python3 -m json.tool
```

Flags freeze/mint authority, low organic activity.

## Execution

```bash
# Buy
outsmart buy --dex jupiter-ultra --token MINT --amount 0.05

# Sell 25% at 2x
outsmart sell --dex jupiter-ultra --token MINT --pct 25
```

### Sizing

| Conviction | Size |
|-----------|------|
| Strong thesis + clean security | 3-5% |
| Looks good, decent signals | 1-2% |
| Smart money buying, unverified | 0.5-1% |
| FOMO | 0% |

### Taking Profits

| Hit | Action |
|-----|--------|
| 2x | Sell 25% |
| 3x | Sell another 25% — house money |
| 5x | Sell another 25% |
| 10x+ | Sell or ride with tight stop |

Never ride a memecoin back to zero.

## Red Flags — Instant Skip

| Flag | How to Detect |
|------|---------------|
| Mint authority enabled | Jupiter Shield |
| Freeze authority | Jupiter Shield |
| Single wallet >30% supply | GMGN |
| LP not burned/locked | GMGN, RugCheck |
| Dev selling into buys | GMGN first 70 buyers |
| Snipers >5% from block 0 | GMGN |

## After — The LP Play

If the token has legs:
```bash
# < 5 min: create DAMM v2 pool with 99% fee
outsmart create-pool --dex meteora-damm-v2 --token MINT --base-amount 1000000 --quote-amount 0.5 --max-fee 9900 --min-fee 200

# > 30 min: DLMM position
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy spot --bins 50
```

## External Tools

| Tool | Use |
|------|-----|
| **GMGN** | Smart money, security, insider detection |
| **Cielo** | Wallet discovery, Mindshare, alerts |
| **Axiom** | Twitter monitor (auto-detects CAs) |
| **DexScreener** | Charts, token profiles, trending |
| **RugCheck** | Contract analysis, LP lock status |
