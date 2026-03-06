---
name: solana-scanner
description: Scan any Solana token for safety — liquidity, holder concentration, red flags, and rug pull indicators. No API keys required.
---

# Solana Token Scanner

Analyze any Solana token for safety before trading. Checks liquidity, holder concentration, price action, and red flags. Uses free public APIs — no keys required.

## Quick Start

To scan a token, run the scan script then analyze:

```bash
bash scripts/scan-token.sh <MINT_ADDRESS> | python3 scripts/analyze-token.py
```

## Examples

User: "Is this token safe? EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
Agent: Run `bash scripts/scan-token.sh EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v | python3 scripts/analyze-token.py`

User: "Scan BONK"
Agent: Look up BONK mint address (DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263), then run scan.

User: "Check if this memecoin is a rug"
Agent: Ask for the mint address, then run scan.

## What It Checks

| Check | What | Risk Signal |
|-------|------|-------------|
| Liquidity | Pool size in USD | <$1K = almost certainly dead/rug |
| Volume | 24h trading volume | <$100 = dead token |
| Holders | Top holder concentration | >50% = extreme rug risk |
| Age | When pair was created | <24h = very high risk |
| Price | 24h price change | >-50% = dump in progress |
| DEX | Which DEX it trades on | No DEX = untradeable |

## Safety Scores

| Score | Rating | Meaning |
|-------|--------|---------|
| 80-100 | 🟢 RELATIVELY_SAFE | Major token, good liquidity |
| 60-79 | 🟡 CAUTION | Some concerns, trade carefully |
| 40-59 | 🟠 HIGH_RISK | Multiple red flags |
| 0-39 | 🔴 AVOID | Likely scam or dead token |

## APIs Used (all free, no keys needed)
- **DexScreener** — liquidity, volume, price, pair age
- **Jupiter Price API** — current pricing
- **Solana RPC** — supply info, largest holders

## Dependencies
- `bash`, `curl`, `python3` (standard on most systems)
- Optional: `SOLANA_RPC_URL` env var for custom RPC (default: public mainnet)

## Limitations
- Public RPC rate limits may affect holder data
- Set `SOLANA_RPC_URL` to a Helius/QuickNode endpoint for full holder analysis
- DexScreener data may lag a few minutes
- This is analysis, not financial advice
