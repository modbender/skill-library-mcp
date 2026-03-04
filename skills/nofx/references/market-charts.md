# NOFX Market Page Usage

## Access Method

URL: `https://nofxai.com/market`

## Feature Overview

### K-line Charts

- TradingView style K-line charts
- Supports multiple timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d
- Real-time price updates

### Technical Indicators

| Indicator | Description | Usage |
|-----------|-------------|-------|
| EMA | Exponential Moving Average | Trend direction |
| MACD | Moving Average Convergence Divergence | Momentum/divergence |
| RSI | Relative Strength Index | Overbought/oversold |
| BOLL | Bollinger Bands | Support/resistance/volatility |
| Volume | Trading volume | Price-volume relationship |

### Order Book Depth

- Buy/sell order distribution
- Large order marking
- Buy/sell pressure comparison

### Real-time Data

- Current price
- 24h change percentage
- 24h trading volume
- Funding rate
- Open interest

## Browser Automation

### Open Market Page

```javascript
browser.navigate("https://nofxai.com/market")
browser.snapshot()
```

### Switch Trading Pair

```javascript
// Click trading pair selector
// Input or select target trading pair
browser.act({kind: "click", ref: "symbolSelector"})
browser.act({kind: "type", ref: "searchBox", text: "ETHUSDT"})
```

### Switch Timeframe

```javascript
// Click corresponding time button
browser.act({kind: "click", ref: "timeframe1h"})
```

## Data Interpretation

### K-line Patterns

| Pattern | Meaning | Trading Suggestion |
|---------|---------|-------------------|
| Large bullish candle | Strong uptrend | Go long with trend |
| Large bearish candle | Strong downtrend | Go short with trend |
| Doji | Hesitation/reversal | Wait for confirmation |
| Hammer | Bottom reversal | Consider going long |
| Inverted hammer | Top reversal | Consider going short |

### RSI Signals

| Value | Status | Action |
|-------|---------|--------|
| > 70 | Overbought | Consider short/take profit |
| < 30 | Oversold | Consider long/buy dip |
| Around 50 | Neutral | Wait for direction |

### MACD Signals

| Signal | Meaning |
|--------|---------|
| Golden cross | DIF crosses above DEA, bullish |
| Death cross | DIF crosses below DEA, bearish |
| Top divergence | Price makes new high but MACD doesn't, beware pullback |
| Bottom divergence | Price makes new low but MACD doesn't, possible bounce |

### Bollinger Bands Usage

| Position | Meaning |
|----------|---------|
| Touch upper band | Overbought, possible pullback |
| Touch lower band | Oversold, possible bounce |
| Bands narrowing | Breakout approaching |
| Bands widening | Increasing volatility |