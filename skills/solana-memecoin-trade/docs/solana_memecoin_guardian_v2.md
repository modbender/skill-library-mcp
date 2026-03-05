# Solana Memecoin Guardian v2  
## OpenClaw Skill Specification

## Overview
Solana Memecoin Guardian v2 is a dual-engine trading skill for Solana memecoins that:
- Selectively copy-trades high-quality smart wallets
- Executes independent AI-driven trades
- Applies strict risk gates and portfolio limits
- Prioritizes capital preservation over aggressive profit chasing

The system is designed to skip most opportunities and only execute when risk conditions are acceptable.

## Core Architecture
- Copy Trade Engine
- AI Analysis Engine
- Shared Risk Gate
- Position Manager
- Rug Alarm System
- Risk Budget Orchestrator

All trade paths must pass through the same Risk Gate.

## Risk Budget Allocation
```yaml
risk_budget_split:
  copy_trade_pct: 60
  ai_trade_pct: 40
```
If daily loss limit is 2.5% of bankroll:
- Copy trades: 1.5%
- AI trades: 1.0%

## Data Sources
- Pump.fun: new/trending/graduating
- DexScreener: liquidity, volume, tx count, price change, pair age, impact estimates
- Bags: smart wallet holdings + internal watchlist
- Smart wallet monitor: buy/sell events

## Risk Gate
```yaml
risk_gates:
  min_liquidity_usd: 50000
  max_entry_slippage_pct: 1.5
  cooldown_token_age_min: 15
  reject_if_mint_authority: true
  reject_if_freeze_authority: true
  max_single_holder_pct: 12
  max_top10_holders_pct: 50
  reject_if_tx_anomaly: true
  max_price_impact_pct: 1.8
```
Fail ⇒ SKIP. Missing authority/holders ⇒ SKIP.

## Copy Trade Engine
Qualification: min 30 trades, win rate ≥ 55%, profit factor ≥ 1.3

Rules:
```yaml
smart_wallets:
  max_price_chase_pct: 20
  copy_delay_sec_min: 30
  copy_delay_sec_max: 120

copy_trade_rules:
  min_age_min: 20
  max_wallet_buys_per_hour: 8
  require_trade_count_5m: 80
```

## AI Trade Engine
Rule-based scoring and stability checks.
```yaml
ai_signal:
  stability_window_min: 20
  min_tx5m: 100
  max_vol_per_tx_usd: 1200
  max_price_change_5m_pct: 15
  require_liq_non_decreasing: true
  riskScore_threshold: 30
```

## Portfolio
```yaml
portfolio:
  bankroll_usd: 1000
  max_open_positions: 3
  max_trades_per_day: 4
  daily_loss_limit_pct: 2.5
  risk_per_trade_pct_copy: 0.5
  risk_per_trade_pct_ai: 0.35
```

## Exits
```yaml
exits:
  stop_loss_pct: 10
  tp1_pct: 20
  tp1_sell_pct: 35
  tp2_pct: 60
  tp2_sell_pct: 35
  trailing_stop_pct: 12
```

## Rug alarms
```yaml
rug_alarms:
  lp_drop_pct: 25
  lp_drop_window_min: 5
  holder_spike_pct: 6
  price_impact_spike_pct: 3.0
```

## Philosophy
Missing 100 pumps is acceptable.  
Surviving one rug is mandatory.
