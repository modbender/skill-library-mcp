"""
#5 Dynamic Spread Market Making — provide two-sided liquidity.

From the article: "Предоставление двусторонней ликвидности с динамическим
расширением спреда от SMA при волатильности."

Logic:
1. Find markets with tight spread and high volume
2. Place BUY below mid-price and SELL above mid-price
3. Capture the bid-ask spread
4. Adjust spread width based on volatility (price change magnitude)

NOTE: This is a simplified market-making strategy. Production market-makers
need WebSocket feeds, sub-second execution, and inventory management.
This version runs on the scan loop interval (e.g. 5 min).

Parameters (config.strategy_params):
    base_spread:      0.04   Base spread width (each side from mid)
    volatility_mult:  2.0    Spread multiplier when volatile
    min_liquidity:    5000   Only liquid markets
    min_volume_24h:   5000   Active markets only
    order_size:       5      USDC per side
    max_inventory:    3      Max positions in one market before rebalancing

Ref: https://github.com/lorine93s/polymarket-market-maker-bot
"""

from typing import List

from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_no_price, get_price_change, get_liquidity, get_volume_24h,
)


class MarketMakingStrategy(Strategy):
    name = "market_making"

    def initialize(self, config: dict) -> None:
        self.base_spread = config.get("base_spread", 0.04)
        self.volatility_mult = config.get("volatility_mult", 2.0)
        self.min_liquidity = config.get("min_liquidity", 5000)
        self.min_volume_24h = config.get("min_volume_24h", 5000)
        self.order_size = config.get("order_size", 5)
        self.max_inventory = config.get("max_inventory", 3)

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        signals = []

        # Track inventory per market
        inventory = {}
        for p in positions:
            cid = p.get("conditionId")
            if cid:
                inventory[cid] = inventory.get(cid, 0) + 1

        for m in markets:
            cid = m.get("condition_id")
            if not cid:
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
            no_price = get_no_price(m)
            if yes_price is None or no_price is None:
                continue

            # Mid price
            mid = (yes_price + (1.0 - no_price)) / 2.0

            # Dynamic spread: widen when volatile
            change = get_price_change(m)
            volatility = abs(change) if change else 0
            spread = self.base_spread
            if volatility > 0.05:
                spread *= self.volatility_mult

            buy_price = round(mid - spread / 2, 2)
            sell_price = round(mid + spread / 2, 2)

            # Clamp prices
            buy_price = max(0.01, min(buy_price, 0.98))
            sell_price = max(0.02, min(sell_price, 0.99))

            if sell_price <= buy_price:
                continue

            inv = inventory.get(cid, 0)

            # Place buy side (if not over-inventoried)
            if inv < self.max_inventory:
                signals.append(Signal(
                    market=cid,
                    side="BUY",
                    outcome="Yes",
                    order_type="LIMIT",
                    amount=self.order_size,
                    price=buy_price,
                    confidence=0.5,
                    reason=f"MM bid: mid={mid:.3f}, spread={spread:.3f}, buy@{buy_price:.2f}",
                ))

            # Place sell side (if we have inventory to sell)
            if inv > 0:
                signals.append(Signal(
                    market=cid,
                    side="SELL",
                    outcome="Yes",
                    order_type="LIMIT",
                    amount=self.order_size,
                    price=sell_price,
                    confidence=0.5,
                    reason=f"MM ask: mid={mid:.3f}, spread={spread:.3f}, sell@{sell_price:.2f}",
                ))

        return signals
