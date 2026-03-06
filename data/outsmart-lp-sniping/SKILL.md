---
name: outsmart-lp-sniping
description: "Buy tokens at or near LP creation on Solana. Use when: user asks about sniping, bonding curve graduation, migration, new pool, LP created, pump fun graduation, launchlab, first buy. NOT for: slow accumulation (use DCA), established tokens (use regular trading), historical analysis."
homepage: https://github.com/outsmartchad/outsmart-cli
metadata: { "openclaw": { "requires": { "bins": ["outsmart"], "env": ["PRIVATE_KEY", "MAINNET_ENDPOINT"] }, "install": [{ "id": "node", "kind": "node", "package": "outsmart", "bins": ["outsmart"], "label": "Install outsmart CLI (npm)" }] } }
---

# LP Sniping

The moment liquidity appears, you buy. Speed is everything.

## When to Use

- "Snipe this token at graduation"
- "Buy the moment LP goes live"
- "PumpFun bonding curve at 90%"
- Token about to migrate to AMM

## When NOT to Use

- Slow accumulation — use DCA skill instead
- Established tokens — use regular dex-trading
- You don't know what the token is — research first

## Commands

```bash
# Competitive buy with Jito MEV tip
outsmart buy --dex meteora-dlmm --pool POOL --amount 0.05 --tip 0.005

# Quick buy via aggregator (if you have the mint but not pool)
outsmart buy --dex jupiter-ultra --token MINT --amount 0.05

# Check what you bought
outsmart info --token MINT
```

## What to Snipe

**PumpFun graduation** — bonding curve fills to 100%, migrates to PumpSwap. Target: 80%+ progress, active community, dev hasn't sold.

**LaunchLab** — same pattern, graduates to Raydium CPMM.

**Known mints** — dev shared the address before pool exists.

## Position Sizing

- Confident in narrative: 2-3% of portfolio
- Looks promising: 1%
- Just want exposure: 0.5%

## After You're In

```bash
# Check if you should hold or dump
outsmart info --token MINT
```

Low organic activity, single wallet >30%, no real volume? Sell and move on.

## Exit Plan

| Hit | Do |
|-----|-----|
| 2x | Sell 50% |
| 3-5x | Sell another 25% |
| 10x+ | Let the rest ride |
| -50% | Full exit |

```bash
outsmart sell --dex jupiter-ultra --token MINT --pct 50
```

## After — The LP Play

If the token has legs:
```bash
# < 5 min, big volume: create DAMM v2 pool with 99% fee
outsmart create-pool --dex meteora-damm-v2 --token MINT --base-amount 1000000 --quote-amount 0.5 --max-fee 9900 --min-fee 200

# > 30 min, established: DLMM position
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy spot --bins 50
```

## Risks

- Rugs — that's why you size small
- Front-run by MEV — use `--tip` for priority
- Late entry — don't chase with bigger size
