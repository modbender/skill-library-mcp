"""
Monitor Daemon -- real-time portfolio monitoring and strategy execution.

Runs as a background process that periodically checks portfolio status,
evaluates strategy signals, monitors risk limits, and triggers
notifications. Persists state to disk for recovery after restarts.
"""
from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("crypto-trader.monitor")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_STATE_PATH = Path(os.environ.get(
    "CRYPTO_MONITOR_STATE_PATH",
    str(Path.home() / ".openclaw" / ".crypto-trader-monitor.json"),
))
_PID_PATH = Path(os.environ.get(
    "CRYPTO_MONITOR_PID_PATH",
    str(Path.home() / ".openclaw" / ".crypto-trader-monitor.pid"),
))

CHECK_ORDERS_INTERVAL = 10
CHECK_RISK_INTERVAL = 60
EVALUATE_STRATEGIES_INTERVAL = 300
SENTIMENT_INTERVAL = 1800
SNAPSHOT_INTERVAL = 60


class MonitorDaemon:
    """Background monitoring daemon for portfolio and strategy management."""

    def __init__(self) -> None:
        self._running = False
        self._state = self._load_state()

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    @staticmethod
    def _load_state() -> Dict[str, Any]:
        if _STATE_PATH.exists():
            try:
                with open(_STATE_PATH, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "running": False,
            "started_at": None,
            "last_check": None,
            "checks_performed": 0,
            "errors": [],
        }

    def _save_state(self) -> None:
        _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump(self._state, fh, indent=2, default=str)

    # ------------------------------------------------------------------
    # PID management
    # ------------------------------------------------------------------

    @staticmethod
    def _write_pid() -> None:
        _PID_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_PID_PATH, "w") as fh:
            fh.write(str(os.getpid()))

    @staticmethod
    def _read_pid() -> Optional[int]:
        if _PID_PATH.exists():
            try:
                return int(_PID_PATH.read_text().strip())
            except (ValueError, OSError):
                pass
        return None

    @staticmethod
    def _remove_pid() -> None:
        try:
            _PID_PATH.unlink(missing_ok=True)
        except OSError:
            pass

    @staticmethod
    def _is_process_running(pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> Dict[str, Any]:
        """Start the monitoring daemon."""
        existing_pid = self._read_pid()
        if existing_pid and self._is_process_running(existing_pid):
            return {
                "status": "already_running",
                "pid": existing_pid,
                "message": "Monitor daemon is already running.",
            }

        self._running = True
        self._state["running"] = True
        self._state["started_at"] = datetime.now(timezone.utc).isoformat()
        self._write_pid()
        self._save_state()

        return {
            "status": "started",
            "pid": os.getpid(),
            "message": "Monitor daemon started.",
        }

    def stop(self) -> Dict[str, Any]:
        """Stop the monitoring daemon."""
        pid = self._read_pid()
        if pid and self._is_process_running(pid):
            try:
                os.kill(pid, signal.SIGTERM)
                self._remove_pid()
                self._state["running"] = False
                self._save_state()
                return {
                    "status": "stopped",
                    "pid": pid,
                    "message": "Monitor daemon stopped.",
                }
            except OSError as exc:
                return {
                    "status": "error",
                    "message": f"Failed to stop daemon (PID {pid}): {exc}",
                }

        self._remove_pid()
        self._state["running"] = False
        self._save_state()
        return {
            "status": "not_running",
            "message": "Monitor daemon was not running.",
        }

    def get_status(self) -> Dict[str, Any]:
        """Get the current daemon status."""
        pid = self._read_pid()
        running = pid is not None and self._is_process_running(pid)

        return {
            "status": "ok",
            "running": running,
            "pid": pid,
            "started_at": self._state.get("started_at"),
            "last_check": self._state.get("last_check"),
            "checks_performed": self._state.get("checks_performed", 0),
            "recent_errors": self._state.get("errors", [])[-5:],
        }

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run_loop(
        self,
        exchange_manager: Any,
        risk_manager: Any,
        strategy_engine: Any,
        notifier: Any = None,
    ) -> None:
        """Run the main monitoring loop. Blocking call."""
        def _signal_handler(signum: int, frame: Any) -> None:
            logger.info("Received signal %d, shutting down...", signum)
            self._running = False

        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)

        self._write_pid()
        logger.info("Monitor daemon started (PID %d).", os.getpid())

        last_orders_check = 0.0
        last_risk_check = 0.0
        last_evaluate = 0.0
        last_sentiment = 0.0
        last_snapshot = 0.0

        while self._running:
            now = time.time()

            try:
                if now - last_orders_check >= CHECK_ORDERS_INTERVAL:
                    self._check_open_orders(exchange_manager, strategy_engine)
                    last_orders_check = now

                if now - last_snapshot >= SNAPSHOT_INTERVAL:
                    self._update_portfolio_snapshot(exchange_manager, risk_manager)
                    last_snapshot = now

                if now - last_risk_check >= CHECK_RISK_INTERVAL:
                    self._check_risk_limits(risk_manager, exchange_manager, strategy_engine, notifier)
                    last_risk_check = now

                if now - last_evaluate >= EVALUATE_STRATEGIES_INTERVAL:
                    self._evaluate_strategies(strategy_engine, exchange_manager, risk_manager, notifier)
                    last_evaluate = now

                if now - last_sentiment >= SENTIMENT_INTERVAL:
                    self._check_sentiment(notifier)
                    last_sentiment = now

                self._state["last_check"] = datetime.now(timezone.utc).isoformat()
                self._state["checks_performed"] = self._state.get("checks_performed", 0) + 1

                if self._state["checks_performed"] % 10 == 0:
                    self._save_state()

            except Exception as exc:
                error_msg = f"{datetime.now(timezone.utc).isoformat()}: {exc}"
                logger.error("Monitor loop error: %s", exc)
                self._state.setdefault("errors", []).append(error_msg)
                if len(self._state["errors"]) > 50:
                    self._state["errors"] = self._state["errors"][-50:]

            time.sleep(1)

        self._state["running"] = False
        self._save_state()
        self._remove_pid()
        logger.info("Monitor daemon stopped.")

    # ------------------------------------------------------------------
    # Monitoring tasks
    # ------------------------------------------------------------------

    def _check_open_orders(self, exchange_manager: Any, strategy_engine: Any) -> None:
        """Check status of all open orders across exchanges."""
        for ex_name in exchange_manager.available_exchanges:
            try:
                open_orders = exchange_manager.get_open_orders(ex_name)
                logger.debug("Exchange %s: %d open orders.", ex_name, len(open_orders))
            except Exception as exc:
                logger.warning("Failed to check orders on %s: %s", ex_name, exc)

    def _update_portfolio_snapshot(self, exchange_manager: Any, risk_manager: Any) -> None:
        """Update portfolio value for risk tracking."""
        total_value = 0.0
        for ex_name in exchange_manager.available_exchanges:
            try:
                balances = exchange_manager.get_balance(ex_name)
                for asset, data in balances.items():
                    if isinstance(data, dict):
                        if asset == "USDT":
                            total_value += data.get("total", 0)
                        else:
                            try:
                                ticker = exchange_manager.get_ticker(ex_name, f"{asset}/USDT")
                                price = ticker.get("last", 0) or 0
                                total_value += data.get("total", 0) * price
                            except Exception:
                                pass
            except Exception as exc:
                logger.warning("Failed to get balance from %s: %s", ex_name, exc)

        if total_value > 0:
            risk_manager.update_portfolio_value(total_value)

    def _check_risk_limits(
        self,
        risk_manager: Any,
        exchange_manager: Any,
        strategy_engine: Any,
        notifier: Any,
    ) -> None:
        """Check if any risk limits are breached."""
        status = risk_manager.get_status()
        daily_pnl = status.get("daily_pnl_eur", 0)
        drawdown = status.get("drawdown_pct", 0)
        max_daily_loss = status.get("limits", {}).get("max_daily_loss_eur", 0)
        max_drawdown = status.get("limits", {}).get("max_drawdown_pct", 0)

        if max_daily_loss and daily_pnl < 0 and abs(daily_pnl) >= max_daily_loss * 0.8:
            logger.warning("Approaching daily loss limit: %.2f / %.2f EUR", abs(daily_pnl), max_daily_loss)
            if notifier:
                notifier.send_alert("risk_limit_hit", {
                    "type": "daily_loss_warning",
                    "current_loss": abs(daily_pnl),
                    "limit": max_daily_loss,
                })

        if max_drawdown and drawdown >= max_drawdown * 0.8:
            logger.warning("Approaching drawdown limit: %.1f%% / %.1f%%", drawdown, max_drawdown)

    def _evaluate_strategies(
        self,
        strategy_engine: Any,
        exchange_manager: Any,
        risk_manager: Any,
        notifier: Any,
    ) -> None:
        """Run strategy evaluations and execute signals."""
        signals = strategy_engine.evaluate_all()

        for signal_data in signals:
            strategy_name = signal_data.get("strategy_name", "unknown")
            exchange = signal_data.get("exchange", "")
            symbol = signal_data.get("symbol", "")
            side = signal_data.get("side", "")
            amount = signal_data.get("amount", 0)
            price = signal_data.get("price")

            try:
                open_orders = exchange_manager.get_open_orders(exchange, symbol)
                balances = exchange_manager.get_balance(exchange)
                total_value = sum(
                    v.get("total", 0) if isinstance(v, dict) else 0
                    for v in balances.values()
                )

                risk_manager.validate_order(
                    strategy=strategy_name,
                    exchange=exchange,
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    price=price,
                    portfolio_value_eur=total_value,
                    open_order_count=len(open_orders),
                )

                order_type = signal_data.get("order_type", "market")
                order = exchange_manager.place_order(
                    exchange, symbol, side, amount, price, order_type,
                )

                logger.info(
                    "Signal executed: %s %s %s %.8f on %s (strategy: %s)",
                    order_type, side, symbol, amount, exchange, strategy_name,
                )

                if notifier:
                    notifier.send_alert("trade_executed", {
                        "strategy": strategy_name,
                        "symbol": symbol,
                        "side": side,
                        "amount": amount,
                        "price": price or order.get("price"),
                        "exchange": exchange,
                        "reason": signal_data.get("reason", ""),
                    })

            except Exception as exc:
                logger.error(
                    "Failed to execute signal for %s: %s", strategy_name, exc,
                )
                if notifier:
                    notifier.send_alert("strategy_error", {
                        "strategy": strategy_name,
                        "error": str(exc),
                    })

    def _check_sentiment(self, notifier: Any) -> None:
        """Run periodic sentiment checks."""
        try:
            from sentiment_analyzer import SentimentAnalyzer
            analyzer = SentimentAnalyzer()
            result = analyzer.get_quick_sentiment("BTC")

            score = result.get("score", 0)
            if abs(score) >= 0.5:
                label = result.get("label", "neutral")
                logger.info("Significant sentiment detected for BTC: %s (%.2f)", label, score)
                if notifier:
                    notifier.send_alert("sentiment_alert", {
                        "symbol": "BTC",
                        "score": score,
                        "label": label,
                    })
        except Exception as exc:
            logger.debug("Sentiment check failed: %s", exc)
