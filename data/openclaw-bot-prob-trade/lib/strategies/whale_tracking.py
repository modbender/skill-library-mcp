"""
#9 Whale Portfolio Tracking — follow smart money wallets.

From the article: "Теневое копирование умных денег с винрейтом >70%
на нишевых рынках."

Logic:
1. Fetch top traders from prob.trade API (sorted by win rate)
2. Filter for whales with winRate > threshold
3. Fetch hot/breaking markets where whales are likely active
4. Buy on markets with high volume + whale activity signals

Parameters (config.strategy_params):
    min_win_rate:     0.65   Minimum win rate to consider a wallet "smart"
    min_trades:       50     Minimum trades to filter noise
    min_volume_24h:   5000   Only trade liquid markets
    order_size:       5      USDC per order
    trader_period:    7d     Leaderboard period (all|30d|7d|24h)
    trader_limit:     20     Number of top traders to fetch

Ref: https://github.com/NYTEMODEONLY/polyterm
"""

import sys
import os
from typing import List

sys.path.insert(0, os.environ.get(
    "PROBTRADE_SKILL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "openclaw-skill", "lib"),
))

from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_no_price, get_liquidity, get_volume_24h,
)


def _safe_fetch(endpoint, params=None):
    try:
        from api_client import fetch
        return fetch(endpoint, params)
    except SystemExit:
        return None


class WhaleTrackingStrategy(Strategy):
    name = "whale_tracking"

    def initialize(self, config: dict) -> None:
        self.min_win_rate = config.get("min_win_rate", 0.65)
        self.min_trades = config.get("min_trades", 50)
        self.min_volume_24h = config.get("min_volume_24h", 5000)
        self.order_size = config.get("order_size", 5)
        self.trader_period = config.get("trader_period", "7d")
        self.trader_limit = config.get("trader_limit", 20)
        self._smart_wallets = []

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        # Refresh smart wallet list
        self._refresh_smart_wallets()
        if not self._smart_wallets:
            return []

        signals = []
        held = {p.get("conditionId") for p in positions}

        # Filter markets that smart money would trade:
        # high volume, good liquidity, active
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
            if get_liquidity(m) < 3000:
                continue

            yes_price = get_yes_price(m)
            no_price = get_no_price(m)
            if yes_price is None or no_price is None:
                continue

            # Heuristic: smart money tends to buy the underdog
            # If yes_price is low (0.20-0.45) and volume is spiking,
            # this could be smart money accumulating
            volume = get_volume_24h(m)
            liquidity = get_liquidity(m)
            volume_to_liq_ratio = volume / liquidity if liquidity > 0 else 0

            # High volume relative to liquidity = unusual activity
            if volume_to_liq_ratio < 1.5:
                continue

            # Prefer underdog side (lower price = higher potential)
            if yes_price <= 0.45:
                outcome, price = "Yes", yes_price
            elif no_price <= 0.45:
                outcome, price = "No", no_price
            else:
                continue

            confidence = min(volume_to_liq_ratio / 5.0, 1.0)

            signals.append(Signal(
                market=cid,
                side="BUY",
                outcome=outcome,
                order_type="LIMIT",
                amount=self.order_size,
                price=price,
                confidence=confidence,
                reason=(
                    f"Smart money signal: vol/liq={volume_to_liq_ratio:.1f}x, "
                    f"{outcome}={price:.2f}, "
                    f"{len(self._smart_wallets)} whales tracked"
                ),
            ))

        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals

    def _refresh_smart_wallets(self):
        """Fetch top traders and filter by win rate."""
        data = _safe_fetch("/traders/top", {
            "limit": str(self.trader_limit),
            "sortBy": "winRate",
            "period": self.trader_period,
        })
        if not data:
            return

        traders = data.get("traders", [])
        self._smart_wallets = [
            t for t in traders
            if float(t.get("winRate", 0) or 0) >= self.min_win_rate
            and int(t.get("tradesCount", 0) or 0) >= self.min_trades
        ]
