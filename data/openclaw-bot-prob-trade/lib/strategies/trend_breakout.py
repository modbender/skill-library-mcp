"""
#2 TBO Trend Breakout — ride the momentum.

From the article: "Импульсная торговля по тренду на базе пробоя
волатильности с высокими винрейтами."

Logic (opposite of momentum/mean-reversion):
1. Fetch breaking markets — biggest price GAINS in 24h
2. Filter for strong upward momentum with high volume
3. Buy YES on rising markets, follow the trend
4. Tight take-profit target — capture the impulse, don't hold

Parameters (config.strategy_params):
    rise_threshold:   0.08   Minimum 24h price RISE to consider
    min_volume_24h:   5000   High volume confirms real momentum
    min_liquidity:    3000   Need liquidity to enter/exit
    max_yes_price:    0.80   Don't buy near certainty
    min_yes_price:    0.20   Skip very cheap (noise)
    order_size:       5      USDC per order

Ref: https://www.youtube.com/watch?v=YknxNkTgNWk
"""

from typing import List

from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_price_change, get_liquidity, get_volume_24h,
)


class TrendBreakoutStrategy(Strategy):
    name = "trend_breakout"

    def initialize(self, config: dict) -> None:
        self.rise_threshold = config.get("rise_threshold", 0.08)
        self.min_volume_24h = config.get("min_volume_24h", 5000)
        self.min_liquidity = config.get("min_liquidity", 3000)
        self.max_yes_price = config.get("max_yes_price", 0.80)
        self.min_yes_price = config.get("min_yes_price", 0.20)
        self.order_size = config.get("order_size", 5)

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        signals = []
        held = {p.get("conditionId") for p in positions}

        for m in markets:
            cid = m.get("condition_id")
            if not cid or cid in held:
                continue
            if not m.get("active") or not m.get("accepting_orders"):
                continue
            if m.get("closed"):
                continue

            # Only RISING markets (positive price change)
            change = get_price_change(m)
            if change is None or change < self.rise_threshold:
                continue

            if get_volume_24h(m) < self.min_volume_24h:
                continue
            if get_liquidity(m) < self.min_liquidity:
                continue

            yes_price = get_yes_price(m)
            if yes_price is None:
                continue
            if yes_price < self.min_yes_price or yes_price > self.max_yes_price:
                continue

            # Volume confirms momentum — higher volume = stronger signal
            vol_score = min(get_volume_24h(m) / 20000, 1.0)
            price_score = min(change / 0.20, 1.0)
            confidence = (vol_score + price_score) / 2

            signals.append(Signal(
                market=cid,
                side="BUY",
                outcome="Yes",
                order_type="LIMIT",
                amount=self.order_size,
                price=yes_price,
                confidence=confidence,
                reason=(
                    f"Breakout: +{change:.2f} in 24h, "
                    f"price {yes_price:.2f}, "
                    f"vol ${get_volume_24h(m):.0f}"
                ),
            ))

        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals
