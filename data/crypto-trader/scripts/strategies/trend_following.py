"""
Trend Following Strategy.

Uses Exponential Moving Averages (EMA) and Relative Strength Index (RSI)
to detect trend direction and momentum. Enters positions when the short
EMA crosses above/below the long EMA, confirmed by RSI signals.

Parameters
----------
symbol : str
    Trading pair, e.g. "BTC/USDT".
timeframe : str
    Candlestick timeframe: "1h", "4h", "1d".
ema_short : int
    Short EMA period (e.g. 9).
ema_long : int
    Long EMA period (e.g. 21).
rsi_period : int
    RSI lookback period (e.g. 14).
rsi_overbought : float
    RSI overbought threshold (e.g. 70).
rsi_oversold : float
    RSI oversold threshold (e.g. 30).
order_amount_usdt : float
    USDT amount per trade.
exchange : str
    Exchange to trade on.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from strategy_engine import BaseStrategy

logger = logging.getLogger("crypto-trader.strategy.trend")


def _calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


def _calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, float("inf"))
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


class TrendFollowingStrategy(BaseStrategy):
    name = "trend_following"
    display_name = "Trend Following"

    def __init__(self, strategy_id: str, params: Dict[str, Any], exchange_manager: Any, risk_manager: Any) -> None:
        super().__init__(strategy_id, params, exchange_manager, risk_manager)
        self.symbol: str = params.get("symbol", "BTC/USDT")
        self.timeframe: str = params.get("timeframe", "4h")
        self.ema_short_period: int = params.get("ema_short", 9)
        self.ema_long_period: int = params.get("ema_long", 21)
        self.rsi_period: int = params.get("rsi_period", 14)
        self.rsi_overbought: float = params.get("rsi_overbought", 70)
        self.rsi_oversold: float = params.get("rsi_oversold", 30)
        self.order_amount_usdt: float = params.get("order_amount_usdt", 25.0)
        self.exchange: str = params.get("exchange", "")

        self.position: Optional[str] = None
        self.entry_price: float = 0.0
        self.highest_since_entry: float = 0.0
        self.last_signal: Optional[str] = None

    def on_start(self) -> None:
        super().on_start()
        if not self.exchange:
            available = self.exchange_manager.available_exchanges
            if available:
                self.exchange = available[0]
            else:
                logger.error("No exchanges available.")
                self.active = False
                return

        candles_needed = max(self.ema_long_period, self.rsi_period) + 10
        logger.info(
            "Trend following started: %s %s on %s, EMA(%d/%d), RSI(%d), need %d candles",
            self.symbol, self.timeframe, self.exchange,
            self.ema_short_period, self.ema_long_period, self.rsi_period,
            candles_needed,
        )

    def evaluate(self) -> List[Dict[str, Any]]:
        """Fetch OHLCV data, compute indicators, and generate signals."""
        if not self.active:
            return []

        candles_needed = max(self.ema_long_period, self.rsi_period) + 10

        try:
            ohlcv = self.exchange_manager.get_ohlcv(
                self.exchange, self.symbol, self.timeframe, limit=candles_needed * 2,
            )
        except Exception as exc:
            logger.error("Failed to fetch OHLCV for %s: %s", self.symbol, exc)
            return []

        if len(ohlcv) < candles_needed:
            logger.warning("Not enough candles (%d < %d) for %s", len(ohlcv), candles_needed, self.symbol)
            return []

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["ema_short"] = _calculate_ema(df["close"], self.ema_short_period)
        df["ema_long"] = _calculate_ema(df["close"], self.ema_long_period)
        df["rsi"] = _calculate_rsi(df["close"], self.rsi_period)

        current = df.iloc[-1]
        previous = df.iloc[-2]

        current_price = current["close"]
        ema_short = current["ema_short"]
        ema_long = current["ema_long"]
        rsi = current["rsi"]

        prev_ema_short = previous["ema_short"]
        prev_ema_long = previous["ema_long"]

        bullish_cross = prev_ema_short <= prev_ema_long and ema_short > ema_long
        bearish_cross = prev_ema_short >= prev_ema_long and ema_short < ema_long

        signals: List[Dict[str, Any]] = []
        amount = self.order_amount_usdt / current_price if current_price > 0 else 0

        if bullish_cross and rsi < self.rsi_overbought:
            if self.position != "long":
                signals.append({
                    "symbol": self.symbol,
                    "side": "buy",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": (
                        f"Bullish EMA cross: EMA({self.ema_short_period})={ema_short:.2f} > "
                        f"EMA({self.ema_long_period})={ema_long:.2f}, RSI={rsi:.1f}"
                    ),
                    "indicators": {
                        "ema_short": round(ema_short, 2),
                        "ema_long": round(ema_long, 2),
                        "rsi": round(rsi, 1),
                        "signal": "bullish_cross",
                    },
                })
                self.last_signal = "buy"

        elif bearish_cross or (self.position == "long" and rsi > self.rsi_overbought):
            if self.position == "long":
                reason_parts = []
                if bearish_cross:
                    reason_parts.append(
                        f"Bearish EMA cross: EMA({self.ema_short_period})={ema_short:.2f} < "
                        f"EMA({self.ema_long_period})={ema_long:.2f}"
                    )
                if rsi > self.rsi_overbought:
                    reason_parts.append(f"RSI overbought: {rsi:.1f} > {self.rsi_overbought}")

                signals.append({
                    "symbol": self.symbol,
                    "side": "sell",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": "; ".join(reason_parts),
                    "indicators": {
                        "ema_short": round(ema_short, 2),
                        "ema_long": round(ema_long, 2),
                        "rsi": round(rsi, 1),
                        "signal": "bearish_cross" if bearish_cross else "rsi_overbought",
                    },
                })
                self.last_signal = "sell"

        if self.position == "long" and current_price > self.highest_since_entry:
            self.highest_since_entry = current_price

        if self.position == "long":
            if self.risk_manager.check_stop_loss(self.entry_price, current_price):
                signals.append({
                    "symbol": self.symbol,
                    "side": "sell",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": f"Stop-loss triggered: entry={self.entry_price:.2f}, current={current_price:.2f}",
                })
            elif self.risk_manager.check_trailing_stop(self.highest_since_entry, current_price):
                signals.append({
                    "symbol": self.symbol,
                    "side": "sell",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": (
                        f"Trailing stop triggered: highest={self.highest_since_entry:.2f}, "
                        f"current={current_price:.2f}"
                    ),
                })
            elif self.risk_manager.check_take_profit(self.entry_price, current_price):
                signals.append({
                    "symbol": self.symbol,
                    "side": "sell",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": f"Take-profit triggered: entry={self.entry_price:.2f}, current={current_price:.2f}",
                })

        return signals

    def on_order_filled(self, order: Dict[str, Any]) -> None:
        """Update position tracking after an order fills."""
        side = order.get("side", "")
        price = order.get("price", 0)

        if side == "buy":
            self.position = "long"
            self.entry_price = price
            self.highest_since_entry = price
            self.stats["trades_executed"] += 1
        elif side == "sell":
            if self.entry_price > 0:
                pnl = ((price - self.entry_price) / self.entry_price) * 100
                self.stats["total_pnl"] += pnl
            self.position = None
            self.entry_price = 0.0
            self.highest_since_entry = 0.0
            self.stats["trades_executed"] += 1

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "position": self.position,
            "entry_price": self.entry_price,
            "highest_since_entry": self.highest_since_entry,
            "last_signal": self.last_signal,
            "timeframe": self.timeframe,
        })
        return base
