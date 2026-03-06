"""
Base class for trading strategies.

To create a custom strategy:
1. Create a file in lib/strategies/ (e.g. my_strategy.py)
2. Subclass Strategy and implement initialize() and scan()
3. Set strategy: my_strategy in config.yaml
4. Run: python3 scripts/bot.py run

Example:
    class MyStrategy(Strategy):
        name = "my_strategy"

        def initialize(self, config):
            self.threshold = config.get("drop_threshold", -0.10)

        def scan(self, markets, positions, balance):
            signals = []
            for m in markets:
                drop = get_price_change(m)
                if drop and drop <= self.threshold:
                    signals.append(Signal(
                        market=m["condition_id"],
                        side="BUY", outcome="Yes",
                        order_type="LIMIT",
                        amount=5,
                        price=get_yes_price(m),
                        confidence=0.7,
                        reason=f"Price dropped {drop:.0%}"
                    ))
            return signals
"""

from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod


@dataclass
class Signal:
    """A trading signal produced by a strategy."""
    market: str            # condition_id
    side: str              # BUY / SELL
    outcome: str           # Yes / No
    order_type: str        # MARKET / LIMIT
    amount: float          # USDC
    price: Optional[float] = None   # required for LIMIT orders
    confidence: float = 0.0         # 0.0 to 1.0
    reason: str = ""                # human-readable explanation


class Strategy(ABC):
    """Base class for all trading strategies."""
    name: str = "unnamed"

    @abstractmethod
    def initialize(self, config: dict) -> None:
        """Called once at startup. Use config['strategy_params'] for custom params."""
        pass

    @abstractmethod
    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        """
        Analyze markets and current state, return trading signals.

        Args:
            markets: list of market dicts from prob.trade API (breaking/hot/etc.)
            positions: list of current open positions
            balance: available USDC balance

        Returns:
            List of Signal objects. Engine will validate each through risk manager
            before execution.
        """
        pass

    def on_order_placed(self, signal: Signal, result: dict) -> None:
        """Optional callback after an order is placed. Override for tracking."""
        pass

    def on_cycle_end(self, signals_generated: int, orders_placed: int) -> None:
        """Optional callback at end of each scan cycle."""
        pass


# --- Helpers for extracting market data ---

def get_yes_price(market: dict) -> Optional[float]:
    """Extract YES token price from market dict."""
    tokens = market.get("tokens", {})
    t1 = tokens.get("token1") or {}
    price = t1.get("price")
    return float(price) if price is not None else None


def get_no_price(market: dict) -> Optional[float]:
    """Extract NO token price from market dict."""
    tokens = market.get("tokens", {})
    t2 = tokens.get("token2") or {}
    price = t2.get("price")
    return float(price) if price is not None else None


def get_price_change(market: dict) -> Optional[float]:
    """Extract 24h price change (absolute) from market dict."""
    pc = market.get("priceChange") or {}
    val = pc.get("oneDay")
    return float(val) if val is not None else None


def get_liquidity(market: dict) -> float:
    """Extract total liquidity from market dict."""
    liq = market.get("liquidity")
    if isinstance(liq, dict):
        return float(liq.get("total", 0) or 0)
    if liq is not None:
        return float(liq)
    return 0.0


def get_volume_24h(market: dict) -> float:
    """Extract 24h volume from market dict (API returns string)."""
    val = market.get("volume_24hr", 0)
    return float(val or 0)
