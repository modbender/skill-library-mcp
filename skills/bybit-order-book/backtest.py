#!/usr/bin/env python3
"""
ByBit Order Book Backtesting Engine

Runs 10 order-book-based trading strategies against processed Parquet data
and produces a full performance report for each.

Strategies:
  1. Order Book Imbalance
  2. Breakout
  3. False Breakout
  4. Scalping
  5. Momentum Trading
  6. Reversal Trading
  7. Spoofing Detection
  8. Optimal Execution
  9. Market Making
 10. Latency Arbitrage

Usage:
    python backtest.py --input ./data/processed/BTCUSDT_ob50.parquet --output ./reports
    python backtest.py --input ./data/processed/BTCUSDT_ob50.parquet --strategies imbalance,breakout
"""

import argparse
import json
import os
import sys
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional

warnings.filterwarnings("ignore")

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: Missing dependencies. Install with:")
    print("  pip install pandas numpy pyarrow --break-system-packages")
    sys.exit(1)


# =============================================================================
# Trade & Performance Tracking
# =============================================================================

@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: Optional[pd.Timestamp]
    side: str  # "long" or "short"
    entry_price: float
    exit_price: float = 0.0
    size: float = 1.0
    pnl: float = 0.0
    is_open: bool = True

    def close(self, exit_price: float, exit_time: pd.Timestamp):
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.is_open = False
        if self.side == "long":
            self.pnl = (self.exit_price - self.entry_price) * self.size
        else:
            self.pnl = (self.entry_price - self.exit_price) * self.size

    @property
    def hold_time(self) -> Optional[timedelta]:
        if self.exit_time and self.entry_time:
            return self.exit_time - self.entry_time
        return None


def compute_performance(trades: List[Trade], strategy_name: str) -> dict:
    """Compute full performance metrics from a list of trades."""
    closed = [t for t in trades if not t.is_open]

    if not closed:
        return {
            "strategy": strategy_name,
            "total_trades": 0,
            "win_rate": 0.0,
            "cumulative_pnl": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_pct": 0.0,
            "avg_pnl_per_trade": 0.0,
            "avg_hold_time": "N/A",
            "profit_factor": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
        }

    pnls = [t.pnl for t in closed]
    cumulative = np.cumsum(pnls)
    winners = [p for p in pnls if p > 0]
    losers = [p for p in pnls if p <= 0]

    # Sharpe ratio (annualized, assuming ~8640 100ms snapshots per 15min)
    pnl_series = pd.Series(pnls)
    if pnl_series.std() > 0:
        sharpe = (pnl_series.mean() / pnl_series.std()) * np.sqrt(252 * 24 * 4)  # ~15min periods in a year
    else:
        sharpe = 0.0

    # Max drawdown
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = running_max - cumulative
    max_dd = float(drawdowns.max()) if len(drawdowns) > 0 else 0.0
    max_dd_pct = (max_dd / running_max[drawdowns.argmax()]) * 100 if running_max[drawdowns.argmax()] > 0 else 0.0

    # Average hold time
    hold_times = [t.hold_time for t in closed if t.hold_time is not None]
    avg_hold = str(sum(hold_times, timedelta()) / len(hold_times)) if hold_times else "N/A"

    # Profit factor
    gross_profit = sum(winners) if winners else 0.0
    gross_loss = abs(sum(losers)) if losers else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf") if gross_profit > 0 else 0.0

    return {
        "strategy": strategy_name,
        "total_trades": len(closed),
        "winners": len(winners),
        "losers": len(losers),
        "win_rate": len(winners) / len(closed) * 100,
        "cumulative_pnl": float(cumulative[-1]),
        "sharpe_ratio": round(sharpe, 3),
        "max_drawdown": round(max_dd, 4),
        "max_drawdown_pct": round(max_dd_pct, 2),
        "avg_pnl_per_trade": round(float(pnl_series.mean()), 4),
        "avg_hold_time": avg_hold,
        "profit_factor": round(profit_factor, 3),
        "best_trade": round(max(pnls), 4),
        "worst_trade": round(min(pnls), 4),
        "equity_curve": cumulative.tolist(),
    }


# =============================================================================
# Base Strategy
# =============================================================================

class Strategy(ABC):
    """Base class for all order book strategies."""

    def __init__(self, name: str, params: dict = None):
        self.name = name
        self.params = params or {}
        self.trades: List[Trade] = []
        self.position: Optional[Trade] = None

    def open_long(self, price: float, time: pd.Timestamp, size: float = 1.0):
        if self.position is None:
            self.position = Trade(entry_time=time, exit_time=None, side="long", entry_price=price, size=size)

    def open_short(self, price: float, time: pd.Timestamp, size: float = 1.0):
        if self.position is None:
            self.position = Trade(entry_time=time, exit_time=None, side="short", entry_price=price, size=size)

    def close_position(self, price: float, time: pd.Timestamp):
        if self.position is not None:
            self.position.close(price, time)
            self.trades.append(self.position)
            self.position = None

    @abstractmethod
    def on_snapshot(self, row: pd.Series, idx: int, df: pd.DataFrame):
        """Process a single order book snapshot. Implement trading logic here."""
        pass

    def run(self, df: pd.DataFrame) -> dict:
        """Run the strategy over the entire dataset."""
        print(f"  Running: {self.name}...")
        for idx in range(len(df)):
            self.on_snapshot(df.iloc[idx], idx, df)

        # Force-close any open position at the end
        if self.position is not None:
            last = df.iloc[-1]
            self.close_position(last["mid_price"], last["timestamp"])

        result = compute_performance(self.trades, self.name)
        print(f"    Trades: {result['total_trades']}, PnL: {result['cumulative_pnl']:.4f}, "
              f"Win Rate: {result['win_rate']:.1f}%, Sharpe: {result['sharpe_ratio']}")
        return result


# =============================================================================
# Strategy Implementations
# =============================================================================

class OrderBookImbalanceStrategy(Strategy):
    """
    Trades based on bid/ask volume imbalance.
    Long when bids >> asks (buying pressure), short when asks >> bids.
    """

    def __init__(self):
        super().__init__("Order Book Imbalance", {
            "imbalance_threshold": 0.3,
            "exit_imbalance": 0.0,
            "lookback": 20,
            "cooldown": 10,
        })
        self.last_trade_idx = -100

    def on_snapshot(self, row, idx, df):
        if idx < self.params["lookback"]:
            return
        if idx - self.last_trade_idx < self.params["cooldown"]:
            return

        imb = row.get("volume_imbalance", 0.0)
        threshold = self.params["imbalance_threshold"]

        # Close on imbalance reversal
        if self.position is not None:
            if self.position.side == "long" and imb < self.params["exit_imbalance"]:
                self.close_position(row["mid_price"], row["timestamp"])
                self.last_trade_idx = idx
            elif self.position.side == "short" and imb > -self.params["exit_imbalance"]:
                self.close_position(row["mid_price"], row["timestamp"])
                self.last_trade_idx = idx
            return

        # Entry signals
        if imb > threshold:
            self.open_long(row["best_ask"], row["timestamp"])
            self.last_trade_idx = idx
        elif imb < -threshold:
            self.open_short(row["best_bid"], row["timestamp"])
            self.last_trade_idx = idx


class BreakoutStrategy(Strategy):
    """
    Detects when price breaks through a support/resistance level defined
    by order book depth concentration. Enters in breakout direction.
    """

    def __init__(self):
        super().__init__("Breakout", {
            "lookback": 100,
            "breakout_pct": 0.001,  # 0.1% price move
            "hold_periods": 50,
            "volume_confirm_ratio": 1.5,
        })
        self.entry_idx = 0

    def on_snapshot(self, row, idx, df):
        lb = self.params["lookback"]
        if idx < lb:
            return

        # Close after hold period
        if self.position is not None:
            if idx - self.entry_idx >= self.params["hold_periods"]:
                self.close_position(row["mid_price"], row["timestamp"])
            return

        window = df.iloc[idx - lb:idx]
        high = window["best_ask"].max()
        low = window["best_bid"].min()
        mid = row["mid_price"]

        # Breakout above resistance
        if mid > high * (1 + self.params["breakout_pct"]):
            if row["total_bid_volume"] > window["total_bid_volume"].mean() * self.params["volume_confirm_ratio"]:
                self.open_long(row["best_ask"], row["timestamp"])
                self.entry_idx = idx

        # Breakout below support
        elif mid < low * (1 - self.params["breakout_pct"]):
            if row["total_ask_volume"] > window["total_ask_volume"].mean() * self.params["volume_confirm_ratio"]:
                self.open_short(row["best_bid"], row["timestamp"])
                self.entry_idx = idx


class FalseBreakoutStrategy(Strategy):
    """
    Fades breakouts that fail — price breaks a level but quickly reverses,
    indicated by absorption (large resting orders) in the book.
    """

    def __init__(self):
        super().__init__("False Breakout", {
            "lookback": 100,
            "breakout_pct": 0.0008,
            "reversal_pct": 0.0003,
            "hold_periods": 30,
            "absorption_ratio": 2.0,
        })
        self.breakout_detected = None
        self.breakout_idx = 0
        self.entry_idx = 0

    def on_snapshot(self, row, idx, df):
        lb = self.params["lookback"]
        if idx < lb:
            return

        # Close after hold period
        if self.position is not None:
            if idx - self.entry_idx >= self.params["hold_periods"]:
                self.close_position(row["mid_price"], row["timestamp"])
            return

        window = df.iloc[idx - lb:idx]
        high = window["best_ask"].max()
        low = window["best_bid"].min()
        mid = row["mid_price"]

        # Detect breakout
        if self.breakout_detected is None:
            if mid > high * (1 + self.params["breakout_pct"]):
                self.breakout_detected = "up"
                self.breakout_idx = idx
            elif mid < low * (1 - self.params["breakout_pct"]):
                self.breakout_detected = "down"
                self.breakout_idx = idx
        else:
            # Check for false breakout (reversal within next few snapshots)
            periods_since = idx - self.breakout_idx
            if periods_since > 20:
                self.breakout_detected = None
                return

            if self.breakout_detected == "up" and mid < high:
                # False upside breakout — go short (fade)
                if row["total_ask_volume"] > row["total_bid_volume"] * self.params["absorption_ratio"]:
                    self.open_short(row["best_bid"], row["timestamp"])
                    self.entry_idx = idx
                    self.breakout_detected = None

            elif self.breakout_detected == "down" and mid > low:
                # False downside breakout — go long (fade)
                if row["total_bid_volume"] > row["total_ask_volume"] * self.params["absorption_ratio"]:
                    self.open_long(row["best_ask"], row["timestamp"])
                    self.entry_idx = idx
                    self.breakout_detected = None


class ScalpingStrategy(Strategy):
    """
    Ultra-short-term strategy exploiting bid-ask bounce.
    Enters on microprice signal and exits on small profit or tight stop.
    """

    def __init__(self):
        super().__init__("Scalping", {
            "microprice_threshold": 0.0002,
            "take_profit_bps": 2.0,
            "stop_loss_bps": 3.0,
            "min_spread_bps": 0.5,
            "cooldown": 5,
        })
        self.last_trade_idx = -100

    def on_snapshot(self, row, idx, df):
        if idx - self.last_trade_idx < self.params["cooldown"]:
            if self.position is None:
                return

        spread_bps = row.get("spread_bps", 100)
        mid = row["mid_price"]

        # Check exits
        if self.position is not None:
            pnl_bps = 0
            if self.position.side == "long":
                pnl_bps = (mid - self.position.entry_price) / self.position.entry_price * 10000
            else:
                pnl_bps = (self.position.entry_price - mid) / self.position.entry_price * 10000

            if pnl_bps >= self.params["take_profit_bps"] or pnl_bps <= -self.params["stop_loss_bps"]:
                self.close_position(mid, row["timestamp"])
                self.last_trade_idx = idx
            return

        # Only scalp in tight spread conditions
        if spread_bps > self.params["min_spread_bps"] * 5:
            return

        micro = row.get("microprice", mid)
        micro_signal = (micro - mid) / mid

        if micro_signal > self.params["microprice_threshold"]:
            self.open_long(row["best_ask"], row["timestamp"])
            self.last_trade_idx = idx
        elif micro_signal < -self.params["microprice_threshold"]:
            self.open_short(row["best_bid"], row["timestamp"])
            self.last_trade_idx = idx


class MomentumTradingStrategy(Strategy):
    """
    Detects momentum from order flow — sustained directional pressure
    in the book over a lookback window.
    """

    def __init__(self):
        super().__init__("Momentum Trading", {
            "lookback": 50,
            "momentum_threshold": 0.0005,
            "exit_reversal_pct": 0.3,
            "hold_periods": 80,
        })
        self.entry_idx = 0

    def on_snapshot(self, row, idx, df):
        lb = self.params["lookback"]
        if idx < lb:
            return

        # Close after hold period or reversal
        if self.position is not None:
            if idx - self.entry_idx >= self.params["hold_periods"]:
                self.close_position(row["mid_price"], row["timestamp"])
                return
            window = df.iloc[idx - 10:idx]
            recent_imb = window["volume_imbalance"].mean()
            if self.position.side == "long" and recent_imb < -self.params["exit_reversal_pct"]:
                self.close_position(row["mid_price"], row["timestamp"])
            elif self.position.side == "short" and recent_imb > self.params["exit_reversal_pct"]:
                self.close_position(row["mid_price"], row["timestamp"])
            return

        window = df.iloc[idx - lb:idx]
        price_change = (row["mid_price"] - window["mid_price"].iloc[0]) / window["mid_price"].iloc[0]
        avg_imbalance = window["volume_imbalance"].mean()

        # Momentum up
        if price_change > self.params["momentum_threshold"] and avg_imbalance > 0.1:
            self.open_long(row["best_ask"], row["timestamp"])
            self.entry_idx = idx
        # Momentum down
        elif price_change < -self.params["momentum_threshold"] and avg_imbalance < -0.1:
            self.open_short(row["best_bid"], row["timestamp"])
            self.entry_idx = idx


class ReversalTradingStrategy(Strategy):
    """
    Mean-reversion strategy that detects overextension via book thinning
    and imbalance extremes, then trades the expected reversal.
    """

    def __init__(self):
        super().__init__("Reversal Trading", {
            "lookback": 100,
            "overextension_pct": 0.002,
            "imbalance_extreme": 0.5,
            "hold_periods": 60,
            "stop_loss_pct": 0.003,
        })
        self.entry_idx = 0

    def on_snapshot(self, row, idx, df):
        lb = self.params["lookback"]
        if idx < lb:
            return

        mid = row["mid_price"]

        # Close conditions
        if self.position is not None:
            if idx - self.entry_idx >= self.params["hold_periods"]:
                self.close_position(mid, row["timestamp"])
                return
            pnl_pct = 0
            if self.position.side == "long":
                pnl_pct = (mid - self.position.entry_price) / self.position.entry_price
            else:
                pnl_pct = (self.position.entry_price - mid) / self.position.entry_price
            if pnl_pct < -self.params["stop_loss_pct"]:
                self.close_position(mid, row["timestamp"])
            return

        window = df.iloc[idx - lb:idx]
        avg_mid = window["mid_price"].mean()
        deviation = (mid - avg_mid) / avg_mid
        imb = row.get("volume_imbalance", 0.0)

        # Overextended up + selling pressure building → short reversal
        if deviation > self.params["overextension_pct"] and imb < -self.params["imbalance_extreme"]:
            self.open_short(row["best_bid"], row["timestamp"])
            self.entry_idx = idx
        # Overextended down + buying pressure building → long reversal
        elif deviation < -self.params["overextension_pct"] and imb > self.params["imbalance_extreme"]:
            self.open_long(row["best_ask"], row["timestamp"])
            self.entry_idx = idx


class SpoofingDetectionStrategy(Strategy):
    """
    Detects potential spoofing: large resting orders that suddenly disappear
    before they can be filled, indicating fake liquidity. Trades the
    likely true direction after spoof removal.
    """

    def __init__(self):
        super().__init__("Spoofing Detection", {
            "volume_spike_ratio": 3.0,
            "disappearance_ratio": 0.3,
            "lookback": 20,
            "hold_periods": 40,
            "cooldown": 15,
        })
        self.prev_bid_vol = 0
        self.prev_ask_vol = 0
        self.entry_idx = 0
        self.last_trade_idx = -100

    def on_snapshot(self, row, idx, df):
        if idx < self.params["lookback"]:
            self.prev_bid_vol = row["total_bid_volume"]
            self.prev_ask_vol = row["total_ask_volume"]
            return

        if idx - self.last_trade_idx < self.params["cooldown"] and self.position is None:
            self.prev_bid_vol = row["total_bid_volume"]
            self.prev_ask_vol = row["total_ask_volume"]
            return

        bid_vol = row["total_bid_volume"]
        ask_vol = row["total_ask_volume"]
        window = df.iloc[idx - self.params["lookback"]:idx]
        avg_bid = window["total_bid_volume"].mean()
        avg_ask = window["total_ask_volume"].mean()

        # Close after hold
        if self.position is not None:
            if idx - self.entry_idx >= self.params["hold_periods"]:
                self.close_position(row["mid_price"], row["timestamp"])
            self.prev_bid_vol = bid_vol
            self.prev_ask_vol = ask_vol
            return

        # Detect bid-side spoof: large bids appeared then vanished
        if (self.prev_bid_vol > avg_bid * self.params["volume_spike_ratio"] and
                bid_vol < self.prev_bid_vol * self.params["disappearance_ratio"]):
            # Fake buy wall removed → price likely to drop
            self.open_short(row["best_bid"], row["timestamp"])
            self.entry_idx = idx
            self.last_trade_idx = idx

        # Detect ask-side spoof: large asks appeared then vanished
        elif (self.prev_ask_vol > avg_ask * self.params["volume_spike_ratio"] and
              ask_vol < self.prev_ask_vol * self.params["disappearance_ratio"]):
            # Fake sell wall removed → price likely to rise
            self.open_long(row["best_ask"], row["timestamp"])
            self.entry_idx = idx
            self.last_trade_idx = idx

        self.prev_bid_vol = bid_vol
        self.prev_ask_vol = ask_vol


class OptimalExecutionStrategy(Strategy):
    """
    TWAP/VWAP-inspired execution that splits a large order into slices,
    executing when the book shows favorable depth. Measures execution quality.
    """

    def __init__(self):
        super().__init__("Optimal Execution", {
            "total_slices": 10,
            "slice_interval": 50,  # snapshots between slices
            "favorable_imbalance": 0.1,
            "direction": "buy",  # simulates buying
        })
        self.slices_executed = 0
        self.slice_prices = []
        self.next_slice_idx = 50

    def on_snapshot(self, row, idx, df):
        if self.slices_executed >= self.params["total_slices"]:
            return

        if idx < self.next_slice_idx:
            return

        imb = row.get("volume_imbalance", 0.0)
        direction = self.params["direction"]

        # Execute slice when conditions are favorable
        favorable = (direction == "buy" and imb > self.params["favorable_imbalance"]) or \
                    (direction == "sell" and imb < -self.params["favorable_imbalance"])

        # Or just execute at the interval (TWAP baseline)
        if favorable or (idx - self.next_slice_idx > self.params["slice_interval"]):
            price = row["best_ask"] if direction == "buy" else row["best_bid"]
            self.slice_prices.append(price)

            # Model each slice as a round-trip trade for PnL tracking
            trade = Trade(
                entry_time=row["timestamp"],
                exit_time=row["timestamp"],
                side="long" if direction == "buy" else "short",
                entry_price=price,
                size=1.0 / self.params["total_slices"],
            )
            # Measure slippage against mid as PnL proxy
            if direction == "buy":
                trade.close(row["mid_price"], row["timestamp"])
            else:
                trade.close(row["mid_price"], row["timestamp"])
            self.trades.append(trade)

            self.slices_executed += 1
            self.next_slice_idx = idx + self.params["slice_interval"]

    def run(self, df):
        """Override to add execution quality metrics."""
        print(f"  Running: {self.name}...")
        for idx in range(len(df)):
            self.on_snapshot(df.iloc[idx], idx, df)

        result = compute_performance(self.trades, self.name)
        if self.slice_prices:
            vwap = np.mean(self.slice_prices)
            result["avg_execution_price"] = round(vwap, 4)
            result["execution_slices"] = self.slices_executed
        print(f"    Slices: {self.slices_executed}, Avg Price: {result.get('avg_execution_price', 'N/A')}")
        return result


class MarketMakingStrategy(Strategy):
    """
    Posts limit orders on both sides of the book, profiting from the spread.
    Uses order book depth to adjust quoting distance.
    """

    def __init__(self):
        super().__init__("Market Making", {
            "quote_offset_bps": 1.5,
            "take_profit_bps": 1.0,
            "stop_loss_bps": 5.0,
            "max_inventory": 3,
            "rebalance_threshold": 2,
            "cooldown": 3,
        })
        self.inventory = 0  # positive = long bias, negative = short bias
        self.last_trade_idx = -100

    def on_snapshot(self, row, idx, df):
        if idx - self.last_trade_idx < self.params["cooldown"] and self.position is None:
            return

        mid = row["mid_price"]
        spread_bps = row.get("spread_bps", 100)

        # Manage open position
        if self.position is not None:
            if self.position.side == "long":
                pnl_bps = (mid - self.position.entry_price) / self.position.entry_price * 10000
            else:
                pnl_bps = (self.position.entry_price - mid) / self.position.entry_price * 10000

            if pnl_bps >= self.params["take_profit_bps"] or pnl_bps <= -self.params["stop_loss_bps"]:
                if self.position.side == "long":
                    self.inventory -= 1
                else:
                    self.inventory += 1
                self.close_position(mid, row["timestamp"])
                self.last_trade_idx = idx
            return

        # Skip if spread is too wide (unfavorable for MM)
        if spread_bps > 10:
            return

        offset = self.params["quote_offset_bps"] / 10000
        imb = row.get("volume_imbalance", 0.0)

        # Skew quotes based on inventory
        if abs(self.inventory) < self.params["max_inventory"]:
            # More likely to get filled on the side with more flow
            if imb > 0.05 and self.inventory < self.params["rebalance_threshold"]:
                # Buying pressure → our ask more likely filled → go short (sell)
                self.open_short(mid * (1 + offset), row["timestamp"])
                self.inventory += 1
                self.last_trade_idx = idx
            elif imb < -0.05 and self.inventory > -self.params["rebalance_threshold"]:
                # Selling pressure → our bid more likely filled → go long (buy)
                self.open_long(mid * (1 - offset), row["timestamp"])
                self.inventory -= 1
                self.last_trade_idx = idx


class LatencyArbitrageStrategy(Strategy):
    """
    Exploits stale book quotes by detecting when the microprice diverges
    significantly from the mid price, indicating a book update lag.
    """

    def __init__(self):
        super().__init__("Latency Arbitrage", {
            "divergence_bps": 1.5,
            "hold_periods": 10,
            "cooldown": 8,
            "min_volume_ratio": 1.2,
        })
        self.entry_idx = 0
        self.last_trade_idx = -100

    def on_snapshot(self, row, idx, df):
        if idx < 10:
            return
        if idx - self.last_trade_idx < self.params["cooldown"] and self.position is None:
            return

        mid = row["mid_price"]
        micro = row.get("microprice", mid)

        # Close after brief hold
        if self.position is not None:
            if idx - self.entry_idx >= self.params["hold_periods"]:
                self.close_position(mid, row["timestamp"])
                self.last_trade_idx = idx
            return

        divergence_bps = abs(micro - mid) / mid * 10000

        if divergence_bps >= self.params["divergence_bps"]:
            # Microprice leads — trade toward it
            if micro > mid:
                self.open_long(row["best_ask"], row["timestamp"])
            else:
                self.open_short(row["best_bid"], row["timestamp"])
            self.entry_idx = idx
            self.last_trade_idx = idx


# =============================================================================
# Strategy Registry
# =============================================================================

STRATEGY_MAP = {
    "imbalance": OrderBookImbalanceStrategy,
    "breakout": BreakoutStrategy,
    "false_breakout": FalseBreakoutStrategy,
    "scalping": ScalpingStrategy,
    "momentum": MomentumTradingStrategy,
    "reversal": ReversalTradingStrategy,
    "spoofing": SpoofingDetectionStrategy,
    "optimal_execution": OptimalExecutionStrategy,
    "market_making": MarketMakingStrategy,
    "latency_arb": LatencyArbitrageStrategy,
}

ALL_STRATEGIES = list(STRATEGY_MAP.keys())


# =============================================================================
# Report Generation
# =============================================================================

def generate_report(results: List[dict], output_dir: str, symbol: str):
    """Generate a comparison report as JSON and markdown."""
    os.makedirs(output_dir, exist_ok=True)

    # Remove equity curves for the summary (they're large)
    summary = []
    for r in results:
        s = {k: v for k, v in r.items() if k != "equity_curve"}
        summary.append(s)

    # JSON report
    json_path = os.path.join(output_dir, f"{symbol}_backtest_report.json")
    with open(json_path, "w") as f:
        json.dump({"symbol": symbol, "strategies": results}, f, indent=2, default=str)

    # Markdown report
    md_path = os.path.join(output_dir, f"{symbol}_backtest_report.md")
    with open(md_path, "w") as f:
        f.write(f"# Order Book Backtest Report — {symbol}\n\n")
        f.write(f"**Depth:** 50 levels | **Strategies:** {len(results)}\n\n")

        # Summary table
        f.write("## Strategy Comparison\n\n")
        f.write("| Strategy | Trades | Win Rate | Cumulative PnL | Sharpe | Max DD | Profit Factor |\n")
        f.write("|----------|--------|----------|----------------|--------|--------|---------------|\n")
        for s in summary:
            f.write(f"| {s['strategy']} | {s['total_trades']} | {s['win_rate']:.1f}% | "
                    f"{s['cumulative_pnl']:.4f} | {s['sharpe_ratio']} | {s['max_drawdown']:.4f} | "
                    f"{s['profit_factor']} |\n")

        # Individual strategy details
        f.write("\n## Detailed Results\n\n")
        for s in summary:
            f.write(f"### {s['strategy']}\n\n")
            for k, v in s.items():
                if k == "strategy":
                    continue
                f.write(f"- **{k.replace('_', ' ').title()}:** {v}\n")
            f.write("\n")

    print(f"\nReports saved:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    return json_path, md_path


# =============================================================================
# Main
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Backtest order book strategies")
    parser.add_argument("--input", type=str, required=True, help="Path to processed Parquet file")
    parser.add_argument("--output", type=str, default="./reports", help="Output directory for reports")
    parser.add_argument("--strategies", type=str, default="all",
                        help=f"Comma-separated strategy names or 'all'. Options: {', '.join(ALL_STRATEGIES)}")
    parser.add_argument("--max-rows", type=int, default=None,
                        help="Limit rows for faster testing (default: use all)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load data
    print(f"Loading data from {args.input}...")
    df = pd.read_parquet(args.input)
    if args.max_rows:
        df = df.head(args.max_rows)
    print(f"  Loaded {len(df):,} snapshots")

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"

    # Required columns check
    required = ["timestamp", "mid_price", "best_bid", "best_ask", "volume_imbalance",
                "total_bid_volume", "total_ask_volume", "spread_bps", "microprice"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"ERROR: Missing columns: {missing}")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)

    # Select strategies
    if args.strategies == "all":
        strategy_names = ALL_STRATEGIES
    else:
        strategy_names = [s.strip() for s in args.strategies.split(",")]
        invalid = [s for s in strategy_names if s not in STRATEGY_MAP]
        if invalid:
            print(f"ERROR: Unknown strategies: {invalid}")
            print(f"Available: {ALL_STRATEGIES}")
            sys.exit(1)

    print(f"\nRunning {len(strategy_names)} strategies on {symbol}...\n")

    # Run each strategy
    results = []
    for name in strategy_names:
        strategy = STRATEGY_MAP[name]()
        result = strategy.run(df)
        results.append(result)

    # Generate reports
    generate_report(results, args.output, symbol)


if __name__ == "__main__":
    main()
