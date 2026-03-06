# Field Presets

## Quick Reference for Common TradingView Fields

All field names are **VERIFIED** from actual tvscreener introspection. Use full field names - short aliases do NOT exist.

---

## Stock Fields

### Price & Volume
```python
StockField.NAME                    # Ticker symbol
StockField.PRICE                   # Current price
StockField.CHANGE_PERCENT          # Daily % change
StockField.VOLUME                  # Current volume
StockField.AVERAGE_VOLUME_10_DAY   # 10-day average volume
StockField.AVERAGE_VOLUME_30_DAY   # 30-day average volume
```

### Valuation & Fundamentals
```python
StockField.MARKET_CAPITALIZATION   # Market cap in USD
StockField.SECTOR                  # Business sector
```

### Technical Indicators - Moving Averages
```python
StockField.SIMPLE_MOVING_AVERAGE_50    # 50-period SMA
StockField.SIMPLE_MOVING_AVERAGE_200   # 200-period SMA
```

### Technical Indicators - Momentum
```python
StockField.RELATIVE_STRENGTH_INDEX_14  # 14-period RSI
StockField.MACD_LEVEL_12_26            # MACD line (12,26,9)
```

---

## Crypto Fields

### Price & Volume
```python
CryptoField.NAME                   # Symbol (BTC, ETH, etc.)
CryptoField.PRICE                  # Current price
CryptoField.CHANGE_PERCENT         # Daily % change
CryptoField.VOLUME                 # 24h volume
CryptoField.AVERAGE_VOLUME_10_DAY  # 10-day average volume
```

### Technical Indicators
```python
CryptoField.SIMPLE_MOVING_AVERAGE_50       # 50-period SMA
CryptoField.SIMPLE_MOVING_AVERAGE_200      # 200-period SMA
CryptoField.RELATIVE_STRENGTH_INDEX_14     # 14-period RSI
CryptoField.MACD_LEVEL_12_26               # MACD line
```

---

## Forex Fields

### Price & Change
```python
ForexField.NAME                    # Currency pair (EUR/USD, etc.)
ForexField.PRICE                   # Current rate
ForexField.CHANGE_PERCENT          # Daily % change
```

### Technical Indicators
```python
ForexField.SIMPLE_MOVING_AVERAGE_50        # 50-period SMA
ForexField.SIMPLE_MOVING_AVERAGE_200       # 200-period SMA
ForexField.RELATIVE_STRENGTH_INDEX_14      # 14-period RSI
ForexField.MACD_LEVEL_12_26                # MACD line
```

---

## Bond Fields

### Price & Yield
```python
BondField.NAME                     # Bond identifier
BondField.PRICE                    # Current price
BondField.CHANGE_PERCENT           # Daily % change
```

### Technical Indicators
```python
BondField.SIMPLE_MOVING_AVERAGE_50         # 50-period SMA
BondField.RELATIVE_STRENGTH_INDEX_14       # 14-period RSI
```

---

## Futures Fields

### Price & Volume
```python
FuturesField.NAME                  # Contract name
FuturesField.PRICE                 # Current price
FuturesField.CHANGE_PERCENT        # Daily % change
FuturesField.VOLUME                # Volume
```

### Technical Indicators
```python
FuturesField.SIMPLE_MOVING_AVERAGE_50      # 50-period SMA
FuturesField.SIMPLE_MOVING_AVERAGE_200     # 200-period SMA
FuturesField.RELATIVE_STRENGTH_INDEX_14    # 14-period RSI
```

---

## Coin Fields

### Price & Volume
```python
CoinField.NAME                     # Coin symbol
CoinField.PRICE                    # Current price
CoinField.CHANGE_PERCENT           # Daily % change
CoinField.VOLUME                   # 24h volume
```

### Technical Indicators
```python
CoinField.SIMPLE_MOVING_AVERAGE_50         # 50-period SMA
CoinField.RELATIVE_STRENGTH_INDEX_14       # 14-period RSI
```

---

## Common Technical Indicators (Stocks)

### Moving Averages
```python
StockField.SIMPLE_MOVING_AVERAGE_50        # 50-period SMA
StockField.SIMPLE_MOVING_AVERAGE_200       # 200-period SMA
# Note: EMA fields exist but naming pattern varies
# Use StockField.search("exponential") to discover
```

### Momentum Oscillators
```python
StockField.RELATIVE_STRENGTH_INDEX_14      # RSI (14-period)
StockField.MACD_LEVEL_12_26                # MACD line (12,26,9)
# Note: MACD signal and histogram have different field names
# Use StockField.search("macd") to discover
```

### Bollinger Bands
```python
# Use StockField.search("bollinger") to find:
# - Upper band
# - Middle band (SMA)
# - Lower band
```

### Average Directional Index (ADX)
```python
# Use StockField.search("directional") to find ADX fields
```

---

## Field Discovery Commands

### Search by Keyword
```python
from tvscreener import StockField

# Find all moving average fields
ma_fields = StockField.search("moving")
for field in ma_fields:
    print(f"{field.name}: {field.description}")
```

### List Technical Indicators
```python
# All technical indicator fields
tech_fields = StockField.technicals()
print(f"Found {len(tech_fields)} technical fields")
```

### List Fundamental Metrics (Stocks Only)
```python
# All fundamental fields
fund_fields = StockField.fundamentals()
print(f"Found {len(fund_fields)} fundamental fields")
```

### Search Specific Indicators
```python
# RSI variations
rsi_fields = StockField.search("rsi")

# MACD variations
macd_fields = StockField.search("macd")

# Bollinger Bands
bb_fields = StockField.search("bollinger")

# Stochastic
stoch_fields = StockField.search("stochastic")

# Volume indicators
vol_fields = StockField.search("volume")
```

---

## Usage Examples

### Basic Screen with Price & Volume
```python
from tvscreener import stock, StockField

screener = stock.Screener()
screener.filter(StockField.PRICE > 50)
screener.filter(StockField.VOLUME > 1000000)
screener.select(
    StockField.NAME,
    StockField.PRICE,
    StockField.VOLUME,
    StockField.CHANGE_PERCENT
)
results = screener.get_scanner_data()
```

### Technical Analysis Screen
```python
screener = stock.Screener()
screener.with_interval("1D")
screener.filter(StockField.PRICE > StockField.SIMPLE_MOVING_AVERAGE_50)
screener.filter(StockField.RELATIVE_STRENGTH_INDEX_14 > 50)
screener.select(
    StockField.NAME,
    StockField.PRICE,
    StockField.SIMPLE_MOVING_AVERAGE_50,
    StockField.RELATIVE_STRENGTH_INDEX_14,
    StockField.MACD_LEVEL_12_26
)
results = screener.get_scanner_data()
```

### Fundamental + Technical Screen
```python
screener = stock.Screener()
screener.filter(StockField.MARKET_CAPITALIZATION > 1000000000)
screener.filter(StockField.SECTOR == "Technology")
screener.filter(StockField.RELATIVE_STRENGTH_INDEX_14 < 70)
screener.select(
    StockField.NAME,
    StockField.PRICE,
    StockField.MARKET_CAPITALIZATION,
    StockField.SECTOR,
    StockField.RELATIVE_STRENGTH_INDEX_14
)
results = screener.get_scanner_data()
```

---

## Important Notes

⚠️ **Field Name Accuracy:**
- Always use FULL field names (e.g., `SIMPLE_MOVING_AVERAGE_50`)
- Short aliases like `SMA50`, `RSI14` do NOT exist
- Use `StockField.search("keyword")` when unsure

⚠️ **Asset Class Differences:**
- Not all fields exist across all asset classes
- Fundamental fields (market cap, sector) only for stocks
- Always test field availability with `.search()`

⚠️ **13,000+ Fields Available:**
- This guide covers the most common fields
- Use discovery commands to explore all available fields
- Custom indicators and exotic metrics require field search
