---
name: btc-analyzer
version: 1.0.0
description: Fetch live BTCUSDT 15m candles from Binance public API and analyze market direction UP/DOWN/SKIP using EMA20 and RSI14. Use when asked to analyze BTC price direction, get trading signal, or check market trend.
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": { "bins": ["python3"] },
      },
  }
---

# BTC Analyzer

Fetch real-time BTCUSDT candlestick data from Binance public REST API and compute a directional trading signal based on EMA20 slope and RSI14 momentum.

## When to Use

- User asks: "analisa BTC sekarang"
- User asks: "BTC akan naik atau turun?"
- User asks: "berikan sinyal trading BTC 15 menit"
- User asks: "cek market BTC sekarang"

## How It Works

This skill runs a local Python script that:
1. Fetches 200 candles of BTCUSDT 15m OHLCV data from Binance public API (no API key needed).
2. Computes EMA20 from closing prices.
3. Computes RSI14 from closing prices.
4. Determines direction based on: price vs EMA20, RSI level, and recent candle slope.
5. Returns a strict JSON object with decision, confidence score, and reasoning.

## Workflow

Step 1 — Run the analyzer script via bash tool:
python3 ~/.npm-global/lib/node_modules/openclaw/skills/btc-analyzer/analyze.py

Step 2 — Parse the JSON output.

Step 3 — Present the result to the user clearly, including:
- Decision (UP / DOWN / SKIP)
- Confidence percentage
- Reason (EMA, RSI, slope context)
- Last close price
- Timestamp

## Output Format

The script returns strict JSON:
{
  "decision": "UP",
  "confidence": 72,
  "reason": "price above EMA20, RSI 58, bullish slope last 3 candles",
  "lastClose": 94500.00,
  "ema20": 94200.00,
  "rsi14": 58.3,
  "timestamp": "2026-02-23T00:00:00Z"
}

Decision values:
- UP: bullish signal, consider long
- DOWN: bearish signal, consider short
- SKIP: no clear signal, stay out

Confidence range: 0-100 (higher = stronger signal)

## Signal Logic

- RSI < 30: decision = UP (oversold)
- RSI > 70: decision = DOWN (overbought)
- Price > EMA20 AND slope up: decision = UP
- Price < EMA20 AND slope down: decision = DOWN
- Otherwise: decision = SKIP

## Error Handling

If Binance API is unreachable or returns an error:
{"decision":"SKIP","confidence":0,"reason":"API error or network issue","lastClose":0,"timestamp":""}

## Guardrails

- Always run the script via bash tool — never fabricate or guess output values.
- Do not hardcode prices or decisions.
- If script fails, show the actual error message to the user.
- This skill uses Binance public API only — no API key or authentication required.
- Data is real-time; do not cache or reuse previous results.
