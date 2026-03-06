#!/usr/bin/env python3
"""
Crypto Trader OpenClaw Skill -- main entrypoint.

Usage
-----
  python main.py --mode status
  python main.py --mode balance --exchange binance
  python main.py --mode start_strategy --strategy grid --params '{...}'
  python main.py --mode stop_strategy --strategy-id <id>
  python main.py --mode list_strategies
  python main.py --mode backtest --strategy grid --params '{...}' --start 2025-01-01 --end 2025-12-31
  python main.py --mode history --days 7
  python main.py --mode sentiment --symbol BTC
  python main.py --mode monitor --action start|status|stop
  python main.py --mode emergency_stop

All output is structured JSON written to stdout.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))

_env_path = _SCRIPTS_DIR.parent.parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

from exchange_manager import ExchangeManager, ExchangeError
from risk_manager import RiskManager, RiskLimitExceeded
from strategy_engine import StrategyEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("crypto-trader.main")


def _output(data: Dict[str, Any]) -> None:
    """Print structured JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def _error(message: str, code: str = "error") -> None:
    """Print a structured error and exit with code 1."""
    _output({"status": "error", "code": code, "message": message})
    sys.exit(1)


def _init_components() -> tuple:
    """Initialize exchange manager, risk manager, and strategy engine."""
    try:
        exchange_mgr = ExchangeManager()
    except Exception as exc:
        _error(f"Failed to initialize exchange manager: {exc}")

    risk_mgr = RiskManager()
    engine = StrategyEngine(exchange_mgr, risk_mgr)

    _register_strategies(engine)

    return exchange_mgr, risk_mgr, engine


def _register_strategies(engine: StrategyEngine) -> None:
    """Register all available strategy classes."""
    try:
        from strategies.grid_trading import GridTradingStrategy
        engine.register_strategy(GridTradingStrategy)
    except ImportError:
        logger.debug("Grid trading strategy not available.")

    try:
        from strategies.dca import DCAStrategy
        engine.register_strategy(DCAStrategy)
    except ImportError:
        logger.debug("DCA strategy not available.")

    try:
        from strategies.trend_following import TrendFollowingStrategy
        engine.register_strategy(TrendFollowingStrategy)
    except ImportError:
        logger.debug("Trend following strategy not available.")

    try:
        from strategies.scalping import ScalpingStrategy
        engine.register_strategy(ScalpingStrategy)
    except ImportError:
        logger.debug("Scalping strategy not available.")

    try:
        from strategies.arbitrage import ArbitrageStrategy
        engine.register_strategy(ArbitrageStrategy)
    except ImportError:
        logger.debug("Arbitrage strategy not available.")

    try:
        from strategies.swing_trading import SwingTradingStrategy
        engine.register_strategy(SwingTradingStrategy)
    except ImportError:
        logger.debug("Swing trading strategy not available.")

    try:
        from strategies.copy_trading import CopyTradingStrategy
        engine.register_strategy(CopyTradingStrategy)
    except ImportError:
        logger.debug("Copy trading strategy not available.")

    try:
        from strategies.rebalancing import RebalancingStrategy
        engine.register_strategy(RebalancingStrategy)
    except ImportError:
        logger.debug("Rebalancing strategy not available.")


# ------------------------------------------------------------------
# Mode: status
# ------------------------------------------------------------------

def _run_status(exchange_mgr: ExchangeManager, risk_mgr: RiskManager, engine: StrategyEngine) -> None:
    """Show portfolio status, active strategies, and risk status."""
    result: Dict[str, Any] = {
        "status": "ok",
        "environment": "paper" if exchange_mgr.demo else "LIVE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exchanges": {},
        "strategies": engine.list_strategies(),
        "risk": risk_mgr.get_status(),
    }

    for ex_name in exchange_mgr.available_exchanges:
        try:
            balances = exchange_mgr.get_balance(ex_name)
            result["exchanges"][ex_name] = {
                "connected": True,
                "balances": balances,
            }
        except ExchangeError as exc:
            result["exchanges"][ex_name] = {
                "connected": False,
                "error": str(exc),
            }

    _output(result)


# ------------------------------------------------------------------
# Mode: balance
# ------------------------------------------------------------------

def _run_balance(exchange_mgr: ExchangeManager, exchange: Optional[str] = None) -> None:
    """Show balances for one or all exchanges."""
    exchanges = [exchange] if exchange else exchange_mgr.available_exchanges
    result: Dict[str, Any] = {
        "status": "ok",
        "environment": "paper" if exchange_mgr.demo else "LIVE",
        "balances": {},
    }

    for ex_name in exchanges:
        try:
            balances = exchange_mgr.get_balance(ex_name)
            result["balances"][ex_name] = balances
        except ExchangeError as exc:
            result["balances"][ex_name] = {"error": str(exc)}

    _output(result)


# ------------------------------------------------------------------
# Mode: start_strategy
# ------------------------------------------------------------------

def _run_start_strategy(engine: StrategyEngine, strategy: str, params_json: Optional[str] = None) -> None:
    """Start a trading strategy."""
    params = {}
    if params_json:
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError as exc:
            _error(f"Invalid JSON params: {exc}")

    result = engine.start_strategy(strategy, params)
    _output(result)


# ------------------------------------------------------------------
# Mode: stop_strategy
# ------------------------------------------------------------------

def _run_stop_strategy(engine: StrategyEngine, strategy_id: str) -> None:
    """Stop a running strategy."""
    result = engine.stop_strategy(strategy_id)
    _output(result)


# ------------------------------------------------------------------
# Mode: list_strategies
# ------------------------------------------------------------------

def _run_list_strategies(engine: StrategyEngine) -> None:
    """List all strategies and their status."""
    strategies = engine.list_strategies()
    available = engine.get_available_strategies()
    _output({
        "status": "ok",
        "available_strategies": available,
        "running_strategies": strategies,
        "running_count": len(strategies),
    })


# ------------------------------------------------------------------
# Mode: history
# ------------------------------------------------------------------

def _run_history(exchange_mgr: ExchangeManager, days: int = 7) -> None:
    """Show trade history."""
    since_ms = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
    result: Dict[str, Any] = {
        "status": "ok",
        "period_days": days,
        "orders": {},
    }

    for ex_name in exchange_mgr.available_exchanges:
        try:
            orders = exchange_mgr.get_order_history(ex_name, since=since_ms)
            result["orders"][ex_name] = orders
        except ExchangeError as exc:
            result["orders"][ex_name] = {"error": str(exc)}

    _output(result)


# ------------------------------------------------------------------
# Mode: backtest
# ------------------------------------------------------------------

def _run_backtest(
    engine: StrategyEngine,
    strategy: str,
    params_json: Optional[str],
    start_date: str,
    end_date: str,
) -> None:
    """Run a backtest for a strategy."""
    try:
        from backtester import Backtester
    except ImportError:
        _error("Backtester module not available. Install dependencies first.")

    params = {}
    if params_json:
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError as exc:
            _error(f"Invalid JSON params: {exc}")

    backtester = Backtester(engine.exchange_manager)
    result = backtester.run(strategy, params, start_date, end_date)
    _output(result)


# ------------------------------------------------------------------
# Mode: sentiment
# ------------------------------------------------------------------

def _run_sentiment(symbol: str) -> None:
    """Run sentiment analysis for a symbol."""
    try:
        from sentiment_analyzer import SentimentAnalyzer
    except ImportError:
        _error("Sentiment analyzer module not available. Install dependencies first.")

    analyzer = SentimentAnalyzer()
    result = analyzer.analyze(symbol)
    _output(result)


# ------------------------------------------------------------------
# Mode: monitor
# ------------------------------------------------------------------

def _run_monitor(action: str) -> None:
    """Control the monitoring daemon."""
    try:
        from monitor_daemon import MonitorDaemon
    except ImportError:
        _error("Monitor daemon module not available.")

    daemon = MonitorDaemon()
    if action == "start":
        result = daemon.start()
    elif action == "stop":
        result = daemon.stop()
    elif action == "status":
        result = daemon.get_status()
    else:
        _error(f"Unknown monitor action: {action}. Use start, stop, or status.")
        return
    _output(result)


# ------------------------------------------------------------------
# Mode: emergency_stop
# ------------------------------------------------------------------

def _run_emergency_stop(
    exchange_mgr: ExchangeManager,
    risk_mgr: RiskManager,
    engine: StrategyEngine,
) -> None:
    """Emergency stop: cancel all orders and stop all strategies."""
    results: Dict[str, Any] = {
        "status": "ok",
        "action": "emergency_stop",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "strategies_stopped": [],
        "orders_cancelled": {},
    }

    stopped = engine.stop_all()
    results["strategies_stopped"] = stopped

    for ex_name in exchange_mgr.available_exchanges:
        try:
            cancelled = exchange_mgr.cancel_all_orders(ex_name)
            results["orders_cancelled"][ex_name] = cancelled
        except ExchangeError as exc:
            results["orders_cancelled"][ex_name] = {"error": str(exc)}

    risk_mgr.activate_kill_switch(reason="emergency_stop")
    results["kill_switch"] = "activated"

    _output(results)


# ------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crypto Trader Skill for OpenClaw"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            "status", "balance", "start_strategy", "stop_strategy",
            "list_strategies", "history", "backtest", "sentiment",
            "monitor", "emergency_stop",
        ],
        help="Operation mode",
    )
    parser.add_argument("--exchange", type=str, help="Exchange name (for balance mode)")
    parser.add_argument("--strategy", type=str, help="Strategy name")
    parser.add_argument("--strategy-id", type=str, help="Strategy instance ID")
    parser.add_argument("--params", type=str, help="Strategy parameters as JSON")
    parser.add_argument("--days", type=int, default=7, help="Number of days for history")
    parser.add_argument("--start", type=str, help="Backtest start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="Backtest end date (YYYY-MM-DD)")
    parser.add_argument("--symbol", type=str, help="Symbol for sentiment analysis")
    parser.add_argument("--action", type=str, help="Monitor action (start/stop/status)")

    args = parser.parse_args()

    exchange_mgr, risk_mgr, engine = _init_components()

    mode = args.mode

    if mode == "status":
        _run_status(exchange_mgr, risk_mgr, engine)

    elif mode == "balance":
        _run_balance(exchange_mgr, args.exchange)

    elif mode == "start_strategy":
        if not args.strategy:
            _error("--strategy is required for start_strategy mode.")
        _run_start_strategy(engine, args.strategy, args.params)

    elif mode == "stop_strategy":
        if not args.strategy_id:
            _error("--strategy-id is required for stop_strategy mode.")
        _run_stop_strategy(engine, args.strategy_id)

    elif mode == "list_strategies":
        _run_list_strategies(engine)

    elif mode == "history":
        _run_history(exchange_mgr, args.days)

    elif mode == "backtest":
        if not args.strategy:
            _error("--strategy is required for backtest mode.")
        if not args.start or not args.end:
            _error("--start and --end dates are required for backtest mode.")
        _run_backtest(engine, args.strategy, args.params, args.start, args.end)

    elif mode == "sentiment":
        if not args.symbol:
            _error("--symbol is required for sentiment mode.")
        _run_sentiment(args.symbol)

    elif mode == "monitor":
        if not args.action:
            _error("--action is required for monitor mode (start/stop/status).")
        _run_monitor(args.action)

    elif mode == "emergency_stop":
        _run_emergency_stop(exchange_mgr, risk_mgr, engine)


if __name__ == "__main__":
    main()
