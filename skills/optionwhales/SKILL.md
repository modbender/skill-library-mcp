---
name: option-flow
description: Query real-time option flow intelligence — intent momentum, trade clustering, and abnormal trade detection. Use when users ask about option flow, unusual options activity, institutional positioning, or market sentiment from derivatives.
homepage: https://www.optionwhales.io
metadata: {"openclaw": {"emoji": "🐋", "requires": {"bins": ["python3", "curl"], "env": ["OPTIONWHALES_API_KEY"]}, "primaryEnv": "OPTIONWHALES_API_KEY"}}
---

# Option Flow Intelligence Skill

Query the OptionWhales Pro API for real-time institutional option flow analysis:
- **Intent Momentum** — clustered option trades scored for directional intent, coherence, and momentum
- **Abnormal Trades** — large or unusual option activity flagged in real-time

> **Free tier available!** Sign up at https://www.optionwhales.io to get a free API
> key instantly — no credit card required. Free keys return the top 3 tickers and
> last 5 abnormal trades, enough to evaluate the data and build integrations.
> Upgrade to Pro for full access.

## When to Use

✅ USE this skill when:
- "What's the option flow on AAPL today?"
- "Show me unusual options activity"
- "What are institutions buying?"
- "Is there bullish or bearish momentum in TSLA?"
- "Show me the top momentum tickers"

## When NOT to Use

❌ DON'T use this skill when:
- Stock price quotes only → use a stock/market data skill
- Historical stock charts → use a charting skill
- GEX / gamma exposure queries → not exposed via Pro API
- Open interest time series → not exposed via Pro API
- Options pricing or Greeks calculation → use a quant tool
- News/earnings analysis → use a news skill
- Crypto or forex → this is US equity options only

## Setup

Requires an OptionWhales API key.

- **Free key (no purchase):** Sign up at https://www.optionwhales.io/settings/api-keys — returns top 3 tickers + last 5 abnormal trades
- **Pro key (subscription):** Full access — all tickers, all fields, historical sessions, WebSocket stream

```bash
# Set the API key (works with either free or pro keys)
export OPTIONWHALES_API_KEY="ow_free_your_key_here"  # or ow_pro_...
```

## API Reference

Base URL: `https://api.optionwhales.io/v1`

All requests require header: `X-API-Key: $OPTIONWHALES_API_KEY`

### Current Flow Rankings

```bash
# Get today's intent momentum rankings (top tickers by conviction)
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/flow/current" | python3 -m json.tool
```

Response includes per-ticker: `intent_primary` (Directional/Gamma/LongVol/ShortVol/Mixed),
`direction_bias` (bullish/bearish/neutral), `intent_confidence` (0-1), `momentum_fast`,
`momentum_slow`, `coherence_last`, `strength_last`, `key_strikes`.

### Ticker Detail (Clusters + Time Series)

```bash
# Get full intent detail for a specific ticker
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/flow/current/AAPL" | python3 -m json.tool
```

Returns: `ranking` (summary), `clusters` (strategy clusters with dollar Greeks),
`cluster_trades` (individual trades), `time_series` (30-min momentum buckets).

### Historical Sessions

```bash
# List available sessions
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/flow/sessions" | python3 -m json.tool

# Get a specific session's rankings
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/flow/2025-06-02" | python3 -m json.tool

# Get a specific ticker from a historical session
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/flow/2025-06-02/AAPL" | python3 -m json.tool
```

### Momentum Rankings (Sorted)

```bash
# Top momentum tickers sorted by |momentum_fast|
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/momentum/rankings" | python3 -m json.tool
```

### Momentum History

```bash
# Get momentum history for a specific ticker
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/momentum/AAPL/history" | python3 -m json.tool
```

### Abnormal Trades

```bash
# Current session unusual/large option trades
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/abnormal-trades/current" | python3 -m json.tool

# Historical session abnormal trades
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/abnormal-trades/2025-06-02" | python3 -m json.tool
```

### Account Usage

```bash
# Check current rate limit and usage stats
curl -s -H "X-API-Key: $OPTIONWHALES_API_KEY" \
  "https://api.optionwhales.io/v1/account/usage" | python3 -m json.tool
```

### WebSocket — Real-Time Abnormal Trades (Pro Only)

```bash
# Connect to real-time abnormal trade stream
python3 -c "
import asyncio, websockets, json
async def stream():
    uri = 'wss://api.optionwhales.io/v1/ws/abnormal-trades?api_key=YOUR_PRO_KEY'
    async with websockets.connect(uri) as ws:
        # Optional: subscribe to specific tickers
        await ws.send(json.dumps({'type': 'subscribe', 'tickers': ['AAPL', 'NVDA', 'TSLA']}))
        async for msg in ws:
            data = json.loads(msg)
            if data['type'] == 'abnormal_trade':
                print(json.dumps(data['data'], indent=2))
asyncio.run(stream())
"
```

WebSocket message types:
- `abnormal_trade` — new abnormal trade detected (contains full trade data)
- `heartbeat` — periodic keepalive with `ts` timestamp
- `subscribed` — confirmation after sending a subscribe message

## Helper Script

A CLI wrapper is included for easy querying:

```bash
# Current flow rankings
python3 scripts/optionflow.py flow

# Flow for specific ticker
python3 scripts/optionflow.py flow --ticker AAPL

# Historical session flow
python3 scripts/optionflow.py flow --session 2025-06-02

# Momentum rankings
python3 scripts/optionflow.py momentum

# Top 5 momentum tickers
python3 scripts/optionflow.py momentum --top 5

# Current abnormal trades
python3 scripts/optionflow.py abnormal

# Historical abnormal trades
python3 scripts/optionflow.py abnormal --session 2025-06-02
```

## Interpreting Results

### Intent Types
| Intent | Meaning |
|--------|---------|
| **Directional** | Net delta-dominant flow — strong directional bet |
| **Gamma** | Gamma-dominant — positioning for rapid price moves |
| **LongVol** | Buying volatility (long vega, positive theta risk) |
| **ShortVol** | Selling volatility (short vega, positive theta) |
| **Mixed** | No dominant Greek — conflicting signals |

### Direction Bias
- **bullish**: Net positive delta flow
- **bearish**: Net negative delta flow
- **neutral**: Delta share below 15% of total flow

### Confidence Score
0–1 scale combining flow coherence (how aligned the trades are) and strength
(total dollar Greek magnitude). Above 0.7 is high conviction.

### Momentum
- `momentum_fast` (α=0.35): responsive to recent flow changes
- `momentum_slow` (α=0.15): trend-smoothed
- Positive = bullish acceleration, negative = bearish acceleration

## Example Queries → Commands

| User asks | Command |
|-----------|---------|
| "What's the flow today?" | `GET /v1/flow/current` |
| "Show TSLA option activity" | `GET /v1/flow/current/TSLA` |
| "Top momentum tickers" | `GET /v1/momentum/rankings` |
| "Any unusual trades?" | `GET /v1/abnormal-trades/current` |
| "Is AAPL bullish or bearish?" | `GET /v1/flow/current/AAPL` → check `direction_bias` |
| "What sessions are available?" | `GET /v1/flow/sessions` |
| "Show my API usage" | `GET /v1/account/usage` |

## Notes

- Data updates every 30 minutes during market hours (9:30 AM – 4:00 PM ET)
- Final daily data available after 7:30 AM ET next trading day (with full OI deltas)
- **Free tier:** 10 requests/minute, 200/day; top 3 tickers, last 5 abnormal trades, limited fields
- **Pro tier:** 60 requests/minute, 5000/day; all tickers, all fields, WebSocket, historical sessions
- US equity options only (no futures, crypto, or forex)
- `is_preliminary: true` means intraday data; `is_final: true` means post-close with full OI enrichment
