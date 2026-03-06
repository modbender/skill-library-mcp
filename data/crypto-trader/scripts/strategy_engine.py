"""
Strategy Engine -- manages the lifecycle of trading strategies.

Handles starting, stopping, listing, and status reporting for all
registered strategies. Each strategy runs as a managed object with
its own configuration and state.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

import yaml

logger = logging.getLogger("crypto-trader.engine")

_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"
_DATA_DIR = _PROJECT_ROOT / "data"
_STATE_PATH = Path(os.environ.get(
    "CRYPTO_STRATEGY_STATE_PATH",
    str(Path.home() / ".openclaw" / ".crypto-trader-strategies.json"),
))


class BaseStrategy:
    """Base class for all trading strategies.

    Subclasses must implement:
    - evaluate(): check conditions and optionally return trade signals
    - on_start(): called when strategy is activated
    - on_stop(): called when strategy is deactivated
    """

    name: str = "base"
    display_name: str = "Base Strategy"

    def __init__(
        self,
        strategy_id: str,
        params: Dict[str, Any],
        exchange_manager: Any,
        risk_manager: Any,
    ) -> None:
        self.strategy_id = strategy_id
        self.params = params
        self.exchange_manager = exchange_manager
        self.risk_manager = risk_manager
        self.active = False
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.last_run: Optional[str] = None
        self.stats: Dict[str, Any] = {
            "trades_executed": 0,
            "total_pnl": 0.0,
            "signals_generated": 0,
        }

    def on_start(self) -> None:
        """Called when the strategy is activated."""
        self.active = True
        logger.info("Strategy %s (%s) started.", self.display_name, self.strategy_id)

    def on_stop(self) -> None:
        """Called when the strategy is deactivated."""
        self.active = False
        logger.info("Strategy %s (%s) stopped.", self.display_name, self.strategy_id)

    def evaluate(self) -> List[Dict[str, Any]]:
        """Evaluate market conditions and return trade signals.

        Returns a list of signal dicts:
        [{"symbol": ..., "side": "buy"/"sell", "amount": ..., "price": ..., "reason": ...}]
        """
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        """Serialize strategy state for persistence."""
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "display_name": self.display_name,
            "params": self.params,
            "active": self.active,
            "created_at": self.created_at,
            "last_run": self.last_run,
            "stats": self.stats,
        }


class StrategyEngine:
    """Manages the lifecycle of trading strategies."""

    def __init__(self, exchange_manager: Any, risk_manager: Any) -> None:
        self.exchange_manager = exchange_manager
        self.risk_manager = risk_manager
        self._strategies: Dict[str, BaseStrategy] = {}
        self._registry: Dict[str, Type[BaseStrategy]] = {}
        self._config = self._load_config()
        self._lock = threading.Lock()

    @staticmethod
    def _load_config() -> Dict[str, Any]:
        path = _CONFIG_DIR / "strategies.yaml"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------

    def register_strategy(self, strategy_class: Type[BaseStrategy]) -> None:
        """Register a strategy class for use."""
        self._registry[strategy_class.name] = strategy_class
        logger.info("Registered strategy: %s", strategy_class.name)

    def get_available_strategies(self) -> List[str]:
        """Return names of all registered strategies."""
        return list(self._registry.keys())

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_strategy(
        self,
        strategy_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create and start a new strategy instance."""
        with self._lock:
            strategy_class = self._registry.get(strategy_name)
            if strategy_class is None:
                available = ", ".join(self._registry.keys()) or "none"
                return {
                    "status": "error",
                    "message": f"Unknown strategy '{strategy_name}'. Available: {available}",
                }

            strat_config = self._config.get(strategy_name, {})
            if not strat_config.get("enabled", True):
                return {
                    "status": "error",
                    "message": f"Strategy '{strategy_name}' is disabled in config.",
                }

            merged_params = {**strat_config.get("default_params", {})}
            if params:
                merged_params.update(params)

            strategy_id = f"{strategy_name}_{uuid.uuid4().hex[:8]}"

            strategy = strategy_class(
                strategy_id=strategy_id,
                params=merged_params,
                exchange_manager=self.exchange_manager,
                risk_manager=self.risk_manager,
            )
            strategy.on_start()
            self._strategies[strategy_id] = strategy
            self._save_state()

            return {
                "status": "ok",
                "strategy_id": strategy_id,
                "strategy_name": strategy_name,
                "params": merged_params,
                "message": f"Strategy '{strategy_name}' started with ID {strategy_id}.",
            }

    def stop_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Stop a running strategy."""
        with self._lock:
            strategy = self._strategies.get(strategy_id)
            if strategy is None:
                return {
                    "status": "error",
                    "message": f"Strategy '{strategy_id}' not found.",
                }
            strategy.on_stop()
            del self._strategies[strategy_id]
            self._save_state()
            return {
                "status": "ok",
                "strategy_id": strategy_id,
                "message": f"Strategy '{strategy_id}' stopped.",
            }

    def stop_all(self) -> List[Dict[str, Any]]:
        """Stop all running strategies."""
        results = []
        with self._lock:
            for sid in list(self._strategies.keys()):
                self._strategies[sid].on_stop()
                results.append({"strategy_id": sid, "status": "stopped"})
            self._strategies.clear()
            self._save_state()
        return results

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate_all(self) -> List[Dict[str, Any]]:
        """Run evaluate() on all active strategies and collect signals."""
        all_signals = []
        for sid, strategy in list(self._strategies.items()):
            if not strategy.active:
                continue
            try:
                signals = strategy.evaluate()
                strategy.last_run = datetime.now(timezone.utc).isoformat()
                strategy.stats["signals_generated"] += len(signals)
                for signal in signals:
                    signal["strategy_id"] = sid
                    signal["strategy_name"] = strategy.name
                all_signals.extend(signals)
            except Exception as exc:
                logger.error("Strategy %s evaluate error: %s", sid, exc)
        return all_signals

    # ------------------------------------------------------------------
    # Status / Listing
    # ------------------------------------------------------------------

    def list_strategies(self) -> List[Dict[str, Any]]:
        """Return status of all strategy instances."""
        return [s.to_dict() for s in self._strategies.values()]

    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Return status of a specific strategy."""
        strategy = self._strategies.get(strategy_id)
        return strategy.to_dict() if strategy else None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save_state(self) -> None:
        """Save current strategy state to disk."""
        state = {
            "strategies": {
                sid: s.to_dict() for sid, s in self._strategies.items()
            },
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, default=str)
