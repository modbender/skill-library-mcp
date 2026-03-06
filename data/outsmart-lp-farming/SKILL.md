---
name: outsmart-lp-farming
description: "Manage LP positions on Solana DEXes to earn swap fees. Use when: user asks about LP farming, providing liquidity, earning yield, compounding fees, DLMM, DAMM v2, rebalancing, creating pools, passive income on Solana. NOT for: lending/borrowing protocols, staking SOL, CEX market making."
homepage: https://github.com/outsmartchad/outsmart-cli
metadata: { "openclaw": { "requires": { "bins": ["outsmart"], "env": ["PRIVATE_KEY", "MAINNET_ENDPOINT"] }, "install": [{ "id": "node", "kind": "node", "package": "outsmart", "bins": ["outsmart"], "label": "Install outsmart CLI (npm)" }] } }
---

# LP Farming

You earn money by providing liquidity to pools. Every time someone swaps through your pool, you get a cut. Two protocols, two completely different games.

## When to Use

- "Farm yield on Solana"
- "Add liquidity to a pool"
- "Create a new pool"
- "Rebalance my LP"
- "Claim my fees"
- "DLMM vs DAMM v2?"

## When NOT to Use

- Staking SOL for validator rewards — different system
- Lending/borrowing (Marginfi, Kamino) — different protocols
- CEX market making — this is on-chain only

## DLMM vs DAMM v2

**DLMM** is for mature tokens. Concentrated bins, you pick the price range, you actively manage. Token needs 30+ min of real volume. Costs ~0.2 SOL. If price moves out of range, you're 100% in the losing side.

**DAMM v2** is for fresh launches. Full range, set-and-forget, decaying fee schedule. The alpha: be the first person to create the pool — you set 99% starting fee and capture everything. Costs ~0.02 SOL.

| | DLMM | DAMM v2 |
|---|---|---|
| When | Token age >30 min | Token age <5 min |
| LP style | Concentrated bins | Full range |
| Fees | Fixed fee tier | Decaying (99% start -> 2% end) |
| Alpha | Tight bins = max capture | First pool creator = everything |
| IL | Binary: in range or fully single-sided | Standard AMM: gradual |
| Cost | ~0.2 SOL | ~0.02 SOL |

## DLMM Commands

### Add liquidity (3 strategies)

```bash
# Spot: even distribution (good default)
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy spot --bins 50

# Curve: concentrated near active bin (stable pairs)
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy curve --bins 30

# Bid-Ask: more at edges (volatile pairs)
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy bid-ask --bins 40
```

### One-sided positions

```bash
# SOL below price = buy wall (DCA in while earning fees)
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --token-amount 0 --strategy spot --bins 40

# Token above price = sell wall (DCA out while earning fees)
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0 --token-amount 1000 --strategy spot --bins 40
```

### Rebalancing

```bash
outsmart claim-fees --dex meteora-dlmm --pool POOL
outsmart remove-liq --dex meteora-dlmm --pool POOL --pct 100
outsmart quote --dex meteora-dlmm --pool POOL
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy spot --bins 50
```

Don't rebalance for small moves — each cycle costs ~0.005-0.02 SOL.

## DAMM v2 Commands

### First pool creator play

```bash
# Check if pool exists
outsmart find-pool --dex meteora-damm-v2 --token TOKEN_MINT

# If not found, create with 99% starting fee
outsmart create-pool --dex meteora-damm-v2 --token TOKEN_MINT \
  --base-amount 1000000 --quote-amount 0.5 \
  --max-fee 9900 --min-fee 200 --duration 86400 --periods 100
```

## Day-to-Day Workflow

```bash
# 1. Find opportunity (volume/liquidity > 1.0 = good fees)
outsmart info --token TOKEN_MINT

# 2. Check pool
outsmart quote --dex meteora-dlmm --pool POOL

# 3. Add LP
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy spot --bins 50

# 4. Monitor
outsmart list-pos --dex meteora-dlmm --pool POOL

# 5. Claim fees
outsmart claim-fees --dex meteora-dlmm --pool POOL

# 6. Exit
outsmart remove-liq --dex meteora-dlmm --pool POOL --pct 100
```

## Risk Management

- DLMM IL is binary: in range or fully single-sided. Use wider bins (50+).
- DAMM v2 IL is standard AMM. Offset by high initial fees if you're first LP.
- Only LP tokens with >$100k liquidity, >24h age, organic buyers.
- Budget ~0.05 SOL for a full LP cycle. Keep 0.1 SOL gas reserve.
