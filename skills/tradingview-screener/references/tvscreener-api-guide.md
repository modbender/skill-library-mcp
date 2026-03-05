# TradingView Screener API Guide

## Screener Types

| Asset Class | Screener Class | Field Enum | Description |
|------------|---------------|------------|-------------|
| Stock | `stock.Screener()` | `StockField` | Equities and stocks |
| Crypto | `crypto.Screener()` | `CryptoField` | Cryptocurrencies |
| Forex | `forex.Screener()` | `ForexField` | Currency pairs |
| Bond | `bond.Screener()` | `BondField` | Bonds and fixed income |
| Futures | `futures.Screener()` | `FuturesField` | Futures contracts |
| Coin | `coin.Screener()` | `CoinField` | Coins and tokens |

## Filter Operators

| Operator | Symbol | Example Usage |
|----------|--------|---------------|
| Greater than | `>` | `filter(StockField.PRICE > 50)` |
| Greater or equal | `>=` | `filter(StockField.PRICE >= 100)` |
| Less than | `<` | `filter(StockField.VOLUME < 1000000)` |
| Less or equal | `<=` | `filter(StockField.CHANGE_PERCENT <= 5)` |
| Equal | `==` | `filter(StockField.SECTOR == "Technology")` |
| Not equal | `!=` | `filter(StockField.SECTOR != "Energy")` |
| Between | `between` | `filter(StockField.PRICE.between(10, 50))` |
| In list | `isin` | `filter(StockField.SECTOR.isin(["Technology", "Healthcare"]))` |

## Code Examples

### Basic Filter
```python
from tvscreener import stock, StockField

screener = stock.Screener()
screener.filter(StockField.PRICE > 100)
screener.filter(StockField.VOLUME > 1000000)
results = screener.get_scanner_data()
```

### Multiple Filters
```python
screener = stock.Screener()
screener.filter(StockField.PRICE.between(50, 200))
screener.filter(StockField.CHANGE_PERCENT > 2)
screener.filter(StockField.SECTOR.isin(["Technology", "Healthcare"]))
results = screener.get_scanner_data()
```

### Column Selection

By default, screeners return: NAME, PRICE, VOLUME, CHANGE_PERCENT

Add custom columns with `.select()`:

```python
screener = stock.Screener()
screener.filter(StockField.PRICE > 50)
screener.select(
    StockField.NAME,
    StockField.PRICE,
    StockField.MARKET_CAPITALIZATION,
    StockField.SIMPLE_MOVING_AVERAGE_50,
    StockField.RELATIVE_STRENGTH_INDEX_14
)
results = screener.get_scanner_data()
```

## Timeframes

Supported intervals for technical indicators:

| Code | Description |
|------|-------------|
| "1" | 1 minute |
| "5" | 5 minutes |
| "15" | 15 minutes |
| "30" | 30 minutes |
| "60" | 1 hour |
| "120" | 2 hours |
| "240" | 4 hours |
| "1D" | Daily |
| "1W" | Weekly |
| "1M" | Monthly |

### Usage
```python
screener = stock.Screener()
screener.with_interval("1D")
screener.filter(StockField.RELATIVE_STRENGTH_INDEX_14 < 30)
results = screener.get_scanner_data()
```

## Field Discovery

### Search by Keyword
```python
# Find all fields containing "moving"
fields = StockField.search("moving")
for field in fields:
    print(field.name, field.description)
```

### Technical Indicators
```python
# List all technical indicator fields
technicals = StockField.technicals()
```

### Fundamental Metrics
```python
# List all fundamental fields (stocks only)
fundamentals = StockField.fundamentals()
```

### Total Available Fields
```python
# StockField has 13,000+ fields
all_fields = StockField.all()
print(f"Total fields: {len(all_fields)}")
```

## Market Filtering

Filter by specific exchanges or markets:

```python
screener = stock.Screener()
screener.set_markets("america")  # US markets
# or
screener.set_markets("NYSE", "NASDAQ")  # Specific exchanges
results = screener.get_scanner_data()
```

Common market values:
- `"america"` - US markets
- `"NYSE"`, `"NASDAQ"`, `"AMEX"` - US exchanges
- `"LSE"` - London Stock Exchange
- `"TSX"` - Toronto Stock Exchange

## Error Handling Patterns

```python
from tvscreener import stock, StockField
import logging

logger = logging.getLogger(__name__)

def safe_screen(filters):
    try:
        screener = stock.Screener()
        for field, op, value in filters:
            if op == ">":
                screener.filter(field > value)
            elif op == "<":
                screener.filter(field < value)
            # ... other operators

        results = screener.get_scanner_data()
        return results

    except ValueError as e:
        logger.error(f"Invalid filter value: {e}")
        return None
    except Exception as e:
        logger.error(f"Screener error: {e}")
        return None
```

## Performance Tips

1. **Limit results**: Use `.limit(n)` to cap results
2. **Select specific columns**: Don't fetch all 13,000 fields
3. **Cache field lookups**: Store StockField.search() results
4. **Batch filters**: Combine related filters in one screener
5. **Use appropriate intervals**: Smaller intervals = more data
