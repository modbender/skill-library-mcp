# Strategy Templates

## Pre-Built Trading Strategies

Six battle-tested strategy templates for common trading approaches.

---

## 1. Momentum Strategy

**Asset Class:** Stock
**Description:** Identifies stocks with strong upward price momentum, rising above key moving averages with healthy volume.

**Key Filters:**
- Price above 50-day SMA
- Price above 200-day SMA
- Positive daily change
- Volume above 10-day average
- RSI above 50 (not overbought)

**CLI Command:**
```bash
python scripts/screen.py \
  --asset stock \
  --filters "PRICE > SIMPLE_MOVING_AVERAGE_50" \
           "PRICE > SIMPLE_MOVING_AVERAGE_200" \
           "CHANGE_PERCENT > 0" \
           "VOLUME > AVERAGE_VOLUME_10_DAY" \
           "RELATIVE_STRENGTH_INDEX_14 > 50" \
           "RELATIVE_STRENGTH_INDEX_14 < 70" \
  --columns NAME PRICE CHANGE_PERCENT VOLUME RELATIVE_STRENGTH_INDEX_14 \
  --timeframe 1D \
  --limit 50
```

**Best For:** Bull markets, trending stocks, swing trading

---

## 2. Value Strategy

**Asset Class:** Stock
**Description:** Finds undervalued stocks with strong fundamentals and oversold technical conditions.

**Key Filters:**
- RSI below 40 (oversold)
- Price below 50-day SMA (potential reversal)
- Positive market cap (established companies)
- Volume above average (liquidity)

**CLI Command:**
```bash
python scripts/screen.py \
  --asset stock \
  --filters "RELATIVE_STRENGTH_INDEX_14 < 40" \
           "PRICE < SIMPLE_MOVING_AVERAGE_50" \
           "MARKET_CAPITALIZATION > 1000000000" \
           "VOLUME > AVERAGE_VOLUME_30_DAY" \
  --columns NAME PRICE CHANGE_PERCENT MARKET_CAPITALIZATION RELATIVE_STRENGTH_INDEX_14 SECTOR \
  --timeframe 1D \
  --limit 50
```

**Best For:** Contrarian trading, long-term value investing, market corrections

---

## 3. Breakout Strategy

**Asset Class:** Stock
**Description:** Catches stocks breaking above resistance with volume confirmation.

**Key Filters:**
- Price near or above 50-day SMA
- Volume surge (2x 10-day average)
- Positive change
- RSI above 50 (momentum)

**CLI Command:**
```bash
python scripts/screen.py \
  --asset stock \
  --filters "PRICE > SIMPLE_MOVING_AVERAGE_50 * 0.98" \
           "VOLUME > AVERAGE_VOLUME_10_DAY * 2" \
           "CHANGE_PERCENT > 2" \
           "RELATIVE_STRENGTH_INDEX_14 > 50" \
  --columns NAME PRICE CHANGE_PERCENT VOLUME SIMPLE_MOVING_AVERAGE_50 \
  --timeframe 1D \
  --limit 30
```

**Best For:** Day trading, momentum trading, volatility plays

---

## 4. Mean Reversion Strategy

**Asset Class:** Stock
**Description:** Identifies oversold stocks likely to bounce back to their moving averages.

**Key Filters:**
- RSI below 30 (oversold)
- Price significantly below 50-day SMA
- Established company (market cap filter)
- Normal volume

**CLI Command:**
```bash
python scripts/screen.py \
  --asset stock \
  --filters "RELATIVE_STRENGTH_INDEX_14 < 30" \
           "PRICE < SIMPLE_MOVING_AVERAGE_50 * 0.95" \
           "MARKET_CAPITALIZATION > 500000000" \
           "VOLUME > AVERAGE_VOLUME_30_DAY * 0.5" \
  --columns NAME PRICE CHANGE_PERCENT RELATIVE_STRENGTH_INDEX_14 SIMPLE_MOVING_AVERAGE_50 \
  --timeframe 1D \
  --limit 40
```

**Best For:** Short-term trading, range-bound markets, oversold bounces

---

## 5. Crypto Momentum Strategy

**Asset Class:** Crypto
**Description:** High-momentum cryptocurrencies with strong volume and positive trends.

**Key Filters:**
- Positive daily change
- Volume above average
- RSI above 50 (bullish momentum)
- Price above 50-period SMA

**CLI Command:**
```bash
python scripts/screen.py \
  --asset crypto \
  --filters "CHANGE_PERCENT > 3" \
           "VOLUME > AVERAGE_VOLUME_10_DAY" \
           "RELATIVE_STRENGTH_INDEX_14 > 50" \
           "RELATIVE_STRENGTH_INDEX_14 < 75" \
           "PRICE > SIMPLE_MOVING_AVERAGE_50" \
  --columns NAME PRICE CHANGE_PERCENT VOLUME RELATIVE_STRENGTH_INDEX_14 \
  --timeframe 1D \
  --limit 30
```

**Best For:** Crypto trading, high volatility, trend following

---

## 6. Forex Trend Strategy

**Asset Class:** Forex
**Description:** Currency pairs with established trends and momentum confirmation.

**Key Filters:**
- 50-day SMA above 200-day SMA (golden cross)
- Price above 50-day SMA
- RSI between 45-65 (trending, not extreme)

**CLI Command:**
```bash
python scripts/screen.py \
  --asset forex \
  --filters "SIMPLE_MOVING_AVERAGE_50 > SIMPLE_MOVING_AVERAGE_200" \
           "PRICE > SIMPLE_MOVING_AVERAGE_50" \
           "RELATIVE_STRENGTH_INDEX_14 > 45" \
           "RELATIVE_STRENGTH_INDEX_14 < 65" \
  --columns NAME PRICE CHANGE_PERCENT SIMPLE_MOVING_AVERAGE_50 SIMPLE_MOVING_AVERAGE_200 \
  --timeframe 1D \
  --limit 20
```

**Best For:** Forex trading, trend following, position trading

---

## Usage Tips

### Combining Strategies

Mix filters from different strategies:

```bash
# Momentum + Value hybrid
python scripts/screen.py \
  --asset stock \
  --filters "PRICE > SIMPLE_MOVING_AVERAGE_50" \
           "MARKET_CAPITALIZATION > 2000000000" \
           "RELATIVE_STRENGTH_INDEX_14 < 60" \
  --limit 50
```

### Adjusting Timeframes

Change timeframes for different trading styles:

- **Day trading:** `--timeframe 5` or `--timeframe 15`
- **Swing trading:** `--timeframe 1D`
- **Position trading:** `--timeframe 1W`

### Market Filtering

Add market filters for geographic focus:

```bash
python scripts/screen.py \
  --asset stock \
  --filters "PRICE > SIMPLE_MOVING_AVERAGE_50" \
  --markets america \
  --limit 50
```

### Sector Filtering

Focus on specific sectors:

```bash
python scripts/screen.py \
  --asset stock \
  --filters "PRICE > SIMPLE_MOVING_AVERAGE_50" \
           "SECTOR == Technology" \
  --limit 50
```

## Risk Warnings

⚠️ **Important:**
- These strategies are templates, not trading advice
- Always backtest before live trading
- Use proper risk management
- Past performance ≠ future results
- Consider transaction costs and slippage
