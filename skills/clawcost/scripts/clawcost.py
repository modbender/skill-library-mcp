#!/usr/bin/env python3
"""
ClawCost - OpenClaw Agent Cost Monitor
Track spending across models with budget alerts.
"""

import json
import glob
import os
import sys
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path


def get_config_path() -> Path:
    """Get config file path for current user."""
    return Path.home() / ".clawcost" / "config.json"


def load_config() -> dict:
    """Load config from file."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"initial_balance": None, "budget_daily": 10.0}


def save_config(config: dict):
    """Save config to file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_openclaw_dir() -> Path:
    """Get OpenClaw sessions directory for current user."""
    return Path.home() / ".openclaw" / "agents" / "main" / "sessions"


def parse_sessions(sessions_dir: Path) -> list:
    """Parse all JSONL session files and extract usage data."""
    usage_data = []

    for filepath in glob.glob(str(sessions_dir / "*.jsonl")):
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "message" and "message" in data:
                            msg = data["message"]
                            if "usage" in msg and msg.get("role") == "assistant":
                                usage = msg["usage"]
                                cost_data = usage.get("cost", {})

                                entry = {
                                    "timestamp": data.get("timestamp", ""),
                                    "model": msg.get("model", "unknown"),
                                    "input_tokens": usage.get("input", 0),
                                    "output_tokens": usage.get("output", 0),
                                    "cache_read": usage.get("cacheRead", 0),
                                    "cache_write": usage.get("cacheWrite", 0),
                                    "cost": cost_data.get("total", 0),
                                }
                                usage_data.append(entry)
                    except json.JSONDecodeError:
                        continue
        except (IOError, PermissionError):
            continue

    return usage_data


def aggregate_data(usage_data: list) -> dict:
    """Aggregate usage data by model and date."""
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    result = {
        "total": {"cost": 0, "tokens": 0},
        "today": {"cost": 0, "tokens": 0},
        "week": {"cost": 0, "tokens": 0},
        "by_model": defaultdict(lambda: {"cost": 0, "tokens": 0, "calls": 0}),
        "by_model_today": defaultdict(lambda: {"cost": 0, "tokens": 0, "calls": 0}),
        "by_date": defaultdict(float),
    }

    for entry in usage_data:
        date = entry["timestamp"][:10] if entry["timestamp"] else ""
        cost = entry["cost"]
        tokens = entry["input_tokens"] + entry["output_tokens"] + entry["cache_read"] + entry["cache_write"]
        model = entry["model"]

        result["total"]["cost"] += cost
        result["total"]["tokens"] += tokens

        if date == today:
            result["today"]["cost"] += cost
            result["today"]["tokens"] += tokens
            # Track models for today
            result["by_model_today"][model]["cost"] += cost
            result["by_model_today"][model]["tokens"] += tokens
            result["by_model_today"][model]["calls"] += 1

        if date >= week_ago:
            result["week"]["cost"] += cost
            result["week"]["tokens"] += tokens

        result["by_model"][model]["cost"] += cost
        result["by_model"][model]["tokens"] += tokens
        result["by_model"][model]["calls"] += 1

        if date:
            result["by_date"][date] += cost

    return result


def format_tokens(n):
    """Format token count to human readable."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def main():
    parser = argparse.ArgumentParser(description="ClawCost - OpenClaw Agent Cost Monitor")
    parser.add_argument("--budget", "-b", type=float, default=None, help="Daily budget in USD")
    parser.add_argument("--set-balance", type=float, default=None, help="Set initial balance (USD)")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    # Get current user
    user = os.environ.get("USER", "unknown")

    # Load config
    config = load_config()

    # Handle --set-balance (sets initial balance for auto-calculation)
    if args.set_balance is not None:
        config["initial_balance"] = args.set_balance
        save_config(config)
        print(f"Initial balance set to ${args.set_balance:.2f}")
        print("Remaining will auto-calculate: initial - total_spent")
        return

    # Use budget from args or config
    budget = args.budget if args.budget is not None else config.get("budget_daily", 10.0)

    sessions_dir = get_openclaw_dir()

    if not sessions_dir.exists():
        print(f"Error: No sessions found at {sessions_dir}", file=sys.stderr)
        sys.exit(1)

    usage_data = parse_sessions(sessions_dir)
    data = aggregate_data(usage_data)

    # Get initial balance from config
    initial_balance = config.get("initial_balance")

    if args.format == "json":
        output = {
            "user": args.user,
            "today": round(data["today"]["cost"], 2),
            "week": round(data["week"]["cost"], 2),
            "total": round(data["total"]["cost"], 2),
            "tokens": data["total"]["tokens"],
            "models": {k: {"cost": round(v["cost"], 2), "calls": v["calls"]}
                      for k, v in data["by_model"].items() if v["cost"] > 0}
        }
        print(json.dumps(output, indent=2))
        return

    # Output JSON for AI to format naturally
    pct = (data["today"]["cost"] / budget * 100) if budget > 0 else 0

    # Clean model names helper
    def clean_name(model):
        return model.replace("claude-", "").replace("-20250929", "").replace("-20251001", "")

    # Models aggregate (all time)
    models = {}
    for model, stats in sorted(data["by_model"].items(), key=lambda x: x[1]["cost"], reverse=True):
        if stats["cost"] > 0:
            pct_model = (stats["cost"] / data["total"]["cost"] * 100) if data["total"]["cost"] > 0 else 0
            models[clean_name(model)] = {
                "cost": round(stats["cost"], 2),
                "calls": stats["calls"],
                "pct": round(pct_model, 1)
            }

    # Models today only
    models_today = {}
    for model, stats in sorted(data["by_model_today"].items(), key=lambda x: x[1]["cost"], reverse=True):
        if stats["cost"] > 0:
            pct_model = (stats["cost"] / data["today"]["cost"] * 100) if data["today"]["cost"] > 0 else 0
            models_today[clean_name(model)] = {
                "cost": round(stats["cost"], 2),
                "calls": stats["calls"],
                "pct": round(pct_model, 1)
            }

    # Daily costs
    daily = {}
    for date in sorted(data["by_date"].keys(), reverse=True)[:7]:
        daily[date] = round(data["by_date"][date], 2)

    # Calculate remaining balance
    balance_info = None
    if initial_balance is not None:
        remaining = initial_balance - data["total"]["cost"]
        balance_info = {
            "initial": round(initial_balance, 2),
            "spent": round(data["total"]["cost"], 2),
            "remaining": round(remaining, 2)
        }

    output = {
        "user": user,
        "balance": balance_info,
        "today": {"cost": round(data["today"]["cost"], 2), "budget": budget, "pct": round(pct, 1)},
        "week": round(data["week"]["cost"], 2),
        "total": {"cost": round(data["total"]["cost"], 2), "tokens": format_tokens(data["total"]["tokens"])},
        "models": models,
        "models_today": models_today,
        "daily": daily
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
