# 🛡️ Rug Checker — Solana Token Risk Analysis

**Instant rug-pull risk reports for any Solana token.** 10-point on-chain analysis. No API keys. No wallet connections. Just data.

```
> "Rug check DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
```

## What It Does

Rug Checker analyzes Solana SPL tokens across 10 risk vectors and produces a visual report card with a composite risk score (0-100). It cross-references three independent data sources to detect:

| Check | What It Catches |
|-------|----------------|
| 🔑 Mint Authority | Can the creator print unlimited tokens? |
| 🧊 Freeze Authority | Can the creator freeze your wallet? |
| 👥 Holder Concentration | Are a few wallets holding everything? |
| 🔒 LP Lock Status | Can liquidity be pulled? (the classic rug) |
| ⏰ Token Age | Is this dangerously new? |
| 💧 Liquidity Depth | Can you actually sell without 90% slippage? |
| 🚩 Rugcheck Flags | Mutable metadata, known scam patterns |
| 🕵️ Insider Activity | Coordinated wallet networks |
| 💸 Transfer Fee | Hidden tax on transfers |
| ✅ Verification | Is it listed on Jupiter? |

## OpenClaw Discord v2 Ready

Tested for OpenClaw Discord channel delivery behavior (v2026.2.14+):
- Sends a compact first message (tier, score, top red flags), then expands on demand
- Uses short follow-up chunks for long reports to keep channel readability high
- Supports component-style follow-up actions when available (`Show Full Risk Breakdown`, `Show Data Sources`, `Re-Run Check`)

## Risk Tiers

| Score | Tier | Meaning |
|-------|------|---------|
| 0-15 | 🟢 SAFE | Low risk indicators across the board |
| 16-35 | 🟡 CAUTION | Some yellow flags — proceed carefully |
| 36-55 | 🟠 WARNING | Multiple risk factors detected |
| 56-75 | 🔴 DANGER | Significant red flags |
| 76-100 | ⛔ CRITICAL | Extreme risk — stay away |

## Example Report

```
╔══════════════════════════════════════════════════════════════╗
║  🛡️  Anvil AI Rug Report                                 ║
╠══════════════════════════════════════════════════════════════╣
║  Token:  $Bonk (Bonk)
║  Mint:   DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
║  Risk:   12/100 🟢 SAFE
╚══════════════════════════════════════════════════════════════╝

## 📊 Market Overview

| Metric | Value |
|--------|-------|
| Price | 0.000007092 |
| Market Cap | $624.1M |
| FDV | $630.3M |
| 24h Volume | $430.6K |
| Total Liquidity | $1.6M |
| Holders | 966796 |

## 🔍 Risk Breakdown

🟢 **Mint Authority        ** ░░░░░░░░░░  0/10  (×2.0)
   └─ Mint authority revoked — no new tokens can be created

🟢 **Freeze Authority      ** ░░░░░░░░░░  0/10  (×1.5)
   └─ No freeze authority — tokens cannot be frozen

🟡 **Holder Concentration  ** ████░░░░░░  4/10  (×1.5)
   └─ Moderate concentration — top 10 hold 40.0% of supply

🟢 **LP Lock Status        ** ░░░░░░░░░░  0/10  (×2.0)
   └─ LP strongly locked (100.0%) — liquidity pull very unlikely

🟢 **Token Age             ** ░░░░░░░░░░  0/10  (×1.0)
   └─ Mature token (1147 days / 3+ years)

🟢 **Liquidity Depth       ** ░░░░░░░░░░  0/10  (×1.0)
   └─ Strong liquidity ($1,602,345)

🟡 **Rugcheck Flags        ** ███░░░░░░░  3/10  (×1.0)
   └─ 1 risk flag(s): Mutable metadata

🟢 **Insider Activity      ** ░░░░░░░░░░  0/10  (×1.5)
   └─ No insider networks detected

🟢 **Transfer Fee          ** ░░░░░░░░░░  0/10  (×1.0)
   └─ No transfer fee

🟢 **Verification          ** ░░░░░░░░░░  0/10  (×0.5)
   └─ Jupiter strict-listed — highest verification tier

## 📈 Composite Score

  [██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 12/100 🟢 SAFE

  0         20        40        60        80       100
  |--SAFE---|--CAUTION-|--WARNING-|--DANGER--|CRITICAL|
```

## How to Use

### As an Agent Skill

Just ask naturally:
- *"Rug check DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"*
- *"Is BONK safe?"*
- *"Is this token a scam? [paste address]"*
- *"Check this pump.fun token for me"*

### Standalone CLI

```bash
# Resolve a token name or address
bash scripts/detect-token.sh bonk
bash scripts/detect-token.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263

# Run full risk analysis
bash scripts/analyze-risk.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263

# Generate visual report
bash scripts/analyze-risk.sh DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 | bash scripts/format-report.sh
```

## Requirements

| Dependency | Purpose |
|-----------|---------|
| `bash` 4+ | Script runtime |
| `curl` | HTTP requests |
| `jq` | JSON parsing |
| `bc` | Floating-point math |

**No API keys required.** All data sources are free, public endpoints.

## Data Sources

| Source | What It Provides |
|--------|-----------------|
| [Rugcheck.xyz](https://rugcheck.xyz) | Risk flags, holder analysis, LP lock status, insider detection |
| [DexScreener](https://dexscreener.com) | Market data, pricing, liquidity, token resolution |
| [Solana RPC](https://api.mainnet-beta.solana.com) | On-chain mint/freeze authority verification |

## Architecture

```
User Input → detect-token.sh → analyze-risk.sh → format-report.sh → Report
                  │                   │
                  ├─ DexScreener      ├─ Rugcheck.xyz
                  └─ Solana RPC       ├─ DexScreener
                                      └─ Solana RPC
                  
All scripts share: common.sh (HTTP, rate limiting, formatting)
```

## Limitations

- **Solana only** — EVM chains not supported (yet)
- **Rugcheck data gaps** — Some stablecoins (USDC, USDT) have incomplete holder/market data on Rugcheck; the tool flags this transparently
- **Not financial advice** — Risk scores are algorithmic estimates, not guarantees
- **Public RPC limits** — Solana's free RPC has rate limits; heavy concurrent use may see 429 errors (handled with retries)
- **Jupiter verification** — Rugcheck's Jupiter verification data may lag behind Jupiter's actual listings

## More from Anvil AI

This skill is part of the **Anvil AI** open-source skill suite.

| Skill | What it does |
|-------|-------------|
| **[vibe-check](https://clawhub.com/skills/vibe-check)** | AI code quality + security review scorecard. |
| **[prom-query](https://clawhub.com/skills/prom-query)** | Prometheus metrics + alert triage from natural language. |
| **[dep-audit](https://clawhub.com/skills/dep-audit)** | Unified dependency vulnerability auditing (npm, pip, Cargo, Go) |
| **[rug-checker](https://clawhub.com/skills/rug-checker)** | This skill — Solana token rug-pull risk analysis |


---

Built by **[Anvil AI](https://anvil-ai.io)**.

