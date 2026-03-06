#!/usr/bin/env python3
"""
Tearsheet Generator Helper Functions

Provides MAE analysis, leverage recommendations, and integration utilities
for the tearsheet-generator skill.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from scipy.stats import skew, kurtosis


@dataclass
class MAEStatistics:
    """MAE percentile statistics."""
    p50: float
    p75: float
    p90: float
    p95: float
    p99: float
    max: float
    mean: float
    std: float
    n_trades: int


@dataclass
class LeverageRecommendation:
    """Leverage recommendation with safety buffer."""
    buffer_pct: float
    max_leverage: float
    mae_p95: float
    effective_threshold: float
    safety_margin: float
    risk_level: str


@dataclass
class LiquidationRisk:
    """Liquidation risk assessment."""
    leverage: float
    threshold_pct: float
    liquidation_count: int
    near_liquidation_count: int
    survival_rate: float
    risk_score: str


def calculate_mae_percentiles(
    trades: List[Dict],
    mae_key: str = 'max_adverse_excursion'
) -> MAEStatistics:
    """
    Calculate MAE percentile statistics from trade list.

    Args:
        trades: List of trade dicts
        mae_key: Key for MAE value in trade dict

    Returns:
        MAEStatistics dataclass with all percentiles
    """
    maes = [
        t[mae_key] for t in trades
        if t.get(mae_key) is not None and t[mae_key] > 0
    ]

    if not maes:
        # Fallback: use absolute return_pct for losing trades
        maes = [
            abs(t.get('return_pct', 0))
            for t in trades
            if t.get('return_pct', 0) < 0
        ]

    if not maes:
        return MAEStatistics(
            p50=0, p75=0, p90=0, p95=0, p99=0,
            max=0, mean=0, std=0, n_trades=0
        )

    return MAEStatistics(
        p50=float(np.percentile(maes, 50)),
        p75=float(np.percentile(maes, 75)),
        p90=float(np.percentile(maes, 90)),
        p95=float(np.percentile(maes, 95)),
        p99=float(np.percentile(maes, 99)),
        max=float(np.max(maes)),
        mean=float(np.mean(maes)),
        std=float(np.std(maes)),
        n_trades=len(maes),
    )


def recommend_leverage(
    mae_p95: float,
    buffers: List[float] = [0.10, 0.20]
) -> List[LeverageRecommendation]:
    """
    Calculate leverage recommendations based on p95 MAE.

    Args:
        mae_p95: 95th percentile MAE (as percentage, e.g., 2.5 = 2.5%)
        buffers: List of safety buffer percentages

    Returns:
        List of LeverageRecommendation for each buffer level
    """
    recommendations = []

    for buffer in buffers:
        if mae_p95 <= 0:
            max_lev = 50.0  # Cap if no data
        else:
            # Effective threshold = mae / (1 - buffer)
            effective_threshold = mae_p95 / (1 - buffer)
            # Max leverage = 100 / effective_threshold
            max_lev = min(100 / effective_threshold, 50.0)

        # Determine risk level
        if max_lev >= 20:
            risk_level = 'LOW'
        elif max_lev >= 10:
            risk_level = 'MODERATE'
        elif max_lev >= 5:
            risk_level = 'ELEVATED'
        else:
            risk_level = 'HIGH'

        recommendations.append(LeverageRecommendation(
            buffer_pct=buffer * 100,
            max_leverage=max_lev,
            mae_p95=mae_p95,
            effective_threshold=mae_p95 / (1 - buffer) if mae_p95 > 0 else 0,
            safety_margin=buffer * (100 / max_lev) if max_lev > 0 else 0,
            risk_level=risk_level,
        ))

    return recommendations


def analyze_liquidation_risk(
    trades: List[Dict],
    leverage: float,
    mae_key: str = 'max_adverse_excursion'
) -> LiquidationRisk:
    """
    Analyze liquidation risk at specified leverage.

    Args:
        trades: List of trade dicts
        leverage: Leverage multiplier to analyze
        mae_key: Key for MAE value in trade dict

    Returns:
        LiquidationRisk assessment
    """
    threshold = 100 / leverage  # Liquidation threshold %

    maes = [
        t.get(mae_key, abs(t.get('return_pct', 0)) if t.get('return_pct', 0) < 0 else 0)
        for t in trades
    ]

    liquidations = sum(1 for mae in maes if mae >= threshold)
    near_liquidations = sum(1 for mae in maes if threshold * 0.5 <= mae < threshold)

    total_trades = len(trades)
    survival_rate = ((total_trades - liquidations) / total_trades * 100) if total_trades > 0 else 100

    # Risk scoring
    liq_pct = liquidations / total_trades * 100 if total_trades > 0 else 0
    if liq_pct == 0 and near_liquidations < total_trades * 0.05:
        risk_score = 'LOW'
    elif liq_pct < 1:
        risk_score = 'MEDIUM'
    elif liq_pct < 5:
        risk_score = 'HIGH'
    else:
        risk_score = 'EXTREME'

    return LiquidationRisk(
        leverage=leverage,
        threshold_pct=threshold,
        liquidation_count=liquidations,
        near_liquidation_count=near_liquidations,
        survival_rate=survival_rate,
        risk_score=risk_score,
    )


def calculate_dynamic_leverage(
    base_leverage: float,
    current_equity: float,
    high_water_mark: float,
    dd_threshold: float = 0.10
) -> float:
    """
    Calculate reduced leverage during drawdown.

    Args:
        base_leverage: Target leverage when not in drawdown
        current_equity: Current account equity
        high_water_mark: Peak equity achieved
        dd_threshold: Drawdown level to start reducing (default 10%)

    Returns:
        Adjusted leverage multiplier
    """
    if high_water_mark <= 0:
        return base_leverage

    drawdown_pct = (high_water_mark - current_equity) / high_water_mark

    if drawdown_pct <= dd_threshold:
        return base_leverage

    # Linear reduction
    reduction_factor = 1 - ((drawdown_pct - dd_threshold) / (1 - dd_threshold))
    adjusted_leverage = 1.0 + (base_leverage - 1.0) * max(0, reduction_factor)

    return max(1.0, adjusted_leverage)


def format_large_number(
    value: float,
    decimals: int = 2,
    prefix: str = "$"
) -> str:
    """
    Format large numbers with K, M, B, T, Q abbreviations.

    Args:
        value: Number to format
        decimals: Decimal places
        prefix: Currency prefix

    Returns:
        Formatted string
    """
    if value == 0:
        return f"{prefix}0"

    if not np.isfinite(value):
        return f"{prefix}∞" if value > 0 else f"-{prefix}∞"

    sign = "-" if value < 0 else ""
    abs_value = abs(value)

    if abs_value >= 1e100:
        return f"{sign}{prefix}>10^100"
    elif abs_value >= 1e24:
        exp = int(np.floor(np.log10(abs_value)))
        mantissa = abs_value / (10 ** exp)
        return f"{sign}{prefix}{mantissa:.1f}e{exp}"

    suffixes = [
        (1e18, "Qi"), (1e15, "Q"), (1e12, "T"),
        (1e9, "B"), (1e6, "M"), (1e3, "K"),
    ]

    for magnitude, suffix in suffixes:
        if abs_value >= magnitude:
            formatted_val = abs_value / magnitude
            if formatted_val >= 100:
                formatted = f"{formatted_val:.0f}"
            elif formatted_val >= 10:
                formatted = f"{formatted_val:.1f}"
            else:
                formatted = f"{formatted_val:.{decimals}f}"
            return f"{sign}{prefix}{formatted}{suffix}"

    if abs_value >= 1:
        return f"{sign}{prefix}{abs_value:,.{decimals}f}"
    else:
        return f"{sign}{prefix}{abs_value:.{decimals}f}"


def generate_mae_analysis_report(trades: List[Dict]) -> Dict:
    """
    Generate comprehensive MAE analysis report.

    Args:
        trades: List of trade dicts with MAE data

    Returns:
        Dict with full MAE analysis
    """
    stats = calculate_mae_percentiles(trades)

    # Get leverage recommendations
    recs = recommend_leverage(stats.p95)

    # Analyze risk at common leverage levels
    risk_analysis = {}
    for lev in [5.0, 10.0, 15.0, 20.0, 25.0]:
        risk_analysis[f'{int(lev)}x'] = analyze_liquidation_risk(trades, lev)

    return {
        'mae_statistics': {
            'p50': stats.p50,
            'p75': stats.p75,
            'p90': stats.p90,
            'p95': stats.p95,
            'p99': stats.p99,
            'max': stats.max,
            'mean': stats.mean,
            'std': stats.std,
            'n_trades': stats.n_trades,
        },
        'leverage_recommendations': [
            {
                'buffer': f"{rec.buffer_pct:.0f}%",
                'max_leverage': f"{rec.max_leverage:.1f}x",
                'effective_threshold': f"{rec.effective_threshold:.2f}%",
                'safety_margin': f"{rec.safety_margin:.2f}%",
                'risk_level': rec.risk_level,
            }
            for rec in recs
        ],
        'risk_analysis': {
            lev: {
                'threshold': f"{risk.threshold_pct:.2f}%",
                'liquidations': risk.liquidation_count,
                'near_liquidations': risk.near_liquidation_count,
                'survival_rate': f"{risk.survival_rate:.1f}%",
                'risk_score': risk.risk_score,
            }
            for lev, risk in risk_analysis.items()
        },
    }


def calculate_optimal_leverage(
    trades: List[Dict],
    metric: str = 'calmar',
    max_leverage: float = 25.0,
    step: float = 0.5
) -> Dict:
    """
    Find optimal leverage by simulation.

    Args:
        trades: List of trade dicts
        metric: Optimization target ('sharpe', 'sortino', 'calmar')
        max_leverage: Maximum leverage to test
        step: Step size for leverage grid

    Returns:
        Dict with optimal leverage and metrics
    """
    results = []
    leverages = np.arange(1.0, max_leverage + step, step)

    for lev in leverages:
        sim = simulate_leveraged_equity(trades, lev)
        risk = analyze_liquidation_risk(trades, lev)

        results.append({
            'leverage': lev,
            'return': sim['total_return'],
            'max_dd': sim['max_drawdown'],
            'sharpe': sim.get('sharpe', 0),
            'sortino': sim.get('sortino', 0),
            'calmar': sim['total_return'] / sim['max_drawdown'] if sim['max_drawdown'] > 0 else 0,
            'liquidations': risk.liquidation_count,
            'survival_rate': risk.survival_rate,
        })

    # Sort by metric
    results.sort(key=lambda x: x[metric], reverse=True)

    # Find best with 0 liquidations
    safe_results = [r for r in results if r['liquidations'] == 0]

    return {
        'optimal': safe_results[0] if safe_results else results[0],
        'max_safe_leverage': safe_results[0]['leverage'] if safe_results else 1.0,
        'all_results': results,
    }


def simulate_leveraged_equity(
    trades: List[Dict],
    leverage: float,
    initial_capital: float = 10000.0
) -> Dict:
    """
    Simulate equity curve with leverage.

    Args:
        trades: List of trade dicts
        leverage: Leverage multiplier
        initial_capital: Starting capital

    Returns:
        Dict with equity curve metrics
    """
    equity = initial_capital
    high_water_mark = initial_capital
    max_drawdown = 0
    equity_curve = [equity]

    for trade in trades:
        base_return = trade.get('return_pct', 0) / 100
        leveraged_return = base_return * leverage

        equity = equity * (1 + leveraged_return)
        equity_curve.append(equity)

        high_water_mark = max(high_water_mark, equity)
        drawdown = (high_water_mark - equity) / high_water_mark
        max_drawdown = max(max_drawdown, drawdown)

    total_return = (equity - initial_capital) / initial_capital * 100

    # Calculate Sharpe/Sortino from returns
    returns = np.diff(equity_curve) / equity_curve[:-1]
    sharpe = np.sqrt(252) * np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0

    downside_returns = returns[returns < 0]
    sortino = np.sqrt(252) * np.mean(returns) / np.std(downside_returns) if len(downside_returns) > 0 and np.std(downside_returns) > 0 else 0

    return {
        'equity_curve': equity_curve,
        'final_equity': equity,
        'total_return': total_return,
        'max_drawdown': max_drawdown * 100,
        'sharpe': sharpe,
        'sortino': sortino,
    }


# Example usage and CLI
if __name__ == '__main__':
    import json
    import sys

    print("Tearsheet Generator Helpers")
    print("=" * 50)

    # Example trades
    example_trades = [
        {'return_pct': 2.5, 'max_adverse_excursion': 1.2},
        {'return_pct': -1.5, 'max_adverse_excursion': 2.8},
        {'return_pct': 3.2, 'max_adverse_excursion': 0.8},
        {'return_pct': -0.8, 'max_adverse_excursion': 1.5},
        {'return_pct': 1.8, 'max_adverse_excursion': 0.5},
    ]

    print("\nMAE Statistics:")
    stats = calculate_mae_percentiles(example_trades)
    print(f"  p50: {stats.p50:.2f}%")
    print(f"  p95: {stats.p95:.2f}%")
    print(f"  max: {stats.max:.2f}%")

    print("\nLeverage Recommendations (based on p95 MAE):")
    recs = recommend_leverage(stats.p95)
    for rec in recs:
        print(f"  {rec.buffer_pct:.0f}% buffer: {rec.max_leverage:.1f}x max ({rec.risk_level})")

    print("\nLiquidation Risk at 10x:")
    risk = analyze_liquidation_risk(example_trades, 10.0)
    print(f"  Threshold: {risk.threshold_pct:.1f}%")
    print(f"  Liquidations: {risk.liquidation_count}")
    print(f"  Survival Rate: {risk.survival_rate:.1f}%")
    print(f"  Risk Score: {risk.risk_score}")
