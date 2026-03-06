# Leverage Mathematics Reference

## Core Concepts

### Leverage Multiplier
Leverage amplifies both gains and losses:
```
Leveraged Return = Base Return * Leverage
```

### Liquidation Threshold
The price move that wipes out your margin:
```
Liquidation Threshold = 100% / Leverage
```

| Leverage | Threshold | Price Move to Liquidate |
|----------|-----------|------------------------|
| 2x | 50% | -50% adverse move |
| 5x | 20% | -20% adverse move |
| 10x | 10% | -10% adverse move |
| 15x | 6.67% | -6.67% adverse move |
| 20x | 5% | -5% adverse move |
| 25x | 4% | -4% adverse move |
| 50x | 2% | -2% adverse move |
| 100x | 1% | -1% adverse move |

## Margin Types

### Isolated Margin
- Each position has separate margin
- Liquidation affects only that position
- Recommended for risk management

### Cross Margin
- All positions share margin pool
- Winning positions can offset losing
- Higher capital efficiency, higher risk

## Liquidation Buffer Analysis

### Why Use Buffers?
Exchange liquidation engines aren't instant:
- Slippage during liquidation
- Fee deduction from margin
- Network latency

### Buffer Calculation
```python
def calculate_buffer_threshold(leverage: float, buffer_pct: float) -> float:
    """
    Calculate effective threshold with safety buffer.

    Args:
        leverage: Trading leverage (e.g., 10)
        buffer_pct: Safety buffer percentage (e.g., 0.10 for 10%)

    Returns:
        Effective threshold to trigger risk reduction
    """
    base_threshold = 100 / leverage  # e.g., 10% for 10x
    effective_threshold = base_threshold * (1 - buffer_pct)
    return effective_threshold
```

### Buffer Scenarios

**10% Buffer:**
```
10x leverage:
- Base threshold: 10%
- With 10% buffer: 9%
- Action: Close position at 9% adverse move
```

**20% Buffer:**
```
10x leverage:
- Base threshold: 10%
- With 20% buffer: 8%
- Action: Close position at 8% adverse move
```

### Buffer Table

| Leverage | Base | 10% Buffer | 20% Buffer | 30% Buffer |
|----------|------|------------|------------|------------|
| 5x | 20.0% | 18.0% | 16.0% | 14.0% |
| 10x | 10.0% | 9.0% | 8.0% | 7.0% |
| 15x | 6.67% | 6.0% | 5.3% | 4.7% |
| 20x | 5.0% | 4.5% | 4.0% | 3.5% |
| 25x | 4.0% | 3.6% | 3.2% | 2.8% |
| 50x | 2.0% | 1.8% | 1.6% | 1.4% |

## Position Sizing

### Fixed Position Sizing
```python
def fixed_position_size(equity: float, risk_per_trade: float, leverage: float) -> float:
    """
    Calculate fixed position size.

    Args:
        equity: Account equity
        risk_per_trade: Maximum risk per trade (e.g., 0.02 for 2%)
        leverage: Trading leverage

    Returns:
        Position size in USD
    """
    risk_amount = equity * risk_per_trade
    position_size = equity * leverage
    return position_size
```

### Dynamic Position Sizing
```python
def dynamic_position_size(
    equity: float,
    high_water_mark: float,
    base_leverage: float,
    drawdown_threshold: float = 0.10
) -> float:
    """
    Calculate dynamic position size based on drawdown.

    Reduces leverage when in drawdown to protect remaining capital.

    Args:
        equity: Current account equity
        high_water_mark: Maximum equity achieved
        base_leverage: Target leverage when not in drawdown
        drawdown_threshold: DD level to start reducing (default 10%)

    Returns:
        Adjusted leverage multiplier
    """
    if high_water_mark <= 0:
        return base_leverage

    drawdown_pct = (high_water_mark - equity) / high_water_mark

    if drawdown_pct <= drawdown_threshold:
        return base_leverage
    else:
        # Linear reduction from base_leverage to 1.0
        reduction_factor = 1 - ((drawdown_pct - drawdown_threshold) /
                                (1 - drawdown_threshold))
        adjusted_leverage = 1.0 + (base_leverage - 1.0) * max(0, reduction_factor)
        return max(1.0, adjusted_leverage)
```

### Kelly Criterion (Advanced)
```python
def kelly_leverage(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Calculate optimal leverage using Kelly Criterion.

    f* = (p * b - q) / b

    where:
        p = probability of winning
        q = probability of losing (1 - p)
        b = odds (avg_win / avg_loss)

    Args:
        win_rate: Historical win rate (0-1)
        avg_win: Average winning trade return
        avg_loss: Average losing trade return (positive number)

    Returns:
        Optimal fraction of capital to risk (Kelly leverage)
    """
    if avg_loss == 0 or win_rate >= 1 or win_rate <= 0:
        return 1.0

    p = win_rate
    q = 1 - win_rate
    b = avg_win / avg_loss

    kelly = (p * b - q) / b

    # Half Kelly is more conservative
    half_kelly = kelly / 2

    return max(0, min(half_kelly, 0.5))  # Cap at 50% of capital
```

## Compound Returns with Leverage

### Geometric vs Arithmetic Returns
```python
def simulate_leveraged_returns(
    base_returns: List[float],
    leverage: float,
    leverage_type: str = 'fixed'
) -> Dict:
    """
    Simulate leveraged equity curve.

    Args:
        base_returns: List of base returns (as decimals, e.g., 0.02 for 2%)
        leverage: Leverage multiplier
        leverage_type: 'fixed' or 'dynamic'

    Returns:
        Dict with equity curve, final return, max drawdown
    """
    equity = 1.0
    high_water_mark = 1.0
    max_drawdown = 0.0
    equity_curve = [equity]
    current_leverage = leverage

    for ret in base_returns:
        if leverage_type == 'dynamic':
            # Reduce leverage in drawdown
            dd_pct = (high_water_mark - equity) / high_water_mark if high_water_mark > 0 else 0
            if dd_pct > 0.10:
                current_leverage = max(1.0, leverage * (1 - dd_pct))
            else:
                current_leverage = leverage

        leveraged_return = ret * current_leverage
        equity = equity * (1 + leveraged_return)
        equity_curve.append(equity)

        # Track high water mark and drawdown
        high_water_mark = max(high_water_mark, equity)
        current_dd = (high_water_mark - equity) / high_water_mark
        max_drawdown = max(max_drawdown, current_dd)

    return {
        'equity_curve': equity_curve,
        'final_equity': equity,
        'total_return': (equity - 1) * 100,
        'max_drawdown': max_drawdown * 100,
        'n_periods': len(base_returns),
    }
```

### Volatility Decay
High leverage + high volatility = performance drag:

```python
def calculate_volatility_decay(
    daily_volatility: float,
    leverage: float,
    days: int = 252
) -> float:
    """
    Estimate volatility decay for leveraged products.

    Leveraged ETFs experience decay due to daily rebalancing.
    This approximates the effect.

    Args:
        daily_volatility: Daily return standard deviation (decimal)
        leverage: Leverage factor
        days: Number of trading days

    Returns:
        Expected decay factor (multiply by base return)
    """
    # Variance decay formula
    variance = daily_volatility ** 2
    decay_per_day = 1 - 0.5 * (leverage ** 2 - leverage) * variance
    total_decay = decay_per_day ** days
    return total_decay
```

## Risk Metrics at Leverage

### Leveraged Sharpe Ratio
```python
def leveraged_sharpe(base_returns: pd.Series, leverage: float) -> float:
    """
    Calculate Sharpe ratio for leveraged returns.

    Note: Sharpe ratio is NOT linear with leverage due to:
    - Transaction costs (scale with leverage)
    - Funding costs (scale with leverage)
    - Volatility decay (quadratic with leverage)
    """
    leveraged_returns = base_returns * leverage
    if leveraged_returns.std() == 0:
        return 0.0

    return np.sqrt(252) * leveraged_returns.mean() / leveraged_returns.std()
```

### Leveraged Sortino Ratio
```python
def leveraged_sortino(base_returns: pd.Series, leverage: float) -> float:
    """Calculate Sortino ratio for leveraged returns."""
    leveraged_returns = base_returns * leverage
    downside = leveraged_returns[leveraged_returns < 0]

    if downside.empty or downside.std() == 0:
        return float('inf') if leveraged_returns.mean() > 0 else 0.0

    return np.sqrt(252) * leveraged_returns.mean() / downside.std()
```

### Leveraged Calmar Ratio
```python
def leveraged_calmar(
    base_returns: pd.Series,
    leverage: float,
    years: float
) -> float:
    """
    Calculate Calmar ratio for leveraged returns.

    Calmar = CAGR / Max Drawdown

    Note: Max drawdown scales faster than CAGR with leverage
    """
    sim = simulate_leveraged_returns(base_returns.tolist(), leverage)
    cagr = (sim['final_equity'] ** (1 / years) - 1) * 100 if years > 0 else 0
    max_dd = sim['max_drawdown']

    if max_dd == 0:
        return 0.0

    return cagr / max_dd
```

## Leverage Optimization

### Optimal Leverage Grid Search
```python
def find_optimal_leverage(
    trades: List[Dict],
    initial_capital: float,
    leverage_range: Tuple[float, float] = (1, 20),
    step: float = 0.5,
    metric: str = 'calmar'
) -> Dict:
    """
    Find optimal leverage by grid search.

    Args:
        trades: List of trade records
        initial_capital: Starting capital
        leverage_range: Min and max leverage to test
        step: Leverage step size
        metric: Optimization target ('sharpe', 'sortino', 'calmar')

    Returns:
        Dict with optimal leverage and performance metrics
    """
    results = []
    leverages = np.arange(leverage_range[0], leverage_range[1] + step, step)

    for lev in leverages:
        sim = simulate_trades_with_leverage(trades, initial_capital, lev)
        results.append({
            'leverage': lev,
            'sharpe': sim['sharpe'],
            'sortino': sim['sortino'],
            'calmar': sim['calmar'],
            'return': sim['total_return'],
            'max_dd': sim['max_drawdown'],
            'liquidations': sim['liquidation_events'],
        })

    # Sort by metric
    results.sort(key=lambda x: x[metric], reverse=True)

    # Find highest metric with 0 liquidations
    safe_results = [r for r in results if r['liquidations'] == 0]

    return {
        'optimal': safe_results[0] if safe_results else results[0],
        'all_results': results,
        'max_safe_leverage': safe_results[0]['leverage'] if safe_results else 1.0,
    }
```

## Hyperliquid-Specific Calculations

### Hyperliquid Leverage Tiers
```python
HYPERLIQUID_TIERS = {
    'BTC': {'max_leverage': 50, 'maintenance_margin': 0.5},
    'ETH': {'max_leverage': 50, 'maintenance_margin': 0.5},
    'SOL': {'max_leverage': 50, 'maintenance_margin': 0.5},
    # ... other assets
}

def get_hyperliquid_liquidation_price(
    entry_price: float,
    leverage: float,
    side: str,
    maintenance_margin: float = 0.005
) -> float:
    """
    Calculate Hyperliquid liquidation price.

    Hyperliquid uses maintenance margin of 0.5% (default).
    """
    if side == 'LONG':
        liq_price = entry_price * (1 - (1 / leverage) + maintenance_margin)
    else:  # SHORT
        liq_price = entry_price * (1 + (1 / leverage) - maintenance_margin)

    return liq_price
```

### Funding Rate Impact
```python
def calculate_funding_impact(
    position_size: float,
    funding_rate: float,  # Per 8 hours
    holding_periods: int  # Number of 8-hour periods
) -> float:
    """
    Calculate total funding paid/received.

    Positive funding rate: longs pay shorts
    Negative funding rate: shorts pay longs
    """
    return position_size * funding_rate * holding_periods
```

## Summary Formulas

| Metric | Formula |
|--------|---------|
| Liquidation Threshold | `100% / leverage` |
| Buffer Threshold | `(100% / leverage) * (1 - buffer)` |
| Leveraged Return | `base_return * leverage` |
| Max Safe Leverage | `100% / p95_mae * (1 - buffer)` |
| Position Size | `equity * leverage` |
| Kelly Fraction | `(win_rate * payoff - loss_rate) / payoff` |
| Volatility Decay | `1 - 0.5 * (lev^2 - lev) * variance` |
