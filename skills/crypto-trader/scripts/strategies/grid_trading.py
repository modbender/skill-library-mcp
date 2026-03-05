"""
Grid Trading Strategy.

Places buy and sell limit orders at evenly spaced price levels within a
defined range. When a buy order fills, a sell order is placed one grid
level higher. When a sell order fills, a buy order is placed one grid
level lower. Profits from the natural oscillation of price within the range.

Parameters
----------
symbol : str
    Trading pair, e.g. "BTC/USDT".
price_range : list[float]
    [lower_bound, upper_bound] price range for the grid.
num_grids : int
    Number of grid levels.
order_amount_usdt : float
    USDT value per grid order.
rebalance_on_breakout : bool
    Whether to shift the grid when price breaks out of range.
exchange : str
    Exchange to trade on (default: first available).
"""
from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional

from strategy_engine import BaseStrategy

logger = logging.getLogger("crypto-trader.strategy.grid")


class GridTradingStrategy(BaseStrategy):
    name = "grid_trading"
    display_name = "Grid Trading"

    def __init__(self, strategy_id: str, params: Dict[str, Any], exchange_manager: Any, risk_manager: Any) -> None:
        super().__init__(strategy_id, params, exchange_manager, risk_manager)
        self.symbol: str = params.get("symbol", "BTC/USDT")
        self.price_range: List[float] = params.get("price_range", [90000, 110000])
        self.num_grids: int = params.get("num_grids", 10)
        self.order_amount_usdt: float = params.get("order_amount_usdt", 10.0)
        self.rebalance_on_breakout: bool = params.get("rebalance_on_breakout", True)
        self.exchange: str = params.get("exchange", "")

        self.grid_levels: List[float] = []
        self.grid_spacing: float = 0.0
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self._initialized = False

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

        self._calculate_grid_levels()
        self._initialized = True
        logger.info(
            "Grid trading started: %s on %s, range %s, %d grids, %.2f USDT/grid",
            self.symbol, self.exchange, self.price_range, self.num_grids, self.order_amount_usdt,
        )

    def _calculate_grid_levels(self) -> None:
        """Calculate evenly spaced grid price levels."""
        lower = self.price_range[0]
        upper = self.price_range[1]

        if lower >= upper:
            logger.error("Invalid price range: lower (%s) >= upper (%s)", lower, upper)
            self.active = False
            return

        self.grid_spacing = (upper - lower) / self.num_grids
        self.grid_levels = [
            round(lower + i * self.grid_spacing, 2)
            for i in range(self.num_grids + 1)
        ]
        logger.info("Grid levels calculated: %d levels, spacing: %.2f", len(self.grid_levels), self.grid_spacing)

    def evaluate(self) -> List[Dict[str, Any]]:
        """Evaluate grid conditions and generate trade signals."""
        if not self._initialized or not self.active:
            return []

        signals: List[Dict[str, Any]] = []

        try:
            ticker = self.exchange_manager.get_ticker(self.exchange, self.symbol)
            current_price = ticker.get("last", 0)
            if not current_price:
                return []
        except Exception as exc:
            logger.error("Failed to get ticker for %s: %s", self.symbol, exc)
            return []

        lower = self.price_range[0]
        upper = self.price_range[1]

        if current_price < lower or current_price > upper:
            if self.rebalance_on_breakout:
                signals.extend(self._handle_breakout(current_price))
            return signals

        signals.extend(self._generate_grid_signals(current_price))
        return signals

    def _generate_grid_signals(self, current_price: float) -> List[Dict[str, Any]]:
        """Generate buy/sell signals based on current price vs grid levels."""
        signals: List[Dict[str, Any]] = []

        if current_price <= 0:
            return signals

        order_amount = self.order_amount_usdt / current_price

        for level in self.grid_levels:
            level_key = f"{level:.2f}"

            if level_key in self.active_orders:
                continue

            if level < current_price:
                signals.append({
                    "symbol": self.symbol,
                    "side": "buy",
                    "amount": round(order_amount, 8),
                    "price": level,
                    "order_type": "limit",
                    "exchange": self.exchange,
                    "reason": f"Grid buy at {level:.2f} (current: {current_price:.2f})",
                    "grid_level": level,
                })
            elif level > current_price:
                signals.append({
                    "symbol": self.symbol,
                    "side": "sell",
                    "amount": round(order_amount, 8),
                    "price": level,
                    "order_type": "limit",
                    "exchange": self.exchange,
                    "reason": f"Grid sell at {level:.2f} (current: {current_price:.2f})",
                    "grid_level": level,
                })

        return signals

    def _handle_breakout(self, current_price: float) -> List[Dict[str, Any]]:
        """Handle price breaking out of the grid range by shifting the grid."""
        signals: List[Dict[str, Any]] = []
        lower = self.price_range[0]
        upper = self.price_range[1]
        range_size = upper - lower

        if current_price > upper:
            new_lower = current_price - range_size / 2
            new_upper = current_price + range_size / 2
            logger.info("Price breakout above grid. Shifting range to [%.2f, %.2f]", new_lower, new_upper)
            self.price_range = [round(new_lower, 2), round(new_upper, 2)]
            self._calculate_grid_levels()
            self.active_orders.clear()

        elif current_price < lower:
            new_lower = current_price - range_size / 2
            new_upper = current_price + range_size / 2
            logger.info("Price breakout below grid. Shifting range to [%.2f, %.2f]", new_lower, new_upper)
            self.price_range = [round(new_lower, 2), round(new_upper, 2)]
            self._calculate_grid_levels()
            self.active_orders.clear()

        return signals

    def on_order_filled(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle a filled order: place the counter-order one grid level away."""
        price = order.get("price", 0)
        side = order.get("side", "")

        if side == "buy":
            sell_price = round(price + self.grid_spacing, 2)
            return {
                "symbol": self.symbol,
                "side": "sell",
                "amount": order.get("amount", 0),
                "price": sell_price,
                "order_type": "limit",
                "exchange": self.exchange,
                "reason": f"Grid counter-sell at {sell_price:.2f} after buy fill at {price:.2f}",
            }
        elif side == "sell":
            buy_price = round(price - self.grid_spacing, 2)
            return {
                "symbol": self.symbol,
                "side": "buy",
                "amount": order.get("amount", 0),
                "price": buy_price,
                "order_type": "limit",
                "exchange": self.exchange,
                "reason": f"Grid counter-buy at {buy_price:.2f} after sell fill at {price:.2f}",
            }
        return None

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "grid_levels_count": len(self.grid_levels),
            "grid_spacing": self.grid_spacing,
            "price_range": self.price_range,
            "active_orders_count": len(self.active_orders),
        })
        return base
