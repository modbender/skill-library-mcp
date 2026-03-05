"""
#8 Value Investor — buy undervalued markets.

From the article: "Агент вычисляет внутреннюю вероятность события
и покупает YES, если цена рынка ниже на 20%+."

Simplified version (no LLM):
1. Scan markets where price is far from 0.50 (high certainty priced in)
2. Look for markets with strong fundamentals (volume, liquidity)
   but price hasn't moved much (potential undervaluation)
3. Use Kelly criterion for position sizing

For full LLM-powered version, extend this class and override
_estimate_fair_value() to call Claude/GPT-4 API.

Parameters (config.strategy_params):
    value_gap:        0.15   Minimum gap between estimated and market price
    min_volume_24h:   3000   Enough trading activity
    min_liquidity:    5000   Enough liquidity to enter
    order_size:       5      USDC per order
    kelly_fraction:   0.25   Fraction of Kelly criterion to use (quarter-Kelly)

Ref: https://github.com/randomness11/probablyprofit
"""

from typing import List, Optional

from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_no_price, get_liquidity, get_volume_24h, get_price_change,
)


class ValueInvestorStrategy(Strategy):
    name = "value_investor"

    def initialize(self, config: dict) -> None:
        self.value_gap = config.get("value_gap", 0.15)
        self.min_volume_24h = config.get("min_volume_24h", 3000)
        self.min_liquidity = config.get("min_liquidity", 5000)
        self.order_size = config.get("order_size", 5)
        self.kelly_fraction = config.get("kelly_fraction", 0.25)

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
            if get_volume_24h(m) < self.min_volume_24h:
                continue
            if get_liquidity(m) < self.min_liquidity:
                continue

            yes_price = get_yes_price(m)
            if yes_price is None or yes_price < 0.05 or yes_price > 0.95:
                continue

            # Estimate fair value
            fair_value = self._estimate_fair_value(m)
            if fair_value is None:
                continue

            # Check if market is undervalued
            gap = fair_value - yes_price
            if gap < self.value_gap:
                continue

            # Kelly criterion for position sizing
            # f* = (bp - q) / b where b = (1/price - 1), p = fair_value, q = 1-p
            b = (1.0 / yes_price) - 1.0
            p = fair_value
            q = 1.0 - p
            kelly = (b * p - q) / b if b > 0 else 0
            kelly = max(0, kelly) * self.kelly_fraction

            # Cap at configured order_size
            amount = min(kelly * balance, self.order_size) if balance > 0 else self.order_size
            if amount < 1.0:
                continue

            signals.append(Signal(
                market=cid,
                side="BUY",
                outcome="Yes",
                order_type="LIMIT",
                amount=round(amount, 2),
                price=yes_price,
                confidence=min(gap / 0.30, 1.0),
                reason=(
                    f"Undervalued: fair={fair_value:.2f} vs market={yes_price:.2f} "
                    f"(gap={gap:+.2f}), Kelly={kelly:.1%}"
                ),
            ))

        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals

    def _estimate_fair_value(self, market: dict) -> Optional[float]:
        """
        Estimate fair probability for a market.

        Default implementation: simple heuristic based on volume/liquidity ratio
        and recent price movement. Markets with high volume and stable prices
        are likely fairly priced; those with low volume may be stale.

        Override this method to use LLM (Claude, GPT-4) for deeper analysis.
        Example:
            def _estimate_fair_value(self, market):
                question = market.get("question", "")
                # Call LLM API to estimate probability
                response = call_llm(f"What is the probability: {question}")
                return parse_probability(response)
        """
        yes_price = get_yes_price(market)
        change = get_price_change(market)
        volume = get_volume_24h(market)
        liquidity = get_liquidity(market)

        if yes_price is None:
            return None

        # Heuristic: if price recently dropped but volume is high,
        # the drop may be an overreaction — fair value is higher
        adjustment = 0.0
        if change is not None and change < -0.05 and volume > 5000:
            # Strong volume + drop = potential overreaction
            adjustment = abs(change) * 0.5  # recover half the drop

        # Volume/liquidity ratio: high ratio = active discovery
        if liquidity > 0 and volume / liquidity > 2.0:
            adjustment += 0.03

        return yes_price + adjustment
