"""
Scalping Strategy.

Executes many small, fast trades targeting tiny profits per trade.
Analyzes the order book spread and short-term price momentum to
enter and exit positions quickly. Relies on tight spreads and
fast execution.

Parameters
----------
symbol : str
    Trading pair.
timeframe : str
    Short timeframe, e.g. "1m".
spread_threshold_pct : float
    Minimum spread to trigger entry.
profit_target_pct : float
    Target profit per trade.
max_hold_seconds : int
    Maximum time to hold a position.
order_amount_usdt : float
    USDT amount per trade.
exchange : str
    Exchange to trade on.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from strategy_engine import BaseStrategy

logger = logging.getLogger("crypto-trader.strategy.scalping")


class ScalpingStrategy(BaseStrategy):
    name = "scalping"
    display_name = "Scalping"

    def __init__(self, strategy_id: str, params: Dict[str, Any], exchange_manager: Any, risk_manager: Any) -> None:
        super().__init__(strategy_id, params, exchange_manager, risk_manager)
        self.symbol: str = params.get("symbol", "BTC/USDT")
        self.timeframe: str = params.get("timeframe", "1m")
        self.spread_threshold: float = params.get("spread_threshold_pct", 0.1)
        self.profit_target: float = params.get("profit_target_pct", 0.15)
        self.max_hold_seconds: int = params.get("max_hold_seconds", 300)
        self.order_amount_usdt: float = params.get("order_amount_usdt", 20.0)
        self.exchange: str = params.get("exchange", "")

        self.position: Optional[str] = None
        self.entry_price: float = 0.0
        self.entry_time: float = 0.0

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

        signals: List[Dict[str, Any]] = []

        try:
            book = self.exchange_manager.get_orderbook(self.exchange, self.symbol, limit=5)
            ticker = self.exchange_manager.get_ticker(self.exchange, self.symbol)
        except Exception as exc:
            logger.error("Failed to get market data for scalping: %s", exc)
            return []

        spread_pct = book.get("spread_pct", 0)
        current_price = ticker.get("last", 0)

        if not current_price or current_price <= 0:
            return []

        if self.position == "long":
            profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100
            hold_time = time.time() - self.entry_time

            if profit_pct >= self.profit_target:
                amount = self.order_amount_usdt / self.entry_price
                signals.append({
                    "symbol": self.symbol,
                    "side": "sell",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": f"Scalp take-profit: +{profit_pct:.3f}% in {hold_time:.0f}s",
                })

            elif profit_pct < -self.profit_target:
                amount = self.order_amount_usdt / self.entry_price
                signals.append({
                    "symbol": self.symbol,
                    "side": "sell",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": f"Scalp stop-loss: {profit_pct:.3f}% in {hold_time:.0f}s",
                })

            elif hold_time > self.max_hold_seconds:
                amount = self.order_amount_usdt / self.entry_price
                signals.append({
                    "symbol": self.symbol,
                    "side": "sell",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": f"Scalp timeout: {profit_pct:.3f}% after {hold_time:.0f}s",
                })

        else:
            if spread_pct and spread_pct <= self.spread_threshold:
                best_bid = book["bids"][0][0] if book.get("bids") else 0
                if best_bid > 0:
                    amount = self.order_amount_usdt / best_bid
                    signals.append({
                        "symbol": self.symbol,
                        "side": "buy",
                        "amount": round(amount, 8),
                        "price": best_bid,
                        "order_type": "limit",
                        "exchange": self.exchange,
                        "reason": f"Scalp entry: spread {spread_pct:.4f}% at bid {best_bid:.2f}",
                    })

        return signals

    def on_order_filled(self, order: Dict[str, Any]) -> None:
        side = order.get("side", "")
        price = order.get("price", 0)
        if side == "buy":
            self.position = "long"
            self.entry_price = price
            self.entry_time = time.time()
            self.stats["trades_executed"] += 1
        elif side == "sell":
            if self.entry_price > 0:
                pnl = ((price - self.entry_price) / self.entry_price) * 100
                self.stats["total_pnl"] += pnl
            self.position = None
            self.entry_price = 0.0
            self.entry_time = 0.0
            self.stats["trades_executed"] += 1
