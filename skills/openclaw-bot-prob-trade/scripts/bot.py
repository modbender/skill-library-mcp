#!/usr/bin/env python3
"""
OpenClaw Trading Bot — CLI entry point.

Usage:
    python3 bot.py run                     Start autonomous trading loop
    python3 bot.py run --strategy momentum Override strategy from config
    python3 bot.py scan                    Single scan (show signals, no orders)
    python3 bot.py status                  Show balance, positions, orders
    python3 bot.py strategies              List available strategies
"""

import argparse
import json
import logging
import os
import sys

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.engine import Engine, load_config
from lib.strategies import list_strategies


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )


def find_config() -> str:
    """Find config.yaml relative to script dir or cwd."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "config.yaml"),
        "config.yaml",
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    print("Error: config.yaml not found", file=sys.stderr)
    sys.exit(1)


def apply_env_overrides(config: dict):
    """Override config values from environment variables."""
    if os.environ.get("DRY_RUN"):
        config["dry_run"] = os.environ["DRY_RUN"].lower() in ("true", "1", "yes")
    if os.environ.get("STRATEGY"):
        config["strategy"] = os.environ["STRATEGY"]
    if os.environ.get("LOOP_INTERVAL"):
        config["loop_interval_sec"] = int(os.environ["LOOP_INTERVAL"])


def cmd_run(args):
    config = load_config(find_config())
    apply_env_overrides(config)

    if args.strategy:
        config["strategy"] = args.strategy

    engine = Engine(config)
    engine.run()


def cmd_scan(args):
    config = load_config(find_config())
    apply_env_overrides(config)

    if args.strategy:
        config["strategy"] = args.strategy

    engine = Engine(config)
    signals = engine.scan_once()

    if not signals:
        print("No signals found")
        return

    print(f"\n{len(signals)} signal(s) found:\n")
    for i, s in enumerate(signals, 1):
        print(f"  {i}. {s.side} {s.outcome} — {s.market[:16]}...")
        print(f"     ${s.amount} @ {s.price or 'MARKET'} "
              f"(confidence: {s.confidence:.0%})")
        print(f"     Reason: {s.reason}")
        print()


def cmd_status(args):
    config = load_config(find_config())
    apply_env_overrides(config)

    # Need a strategy to instantiate engine, use config default
    engine = Engine(config)
    data = engine.status()

    print(json.dumps(data, indent=2, default=str))


def cmd_strategies(_args):
    names = list_strategies()
    if not names:
        print("No strategies found in lib/strategies/")
        return
    print("Available strategies:")
    for name in names:
        print(f"  - {name}")


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="OpenClaw Trading Bot for Polymarket via prob.trade"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # run
    sub = subparsers.add_parser("run", help="Start autonomous trading loop")
    sub.add_argument("--strategy", help="Override strategy name")
    sub.set_defaults(func=cmd_run)

    # scan
    sub = subparsers.add_parser("scan", help="Single scan (no orders)")
    sub.add_argument("--strategy", help="Override strategy name")
    sub.set_defaults(func=cmd_scan)

    # status
    sub = subparsers.add_parser("status", help="Balance, positions, orders")
    sub.set_defaults(func=cmd_status)

    # strategies
    sub = subparsers.add_parser("strategies", help="List available strategies")
    sub.set_defaults(func=cmd_strategies)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
