"""
Trading engine — main loop that orchestrates strategy scanning and order execution.

Architecture:
    engine.py (this) → strategy.scan() → signals → risk_manager.validate() → api_client.trading_request()
"""

import json
import logging
import os
import signal
import sys
import time
from typing import Optional

# Import api_client from the probtrade skill
_skill_path = os.environ.get(
    "PROBTRADE_SKILL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "openclaw-skill", "lib"),
)
_skill_path = os.path.abspath(_skill_path)
if _skill_path not in sys.path:
    sys.path.insert(0, _skill_path)

from api_client import fetch, trading_request  # noqa: E402

from .risk_manager import RiskConfig, RiskManager, TradingState
from .strategy_base import Signal, Strategy
from .strategies import get_strategy, list_strategies

logger = logging.getLogger("bot.engine")


class Engine:
    def __init__(self, config: dict):
        self.config = config
        self.dry_run = config.get("dry_run", True)
        self.loop_interval = config.get("loop_interval_sec", 300)
        self.running = False

        # Risk manager
        risk_cfg = config.get("risk", {})
        self.risk = RiskManager(RiskConfig(**risk_cfg))

        # Strategy
        strategy_name = config.get("strategy", "")
        if not strategy_name:
            raise ValueError("No strategy specified in config")
        self.strategy: Strategy = get_strategy(strategy_name)
        self.strategy.initialize(config.get("strategy_params", {}))
        logger.info(f"Strategy loaded: {self.strategy.name}")

    # --- Public API ---

    def run(self):
        """Start the autonomous trading loop."""
        self.running = True
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        mode = "DRY RUN" if self.dry_run else "LIVE"
        logger.info(f"Engine started [{mode}] — interval {self.loop_interval}s")
        logger.info(f"Strategy: {self.strategy.name}")
        logger.info(f"Risk limits: max_pos=${self.risk.config.max_position_size}, "
                     f"daily=${self.risk.config.max_daily_spend}, "
                     f"max_positions={self.risk.config.max_open_positions}")

        while self.running:
            try:
                self._cycle()
            except Exception as e:
                logger.error(f"Cycle error: {e}", exc_info=True)

            if self.running:
                logger.info(f"Sleeping {self.loop_interval}s...")
                _interruptible_sleep(self.loop_interval, lambda: self.running)

        logger.info("Engine stopped")

    def scan_once(self) -> list:
        """Run a single scan cycle without placing orders. Returns signals."""
        state = self._get_state()
        if state is None:
            return []
        markets = self._fetch_markets()
        if not markets:
            return []
        return self.strategy.scan(markets, state.positions, state.balance)

    def status(self) -> dict:
        """Get current bot status: balance, positions, orders."""
        state = self._get_state()
        if state is None:
            return {"error": "Could not fetch trading state"}
        return {
            "balance": state.balance,
            "trading_ready": state.trading_ready,
            "positions_count": len(state.positions),
            "positions": state.positions,
            "open_orders_count": len(state.open_orders),
            "open_orders": state.open_orders,
            "risk": {
                "daily_spent": self.risk.daily_spent,
                "daily_limit": self.risk.config.max_daily_spend,
                "circuit_breaker": self.risk.circuit_breaker_active,
                "consecutive_losses": self.risk.consecutive_losses,
            },
            "strategy": self.strategy.name,
            "dry_run": self.dry_run,
        }

    # --- Private ---

    def _cycle(self):
        """One complete scan-and-trade cycle."""
        # 1. Get current state
        state = self._get_state()
        if state is None:
            logger.warning("Could not fetch state, skipping cycle")
            return

        logger.info(
            f"Balance: ${state.balance:.2f} | "
            f"Positions: {len(state.positions)} | "
            f"Orders: {len(state.open_orders)}"
        )

        # 2. Pre-check risk
        allowed, reason = self.risk.pre_check(state)
        if not allowed:
            logger.warning(f"Trading blocked: {reason}")
            return

        # 3. Fetch markets
        markets = self._fetch_markets()
        if not markets:
            logger.info("No markets fetched, skipping cycle")
            return

        # 4. Strategy scan
        signals = self.strategy.scan(markets, state.positions, state.balance)
        logger.info(f"Strategy produced {len(signals)} signal(s)")

        # 5. Execute signals
        orders_placed = 0
        for sig in signals:
            ok, reason = self.risk.validate_signal(sig, state)
            if not ok:
                logger.info(f"Signal rejected: {reason} — {sig.market} {sig.side} {sig.outcome}")
                continue

            if self.dry_run:
                logger.info(
                    f"[DRY RUN] Would {sig.side} {sig.outcome} on {sig.market} "
                    f"— ${sig.amount} @ {sig.price or 'MARKET'} "
                    f"(confidence: {sig.confidence:.0%}, reason: {sig.reason})"
                )
                orders_placed += 1
            else:
                result = self._place_order(sig)
                if result:
                    self.risk.record_order(sig)
                    self.strategy.on_order_placed(sig, result)
                    orders_placed += 1
                    # Update balance for subsequent signals
                    state.balance -= sig.amount

        self.strategy.on_cycle_end(len(signals), orders_placed)
        logger.info(f"Cycle done: {len(signals)} signals, {orders_placed} orders placed")

    def _get_state(self) -> Optional[TradingState]:
        """Fetch balance, positions, and open orders from prob.trade."""
        state = TradingState()

        balance_data = _safe_api(lambda: trading_request("GET", "/balance"))
        if balance_data is None:
            return None
        state.balance = float(balance_data.get("available", 0))
        state.trading_ready = balance_data.get("tradingReady", False)

        pos_data = _safe_api(lambda: trading_request("GET", "/positions"))
        if pos_data is not None:
            state.positions = pos_data.get("positions", [])

        orders_data = _safe_api(lambda: trading_request("GET", "/orders"))
        if orders_data is not None:
            state.open_orders = orders_data.get("orders", [])

        return state

    def _fetch_markets(self) -> list:
        """Fetch markets for the strategy to analyze."""
        data = _safe_api(lambda: fetch("/markets/breaking", {"limit": 30}))
        if data is None:
            return []
        return data.get("markets", [])

    def _place_order(self, signal: Signal) -> Optional[dict]:
        """Place an order via prob.trade Trading API."""
        body = {
            "market": signal.market,
            "side": signal.side,
            "outcome": signal.outcome,
            "type": signal.order_type,
            "amount": signal.amount,
        }
        if signal.price is not None:
            body["price"] = signal.price

        result = _safe_api(lambda: trading_request("POST", "/order", body))
        if result:
            logger.info(
                f"Order placed: {result.get('orderId')} "
                f"— {signal.side} {signal.outcome} {signal.market} "
                f"${signal.amount} @ {signal.price or 'MARKET'}"
            )
        return result

    def _shutdown(self, signum, frame):
        logger.info(f"Shutdown signal received ({signum})")
        self.running = False


def _safe_api(fn):
    """Wrap API call, catching SystemExit from api_client on errors."""
    try:
        return fn()
    except SystemExit:
        return None
    except Exception as e:
        logger.error(f"API error: {e}")
        return None


def _interruptible_sleep(seconds: float, check_fn):
    """Sleep in 1-second intervals, checking if we should stop."""
    end = time.time() + seconds
    while time.time() < end and check_fn():
        time.sleep(min(1.0, end - time.time()))


def load_config(path: str) -> dict:
    """
    Parse simple YAML config (key: value lines). No PyYAML dependency.
    Supports nested keys via indentation (one level deep).
    """
    config = {}
    current_section = None

    with open(path, "r") as f:
        for line in f:
            raw = line.rstrip("\n")
            stripped = raw.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith("#"):
                continue

            if ":" not in stripped:
                continue

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # Detect indentation for nested sections
            indent = len(raw) - len(raw.lstrip())

            if indent == 0:
                # Top-level key
                if not value:
                    # Section header (e.g. "risk:")
                    current_section = key
                    config[current_section] = {}
                else:
                    current_section = None
                    config[key] = _parse_value(value)
            elif current_section is not None:
                # Nested key
                config[current_section][key] = _parse_value(value)

    return config


def _parse_value(value: str):
    """Auto-detect type: bool, int, float, or string."""
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
