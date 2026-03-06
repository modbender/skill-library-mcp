"""
Arbitrage Strategy.

Monitors the same trading pair across multiple exchanges and exploits
price differences. When the spread between the cheapest ask and the
most expensive bid exceeds fees + threshold, simultaneously buys on the
cheap exchange and sells on the expensive one.

Parameters
----------
symbol : str
    Trading pair.
exchanges : list[str]
    Exchanges to monitor for arbitrage opportunities.
min_spread_pct : float
    Minimum spread percentage after fees to trigger.
order_amount_usdt : float
    USDT amount per arbitrage trade.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from strategy_engine import BaseStrategy

logger = logging.getLogger("crypto-trader.strategy.arbitrage")


class ArbitrageStrategy(BaseStrategy):
    name = "arbitrage"
    display_name = "Cross-Exchange Arbitrage"

    def __init__(self, strategy_id: str, params: Dict[str, Any], exchange_manager: Any, risk_manager: Any) -> None:
        super().__init__(strategy_id, params, exchange_manager, risk_manager)
        self.symbol: str = params.get("symbol", "BTC/USDT")
        self.target_exchanges: List[str] = params.get("exchanges", [])
        self.min_spread_pct: float = params.get("min_spread_pct", 0.3)
        self.order_amount_usdt: float = params.get("order_amount_usdt", 50.0)
        self.fee_pct: float = params.get("fee_pct", 0.1)

    def on_start(self) -> None:
        super().on_start()
        if not self.target_exchanges:
            self.target_exchanges = self.exchange_manager.available_exchanges

        if len(self.target_exchanges) < 2:
            logger.error("Arbitrage requires at least 2 exchanges. Available: %s", self.target_exchanges)
            self.active = False
            return

        logger.info(
            "Arbitrage started: %s across %s, min spread: %.2f%%",
            self.symbol, self.target_exchanges, self.min_spread_pct,
        )

    def evaluate(self) -> List[Dict[str, Any]]:
        if not self.active or len(self.target_exchanges) < 2:
            return []

        prices: Dict[str, Dict[str, float]] = {}

        for ex_name in self.target_exchanges:
            try:
                ticker = self.exchange_manager.get_ticker(ex_name, self.symbol)
                bid = ticker.get("bid", 0) or 0
                ask = ticker.get("ask", 0) or 0
                if bid > 0 and ask > 0:
                    prices[ex_name] = {"bid": bid, "ask": ask}
            except Exception as exc:
                logger.warning("Failed to get ticker from %s: %s", ex_name, exc)

        if len(prices) < 2:
            return []

        signals: List[Dict[str, Any]] = []

        exchange_list = list(prices.keys())
        for i in range(len(exchange_list)):
            for j in range(i + 1, len(exchange_list)):
                ex_a = exchange_list[i]
                ex_b = exchange_list[j]

                ask_a = prices[ex_a]["ask"]
                bid_b = prices[ex_b]["bid"]
                spread_ab = ((bid_b - ask_a) / ask_a) * 100

                ask_b = prices[ex_b]["ask"]
                bid_a = prices[ex_a]["bid"]
                spread_ba = ((bid_a - ask_b) / ask_b) * 100

                total_fee = self.fee_pct * 2

                if spread_ab > total_fee + self.min_spread_pct:
                    net_profit_pct = spread_ab - total_fee
                    amount = self.order_amount_usdt / ask_a
                    signals.append({
                        "symbol": self.symbol,
                        "side": "buy",
                        "amount": round(amount, 8),
                        "price": ask_a,
                        "order_type": "limit",
                        "exchange": ex_a,
                        "reason": (
                            f"Arbitrage: buy on {ex_a} at {ask_a:.2f}, "
                            f"sell on {ex_b} at {bid_b:.2f}, "
                            f"spread {spread_ab:.3f}%, net {net_profit_pct:.3f}%"
                        ),
                        "arb_pair": {"buy_exchange": ex_a, "sell_exchange": ex_b},
                    })
                    signals.append({
                        "symbol": self.symbol,
                        "side": "sell",
                        "amount": round(amount, 8),
                        "price": bid_b,
                        "order_type": "limit",
                        "exchange": ex_b,
                        "reason": f"Arbitrage counter-sell on {ex_b}",
                        "arb_pair": {"buy_exchange": ex_a, "sell_exchange": ex_b},
                    })

                if spread_ba > total_fee + self.min_spread_pct:
                    net_profit_pct = spread_ba - total_fee
                    amount = self.order_amount_usdt / ask_b
                    signals.append({
                        "symbol": self.symbol,
                        "side": "buy",
                        "amount": round(amount, 8),
                        "price": ask_b,
                        "order_type": "limit",
                        "exchange": ex_b,
                        "reason": (
                            f"Arbitrage: buy on {ex_b} at {ask_b:.2f}, "
                            f"sell on {ex_a} at {bid_a:.2f}, "
                            f"spread {spread_ba:.3f}%, net {net_profit_pct:.3f}%"
                        ),
                        "arb_pair": {"buy_exchange": ex_b, "sell_exchange": ex_a},
                    })
                    signals.append({
                        "symbol": self.symbol,
                        "side": "sell",
                        "amount": round(amount, 8),
                        "price": bid_a,
                        "order_type": "limit",
                        "exchange": ex_a,
                        "reason": f"Arbitrage counter-sell on {ex_a}",
                        "arb_pair": {"buy_exchange": ex_b, "sell_exchange": ex_a},
                    })

        return signals
