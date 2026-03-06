# NOFX Grid Trading Detailed Guide

## Grid Trading Principles

Grid trading automatically buys low and sells high within a set price range, suitable for ranging markets.

```
Upper $2200 ─────────────────
         │  Sell │  Sell │
         ├───────┼───────┤
         │       │       │
         ├───────┼───────┤  ← Grid
         │       │       │
         ├───────┼───────┤
         │  Buy  │  Buy  │
Lower $1800 ─────────────────
```

## Complete Configuration Examples

### Example 1: ETH Uniform Grid

```json
{
  "strategy_type": "grid_trading",
  "grid_config": {
    "symbol": "ETHUSDT",
    "grid_count": 20,
    "total_investment": 5000,
    "leverage": 3,
    "upper_price": 2200,
    "lower_price": 1800,
    "use_atr_bounds": false,
    "distribution": "uniform",
    "max_drawdown_pct": 10,
    "stop_loss_pct": 5,
    "daily_loss_limit_pct": 8,
    "use_maker_only": true,
    "enable_direction_adjust": false
  }
}
```

### Example 2: BTC Adaptive Boundaries

```json
{
  "strategy_type": "grid_trading",
  "grid_config": {
    "symbol": "BTCUSDT",
    "grid_count": 30,
    "total_investment": 10000,
    "leverage": 2,
    "use_atr_bounds": true,
    "atr_multiplier": 2.5,
    "distribution": "gaussian",
    "max_drawdown_pct": 15,
    "stop_loss_pct": 3,
    "use_maker_only": true,
    "enable_direction_adjust": true,
    "direction_bias_ratio": 0.6
  }
}
```

### Example 3: Long-Biased Grid

```json
{
  "strategy_type": "grid_trading",
  "grid_config": {
    "symbol": "SOLUSDT",
    "grid_count": 15,
    "total_investment": 3000,
    "leverage": 5,
    "upper_price": 90,
    "lower_price": 70,
    "distribution": "pyramid",
    "enable_direction_adjust": true,
    "direction_bias_ratio": 0.7
  }
}
```

## Parameter Details

### Basic Parameters

| Parameter | Description | Suggested Value |
|-----------|-------------|-----------------|
| `symbol` | Trading pair | BTCUSDT, ETHUSDT etc. |
| `grid_count` | Grid quantity | 10-50, more for precision |
| `total_investment` | Total investment (USDT) | Based on capital |
| `leverage` | Leverage multiplier | 1-5x recommended |

### Boundary Settings

| Parameter | Description |
|-----------|-------------|
| `upper_price` | Upper boundary price |
| `lower_price` | Lower boundary price |
| `use_atr_bounds` | Use ATR to auto-calculate boundaries |
| `atr_multiplier` | ATR multiplier (default 2.0) |

### Distribution Types

| Type | Description | Use Case |
|------|-------------|----------|
| `uniform` | Even distribution | No clear direction bias |
| `gaussian` | Dense in middle | Expect price to range in center |
| `pyramid` | Dense at current price | Expect small range |

### Risk Control Parameters

| Parameter | Description | Suggested Value |
|-----------|-------------|-----------------|
| `max_drawdown_pct` | Max drawdown stop-loss | 10-20% |
| `stop_loss_pct` | Single position stop-loss | 3-5% |
| `daily_loss_limit_pct` | Daily loss limit | 5-10% |

### Advanced Parameters

| Parameter | Description |
|-----------|-------------|
| `use_maker_only` | Only place Maker orders, lower fees |
| `enable_direction_adjust` | Auto-adjust grid direction |
| `direction_bias_ratio` | Direction bias ratio (0.7 = 70% long/30% short) |

## Grid Calculations

### Grid Spacing

```
Spacing = (Upper - Lower) / Grid Count
Example: (2200 - 1800) / 20 = $20/grid
```

### Position per Grid

```
Per Grid Investment = Total Investment / Grid Count * Leverage
Example: 5000 / 20 * 3 = $750/grid
```

### Expected Return

```
Single Arbitrage = Per Grid Investment * Spacing%
Example: 750 * (20/2000) = $7.5/trade
```

## Suitable Market Conditions

| Market Type | Grid Suitable | Recommendation |
|-------------|---------------|----------------|
| Range-bound | ✅ Very suitable | Standard grid |
| Slow uptrend | ✅ Suitable | Long-biased grid |
| Slow downtrend | ⚠️ Cautious | Short-bias + small position |
| High volatility | ❌ Not suitable | Pause grid |
| Trending market | ❌ Not suitable | Use trend strategy |

## Common Questions

### Q: How to choose grid count?

- High volatility: 10-15 grids, large spacing
- Low volatility: 25-50 grids, small spacing
- Small capital: 10-20 grids
- Large capital: 30-50 grids

### Q: How to set boundaries?

1. Look at recent support/resistance levels
2. Use ATR auto-calculation (recommended)
3. Leave 10-20% buffer above and below

### Q: When to stop?

- Price breaks boundaries
- Reaches maximum drawdown
- Trending market appears
- Before major news events