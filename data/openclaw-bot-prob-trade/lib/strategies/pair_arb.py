"""
Asynchronous Pair Cost Arbitrage.

From the article: "Покупка YES и NO токенов в разное время при условии,
что их средняя суммарная стоимость < $1.00."

Logic:
1. Scan markets where YES + NO price < target_sum (e.g. < 0.95)
2. Buy the cheaper side
3. Over time, accumulate both sides
4. Guaranteed profit when market resolves (YES + NO always = 1.00 USDC)

Parameters (config.strategy_params):
    target_sum:       0.95   Max combined YES+NO price to enter
    min_liquidity:    5000   Minimum market liquidity ($)
    min_volume_24h:   2000   Minimum 24h volume ($)
    order_size:       5      USDC per order
"""

from typing import List
from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_no_price, get_liquidity, get_volume_24h,
)


class PairArbStrategy(Strategy):
    name = "pair_arb"

    def initialize(self, config: dict) -> None:
        self.target_sum = config.get("target_sum", 0.95)
        self.min_liquidity = config.get("min_liquidity", 5000)
        self.min_volume_24h = config.get("min_volume_24h", 2000)
        self.order_size = config.get("order_size", 5)

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        signals = []

        for m in markets:
            cid = m.get("condition_id")
            if not cid:
                continue

            if not m.get("active") or not m.get("accepting_orders"):
                continue
            if m.get("closed"):
                continue

            if get_liquidity(m) < self.min_liquidity:
                continue
            if get_volume_24h(m) < self.min_volume_24h:
                continue

            yes_price = get_yes_price(m)
            no_price = get_no_price(m)
            if yes_price is None or no_price is None:
                continue

            combined = yes_price + no_price
            if combined >= self.target_sum:
                continue

            # Buy the cheaper side
            spread = 1.0 - combined
            if yes_price <= no_price:
                side_outcome = "Yes"
                price = yes_price
            else:
                side_outcome = "No"
                price = no_price

            signals.append(Signal(
                market=cid,
                side="BUY",
                outcome=side_outcome,
                order_type="LIMIT",
                amount=self.order_size,
                price=price,
                confidence=min(spread / 0.10, 1.0),  # bigger spread = higher confidence
                reason=f"YES={yes_price:.3f} + NO={no_price:.3f} = {combined:.3f} (spread {spread:.3f})",
            ))

        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals
