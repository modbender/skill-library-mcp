"""
#11 Expiration Timing Volatility — trade before market resolution.

From the article: "Вход за 24-48 часов до экспирации рынка для захвата
запоздалой волатильности, без удержания до конца."

Logic:
1. Fetch markets expiring within a time window (24-72h)
2. Filter for markets with significant price movement potential
3. Buy the side with momentum (breaking price change direction)
4. Target quick exit before resolution — NOT holding to expiry

Parameters (config.strategy_params):
    hours_before_min:  24   Earliest to enter (hours before expiry)
    hours_before_max:  72   Latest window start
    min_volume_24h:    3000 Minimum volume
    min_liquidity:     2000 Minimum liquidity
    order_size:        5    USDC per order
    min_price:         0.15 Skip very cheap markets
    max_price:         0.85 Skip near-certain markets
"""

import time
from typing import List

from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_no_price, get_price_change, get_liquidity, get_volume_24h,
)


class ExpirationTimingStrategy(Strategy):
    name = "expiration_timing"

    def initialize(self, config: dict) -> None:
        self.hours_min = config.get("hours_before_min", 24)
        self.hours_max = config.get("hours_before_max", 72)
        self.min_volume_24h = config.get("min_volume_24h", 3000)
        self.min_liquidity = config.get("min_liquidity", 2000)
        self.order_size = config.get("order_size", 5)
        self.min_price = config.get("min_price", 0.15)
        self.max_price = config.get("max_price", 0.85)

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        signals = []
        held = {p.get("conditionId") for p in positions}
        now = time.time()

        for m in markets:
            cid = m.get("condition_id")
            if not cid or cid in held:
                continue
            if not m.get("active") or not m.get("accepting_orders"):
                continue
            if m.get("closed"):
                continue

            # Check expiration window
            end_date = m.get("end_date_iso")
            if not end_date:
                continue

            hours_left = _hours_until(end_date, now)
            if hours_left is None:
                continue
            if hours_left < self.hours_min or hours_left > self.hours_max:
                continue

            if get_volume_24h(m) < self.min_volume_24h:
                continue
            if get_liquidity(m) < self.min_liquidity:
                continue

            yes_price = get_yes_price(m)
            no_price = get_no_price(m)
            if yes_price is None or no_price is None:
                continue

            # Price must be in the "uncertain" range — where volatility is highest
            if yes_price < self.min_price or yes_price > self.max_price:
                continue

            # Determine direction from recent price change
            change = get_price_change(m)

            # If price is moving toward Yes, follow the momentum
            if change is not None and change > 0.03:
                outcome, price = "Yes", yes_price
            elif change is not None and change < -0.03:
                outcome, price = "No", no_price
            else:
                # No clear direction — pick the side closer to 0.50
                if abs(yes_price - 0.50) <= abs(no_price - 0.50):
                    outcome, price = "Yes", yes_price
                else:
                    outcome, price = "No", no_price

            # Closer to expiry = more urgency = higher confidence
            urgency = 1.0 - (hours_left - self.hours_min) / (self.hours_max - self.hours_min)
            confidence = min(urgency * 0.8 + 0.2, 1.0)

            signals.append(Signal(
                market=cid,
                side="BUY",
                outcome=outcome,
                order_type="LIMIT",
                amount=self.order_size,
                price=price,
                confidence=confidence,
                reason=(
                    f"Expires in {hours_left:.0f}h, "
                    f"{outcome}={price:.2f}, "
                    f"change={change or 0:+.2f}"
                ),
            ))

        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals


def _hours_until(iso_date: str, now: float) -> float:
    """Parse ISO date and return hours until that time."""
    try:
        # Handle common ISO formats
        clean = iso_date.replace("Z", "+00:00")
        if "T" in clean:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(clean)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return (dt.timestamp() - now) / 3600
    except (ValueError, TypeError):
        pass
    return None
