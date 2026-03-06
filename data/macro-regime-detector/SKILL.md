---
name: macro-regime-detector
version: 1.0.0
description: Detect the current macro regime (Risk-On, Risk-Off, Inflationary, Deflationary, Stagflation) using multi-source intelligence. Combines Fear & Greed, DXY, yield curve, VIX, gold/BTC ratio, Reddit sentiment, and major news events. Use when you need macro regime analysis, risk-on vs risk-off determination, portfolio positioning advice, or crypto market context.
author: JamieRossouw
tags: [macro, regime, risk-on, risk-off, sentiment, inflation, crypto, investing]
---

# Macro Regime Detector

Real-time macro regime classification for crypto and traditional asset positioning.

## Regimes Detected

| Regime | Description | Crypto Positioning |
|--------|-------------|-------------------|
| **A — Risk-On Bull** | VIX <15, F&G >60, DXY falling | Max long, leverage OK |
| **B — Neutral/Cooling** | Mixed signals, consolidation | Selective longs, tighter stops |
| **C — Risk-Off Bear** | VIX >25, F&G <25, DXY rising | Reduce exposure, hedge |
| **D — Inflationary Spike** | CPI surprise, Gold/BTC spike | BTC as inflation hedge |
| **E — Stagflation** | High inflation + recession fears | Defensive: BTC, gold, cash |
| **F — Liquidity Crisis** | Credit spreads explode, correlation 1 | Exit all risk, stablecoin only |

## Signal Sources

- **Fear & Greed** (`alternative.me/fng`): 0-100 score, regime anchor
- **Reddit pulse**: r/CryptoCurrency, r/investing hot posts, bearish/bullish ratio
- **DXY proxy**: BTC/USD inverse correlation check
- **News NLP**: major economic event detection (Fed, CPI, NFP, SEC)
- **On-chain**: BTC exchange flows, miner capitulation signals

## How to Use

Ask: *"What macro regime are we in?"* or *"Should I be long or short crypto right now?"*

Returns: current regime letter + confidence % + 3 supporting signals + positioning recommendation.

## Regime History (current session)

- Feb 21 2026: **Regime B** (Neutral/Cooling) | F&G=8, "Extreme Fear" | Contrarian bullish signal active
