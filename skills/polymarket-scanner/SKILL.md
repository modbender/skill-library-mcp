---
name: polymarket-scanner
description: Automated Polymarket prediction market scanner and trader via Simmer API. Use when analyzing prediction markets, scanning for trading opportunities, executing virtual ($SIM) or real (USDC) trades, checking positions, or managing a Polymarket portfolio. Triggers on "polymarket", "prediction market", "simmer", "trade", "market scan", "betting odds", "arbitrage opportunities".
version: 1.0.0
---

# Polymarket Scanner

Automated prediction market scanner that finds mispriced markets and executes trades via the Simmer Markets API.

## Setup

### Required
- `SIMMER_API_KEY` env var (get from https://simmer.markets)
- Simmer agent registered and claimed

### Optional
- Telegram bot for trade notifications

## Commands

### Auto-scan (default)
```bash
python scripts/scanner.py
```
Scans top 20 opportunities, filters by score/divergence/warnings, executes qualifying trades.

### Check positions
```bash
python scripts/scanner.py --positions
```

### Check balance
```bash
python scripts/scanner.py --status
```

## Trading Rules (built-in)

| Rule | Virtual ($SIM) | Real (USDC) |
|------|---------------|-------------|
| Single trade | ≤10% balance | ≤$100 |
| Daily limit | ≤30% balance | ≤$500 |
| Stop-loss | -15% | -10% |
| Max positions | 5 | 3 |
| Min opportunity score | 25 | 40 |
| Min divergence | 3% | 5% |

## Strategy
1. **Cross-platform arbitrage** — Price divergence between Polymarket and external sources
2. **Momentum shifts** — Rapid price changes indicating mispricing
3. **Data-driven events** — Weather, economic data, quantifiable outcomes preferred

## Architecture
```
Cron (every 4h) → scanner.py → Simmer API
  ├── Get balance & positions
  ├── Scan opportunities (score, divergence, warnings)
  ├── Filter by trading rules
  ├── Execute qualifying trades (SIM auto, USDC manual)
  └── Log to trading_log.jsonl
```

## Risk Controls
- All trades logged to `trading_log.jsonl`
- Serious spread warnings (>10%) auto-skip
- Already-held markets auto-skip
- Balance <$100 auto-stop
- Real USDC trades require human confirmation
