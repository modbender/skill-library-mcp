# MAE Analysis Deep Dive

## Maximum Adverse Excursion (MAE) Theory

MAE is the maximum unrealized loss experienced during a trade before the exit point. It measures the "worst it got" during each position.

## Why MAE Matters for Leverage

For leveraged trading, MAE determines survival:
- At 10x leverage, a 10% MAE = 100% loss (liquidation)
- At 20x leverage, a 5% MAE = 100% loss (liquidation)

## Calculating MAE

### For Long Positions
```python
mae_pct = ((lowest_price_during_trade - entry_price) / entry_price) * 100
# Example: Entry $100, lowest $97 -> MAE = -3%
```

### For Short Positions
```python
mae_pct = ((entry_price - highest_price_during_trade) / entry_price) * 100
# Example: Entry $100, highest $103 -> MAE = -3%
```

## Percentile Analysis

### Why Use Percentiles?

Mean/average MAE underestimates risk because:
- One large MAE event = liquidation
- Distribution is often right-skewed (fat tail)
- Outliers matter more than average

### Recommended Percentiles

| Percentile | Use Case |
|------------|----------|
| p50 (median) | Typical trade behavior |
| p75 | Conservative risk estimate |
| p90 | Aggressive trading threshold |
| p95 | Recommended for leverage |
| p99 | Maximum expected (excl. black swan) |
| max | Actual worst case observed |

## Implementation

```python
import numpy as np
from typing import List, Dict

def calculate_mae_statistics(trades: List[Dict]) -> Dict:
    """
    Comprehensive MAE statistics calculation.

    Args:
        trades: List of trade dicts with 'max_adverse_excursion' key

    Returns:
        Dict with percentiles, moments, and risk metrics
    """
    maes = [
        t['max_adverse_excursion']
        for t in trades
        if t.get('max_adverse_excursion') is not None
    ]

    if not maes:
        return {'error': 'No MAE data available'}

    maes = np.array(maes)

    return {
        # Central tendency
        'mean': float(np.mean(maes)),
        'median': float(np.median(maes)),
        'mode': float(np.argmax(np.bincount(np.round(maes * 100).astype(int))) / 100),

        # Dispersion
        'std': float(np.std(maes)),
        'variance': float(np.var(maes)),
        'range': float(np.max(maes) - np.min(maes)),
        'iqr': float(np.percentile(maes, 75) - np.percentile(maes, 25)),

        # Percentiles (key for leverage decisions)
        'p25': float(np.percentile(maes, 25)),
        'p50': float(np.percentile(maes, 50)),
        'p75': float(np.percentile(maes, 75)),
        'p90': float(np.percentile(maes, 90)),
        'p95': float(np.percentile(maes, 95)),
        'p99': float(np.percentile(maes, 99)),

        # Extremes
        'min': float(np.min(maes)),
        'max': float(np.max(maes)),

        # Shape
        'skewness': float(skew(maes)) if len(maes) > 2 else 0,
        'kurtosis': float(kurtosis(maes)) if len(maes) > 3 else 0,

        # Count
        'n_trades': len(maes),
        'n_with_data': len(maes),
    }


def analyze_mae_by_side(trades: List[Dict]) -> Dict:
    """Analyze MAE separately for longs and shorts."""
    longs = [t for t in trades if t.get('side') == 'LONG']
    shorts = [t for t in trades if t.get('side') == 'SHORT']

    return {
        'long': calculate_mae_statistics(longs),
        'short': calculate_mae_statistics(shorts),
        'combined': calculate_mae_statistics(trades),
    }


def analyze_mae_by_timeframe(trades: List[Dict]) -> Dict:
    """Analyze MAE by trade duration buckets."""
    from datetime import timedelta

    buckets = {
        'intraday': [],      # < 24h
        'swing': [],         # 1-7 days
        'position': [],      # > 7 days
    }

    for t in trades:
        duration = t['exit_time'] - t['entry_time']
        if duration < timedelta(days=1):
            buckets['intraday'].append(t)
        elif duration < timedelta(days=7):
            buckets['swing'].append(t)
        else:
            buckets['position'].append(t)

    return {
        name: calculate_mae_statistics(trades)
        for name, trades in buckets.items()
    }
```

## MAE vs Drawdown

| Metric | Scope | Calculation | Use Case |
|--------|-------|-------------|----------|
| MAE | Per-trade | Worst point in single trade | Position sizing |
| Max Drawdown | Portfolio | Worst peak-to-trough | Strategy evaluation |
| Intra-trade DD | Per-trade | Same as MAE | Alternative term |
| Underwater | Portfolio | Time below high-water mark | Recovery analysis |

## Leverage Safety Formula

```python
def calculate_safe_leverage(mae_p95: float, buffer_pct: float = 0.10) -> float:
    """
    Calculate maximum safe leverage based on p95 MAE.

    Formula:
        max_leverage = 100 / (mae_p95 / (1 - buffer))

    Example:
        mae_p95 = 2.5%
        buffer = 10%
        max_leverage = 100 / (2.5 / 0.9) = 100 / 2.78 = 36x

    Args:
        mae_p95: 95th percentile MAE as percentage (e.g., 2.5 = 2.5%)
        buffer_pct: Safety buffer (0.10 = 10%)

    Returns:
        Maximum recommended leverage (capped at 50x)
    """
    if mae_p95 <= 0:
        return 50.0  # Maximum cap if no MAE data

    # Effective threshold with buffer
    effective_threshold = mae_p95 / (1 - buffer_pct)

    # Maximum leverage before hitting threshold
    max_lev = 100 / effective_threshold

    return min(max_lev, 50.0)  # Cap at 50x
```

## Risk Score Calculation

```python
def calculate_risk_score(
    mae_stats: Dict,
    leverage: float,
    n_trades: int
) -> Dict:
    """
    Calculate comprehensive risk score for leverage level.

    Returns:
        Dict with score, grade, and breakdown
    """
    # Get liquidation threshold for leverage
    liq_threshold = 100 / leverage

    # Calculate probability of liquidation
    maes = mae_stats['all_values']  # Assume we have raw values
    liquidation_prob = np.mean(maes >= liq_threshold) if maes else 0

    # Near-liquidation (within 50% of threshold)
    near_liq_prob = np.mean(maes >= liq_threshold * 0.5) if maes else 0

    # Score components (0-100, higher = safer)
    scores = {
        'liquidation_safety': (1 - liquidation_prob) * 100,
        'near_liq_safety': (1 - near_liq_prob) * 100,
        'p95_margin': max(0, (liq_threshold - mae_stats['p95']) / liq_threshold * 100),
        'consistency': 100 - min(100, mae_stats['std'] / mae_stats['mean'] * 100),
        'sample_size': min(100, n_trades / 5),  # Bonus for more trades
    }

    # Weighted average
    weights = {
        'liquidation_safety': 0.35,
        'near_liq_safety': 0.25,
        'p95_margin': 0.25,
        'consistency': 0.10,
        'sample_size': 0.05,
    }

    total_score = sum(scores[k] * weights[k] for k in scores)

    # Grade
    if total_score >= 90:
        grade = 'A'
        risk_level = 'LOW'
    elif total_score >= 75:
        grade = 'B'
        risk_level = 'MODERATE'
    elif total_score >= 60:
        grade = 'C'
        risk_level = 'ELEVATED'
    elif total_score >= 40:
        grade = 'D'
        risk_level = 'HIGH'
    else:
        grade = 'F'
        risk_level = 'EXTREME'

    return {
        'total_score': total_score,
        'grade': grade,
        'risk_level': risk_level,
        'components': scores,
        'liquidation_probability': liquidation_prob,
        'near_liquidation_probability': near_liq_prob,
    }
```

## Visualization

### MAE Distribution Histogram

```python
import matplotlib.pyplot as plt

def plot_mae_distribution(maes: List[float], leverage: float, output_path: str):
    """Plot MAE distribution with liquidation threshold."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Histogram
    ax.hist(maes, bins=50, density=True, alpha=0.7, color='#3fb950')

    # Liquidation threshold
    liq_threshold = 100 / leverage
    ax.axvline(liq_threshold, color='#f85149', linestyle='--',
               linewidth=2, label=f'{leverage}x Liquidation ({liq_threshold:.1f}%)')

    # Percentiles
    for p, color in [(90, '#58a6ff'), (95, '#d29922'), (99, '#a371f7')]:
        pval = np.percentile(maes, p)
        ax.axvline(pval, color=color, linestyle=':',
                   label=f'p{p}: {pval:.2f}%')

    ax.set_xlabel('MAE (%)')
    ax.set_ylabel('Density')
    ax.set_title(f'MAE Distribution ({len(maes)} trades)')
    ax.legend()

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
```

## Best Practices

1. **Minimum Sample Size**: Need 100+ trades for reliable p95/p99
2. **Time Period Coverage**: Include different market conditions
3. **Regime Segmentation**: Analyze MAE separately by regime
4. **Side Analysis**: Longs and shorts may have different MAE profiles
5. **Regular Updates**: Re-analyze as strategy evolves
6. **Stress Testing**: Consider what happens at 2x historical max MAE

## Common Mistakes

| Mistake | Why It's Dangerous |
|---------|-------------------|
| Using mean MAE | Ignores tail risk |
| Ignoring outliers | One outlier = liquidation |
| Small sample size | p95 unreliable with <50 trades |
| Not updating | Market conditions change |
| Single regime data | Bull market MAE != bear market MAE |
