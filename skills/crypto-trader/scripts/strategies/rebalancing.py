"""
Portfolio Rebalancing Strategy.

Maintains a target asset allocation by periodically checking current
portfolio weights against targets and generating buy/sell orders to
bring the portfolio back into balance when drift exceeds a threshold.

Parameters
----------
target_allocation : dict
    Target allocation as {symbol: percentage}. Use "_cash" for cash reserve.
rebalance_threshold_pct : float
    Minimum drift percentage to trigger rebalancing.
interval : str
    Check interval: "daily", "weekly", "monthly".
exchange : str
    Exchange to trade on.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from strategy_engine import BaseStrategy

logger = logging.getLogger("crypto-trader.strategy.rebalance")

INTERVAL_SECONDS = {
    "hourly": 3600,
    "daily": 86400,
    "weekly": 604800,
    "monthly": 2592000,
}


class RebalancingStrategy(BaseStrategy):
    name = "rebalancing"
    display_name = "Portfolio Rebalancing"

    def __init__(self, strategy_id: str, params: Dict[str, Any], exchange_manager: Any, risk_manager: Any) -> None:
        super().__init__(strategy_id, params, exchange_manager, risk_manager)
        self.target_allocation: Dict[str, float] = params.get("target_allocation", {})
        self.threshold_pct: float = params.get("rebalance_threshold_pct", 5.0)
        self.interval: str = params.get("interval", "weekly")
        self.exchange: str = params.get("exchange", "")

        self.last_rebalance_time: float = 0.0

    def on_start(self) -> None:
        super().on_start()
        if not self.exchange:
            available = self.exchange_manager.available_exchanges
            if available:
                self.exchange = available[0]
            else:
                self.active = False
                return

        total_target = sum(self.target_allocation.values())
        if abs(total_target - 100.0) > 0.1:
            logger.warning("Target allocation sums to %.1f%% (should be 100%%).", total_target)

        logger.info(
            "Rebalancing started: %d assets, threshold %.1f%%, interval %s",
            len(self.target_allocation), self.threshold_pct, self.interval,
        )

    def evaluate(self) -> List[Dict[str, Any]]:
        if not self.active:
            return []

        interval_secs = INTERVAL_SECONDS.get(self.interval, 604800)
        if time.time() - self.last_rebalance_time < interval_secs:
            return []

        try:
            current_weights = self._get_current_weights()
        except Exception as exc:
            logger.error("Failed to calculate current weights: %s", exc)
            return []

        signals = self._calculate_rebalance_orders(current_weights)

        if signals:
            self.last_rebalance_time = time.time()

        return signals

    def _get_current_weights(self) -> Dict[str, float]:
        """Calculate current portfolio weights as percentages."""
        balances = self.exchange_manager.get_balance(self.exchange)
        weights: Dict[str, float] = {}
        total_value_usdt = 0.0

        asset_values: Dict[str, float] = {}

        for symbol, target_pct in self.target_allocation.items():
            if symbol == "_cash":
                usdt_balance = balances.get("USDT", {})
                cash_value = usdt_balance.get("total", 0) if isinstance(usdt_balance, dict) else 0
                asset_values["_cash"] = cash_value
                total_value_usdt += cash_value
            else:
                base_asset = symbol.split("/")[0]
                asset_balance = balances.get(base_asset, {})
                quantity = asset_balance.get("total", 0) if isinstance(asset_balance, dict) else 0

                if quantity > 0:
                    try:
                        ticker = self.exchange_manager.get_ticker(self.exchange, symbol)
                        price = ticker.get("last", 0) or 0
                        value = quantity * price
                    except Exception:
                        value = 0
                else:
                    value = 0

                asset_values[symbol] = value
                total_value_usdt += value

        if total_value_usdt > 0:
            for symbol, value in asset_values.items():
                weights[symbol] = round((value / total_value_usdt) * 100, 2)

        return weights

    def _calculate_rebalance_orders(self, current_weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Calculate orders needed to rebalance to target allocation."""
        signals: List[Dict[str, Any]] = []

        for symbol, target_pct in self.target_allocation.items():
            if symbol == "_cash":
                continue

            current_pct = current_weights.get(symbol, 0)
            drift = current_pct - target_pct

            if abs(drift) < self.threshold_pct:
                continue

            try:
                ticker = self.exchange_manager.get_ticker(self.exchange, symbol)
                price = ticker.get("last", 0) or 0
                if price <= 0:
                    continue
            except Exception:
                continue

            balances = self.exchange_manager.get_balance(self.exchange)
            total_value = sum(
                self._get_asset_value(s, balances)
                for s in self.target_allocation
            )

            if total_value <= 0:
                continue

            target_value = total_value * (target_pct / 100)
            current_value = total_value * (current_pct / 100)
            diff_value = target_value - current_value

            amount = abs(diff_value) / price

            if diff_value > 0:
                signals.append({
                    "symbol": symbol,
                    "side": "buy",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": (
                        f"Rebalance: {symbol} is {current_pct:.1f}% "
                        f"(target: {target_pct:.1f}%, drift: {drift:+.1f}%). "
                        f"Buying {abs(diff_value):.2f} USDT worth."
                    ),
                })
            elif diff_value < 0:
                signals.append({
                    "symbol": symbol,
                    "side": "sell",
                    "amount": round(amount, 8),
                    "price": None,
                    "order_type": "market",
                    "exchange": self.exchange,
                    "reason": (
                        f"Rebalance: {symbol} is {current_pct:.1f}% "
                        f"(target: {target_pct:.1f}%, drift: {drift:+.1f}%). "
                        f"Selling {abs(diff_value):.2f} USDT worth."
                    ),
                })

        return signals

    def _get_asset_value(self, symbol: str, balances: Dict[str, Any]) -> float:
        """Get the USDT value of a portfolio asset."""
        if symbol == "_cash":
            usdt = balances.get("USDT", {})
            return usdt.get("total", 0) if isinstance(usdt, dict) else 0

        base = symbol.split("/")[0]
        asset = balances.get(base, {})
        qty = asset.get("total", 0) if isinstance(asset, dict) else 0
        if qty <= 0:
            return 0

        try:
            ticker = self.exchange_manager.get_ticker(self.exchange, symbol)
            return qty * (ticker.get("last", 0) or 0)
        except Exception:
            return 0

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "target_allocation": self.target_allocation,
            "threshold_pct": self.threshold_pct,
            "interval": self.interval,
        })
        return base
