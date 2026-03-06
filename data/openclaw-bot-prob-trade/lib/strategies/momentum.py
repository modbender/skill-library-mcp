"""
AI Contrarian Momentum — mean reversion on breaking markets.

From the article: "Ставки против толпы в периоды рыночной паники."

Logic:
1. Fetch breaking markets (biggest 24h price drops)
2. Filter: drop >= threshold, enough liquidity/volume, price in range
3. BUY YES at current price, betting on reversion

Parameters (config.strategy_params):
    drop_threshold:  -0.10   Minimum 24h drop to consider (absolute)
    take_profit:      0.10   Target price rise for exit
    min_liquidity:    5000   Minimum market liquidity ($)
    min_volume_24h:   1000   Minimum 24h volume ($)
    min_yes_price:    0.10   Skip dead markets
    max_yes_price:    0.85   Skip overpriced markets
    order_size:       5      USDC per order
"""

from typing import List
from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_price_change, get_liquidity, get_volume_24h,
)


class MomentumStrategy(Strategy):
    name = "momentum"

    def initialize(self, config: dict) -> None:
        self.drop_threshold = config.get("drop_threshold", -0.10)
        self.take_profit = config.get("take_profit", 0.10)
        self.min_liquidity = config.get("min_liquidity", 5000)
        self.min_volume_24h = config.get("min_volume_24h", 1000)
        self.min_yes_price = config.get("min_yes_price", 0.10)
        self.max_yes_price = config.get("max_yes_price", 0.85)
        self.order_size = config.get("order_size", 5)

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        signals = []

        # Markets we already have positions in
        held_markets = {p.get("conditionId") for p in positions}

        for m in markets:
            cid = m.get("condition_id")
            if not cid or cid in held_markets:
                continue

            # Must be active and accepting orders
            if not m.get("active") or not m.get("accepting_orders"):
                continue
            if m.get("closed"):
                continue

            # Price change filter
            drop = get_price_change(m)
            if drop is None or drop > self.drop_threshold:
                continue

            # Liquidity filter
            if get_liquidity(m) < self.min_liquidity:
                continue

            # Volume filter
            if get_volume_24h(m) < self.min_volume_24h:
                continue

            # Price range filter
            yes_price = get_yes_price(m)
            if yes_price is None:
                continue
            if yes_price < self.min_yes_price or yes_price > self.max_yes_price:
                continue

            signals.append(Signal(
                market=cid,
                side="BUY",
                outcome="Yes",
                order_type="LIMIT",
                amount=self.order_size,
                price=yes_price,
                confidence=min(abs(drop) / 0.20, 1.0),  # higher drop = higher confidence
                reason=f"24h drop {drop:+.2f}, price {yes_price:.2f}, liq ${get_liquidity(m):.0f}",
            ))

        # Sort by confidence (biggest drops first)
        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals
