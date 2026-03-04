#!/usr/bin/env python3
"""🐾 AI Usage & Cost Reporter — CLI dashboard.

Usage:
    python report.py                    # full report
    python report.py --days 7           # last 7 days
    python report.py --model claude     # filter by model
    python report.py --task-type coding # filter by task type
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_USAGE_PATH = _HERE / "usage.jsonl"
_PRICING_PATH = _HERE / "pricing.json"


def _load_entries(days: int | None, model: str | None, task_type: str | None) -> list[dict]:
    if not _USAGE_PATH.exists():
        return []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat() if days else None
    entries = []
    for line in _USAGE_PATH.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        if cutoff and e["timestamp"] < cutoff:
            continue
        if model and model.lower() not in e["model"].lower():
            continue
        if task_type and task_type.lower() not in e["taskType"].lower():
            continue
        entries.append(e)
    return entries


def _load_pricing():
    with open(_PRICING_PATH) as f:
        return json.load(f)


def _fmt_cost(c: float) -> str:
    return f"${c:,.4f}" if c < 1 else f"${c:,.2f}"


def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def report_summary(entries: list[dict]):
    total_calls = len(entries)
    total_in = sum(e["tokens"]["input"] for e in entries)
    total_out = sum(e["tokens"]["output"] for e in entries)
    total_cost = sum(e["costEstimate"] for e in entries)
    print("═" * 50)
    print("  🐾 AI USAGE SUMMARY")
    print("═" * 50)
    print(f"  Total calls:    {total_calls:,}")
    print(f"  Input tokens:   {_fmt_tokens(total_in)}")
    print(f"  Output tokens:  {_fmt_tokens(total_out)}")
    print(f"  Total tokens:   {_fmt_tokens(total_in + total_out)}")
    print(f"  Total cost:     {_fmt_cost(total_cost)}")
    print()


def report_by_model(entries: list[dict]):
    agg: dict[str, dict] = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
    for e in entries:
        b = agg[e["model"]]
        b["calls"] += 1
        b["tokens"] += e["tokens"]["total"]
        b["cost"] += e["costEstimate"]
    rows = sorted(agg.items(), key=lambda x: x[1]["cost"], reverse=True)
    print("── By Model ──")
    for name, d in rows:
        print(f"  {name:<24} {d['calls']:>5} calls  {_fmt_tokens(d['tokens']):>8} tok  {_fmt_cost(d['cost']):>10}")
    print()


def report_by_task(entries: list[dict]):
    agg: dict[str, dict] = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
    for e in entries:
        b = agg[e["taskType"]]
        b["calls"] += 1
        b["tokens"] += e["tokens"]["total"]
        b["cost"] += e["costEstimate"]
    rows = sorted(agg.items(), key=lambda x: x[1]["cost"], reverse=True)
    print("── By Task Type ──")
    for name, d in rows:
        print(f"  {name:<24} {d['calls']:>5} calls  {_fmt_tokens(d['tokens']):>8} tok  {_fmt_cost(d['cost']):>10}")
    print()


def report_by_day(entries: list[dict], max_days: int = 10):
    agg: dict[str, dict] = defaultdict(lambda: {"calls": 0, "cost": 0.0})
    for e in entries:
        day = e["timestamp"][:10]
        agg[day]["calls"] += 1
        agg[day]["cost"] += e["costEstimate"]
    rows = sorted(agg.items(), reverse=True)[:max_days]
    print("── By Day (last 10) ──")
    for day, d in rows:
        bar = "█" * max(1, int(d["cost"] * 20 / max(r[1]["cost"] for r in rows))) if rows else ""
        print(f"  {day}  {d['calls']:>5} calls  {_fmt_cost(d['cost']):>10}  {bar}")
    print()


def report_routing(entries: list[dict]):
    """🐾 sniff out wasteful routing"""
    pricing = _load_pricing()
    simple_tasks = set(pricing.get("simple_task_types", []))
    expensive = {"claude-opus-4", "o1", "gpt-5.3"}
    warnings = []

    # Flag expensive models on simple tasks
    for e in entries:
        model_low = e["model"].lower()
        if any(x in model_low for x in expensive) and e["taskType"].lower() in simple_tasks:
            warnings.append(f"  ⚠️  {e['model']} used for simple task '{e['taskType']}' — consider a cheaper model")

    # Flag >25% spend from single source
    total_cost = sum(e["costEstimate"] for e in entries)
    if total_cost > 0:
        by_source: dict[str, float] = defaultdict(float)
        for e in entries:
            by_source[e["source"]] += e["costEstimate"]
        for src, cost in by_source.items():
            pct = cost / total_cost * 100
            if pct > 25:
                warnings.append(f"  📊 Source '{src}' accounts for {pct:.0f}% of spend ({_fmt_cost(cost)})")

    if warnings:
        print("── 🐾 Routing Suggestions ──")
        seen = set()
        for w in warnings:
            if w not in seen:
                seen.add(w)
                print(w)
        print()
    else:
        print("── 🐾 Routing: all good! ──\n")


def main():
    p = argparse.ArgumentParser(description="AI Usage & Cost Report 🐾")
    p.add_argument("--days", type=int, default=None, help="Filter to last N days")
    p.add_argument("--model", type=str, default=None, help="Filter by model name (substring)")
    p.add_argument("--task-type", type=str, default=None, help="Filter by task type (substring)")
    args = p.parse_args()

    entries = _load_entries(args.days, args.model, args.task_type)
    if not entries:
        print("🐾 No usage entries found. Start tracking with tracker.py!")
        return

    report_summary(entries)
    report_by_model(entries)
    report_by_task(entries)
    report_by_day(entries)
    report_routing(entries)


if __name__ == "__main__":
    main()
