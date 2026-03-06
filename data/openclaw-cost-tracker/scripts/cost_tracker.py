#!/usr/bin/env python3
"""
OpenClaw Cost Tracker
Parses OpenClaw session JSONL files to compute per-model token usage and costs.
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path


def find_agents_dir() -> Path:
    """Auto-discover the OpenClaw agents directory."""
    candidates = [
        Path.home() / ".openclaw" / "agents",
        Path("/root/.openclaw/agents"),
    ]
    # Also check OPENCLAW_HOME env
    env_home = os.environ.get("OPENCLAW_HOME")
    if env_home:
        candidates.insert(0, Path(env_home) / "agents")

    for p in candidates:
        if p.is_dir():
            return p

    print("Error: Could not find OpenClaw agents directory.", file=sys.stderr)
    print("Set OPENCLAW_HOME or ensure ~/.openclaw/agents exists.", file=sys.stderr)
    sys.exit(1)


def parse_sessions(agents_dir: Path, days: int = 0, since: Optional[str] = None) -> Dict[str, Any]:
    """Parse all session JSONL files and extract usage data.
    
    Args:
        agents_dir: Path to the agents directory
        days: Number of days to look back (0 = all time)
        since: ISO date string to filter from (overrides days)
    """
    if since:
        threshold = datetime.fromisoformat(since)
    elif days > 0:
        threshold = datetime.now() - timedelta(days=days)
    else:
        threshold = datetime.min

    model_usage: Dict[str, Dict[str, Any]] = {}
    daily_costs: Dict[str, Dict[str, float]] = {}  # date -> {model: cost}
    total_files = 0
    total_entries = 0

    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue

        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.is_dir():
            continue

        for session_file in sessions_dir.glob("*.jsonl"):
            # Quick filter: skip old files by mtime
            if days > 0:
                mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                if mtime < threshold:
                    continue

            total_files += 1

            try:
                with open(session_file, "r") as f:
                    for line in f:
                        if '"usage"' not in line:
                            continue
                        try:
                            entry = json.loads(line)
                            msg = entry.get("message", entry)

                            if not (msg.get("usage") and msg.get("model")):
                                continue

                            # Timestamp filtering
                            ts = msg.get("timestamp") or entry.get("timestamp")
                            if ts and days > 0:
                                try:
                                    if isinstance(ts, (int, float)):
                                        entry_time = datetime.fromtimestamp(ts / 1000 if ts > 1e12 else ts)
                                    else:
                                        entry_time = datetime.fromisoformat(
                                            str(ts).replace("Z", "+00:00")
                                        ).replace(tzinfo=None)
                                except (ValueError, OSError):
                                    entry_time = datetime.now()
                                if entry_time < threshold:
                                    continue

                            model = msg["model"]
                            u = msg["usage"]
                            cost = u.get("cost", {}).get("total", 0)

                            if model not in model_usage:
                                model_usage[model] = {
                                    "model": model,
                                    "totalTokens": 0,
                                    "inputTokens": 0,
                                    "outputTokens": 0,
                                    "cacheReadTokens": 0,
                                    "cacheWriteTokens": 0,
                                    "totalCost": 0.0,
                                    "requestCount": 0,
                                }

                            mu = model_usage[model]
                            mu["totalTokens"] += u.get("totalTokens", 0)
                            mu["inputTokens"] += u.get("input", 0)
                            mu["outputTokens"] += u.get("output", 0)
                            mu["cacheReadTokens"] += u.get("cacheRead", 0)
                            mu["cacheWriteTokens"] += u.get("cacheWrite", 0)
                            mu["totalCost"] += cost
                            mu["requestCount"] += 1
                            total_entries += 1

                            # Track daily costs
                            if ts:
                                if isinstance(ts, (int, float)):
                                    day = datetime.fromtimestamp(ts / 1000 if ts > 1e12 else ts).strftime("%Y-%m-%d")
                                else:
                                    day = str(ts)[:10]
                                if day not in daily_costs:
                                    daily_costs[day] = {}
                                daily_costs[day][model] = (
                                    daily_costs[day].get(model, 0) + cost
                                )

                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
            except (OSError, IOError):
                continue

    return {
        "models": model_usage,
        "dailyCosts": daily_costs,
        "meta": {
            "agentsDir": str(agents_dir),
            "filesScanned": total_files,
            "entriesParsed": total_entries,
            "range": f"{days}d" if days > 0 else "all time",
            "timestamp": datetime.now().isoformat() + "Z",
        },
    }


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_cost(n: float) -> str:
    if n >= 1:
        return f"${n:.2f}"
    if n >= 0.01:
        return f"${n:.2f}"
    return f"${n:.4f}"


def short_model_name(model: str) -> str:
    name = model.split("/")[-1] if "/" in model else model
    name = name.replace("claude-", "").replace("gpt-", "GPT-")
    # Remove date suffix like -20250514
    import re
    name = re.sub(r"-\d{8}$", "", name)
    return name


def format_text(data: Dict[str, Any]) -> str:
    models = sorted(
        data["models"].values(), key=lambda m: m["totalCost"], reverse=True
    )
    daily = data["dailyCosts"]
    meta = data["meta"]

    grand_cost = sum(m["totalCost"] for m in models)
    grand_tokens = sum(m["totalTokens"] for m in models)
    grand_reqs = sum(m["requestCount"] for m in models)

    lines = []
    lines.append("⚡ OPENCLAW COST REPORT")
    lines.append("=" * 55)
    lines.append(f"  Range: {meta['range']}  |  Files: {meta['filesScanned']}  |  Entries: {meta['entriesParsed']}")
    lines.append("")

    # Grand totals
    lines.append(f"  💰 Total Cost:     {format_cost(grand_cost)}")
    lines.append(f"  🔢 Total Tokens:   {format_tokens(grand_tokens)}")
    lines.append(f"  📡 Total Requests: {grand_reqs:,}")
    lines.append("")

    # Per-model breakdown
    lines.append("  MODEL BREAKDOWN")
    lines.append("  " + "-" * 53)

    for m in models:
        if m["requestCount"] == 0:
            continue
        name = short_model_name(m["model"])
        pct = (m["totalCost"] / grand_cost * 100) if grand_cost > 0 else 0
        bar_len = int(pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)

        lines.append(f"  {name}")
        lines.append(
            f"    {format_cost(m['totalCost']):>10}  {bar}  {pct:.0f}%"
        )
        lines.append(
            f"    {format_tokens(m['totalTokens'])} tokens  •  "
            f"{m['requestCount']:,} reqs  •  "
            f"in:{format_tokens(m['inputTokens'])} out:{format_tokens(m['outputTokens'])} "
            f"cache:{format_tokens(m['cacheReadTokens'])}"
        )
        lines.append("")

    # Daily breakdown (last 7 days max)
    if daily:
        sorted_days = sorted(daily.keys(), reverse=True)[:7]
        sorted_days.reverse()

        lines.append("  DAILY SPEND")
        lines.append("  " + "-" * 53)

        max_day_cost = max(sum(v.values()) for v in daily.values()) if daily else 1
        for day in sorted_days:
            day_total = sum(daily[day].values())
            bar_len = int((day_total / max_day_cost) * 25) if max_day_cost > 0 else 0
            bar = "█" * bar_len

            lines.append(f"  {day}  {format_cost(day_total):>10}  {bar}")

        lines.append("")

    lines.append(f"  Generated: {meta['timestamp']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Track OpenClaw token usage and costs"
    )
    parser.add_argument(
        "--days", type=int, default=0,
        help="Days to look back (0 = all time, default: 0)"
    )
    parser.add_argument(
        "--since", type=str, default=None,
        help="ISO date to filter from (e.g. 2026-02-01)"
    )
    parser.add_argument(
        "--format", choices=["json", "text"], default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--agents-dir", type=str, default=None,
        help="Path to OpenClaw agents directory"
    )

    args = parser.parse_args()

    agents_dir = Path(args.agents_dir) if args.agents_dir else find_agents_dir()
    data = parse_sessions(agents_dir, days=args.days, since=args.since)

    if args.format == "json":
        # Convert for JSON serialization
        output = {
            "models": list(data["models"].values()),
            "daily": [
                {"date": d, "cost": sum(v.values()), "byModel": v}
                for d, v in sorted(data["dailyCosts"].items())
            ],
            "grandTotal": {
                "totalCost": sum(m["totalCost"] for m in data["models"].values()),
                "totalTokens": sum(m["totalTokens"] for m in data["models"].values()),
                "totalRequests": sum(m["requestCount"] for m in data["models"].values()),
            },
            "meta": data["meta"],
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text(data))


if __name__ == "__main__":
    main()
