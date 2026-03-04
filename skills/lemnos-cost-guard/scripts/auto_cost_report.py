#!/usr/bin/env python3
"""
auto_cost_report.py — Automatic cost reporting from OpenClaw session files.
NO MANUAL LOGGING REQUIRED. Reads directly from OpenClaw's session JSONL files.

Usage:
  python3 auto_cost_report.py                   # Today's running total (brief)
  python3 auto_cost_report.py --date 2026-02-24 # Specific date
  python3 auto_cost_report.py --days 7          # Last 7 days
  python3 auto_cost_report.py --format full     # Full breakdown
  python3 auto_cost_report.py --budget 5.00     # Check against budget

How it works:
  OpenClaw writes message.usage.cost.total to session JSONL files after every API call.
  This script reads those files, filters by timestamp, and aggregates costs.
  No manual track_cost.py calls needed.
"""

import json
import os
import argparse
from datetime import datetime, timezone, timedelta
from collections import defaultdict

SESSION_DIR = "/root/.openclaw/agents/main/sessions"

BUDGET_DEFAULT = 5.00


def get_date_strings(days=1, date=None):
    """Return list of YYYY-MM-DD strings to include."""
    if date:
        return [date]
    today = datetime.now(timezone.utc)
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]


def load_usage(date_strings):
    """Read all session files and return usage entries matching the given dates."""
    date_set = set(date_strings)
    entries = []

    if not os.path.exists(SESSION_DIR):
        return entries

    for fname in os.listdir(SESSION_DIR):
        if not fname.endswith(".jsonl"):
            continue
        fpath = os.path.join(SESSION_DIR, fname)
        session_id = fname.replace(".jsonl", "")

        try:
            with open(fpath) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        ts = obj.get("timestamp", "")
                        if not ts:
                            ts = obj.get("message", {}).get("timestamp", "")
                        if not ts or ts[:10] not in date_set:
                            continue
                        usage = obj.get("message", {}).get("usage", {})
                        if usage and "cost" in usage:
                            entries.append({
                                "session_id": session_id[:8],
                                "timestamp": ts,
                                "date": ts[:10],
                                "input": usage.get("input", 0),
                                "output": usage.get("output", 0),
                                "cache_read": usage.get("cacheRead", 0),
                                "cache_write": usage.get("cacheWrite", 0),
                                "cost": usage["cost"].get("total", 0),
                                "model": obj.get("data", {}).get("modelId", "unknown"),
                            })
                    except (json.JSONDecodeError, KeyError):
                        continue
        except (IOError, OSError):
            continue

    return entries


def report(days=1, date=None, budget=BUDGET_DEFAULT, fmt="brief"):
    date_strings = get_date_strings(days=days, date=date)
    entries = load_usage(date_strings)

    if not entries:
        label = date if date else f"last {days} day(s)"
        print(f"No cost data found for {label}.")
        print("  (Check that sessions exist at: " + SESSION_DIR + ")")
        return

    total_cost = sum(e["cost"] for e in entries)
    total_input = sum(e["input"] for e in entries)
    total_output = sum(e["output"] for e in entries)
    total_cache_read = sum(e["cache_read"] for e in entries)
    total_cache_write = sum(e["cache_write"] for e in entries)
    total_tokens = total_input + total_output
    calls = len(entries)
    budget_pct = (total_cost / budget) * 100 if budget else 0

    # Budget status
    if budget_pct >= 100:
        status = "🔴 OVER BUDGET"
    elif budget_pct >= 80:
        status = "⚠️  WARNING"
    else:
        status = "✅ OK"

    now_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
    label = date if date else (f"today {now_utc}" if days == 1 else f"last {days} days")

    if fmt == "brief":
        print(f"💰 COST ({label}): ${total_cost:.2f} / ${budget:.2f} ({budget_pct:.0f}%) {status}")
        print(f"   {calls} calls | {total_input:,} in + {total_output:,} out + {total_cache_read:,} cached")
    else:
        print(f"\n{'='*55}")
        print(f"COST REPORT — {label}")
        print(f"{'='*55}")
        print(f"Total Cost:        ${total_cost:.4f} / ${budget:.2f} ({budget_pct:.0f}%) {status}")
        print(f"API Calls:         {calls}")
        print(f"Input Tokens:      {total_input:,}")
        print(f"Output Tokens:     {total_output:,}")
        print(f"Cache Reads:       {total_cache_read:,}")
        print(f"Cache Writes:      {total_cache_write:,}")
        print(f"Total Tokens:      {total_tokens:,}")

        # By date
        by_date = defaultdict(float)
        for e in entries:
            by_date[e["date"]] += e["cost"]
        if len(by_date) > 1:
            print(f"\nBy Date:")
            for d in sorted(by_date):
                print(f"  {d}: ${by_date[d]:.4f}")

        # By model
        by_model = defaultdict(float)
        for e in entries:
            by_model[e["model"]] += e["cost"]
        print(f"\nBy Model:")
        for m, c in sorted(by_model.items(), key=lambda x: -x[1]):
            print(f"  {m}: ${c:.4f}")

        # By session
        by_session = defaultdict(float)
        for e in entries:
            by_session[e["session_id"]] += e["cost"]
        print(f"\nBy Session:")
        for s, c in sorted(by_session.items(), key=lambda x: -x[1]):
            print(f"  {s}...: ${c:.4f}")

        # Alerts
        print()
        heavy = [e for e in entries if e["output"] > 5000]
        if heavy:
            print(f"⚠️  {len(heavy)} call(s) with >5K output tokens (context bloat risk)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto cost report from OpenClaw session files")
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--date", type=str, help="Specific date YYYY-MM-DD")
    parser.add_argument("--budget", type=float, default=BUDGET_DEFAULT)
    parser.add_argument("--format", choices=["brief", "full"], default="brief")
    args = parser.parse_args()

    report(days=args.days, date=args.date, budget=args.budget, fmt=args.format)
