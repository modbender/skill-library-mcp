"""
Swing Trading Strategy.

Identifies medium-term price swings using Bollinger Bands, MACD, and
volume analysis. Holds positions for 2-14 days, entering at support
levels and exiting at resistance with trailing stops.

Parameters
----------
symbol : str
    Trading pair.
timeframe : str
    Candlestick timeframe: "4h" or "1d".
bb_period : int
    Bollinger Bands period.
bb_std : float
    Bollinger Bands standard deviation multiplier.
macd_fast : int
    MACD fast EMA period.
macd_slow : int
    MACD slow EMA period.
macd_signal : int
    MACD signal line period.
order_amount_usdt : float
    USDT amount per trade.
max_hold_days : int
    Maximum hold duration in days.
exchange : str
    Exchange to trade on.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import pandas as pd

from strategy_engine import BaseStrategy

logger = logging.getLogger("crypto-trader.strategy.swing")


def _bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Calculate Bollinger Bands (middle, upper, lower)."""
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return middle, upper, lower


def _macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculate MACD line, signal line, and histogram."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


class SwingTradingStrategy(BaseStrategy):
    name = "swing_trading"
    display_name = "Swing Trading"

    def __init__(self, strategy_id: str, params: Dict[str, Any], exchange_manager: Any, risk_manager: Any) -> None:
        super().__init__(strategy_id, params, exchange_manager, risk_manager)
        self.symbol: str = params.get("symbol", "BTC/USDT")
        self.timeframe: str = params.get("timeframe", "1d")
        self.bb_period: int = params.get("bb_period", 20)
        self.bb_std: float = params.get("bb_std", 2.0)
        self.macd_fast: int = params.get("macd_fast", 12)
        self.macd_slow: int = params.get("macd_slow", 26)
        self.macd_signal: int = params.get("macd_signal", 9)
        self.order_amount_usdt: float = params.get("order_amount_usdt", 50.0)
        self.max_hold_days: int = params.get("max_hold_days", 14)
        self.exchange: str = params.get("exchange", "")

        self.position: Optional[str] = None
        self.entry_price: float = 0.0
        self.entry_time: float = 0.0
        self.highest_since_entry: float = 0.0

    def on_start(self) -> None:
        super().on_start()
        if not self.exchange:
            available = self.exchange_manager.available_exchanges
            if available:
                self.exchange = available[0]
            else:
                self.active = False
                return

    def evaluate(self) -> List[Dict[str, Any]]:
        if not self.active:
            return []

        candles_needed = max(self.bb_period, self.macd_slow) + 20

        try:
            ohlcv = self.exchange_manager.get_ohlcv(
                self.exchange, self.symbol, self.timeframe, limit=candles_needed * 2,
            )
        except Exception as exc:
            logger.error("Failed to fetch OHLCV for swing: %s", exc)
            return []

        if len(ohlcv) < candles_needed:
            return []

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

        bb_mid, bb_upper, bb_lower = _bollinger_bands(df["close"], self.bb_period, self.bb_std)
        macd_line, signal_line, histogram = _macd(
            df["close"], self.macd_fast, self.macd_slow, self.macd_signal
        )

        df["bb_mid"] = bb_mid
        df["bb_upper"] = bb_upper
        df["bb_lower"] = bb_lower
        df["macd"] = macd_line
        df["macd_signal"] = signal_line
        df["macd_hist"] = histogram

        current = df.iloc[-1]
        previous = df.iloc[-2]
        price = current["close"]

        signals: List[Dict[str, Any]] = []
        amount = self.order_amount_usdt / price if price > 0 else 0

        if self.position == "long":
            hold_days = (time.time() - self.entry_time) / 86400
            if price > self.highest_since_entry:
                self.highest_since_entry = price

            if self.risk_manager.check_stop_loss(self.entry_price, price):
                signals.append(self._sell_signal(amount, price, "Stop-loss triggered"))
            elif self.risk_manager.check_trailing_stop(self.highest_since_entry, price):
                signals.append(self._sell_signal(amount, price, "Trailing stop triggered"))
            elif self.risk_manager.check_take_profit(self.entry_price, price):
                signals.append(self._sell_signal(amount, price, "Take-profit triggered"))
            elif price >= current["bb_upper"]:
                signals.append(self._sell_signal(amount, price, f"Price at upper BB ({current['bb_upper']:.2f})"))
            elif previous["macd_hist"] > 0 and current["macd_hist"] < 0:
                signals.append(self._sell_signal(amount, price, "MACD histogram crossed below zero"))
            elif hold_days > self.max_hold_days:
                signals.append(self._sell_signal(amount, price, f"Max hold time ({self.max_hold_days}d) reached"))

        else:
            near_lower_bb = price <= current["bb_lower"] * 1.02
            macd_bullish = previous["macd_hist"] < 0 and current["macd_hist"] > 0
            volume_surge = current["volume"] > df["volume"].rolling(20).mean().iloc[-1] * 1.5 if len(df) > 20 else False

            if near_lower_bb and macd_bullish:
                reason = (
                    f"Swing entry: price near lower BB ({current['bb_lower']:.2f}), "
                    f"MACD histogram turning positive"
                )
                if volume_surge:
                    reason += ", volume surge detected"
                signals.append({
                    "symbol": self.symbol,
                    "side": "buy",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": reason,
                    "indicators": {
                        "bb_lower": round(current["bb_lower"], 2),
                        "bb_upper": round(current["bb_upper"], 2),
                        "macd_hist": round(current["macd_hist"], 4),
                    },
                })

        return signals

    def _sell_signal(self, amount: float, price: float, reason: str) -> Dict[str, Any]:
        pnl = ((price - self.entry_price) / self.entry_price * 100) if self.entry_price > 0 else 0
        return {
            "symbol": self.symbol,
            "side": "sell",
            "amount": round(amount, 8),
            "price": None,
            "order_type": "market",
            "exchange": self.exchange,
            "reason": f"{reason} (P&L: {pnl:+.2f}%)",
        }

    def on_order_filled(self, order: Dict[str, Any]) -> None:
        side = order.get("side", "")
        price = order.get("price", 0)
        if side == "buy":
            self.position = "long"
            self.entry_price = price
            self.entry_time = time.time()
            self.highest_since_entry = price
            self.stats["trades_executed"] += 1
        elif side == "sell":
            if self.entry_price > 0:
                pnl = ((price - self.entry_price) / self.entry_price) * 100
                self.stats["total_pnl"] += pnl
            self.position = None
            self.entry_price = 0.0
            self.entry_time = 0.0
            self.highest_since_entry = 0.0
            self.stats["trades_executed"] += 1
