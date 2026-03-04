---
name: hourly-momentum-trader
version: 1.0.0
description: Momentum-based trading agent for hourly crypto candles. Uses RSI, MACD, OBV, EMA, and Bollinger Band confluence to score directional momentum from -10 to +10. Optimized for Polymarket hourly binary markets and short-term spot/perp entries. Use when you need hourly candle signals, momentum scoring, short-term crypto direction, or Polymarket hourly market edge detection.
author: JamieRossouw
tags: [momentum, hourly, crypto, polymarket, rsi, macd, signals, trading]
---

# Hourly Momentum Trader

Directional momentum scoring for 1-hour crypto candles with Polymarket binary market integration.

## Momentum Score System (-10 to +10)

Each signal contributes to the composite score:

| Signal | Bullish (+) | Bearish (-) | Weight |
|--------|------------|------------|--------|
| RSI | <40 oversold | >70 overbought | ±1 |
| RSI divergence | Bull div | Bear div | ±2 |
| MACD cross | Bullish cross | Bearish cross | ±1 |
| MACD histogram | Rising | Falling | ±1 |
| EMA cross | EMA20>EMA50 | EMA20<EMA50 | ±1 |
| EMA200 | Price above | Price below | ±1 |
| Bollinger | Near lower (oversold) | Near upper (overbought) | ±1 |
| OBV trend | Rising (accumulation) | Falling (distribution) | ±1 |
| OBV divergence | Bull div | Bear div | ±2 |
| Volume | High volume on move | Low volume | ±1 |

## Live Bet Integration (Polymarket Argus Strategy)

Combine momentum score with Polymarket market odds:

```python
# Edge formula
our_prob = 0.50 + (momentum_score * 0.05)  # score 6 = 80% confidence
market_prob_up = polymarket_up_price  # e.g. 0.35 (35% UP consensus)
edge = our_prob - market_prob_up  # e.g. 0.80 - 0.35 = 45% edge!

# Bet when:
# - abs(momentum_score) >= 3
# - abs(edge) >= 0.10 (10%)
# - market is fresh (<30 min old)
# - USDC.e balance >= $5
```

## Counter-Consensus Setups (L023)

Highest-EV Polymarket plays:
- Momentum score ≥+3 AND market DOWN >70% → **BET UP** (counter-consensus, 3-5x payout)
- Momentum score ≤-3 AND market UP >70% → **BET DOWN** (counter-consensus, 3-5x payout)

Example: SOL score=+4, Polymarket DOWN 80% → buy UP at 0.20 → if wins: 5x return

## Signals Output Format

```json
{
  "asset": "BTC",
  "score": 3,
  "rsi": 64.9,
  "rsi_status": "neutral",
  "macd_hist": 10.39,
  "macd_direction": "rising",
  "obv_trend": "rising",
  "bb_pct": 0.72,
  "ema_cross": "bullish",
  "bias": "BULLISH",
  "confidence_pct": 65,
  "polymarket_edge": {
    "btc_4pm_et": { "market_up": 0.515, "our_p": 0.65, "edge": 0.135, "direction": "UP" }
  }
}
```

## Watchlist (Default)

BTC, ETH, SOL, XRP, ATOM, ADA, SUI, LTC, NEAR, AVAX, BNB, LINK, DOT, TRX, DOGE
