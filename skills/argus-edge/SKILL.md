---
name: argus-edge
version: 1.0.0
description: Argus-style prediction market edge detection and betting strategy. Computes expected value from TA-implied probability vs market odds, sizes bets via Kelly criterion, and applies freshness/consensus guards. Validated at 77.8% win rate on primary (fresh) Polymarket bets. Use for prediction market betting, EV calculation, Polymarket strategy, or market making.
author: JamieRossouw
tags: [polymarket, prediction-markets, edge, kelly, betting-strategy, ev, crypto]
---

# Argus Edge — Prediction Market Betting Engine

The complete Argus strategy for finding and exploiting edge in crypto prediction markets.

## Core Formula

```
Edge = our_P(win) - market_implied_P(win)
Bet when: edge ≥ 10% AND fresh market (<30 min old) AND TA score ≥ ±2
Kelly stake = (edge × bankroll) / odds
```

## Strategy Rules

### Freshness Guard
- Skip markets >92% consensus (dead signal, L020)
- Prioritize markets <30 min old (primary window)
- Primary bets WR: 77.8% vs overall 56.6%

### Counter-Consensus Rule (L023)
TA score ≥+1 + market DOWN >80% + ≥20 min remaining → bet UP (counter-consensus has positive EV, validated at 5x+ payout)

### Asset Calibration
| Asset | TA Reliability | Bias | Min Score |
|-------|---------------|------|-----------|
| BTC | 0.75 | Neutral | ±3 |
| ETH | 0.80 | UP+0.05 | ±2 |
| SOL | 0.90 | UP+0.05 | ±1 |
| XRP | 0.70 | UP+0.08 | ±2 |

## Usage

```
Use argus-edge to find the best Polymarket bet right now

Use argus-edge to calculate edge on BTC 11am ET market

Use argus-edge for full market scan with Kelly sizing
```

## Battle-Tested
Derived from 100+ live Polymarket bets. 25 documented lessons (L001–L025).
