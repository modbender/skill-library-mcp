"""
Risk Manager -- enforces trading limits, stop-loss, take-profit, and kill-switch.

All pre-trade validations and portfolio-level risk checks run through this
module. The risk manager loads its configuration from config/risk_limits.yaml
and keeps an in-memory ledger of daily P&L and drawdown tracking.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("crypto-trader.risk")

_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"
_DATA_DIR = _PROJECT_ROOT / "data"
_STATE_PATH = Path(os.environ.get(
    "CRYPTO_RISK_STATE_PATH",
    str(Path.home() / ".openclaw" / ".crypto-trader-risk-state.json"),
))


class RiskLimitExceeded(Exception):
    """Raised when a trade would violate risk limits."""

    def __init__(self, rule: str, message: str) -> None:
        self.rule = rule
        self.message = message
        super().__init__(f"[{rule}] {message}")


class RiskManager:
    """Enforces global and per-strategy risk limits."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self._config = self._load_config(config_path)
        self._global = self._config.get("global_limits", {})
        self._overrides = self._config.get("strategy_overrides", {})
        self._stop_loss_cfg = self._config.get("stop_loss", {})
        self._take_profit_cfg = self._config.get("take_profit", {})

        self._state = self._load_state()
        self._lock = threading.Lock()
        self._killed = False

    # ------------------------------------------------------------------
    # Config & State
    # ------------------------------------------------------------------

    @staticmethod
    def _load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
        path = Path(config_path) if config_path else _CONFIG_DIR / "risk_limits.yaml"
        if not path.exists():
            logger.warning("Risk config not found at %s, using defaults.", path)
            return {}
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def _load_state(self) -> Dict[str, Any]:
        if _STATE_PATH.exists():
            try:
                with open(_STATE_PATH, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                logger.warning("Corrupt risk state file, resetting.")
        return self._default_state()

    @staticmethod
    def _default_state() -> Dict[str, Any]:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return {
            "date": today,
            "daily_pnl_eur": 0.0,
            "portfolio_ath_eur": 0.0,
            "current_portfolio_eur": 0.0,
            "open_order_count": 0,
            "trades_today": [],
            "killed": False,
        }

    def _save_state(self) -> None:
        _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump(self._state, fh, indent=2, default=str)

    def _reset_daily_if_needed(self) -> None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._state.get("date") != today:
            logger.info("New trading day, resetting daily counters.")
            self._state["date"] = today
            self._state["daily_pnl_eur"] = 0.0
            self._state["trades_today"] = []
            self._killed = self._state.get("killed", False)
            self._save_state()

    # ------------------------------------------------------------------
    # Getters for limits (with per-strategy overrides)
    # ------------------------------------------------------------------

    def _get_limit(self, strategy: Optional[str], key: str) -> Any:
        """Return the limit value, checking strategy overrides first."""
        if strategy:
            override = self._overrides.get(strategy, {})
            if key in override:
                return override[key]
        return self._global.get(key)

    # ------------------------------------------------------------------
    # Pre-Trade Validation
    # ------------------------------------------------------------------

    def validate_order(
        self,
        strategy: Optional[str],
        exchange: str,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float],
        portfolio_value_eur: float,
        open_order_count: int,
    ) -> None:
        """Validate a proposed order against all risk limits.

        Raises RiskLimitExceeded if any limit is violated.
        """
        with self._lock:
            self._reset_daily_if_needed()

            if self._killed or self._state.get("killed", False):
                raise RiskLimitExceeded(
                    "kill_switch",
                    "Emergency kill switch is active. All trading is halted. "
                    "Reset manually to resume."
                )

            estimated_cost = amount * (price or 0)

            max_order = self._get_limit(strategy, "max_order_size_eur")
            if max_order and estimated_cost > max_order:
                raise RiskLimitExceeded(
                    "max_order_size",
                    f"Order cost {estimated_cost:.2f} EUR exceeds max "
                    f"{max_order:.2f} EUR for strategy '{strategy}'."
                )

            max_open = self._get_limit(strategy, "max_open_orders")
            if max_open and open_order_count >= max_open:
                raise RiskLimitExceeded(
                    "max_open_orders",
                    f"Already {open_order_count} open orders (max {max_open}) "
                    f"for strategy '{strategy}'."
                )

            if side == "buy" and portfolio_value_eur > 0:
                max_pos_pct = self._get_limit(strategy, "max_position_size_pct")
                if max_pos_pct:
                    pos_pct = (estimated_cost / portfolio_value_eur) * 100
                    if pos_pct > max_pos_pct:
                        raise RiskLimitExceeded(
                            "max_position_size",
                            f"Position would be {pos_pct:.1f}% of portfolio "
                            f"(max {max_pos_pct:.1f}%)."
                        )

            max_daily_loss = self._get_limit(strategy, "max_daily_loss_eur")
            if max_daily_loss:
                current_loss = self._state.get("daily_pnl_eur", 0)
                if current_loss < 0 and abs(current_loss) >= max_daily_loss:
                    raise RiskLimitExceeded(
                        "max_daily_loss",
                        f"Daily loss {abs(current_loss):.2f} EUR has reached "
                        f"limit of {max_daily_loss:.2f} EUR."
                    )

            self._check_drawdown(portfolio_value_eur)

    def _check_drawdown(self, portfolio_value_eur: float) -> None:
        """Check if drawdown from ATH exceeds limit."""
        ath = self._state.get("portfolio_ath_eur", 0)
        if portfolio_value_eur > ath:
            self._state["portfolio_ath_eur"] = portfolio_value_eur
            self._save_state()
            return

        if ath <= 0:
            return

        drawdown_pct = ((ath - portfolio_value_eur) / ath) * 100
        max_dd = self._global.get("max_drawdown_pct", 100)
        if drawdown_pct >= max_dd:
            raise RiskLimitExceeded(
                "max_drawdown",
                f"Portfolio drawdown {drawdown_pct:.1f}% from ATH "
                f"({ath:.2f} EUR) exceeds limit of {max_dd:.1f}%."
            )

    # ------------------------------------------------------------------
    # Post-Trade Updates
    # ------------------------------------------------------------------

    def record_trade(self, trade_info: Dict[str, Any]) -> None:
        """Record a completed trade for daily P&L tracking."""
        with self._lock:
            self._reset_daily_if_needed()
            pnl = trade_info.get("realized_pnl_eur", 0)
            self._state["daily_pnl_eur"] = self._state.get("daily_pnl_eur", 0) + pnl
            self._state["trades_today"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "symbol": trade_info.get("symbol"),
                "side": trade_info.get("side"),
                "amount": trade_info.get("amount"),
                "price": trade_info.get("price"),
                "pnl_eur": pnl,
            })
            self._save_state()

    def update_portfolio_value(self, portfolio_value_eur: float) -> None:
        """Update the current portfolio value for drawdown tracking."""
        with self._lock:
            self._state["current_portfolio_eur"] = portfolio_value_eur
            if portfolio_value_eur > self._state.get("portfolio_ath_eur", 0):
                self._state["portfolio_ath_eur"] = portfolio_value_eur
            self._save_state()

    # ------------------------------------------------------------------
    # Stop-Loss / Take-Profit
    # ------------------------------------------------------------------

    def check_stop_loss(
        self,
        entry_price: float,
        current_price: float,
        custom_pct: Optional[float] = None,
    ) -> bool:
        """Return True if stop-loss should trigger."""
        if not self._stop_loss_cfg.get("enabled", True):
            return False
        threshold = custom_pct or self._stop_loss_cfg.get("default_pct", 5.0)
        loss_pct = ((entry_price - current_price) / entry_price) * 100
        return loss_pct >= threshold

    def check_trailing_stop(
        self,
        highest_price: float,
        current_price: float,
        custom_pct: Optional[float] = None,
    ) -> bool:
        """Return True if trailing stop should trigger."""
        if not self._stop_loss_cfg.get("trailing_enabled", False):
            return False
        threshold = custom_pct or self._stop_loss_cfg.get("trailing_pct", 3.0)
        drop_pct = ((highest_price - current_price) / highest_price) * 100
        return drop_pct >= threshold

    def check_take_profit(
        self,
        entry_price: float,
        current_price: float,
        custom_pct: Optional[float] = None,
    ) -> bool:
        """Return True if take-profit should trigger."""
        if not self._take_profit_cfg.get("enabled", True):
            return False
        threshold = custom_pct or self._take_profit_cfg.get("default_pct", 10.0)
        profit_pct = ((current_price - entry_price) / entry_price) * 100
        return profit_pct >= threshold

    def check_partial_take_profit(
        self,
        entry_price: float,
        current_price: float,
    ) -> Optional[float]:
        """Return the fraction to sell if partial take-profit triggers, else None."""
        if not self._take_profit_cfg.get("partial_exit_enabled", False):
            return None
        trigger_pct = self._take_profit_cfg.get("partial_exit_trigger_pct", 5.0)
        exit_fraction = self._take_profit_cfg.get("partial_exit_pct", 50.0) / 100.0
        profit_pct = ((current_price - entry_price) / entry_price) * 100
        if profit_pct >= trigger_pct:
            return exit_fraction
        return None

    # ------------------------------------------------------------------
    # Kill Switch
    # ------------------------------------------------------------------

    def activate_kill_switch(self, reason: str = "manual") -> None:
        """Activate emergency kill switch -- halts all trading."""
        with self._lock:
            self._killed = True
            self._state["killed"] = True
            self._state["kill_reason"] = reason
            self._state["kill_timestamp"] = datetime.now(timezone.utc).isoformat()
            self._save_state()
            logger.critical("KILL SWITCH ACTIVATED: %s", reason)

    def deactivate_kill_switch(self) -> None:
        """Deactivate the kill switch to resume trading."""
        with self._lock:
            self._killed = False
            self._state["killed"] = False
            self._state.pop("kill_reason", None)
            self._state.pop("kill_timestamp", None)
            self._save_state()
            logger.info("Kill switch deactivated. Trading can resume.")

    @property
    def is_killed(self) -> bool:
        return self._killed or self._state.get("killed", False)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Return current risk status."""
        with self._lock:
            self._reset_daily_if_needed()
            ath = self._state.get("portfolio_ath_eur", 0)
            current = self._state.get("current_portfolio_eur", 0)
            drawdown = 0.0
            if ath > 0:
                drawdown = round(((ath - current) / ath) * 100, 2)

            return {
                "date": self._state.get("date"),
                "daily_pnl_eur": round(self._state.get("daily_pnl_eur", 0), 2),
                "portfolio_ath_eur": round(ath, 2),
                "current_portfolio_eur": round(current, 2),
                "drawdown_pct": drawdown,
                "trades_today_count": len(self._state.get("trades_today", [])),
                "kill_switch_active": self.is_killed,
                "limits": {
                    "max_daily_loss_eur": self._global.get("max_daily_loss_eur"),
                    "max_drawdown_pct": self._global.get("max_drawdown_pct"),
                    "max_order_size_eur": self._global.get("max_order_size_eur"),
                    "max_open_orders": self._global.get("max_open_orders"),
                    "emergency_stop_loss_pct": self._global.get("emergency_stop_loss_pct"),
                },
            }
