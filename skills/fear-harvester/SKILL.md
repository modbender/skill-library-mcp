---
name: FearHarvester Skill
description: Autonomous DCA agent for extreme fear markets.
---

# FearHarvester Skill

Autonomous DCA agent for extreme fear markets.

## Strategy
- Monitor Fear & Greed index continuously
- When F&G < 10 (Extreme Fear): DCA into BTC/ETH
- When F&G > 50 (Neutral/Greed recovery): rebalance into yield
- Removes human emotion from "buy the fear"

## Usage
```bash
uv run python scripts/backtest.py --start 2018-01-01 --capital 10000
uv run python scripts/signals.py --live
uv run python scripts/executor.py --dry-run
```

## Historical edge (2018-2024)
Buying F&G < 10, holding 90d → 40-80% average return
