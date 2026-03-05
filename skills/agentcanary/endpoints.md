---
name: agentcanary
description: Market intelligence for AI agents. Macro regime detection, risk scoring, trading signals, whale alerts, funding arbitrage, and market briefs from 250+ sources. Not raw data. Intelligence. API-only, no secrets in the prompt.
---

# AgentCanary

Market intelligence for AI agents. Macro regime detection, risk scoring, trading signals, whale alerts, funding arbitrage, and market briefs — from 250+ sources. Not raw data. Intelligence.

API-only. No secrets in the prompt. No binaries. No local execution. No filesystem access.

**Status:** API is live. Paid tiers opening soon. Free tier: real-time prices (50 calls/day).
**Live proof:** [@AgentCanary on Telegram](https://t.me/AgentCanary) — 3x/day auto-generated market intelligence from the same API.
**Website:** [agentcanary.ai](https://agentcanary.ai)

> This API powers Proximity, a crypto intelligence iOS app with 6 months of daily usage across 20+ countries.

---

## Security

AgentCanary is designed for the post-ClawHavoc world.

- **API-only** — HTTP GET calls returning JSON. No local code execution, no binaries, no shell commands.
- **No secrets in the prompt** — wallet-based auth when billing is live. No API keys pass through the LLM context window.
- **Read-only** — the skill fetches data. It cannot write, modify, or access your filesystem.
- **No filesystem access** — no file reads, no file writes, no directory listing.
- **VirusTotal verified** — clean scan published before launch.

824 malicious skills were found on ClawHub. Crypto and finance is the #1 target category. AgentCanary is the finance skill that can't steal from you.

---

## Default Agent Pattern

Most autonomous agents use AgentCanary as a **risk gate**, not a trade signal.

```
1. Call /macro-snapshot/regime every 4–6 hours
2. If Risk-Off → suppress trading, reduce exposure
3. If Risk-On → allow strategy execution
4. Use severity alerts as interrupts, not drivers
5. Call /signal-state before entering positions for confirmation
```

AgentCanary is risk intelligence middleware. It tells your agent **when conditions are favorable** — your agent decides what to do with that context.

---

## What AgentCanary Does Not Do

AgentCanary does not:

- **Predict prices** — it classifies regimes and states, not future values
- **Guarantee returns** — regime context improves decisions but does not eliminate risk
- **Replace execution logic** — it provides intelligence, not order placement
- **Optimize strategies** — it provides macro/micro context for your strategy to consume
- **Provide financial advice** — all outputs are informational, not recommendations

This is context intelligence, not alpha signals.

---

## Signal Stability & Cadence

Not all signals update at the same frequency. Call accordingly.

| Signal | Update Frequency | Recommended Cadence | Noise Level |
|---|---|---|---|
| Macro regime | Every 6h (FRED data lag) | Every 4–6 hours | Very low |
| Signal states (1d) | Daily close | Every 4–6 hours | Low |
| Signal states (4h) | Every 4h candle | Every 1–2 hours | Moderate |
| Whale alerts | Real-time | Every 15–30 min | Event-driven |
| Funding rates | Every 8h (funding interval) | Every 4–8 hours | Low |
| Market structure | Near real-time | Every 30–60 min | Moderate |
| Breaking news | Real-time | Every 15–30 min | Event-driven |
| Prices | Near real-time | As needed | N/A |

---

## When AgentCanary Can Be Wrong

- **Sudden geopolitical shocks** — regime indicators are backward-looking by design
- **Exchange-specific outages** — orderbook, funding, and liquidation data may be partial
- **Thin liquidity regimes** — market structure signals may overweight noise
- **FRED data delays** — some macro series publish with a 1–4 week lag

The API returns the best available interpretation of the best available data. It does not hallucinate, fabricate, or extrapolate beyond its inputs.

---

## What Your Agent Gets

### 22 Capability Areas

---

### 1. Macro Regime Detection

Current macro regime with composite scores, flags, and natural language explanation. Business cycle phase, risk gauge, growth/inflation direction, and z-scores on 26 FRED indicators.

**Endpoints:** `GET /macro-snapshot` · `GET /macro-snapshot/regime`

**Response (`/macro-snapshot/regime`):**
```json
{
  "asOf": "2026-02-20T19:32:58Z",
  "regime": {
    "label": "Risk-On · Neutral",
    "explanation": "clear risk-on conditions: investors are favoring risk assets and credit conditions are supportive. Policy stance is on hold...",
    "flags": ["RISK_ON", "LOW_STRESS"],
    "scores": {
      "riskOn": 5.69,
      "tightening": 0,
      "inflation": -1.35,
      "liquidity": 1.10,
      "stress": 0.50
    }
  }
}
```

**Response (`/macro-snapshot` — includes business cycle + z-scores):**
```json
{
  "asOf": "2026-02-20T19:32:57Z",
  "regime": { "label": "Risk-On · Neutral", "flags": ["RISK_ON", "LOW_STRESS"], "scores": { ... } },
  "businessCycle": {
    "phase": "EXPANSION",
    "riskGauge": { "value": 35, "level": "LOW" },
    "growth": { "direction": "UP" },
    "inflation": { "direction": "DOWN" }
  },
  "detail": {
    "series": {
      "10Y_yield": { "value": 4.28, "z20": 1.2 },
      "DXY": { "value": 104.3, "z20": 0.8 },
      "2s10s_spread": { "value": 0.32, "z20": -0.3 },
      "HY_spread": { "value": 3.1, "z20": -0.4 }
    }
  }
}
```

---

### 2. AI Market Analysis

Daily AI-generated market report: sentiment, market phase, fear & greed index, narratives, movers, correlations, divergences, and alerts.

**Endpoint:** `GET /market-analysis/latest`

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-02-20T16:03:26Z",
    "todaysPulse": {
      "sentiment": "neutral",
      "summary": "Today's market displays mixed movements with cryptocurrencies experiencing cautious optimism...",
      "overallSentiment": {
        "direction": "neutral",
        "confidence": 5,
        "description": "Markets demonstrate stability with minor fluctuations..."
      },
      "marketPhase": {
        "phase": "accumulation",
        "description": "Investors are cautiously accumulating positions..."
      },
      "fearAndGreed": {
        "value": 9,
        "interpretation": "Extreme Fear"
      }
    }
  }
}
```

---

### 3. Breaking News

Real-time RSS from Bloomberg, FT, Decrypt, CoinDesk, CoinTelegraph. Auto-categorized, auto-extracted tickers (crypto + stock + forex), FinBERT sentiment with confidence scores.

**Endpoint:** `GET /news/breaking?limit=100`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "title": "Fed Signals Higher-for-Longer as CLARITY Act Stalls",
      "description": "...",
      "url": "https://...",
      "source": "Bloomberg",
      "sourceId": "bloomberg",
      "publishedAt": "2026-02-20T13:45:00Z",
      "primaryCategory": "macro",
      "categories": ["general", "market"],
      "tags": ["fed", "rates", "policy"],
      "tickers": ["SPY"],
      "cryptoTickers": [],
      "stockTickers": ["SPY"],
      "forexPairs": ["DXY"],
      "sentiment": "POSITIVE",
      "sentimentScore": 0.40,
      "sentimentMethod": "finbert",
      "finbertConfidence": 0.40,
      "finbertScores": {
        "negative": 0.12,
        "neutral": 0.48,
        "positive": 0.40
      },
      "priority": 2,
      "wordCount": 245
    }
  ]
}
```

Sentiment values: `VERY_POSITIVE`, `POSITIVE`, `NEUTRAL`, `NEGATIVE`, `VERY_NEGATIVE`.

---

### 4. Newsletter Intelligence

50+ newsletters ingested daily. Full-text parsed, tickers extracted, tagged, categorized, FinBERT scored.

**Endpoint:** `GET /newsletters?limit=100`

**Response:**
```json
{
  "success": true,
  "count": 48,
  "timeframe": "48 hours",
  "newsletters": [
    {
      "id": 7530,
      "subject": "Whale Flow Shift: Exchange Redistribution Grows",
      "senderEmail": "newsletter@cryptoquant.com",
      "mailDate": "2026-02-20T14:00:00Z",
      "categories": ["crypto", "news"],
      "tags": ["whale", "exchange", "flow"],
      "tickers": ["BTC", "ETH"],
      "sentiment": "positive",
      "content": "..."
    }
  ]
}
```

---

### 5. Social Messages (X & Telegram)

300+ messages/day scraped from 200+ X and Telegram channels. Each message has FinBERT sentiment, tickers, categories, and source URL.

**Endpoint:** `GET /xtg-messages?limit=300`

**Response:**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "messageId": 311962,
        "platform": "telegram",
        "content": "Trump plans new 'general customs duty' following court defeat",
        "sentiment": "neutral",
        "categories": [],
        "tickers": ["TRUMP"],
        "tags": [],
        "url": "https://t.me/hs_cryptonews/5352",
        "timestamp": "2026-02-20T16:56:02Z",
        "finbertSentiment": {
          "sentiment": "neutral",
          "score": 0,
          "confidence": 0.87,
          "scores": {
            "negative": 0,
            "neutral": 0.87,
            "positive": 0
          }
        }
      }
    ]
  }
}
```

---

### 6. Signal States

ROC-based regime classification on 100 coins across daily and 4-hour timeframes. States: `IGNITION`, `ACCUMULATION`, `DISTRIBUTION`, `CAPITULATION`.

**Endpoint:** `GET /signal-state`

**Response:**
```json
{
  "success": true,
  "count": 100,
  "data": [
    {
      "coinId": "2bd4bbbb9e",
      "symbol": "btc",
      "currentPrice": 67718,
      "marketCap": 1353819006705,
      "timeframes": {
        "1d": {
          "state": "IGNITION",
          "roc7": 1.12,
          "acc7": 1.94,
          "lastRocCrossAt": "2026-02-20T03:30:00Z"
        },
        "4h": {
          "state": "IGNITION",
          "roc7": 0.87,
          "acc7": 0.59
        }
      },
      "lastUpdated": "2026-02-20T19:00:00Z"
    }
  ]
}
```

Signal state meanings:
- **IGNITION** — positive momentum with positive acceleration (early trend)
- **ACCUMULATION** — negative momentum with positive acceleration (bottoming)
- **DISTRIBUTION** — positive momentum with negative acceleration (topping)
- **CAPITULATION** — negative momentum with negative acceleration (accelerating decline)

---

### 7. Real-Time Prices

1,181 assets: 941 crypto, 195 stocks, 34 FX pairs, 10 commodities, ETFs. One endpoint.

**Endpoint:** `GET /realtime-prices`

**Response:**
```json
[
  {
    "symbol": "btc",
    "price": 67716,
    "marketcap": 1353819006705,
    "volume": 51785644228,
    "type": "crypto",
    "source": "coingecko",
    "timestamp": "2026-02-20T19:17:29Z"
  },
  {
    "symbol": "COIN",
    "price": 170.01,
    "type": "stock",
    "timestamp": "2026-02-20T19:15:00Z"
  },
  {
    "symbol": "XAU/USD",
    "price": 2934.50,
    "type": "commodity",
    "timestamp": "2026-02-20T19:20:00Z"
  }
]
```

Note: stocks return `price` only (no volume/marketcap). Crypto includes full market data.

---

### 8. Market Structure

Composite BTC snapshot: funding rates across exchanges, liquidations, open interest, orderbook imbalance, crowding and volatility scores.

**Endpoint:** `GET /market-structure`

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "timeframe": "24h",
  "timestamp": "2026-02-20T19:30:00Z",
  "data": {
    "funding": {
      "currentRate": 0.0000671,
      "avgRate": 0.0000407,
      "rateChange": 0.0000264,
      "currentOI": 177355.41,
      "oiChangePercent": 5.93,
      "fundingTrend": "flat",
      "exchanges": [
        { "exchange": "hyperliquid", "fundingRate": 0.0000032, "openInterest": 20054.57 },
        { "exchange": "bybit", "fundingRate": 0.0001, "openInterest": 46456.79 }
      ]
    }
  },
  "scores": { ... },
  "signal": { ... }
}
```

---

### 9. Orderbook Analytics

8 liquidity bands, top bid/ask walls with notional USD, wall persistence tracking, liquidity change detection.

**Endpoints:**
- `GET /orderbook/depth?symbol=BTCUSDT&marketType=spot&exchange=binance`
- `GET /orderbook/depth/history?symbol=BTCUSDT&marketType=spot&exchange=binance`
- `GET /orderbook/wall-persistence?symbol=BTCUSDT&marketType=spot&exchange=binance&side=bid&priceBucket=84000`
- `GET /orderbook/liquidity-change?symbol=BTCUSDT&marketType=spot&exchange=binance`

**Response (`/orderbook/depth`):**
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-02-20T19:33:00Z",
    "metadata": {
      "baseAsset": "BTC",
      "exchange": "binance",
      "marketType": "spot",
      "symbol": "BTCUSDT"
    },
    "topBidWalls": [
      { "price": 66666, "size": 22.61, "notionalUsd": 1507016, "distancePct": 1.60 },
      { "price": 66500, "size": 16.08, "notionalUsd": 1069454, "distancePct": 1.85 }
    ],
    "topAskWalls": [
      { "price": 68000, "size": 18.42, "notionalUsd": 1252560, "distancePct": 0.35 }
    ]
  }
}
```

---

### 10. Whale Alerts

On-chain whale transactions from Whale Alert. Symbol, amount, USD value, transaction description.

**Endpoint:** `GET /whale-alerts`

**Response:**
```json
[
  {
    "alertId": 8060196,
    "timestamp": "2026-02-20T18:53:42Z",
    "symbol": "BTC",
    "amount": 3765,
    "value": 255371985,
    "text": "transferred from unknown wallet to unknown wallet",
    "link": "ed1912d9797db53b24fd7a00"
  }
]
```

---

### 11. Hyperliquid Whale Alerts

Real-time whale position changes on Hyperliquid with entry price, liquidation price, and position value.

**Endpoint:** `GET /hyperliquid-whale-alerts`

**Response:**
```json
[
  {
    "user": "0x68a4...c01a",
    "symbol": "BTC",
    "position_size": 29.04,
    "entry_price": 67799.20,
    "liq_price": 66962.68,
    "position_value_usd": 1967589.67,
    "position_action": 2,
    "create_time": "2026-02-20T19:27:29Z"
  }
]
```

---

### 12. Hyperliquid Whale Positions

Current whale positions with leverage, margin, unrealized PnL, and mark price.

**Endpoint:** `GET /hyperliquid-whale-positions`

**Response:**
```json
[
  {
    "symbol": "ADA",
    "user": "0x123d...3bff",
    "entry_price": 0.4537,
    "mark_price": 0.28242,
    "position_size": 6502562,
    "position_value_usd": 1836258.48,
    "leverage": 10,
    "margin_mode": "cross",
    "margin_balance": 183625.85,
    "unrealized_pnl": -1113750.99,
    "funding_fee": -1400.94,
    "liq_price": 0,
    "create_time": "2025-10-08T06:38:25Z",
    "update_time": "2026-02-20T19:29:35Z"
  }
]
```

---

### 13. Funding Rate Arbitrage

Cross-exchange funding rate arbitrage opportunities ranked by APR. 347 pairs scanned.

**Endpoints:** `GET /fundingrate/arbitrage/top` (top 10) · `GET /fundingrate/arbitrage/latest` (all 347)

**Response:**
```json
[
  {
    "symbol": "RPL",
    "buy": {
      "exchange": "Bybit",
      "open_interest_usd": 2263414,
      "funding_rate_interval": 1,
      "funding_rate": -0.250035
    },
    "sell": {
      "exchange": "Bitget",
      "open_interest_usd": 1668842,
      "funding_rate_interval": 1,
      "funding_rate": -0.0939
    },
    "apr": 1367.74,
    "funding": 0.1561,
    "fee": 0.03,
    "spread": 0.72,
    "next_funding_time": "2026-02-20T20:00:00Z"
  }
]
```

---

### 14. Technical Indicators (29 per coin)

RSI, MACD, Bollinger, Ichimoku, VWAP, PSAR, and 23 more. Composite buy/sell/neutral signal. 365 daily data points.

**Endpoint:** `GET /cointa?id={coinId}`

**Response:**
```json
{
  "success": true,
  "data": {
    "coinId": "2bd4bbbb9e",
    "timeframe": "1d",
    "latestPrice": 67583,
    "priceChange24h": 0.94,
    "dataPoints": 365,
    "oscillators": { "signal": "sell", "buy": 1, "sell": 3, "neutral": 6 },
    "movingAverages": { "signal": "sell", "buy": 0, "sell": 14, "neutral": 0 },
    "summary": { "signal": "sell", "buy": 1, "sell": 17, "neutral": 6 },
    "indicators": {
      "rsi": { "current": 36.27, "previous": 34.45, "signal": "neutral" },
      "macd": { "value": -2340, "signal": "sell" },
      "bollingerBands": { "upper": 75200, "middle": 70100, "lower": 65000 }
    }
  }
}
```

---

### 15. RSI Screening

606 coins, 14-period RSI. Ranked overbought/oversold lists. Also supports multi-timeframe RSI (5m, 15m, 1h, 4h, 1d, 1w) per coin.

**Endpoints:**
- `GET /coin-rsi/statistics` — full screening (overbought + oversold lists)
- `GET /coin-rsi?coinid={coinId}` — single coin RSI history (100 data points)
- `GET /coin-rsi/multi?coinids={coinId}` — 6 timeframes for one coin

**Response (`/coin-rsi/statistics`):**
```json
{
  "timestamp": "2026-02-20T18:00:00Z",
  "period": 14,
  "timeframe": "1h",
  "total": 606,
  "overbought": [
    { "symbol": "grp", "coinid": "f7b9dd8ea1", "rsi": 96.44 }
  ],
  "oversold": [
    { "symbol": "link", "coinid": "abc123", "rsi": 22.4 }
  ],
  "neutral": [ ... ]
}
```

**Response (`/coin-rsi/multi`):**
```json
{
  "period": 14,
  "coins": [
    {
      "coinid": "2bd4bbbb9e",
      "symbol": "btc",
      "timeframes": {
        "5m":  { "rsi": 48.32, "timestamp": "2026-02-20T19:25:00Z" },
        "15m": { "rsi": 51.92, "timestamp": "2026-02-20T19:15:00Z" },
        "1h":  { "rsi": 58.33, "timestamp": "2026-02-20T18:00:00Z" },
        "4h":  { "rsi": 53.05, "timestamp": "2026-02-20T16:00:00Z" },
        "1d":  { "rsi": 34.32, "timestamp": "2026-02-19T00:00:00Z" },
        "1w":  { "rsi": 29.65, "timestamp": "2026-02-12T00:00:00Z" }
      }
    }
  ]
}
```

---

### 16. ROC Momentum

90-day rate of change with acceleration, volatility, and percentile bands.

**Endpoints:** `GET /roc/{coinId}` · `GET /roc/{coinId}/multi`

**Response (`/roc/{coinId}`):**
```json
{
  "success": true,
  "coinId": "2bd4bbbb9e",
  "symbol": "btc",
  "currentPrice": 67660,
  "dataPoints": 90,
  "data": [
    {
      "timestamp": "2026-02-19T00:00:00Z",
      "roc_7": 1.12,
      "roc_14": -3.45,
      "roc_30": -8.20,
      "roc_90": -26.46,
      "roc_acc_7": 1.94,
      "roc_acc_14": 0.45,
      "roc_std_30": 2.02,
      "roc_p20_90": -1.67,
      "roc_p80_90": 1.10,
      "roc_bandwidth_90": 2.78
    }
  ]
}
```

---

### 17. Stablecoin Dominance

USDT and USDC dominance as risk-on/risk-off signals. 169 data points of historical dominance.

**Endpoints:** `GET /usdt-dominance` · `GET /usdc-dominance`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "time": 1771009200,
      "dominance": 7.79,
      "usdtMarketCap": 183827196218,
      "totalMarketCap": 2360762748154
    }
  ],
  "stats": {
    "current": 7.79,
    "min": 6.12,
    "max": 8.45
  }
}
```

Interpretation: Rising stablecoin dominance = Risk-Off (capital moving to safety). Falling = Risk-On.

---

### 18. Exchange Volumes

Aggregated exchange trading volumes. 168 data points of historical volume.

**Endpoint:** `GET /exchange-volumes`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "time": 1771012800,
      "volume": 40363280838.77
    }
  ],
  "metadata": { ... }
}
```

---

### 19. Exchange Wallet Assets

39+ wallets across major exchanges. Balance, USD value, wallet address per exchange.

**Endpoint:** `GET /exchange-assets?symbol=BTC`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "time": 1771549200,
      "timestamp": "2026-02-20T01:00:00Z",
      "assets": [
        {
          "exchange_name": "Binance",
          "wallet_address": "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo",
          "balance": 248597.58,
          "balance_usd": 16641564933,
          "symbol": "BTC",
          "assets_name": "Bitcoin",
          "price": 66941.78
        }
      ]
    }
  ]
}
```

---

### 20. OHLCV Candlestick Data

Candlestick data for any tracked coin. Configurable resolution (1m to 1d) and date range.

**Endpoint:** `GET /chartdata?coinId={coinId}&from={ISO}&to={ISO}&resolution={minutes}`

**Response:**
```json
{
  "message": "Chart data request received successfully",
  "data": {
    "coinId": "2bd4bbbb9e",
    "from": "2026-02-19T00:00:00Z",
    "to": "2026-02-20T00:00:00Z",
    "resolution": "1",
    "chartData": [
      {
        "open": 66437,
        "high": 66437,
        "low": 66418,
        "close": 66418,
        "volume": 0,
        "time": 1771459260000
      }
    ]
  }
}
```

Resolution is in minutes: `1`, `5`, `15`, `60`, `240`, `1440` (1d).

---

### 21. Polymarket / Fed Odds

Real-time FOMC decision odds from Polymarket.

**Endpoint:** `GET /polymarket/events/current`

**Response:**
```json
{
  "success": true,
  "event": {
    "slug": "fed-decision-in-march-885",
    "active": true,
    "description": "This market will resolve to the amount of basis points the upper bound of the target federal funds rate is changed by..."
  }
}
```

---

### 22. Economic Calendar

Global macro events with impact scoring, forecast and previous values.

**Endpoints:** `GET /financial-calendar` · `GET /financial-calendar/high-impact`

**Response:**
```json
{
  "success": true,
  "count": 50,
  "data": [
    {
      "countryCode": "USA",
      "countryName": "US",
      "calendarName": "Producer Price Index (YoY)(Jan)",
      "publishTimestamp": "2026-02-27T13:30:00Z",
      "importanceLevel": 3,
      "forecastValue": "",
      "previousValue": "3.0%",
      "publishedValue": "",
      "dataEffect": "Waiting",
      "hasExactPublishTime": 1
    }
  ]
}
```

Importance levels: 1 (low), 2 (medium), 3 (high).

---

### 23. Treasury Tracking

209 entities, 35 countries, $137B+ in tracked crypto treasury holdings across 25 assets.

**Endpoint:** `GET /treasury/stats`

**Response:**
```json
{
  "totalEntities": 209,
  "totalCountries": 35,
  "totalAssets": 25,
  "totalValueUsd": 137475379615,
  "assetBreakdown": {
    "bitcoin": 119409867524,
    "ethereum": 12418621630,
    "solana": 1526799922,
    "world-liberty-financial": 850824774,
    "ripple": 672052530,
    "binancecoin": 420112022,
    "tron": 192779348,
    "hyperliquid": 128637748,
    "sui": 104140585,
    "dogecoin": 77589170,
    "zcash": 76910116
  },
  "timestamp": "2026-02-20T19:33:00Z"
}
```

---

## Endpoint Reference

| # | Capability | Endpoint | Params |
|---|-----------|----------|--------|
| 1 | Macro Snapshot | `GET /macro-snapshot` | — |
| 2 | Macro Regime | `GET /macro-snapshot/regime` | — |
| 3 | Market Analysis | `GET /market-analysis/latest` | — |
| 4 | Breaking News | `GET /news/breaking` | `limit` |
| 5 | Newsletters | `GET /newsletters` | `limit` |
| 6 | Social Messages | `GET /xtg-messages` | `limit` |
| 7 | Signal States | `GET /signal-state` | — |
| 8 | Prices | `GET /realtime-prices` | — |
| 9 | Market Structure | `GET /market-structure` | — |
| 10 | Orderbook Depth | `GET /orderbook/depth` | `symbol`, `marketType`, `exchange` |
| 11 | Orderbook History | `GET /orderbook/depth/history` | `symbol`, `marketType`, `exchange` |
| 12 | Wall Persistence | `GET /orderbook/wall-persistence` | `symbol`, `marketType`, `exchange`, `side`, `priceBucket` |
| 13 | Liquidity Change | `GET /orderbook/liquidity-change` | `symbol`, `marketType`, `exchange` |
| 14 | Whale Alerts | `GET /whale-alerts` | `symbol` (optional) |
| 15 | HL Whale Alerts | `GET /hyperliquid-whale-alerts` | — |
| 16 | HL Whale Positions | `GET /hyperliquid-whale-positions` | — |
| 17 | Funding Arb (Top) | `GET /fundingrate/arbitrage/top` | — |
| 18 | Funding Arb (All) | `GET /fundingrate/arbitrage/latest` | — |
| 19 | Tech Indicators | `GET /cointa` | `id` (coinId) |
| 20 | RSI Statistics | `GET /coin-rsi/statistics` | — |
| 21 | RSI (Single) | `GET /coin-rsi` | `coinid` |
| 22 | RSI Multi-TF | `GET /coin-rsi/multi` | `coinids` |
| 23 | ROC (Single) | `GET /roc/{coinId}` | — |
| 24 | ROC Multi | `GET /roc/{coinId}/multi` | — |
| 25 | USDT Dominance | `GET /usdt-dominance` | — |
| 26 | USDC Dominance | `GET /usdc-dominance` | — |
| 27 | Exchange Volumes | `GET /exchange-volumes` | — |
| 28 | Exchange Assets | `GET /exchange-assets` | `symbol` |
| 29 | OHLCV | `GET /chartdata` | `coinId`, `from`, `to`, `resolution` |
| 30 | Calendar | `GET /financial-calendar` | — |
| 31 | Calendar (High) | `GET /financial-calendar/high-impact` | — |
| 32 | Treasury Stats | `GET /treasury/stats` | — |
| 33 | Polymarket | `GET /polymarket/events/current` | — |

Base URL: Provided with your API key after signup.
Auth: API key (query parameter)

---

## Pricing

| Tier | Deposit | Per Call | Access |
|---|---|---|---|
| Explorer | Free | — | Real-time prices only. 50 calls/day. |
| Builder | $50 USDC | $0.005 | Prices + macro + regime + z-scores + signals + news |
| Signal | $150 USDC | $0.003 | All 33 endpoints. AI reports. Orderbook. Webhooks. |
| Institutional | $500 USDC | $0.002 | Unlimited. White-label. Custom integrations. SLA. |

Deposit USDC, EURC, USDT, or SOL on Base, Solana, or Ethereum. Credits never expire. No subscriptions. No KYC.

**Get notified when API access opens:** [agentcanary.ai](https://agentcanary.ai)

---

## Links

- **Telegram:** [t.me/AgentCanary](https://t.me/AgentCanary) — live market intelligence 3x/day
- **Website:** [agentcanary.ai](https://agentcanary.ai)

---

*AgentCanary provides market data and intelligence for informational purposes only. Nothing constitutes financial advice. Do your own research.*
