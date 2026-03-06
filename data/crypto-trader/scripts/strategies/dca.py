"""
Dollar Cost Averaging (DCA) Strategy.

Buys a fixed USDT amount of a cryptocurrency at regular intervals
regardless of the current price. This spreads the purchase over time,
reducing the impact of volatility and achieving a better average entry price.

Parameters
----------
symbol : str
    Trading pair, e.g. "BTC/USDT".
interval : str
    Purchase interval: "hourly", "daily", "weekly", "monthly".
amount_per_buy_usdt : float
    USDT amount to buy each interval.
max_total_investment_usdt : float
    Optional cap on total invested amount. 0 = unlimited.
exchange : str
    Exchange to trade on (default: first available).
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from strategy_engine import BaseStrategy

logger = logging.getLogger("crypto-trader.strategy.dca")

INTERVAL_SECONDS = {
    "minutely": 60,
    "hourly": 3600,
    "daily": 86400,
    "weekly": 604800,
    "monthly": 2592000,
}


class DCAStrategy(BaseStrategy):
    name = "dca"
    display_name = "Dollar Cost Averaging"

    def __init__(self, strategy_id: str, params: Dict[str, Any], exchange_manager: Any, risk_manager: Any) -> None:
        super().__init__(strategy_id, params, exchange_manager, risk_manager)
        self.symbol: str = params.get("symbol", "BTC/USDT")
        self.interval: str = params.get("interval", "daily")
        self.amount_per_buy: float = params.get("amount_per_buy_usdt", 10.0)
        self.max_total: float = params.get("max_total_investment_usdt", 0)
        self.exchange: str = params.get("exchange", "")

        self.total_invested: float = 0.0
        self.total_bought: float = 0.0
        self.buy_count: int = 0
        self.avg_price: float = 0.0
        self.last_buy_time: float = 0.0

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

        logger.info(
            "DCA started: %s on %s, %s buys of %.2f USDT, max total: %.2f",
            self.symbol, self.exchange, self.interval, self.amount_per_buy,
            self.max_total if self.max_total > 0 else float("inf"),
        )

    def evaluate(self) -> List[Dict[str, Any]]:
        """Check if it's time for the next DCA purchase."""
        if not self.active:
            return []

        interval_secs = INTERVAL_SECONDS.get(self.interval, 86400)
        now = time.time()

        if now - self.last_buy_time < interval_secs:
            return []

        if self.max_total > 0 and self.total_invested >= self.max_total:
            logger.info(
                "DCA max investment reached (%.2f / %.2f USDT). Strategy paused.",
                self.total_invested, self.max_total,
            )
            return []

        try:
            ticker = self.exchange_manager.get_ticker(self.exchange, self.symbol)
            current_price = ticker.get("last", 0)
            if not current_price or current_price <= 0:
                return []
        except Exception as exc:
            logger.error("Failed to get ticker for %s: %s", self.symbol, exc)
            return []

        amount = self.amount_per_buy / current_price

        return [{
            "symbol": self.symbol,
            "side": "buy",
            "amount": round(amount, 8),
            "price": None,
            "order_type": "market",
            "exchange": self.exchange,
            "reason": (
                f"DCA buy #{self.buy_count + 1}: {self.amount_per_buy:.2f} USDT "
                f"of {self.symbol} at {current_price:.2f} "
                f"(avg: {self.avg_price:.2f}, total: {self.total_invested:.2f} USDT)"
            ),
        }]

    def on_order_filled(self, order: Dict[str, Any]) -> None:
        """Update DCA stats after a buy order fills."""
        price = order.get("price") or order.get("cost", 0) / max(order.get("amount", 1), 1e-8)
        amount = order.get("amount", 0)
        cost = order.get("cost") or (price * amount)

        self.total_invested += cost
        self.total_bought += amount
        self.buy_count += 1
        self.last_buy_time = time.time()

        if self.total_bought > 0:
            self.avg_price = self.total_invested / self.total_bought

        self.stats["trades_executed"] = self.buy_count
        self.stats["total_invested_usdt"] = round(self.total_invested, 2)
        self.stats["total_bought"] = round(self.total_bought, 8)
        self.stats["avg_price"] = round(self.avg_price, 2)

        logger.info(
            "DCA buy filled: %.8f %s at %.2f (avg: %.2f, total: %.2f USDT)",
            amount, self.symbol, price, self.avg_price, self.total_invested,
        )

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "total_invested_usdt": round(self.total_invested, 2),
            "total_bought": round(self.total_bought, 8),
            "buy_count": self.buy_count,
            "avg_price": round(self.avg_price, 2),
            "interval": self.interval,
            "next_buy_in_seconds": max(
                0,
                INTERVAL_SECONDS.get(self.interval, 86400) - (time.time() - self.last_buy_time),
            ),
        })
        return base
