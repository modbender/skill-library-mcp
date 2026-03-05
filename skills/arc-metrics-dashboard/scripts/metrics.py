#!/usr/bin/env python3
"""Metrics Dashboard for autonomous agents.

Track operational metrics: counters, timers, events, gauges.
Generate text dashboards and export data.
"""

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

METRICS_DIR = Path.home() / ".openclaw" / "metrics"


def ensure_dir():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)


def get_today_file():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return METRICS_DIR / f"metrics-{today}.json"


def load_entries(filepath):
    if not filepath.exists():
        return []
    with open(filepath) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_entries(filepath, entries):
    with open(filepath, "w") as f:
        json.dump(entries, f, indent=2)


def record(name, metric_type, value=None, tags=None, message=None):
    """Record a metric entry."""
    ensure_dir()
    filepath = get_today_file()
    entries = load_entries(filepath)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "type": metric_type,
    }
    if value is not None:
        entry["value"] = value
    if tags:
        entry["tags"] = tags
    if message:
        entry["message"] = message

    entries.append(entry)
    save_entries(filepath, entries)
    return entry


def load_all_entries(period="day"):
    """Load entries for a time period."""
    ensure_dir()
    now = datetime.now(timezone.utc)

    if period == "day":
        files = [get_today_file()]
    elif period == "week":
        files = []
        for i in range(7):
            d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            f = METRICS_DIR / f"metrics-{d}.json"
            if f.exists():
                files.append(f)
    else:
        files = sorted(METRICS_DIR.glob("metrics-*.json"))

    all_entries = []
    for f in files:
        all_entries.extend(load_entries(f))
    return all_entries


def dashboard():
    """Generate a text-based dashboard."""
    entries = load_all_entries("day")
    all_entries = load_all_entries("all")

    # Basic stats
    total_today = len(entries)
    total_all = len(all_entries)

    # First metric timestamp (uptime approximation)
    if all_entries:
        first_ts = all_entries[0].get("timestamp", "")
        try:
            first_dt = datetime.fromisoformat(first_ts.replace("+00:00", "+00:00"))
            uptime = datetime.now(timezone.utc) - first_dt
            uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
        except:
            uptime_str = "unknown"
    else:
        uptime_str = "no data"

    # Count by metric name
    by_name = {}
    for e in entries:
        name = e.get("name", "unknown")
        by_name[name] = by_name.get(name, 0) + 1

    # Errors
    errors = [e for e in entries if e.get("type") == "error"]
    error_rate = (len(errors) / total_today * 100) if total_today > 0 else 0

    # Timers (average duration)
    timers = {}
    for e in entries:
        if e.get("type") == "timer":
            name = e.get("name", "unknown")
            val = e.get("value", 0)
            if name not in timers:
                timers[name] = []
            timers[name].append(val)

    # Counters (sum)
    counters = {}
    for e in entries:
        if e.get("type") == "counter":
            name = e.get("name", "unknown")
            val = e.get("value", 1)
            counters[name] = counters.get(name, 0) + val

    # Gauges (latest value)
    gauges = {}
    for e in entries:
        if e.get("type") == "gauge":
            name = e.get("name", "unknown")
            gauges[name] = e.get("value", 0)

    # Print dashboard
    print("=" * 50)
    print("  AGENT METRICS DASHBOARD")
    print("=" * 50)
    print(f"  Uptime (est):    {uptime_str}")
    print(f"  Events today:    {total_today}")
    print(f"  Events total:    {total_all}")
    print(f"  Error rate:      {error_rate:.1f}%")
    print()

    if counters:
        print("  COUNTERS")
        print("  " + "-" * 40)
        for name, val in sorted(counters.items(), key=lambda x: -x[1]):
            print(f"  {name:30s} {val:>8}")
        print()

    if gauges:
        print("  GAUGES")
        print("  " + "-" * 40)
        for name, val in sorted(gauges.items()):
            print(f"  {name:30s} {val:>8}")
        print()

    if timers:
        print("  TIMERS (avg)")
        print("  " + "-" * 40)
        for name, vals in sorted(timers.items()):
            avg = sum(vals) / len(vals)
            print(f"  {name:30s} {avg:>7.2f}s ({len(vals)} samples)")
        print()

    if by_name:
        print("  TOP METRICS")
        print("  " + "-" * 40)
        for name, count in sorted(by_name.items(), key=lambda x: -x[1])[:10]:
            print(f"  {name:30s} {count:>8} events")
        print()

    if errors:
        print(f"  RECENT ERRORS ({len(errors)} today)")
        print("  " + "-" * 40)
        for e in errors[-5:]:
            ts = e.get("timestamp", "?")[:19]
            msg = e.get("message", e.get("name", "?"))[:50]
            print(f"  {ts} | {msg}")


def view_entries(name=None, period="day"):
    """View metric entries."""
    entries = load_all_entries(period)

    if name:
        entries = [e for e in entries if e.get("name") == name]

    for e in entries:
        ts = e.get("timestamp", "?")[:19]
        n = e.get("name", "?")
        t = e.get("type", "?")
        v = e.get("value", "")
        tags = json.dumps(e.get("tags", {})) if e.get("tags") else ""
        msg = e.get("message", "")
        detail = str(v) if v != "" else msg
        if tags:
            detail += f" {tags}"
        print(f"  {ts} | {t:8s} | {n:25s} | {detail[:60]}")


def export_metrics(fmt="json", period="all"):
    """Export metrics."""
    entries = load_all_entries(period)

    if fmt == "json":
        print(json.dumps(entries, indent=2))
    elif fmt == "csv":
        if not entries:
            return
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "name", "type", "value", "tags", "message"])
        for e in entries:
            writer.writerow([
                e.get("timestamp", ""),
                e.get("name", ""),
                e.get("type", ""),
                e.get("value", ""),
                json.dumps(e.get("tags", {})),
                e.get("message", ""),
            ])
        print(output.getvalue())


def main():
    parser = argparse.ArgumentParser(description="Agent Metrics Dashboard")
    sub = parser.add_subparsers(dest="command")

    # Record
    p_rec = sub.add_parser("record", help="Record a metric")
    p_rec.add_argument("--name", required=True)
    p_rec.add_argument("--value", type=float, default=1)
    p_rec.add_argument("--tags", default=None)

    # Timer
    p_timer = sub.add_parser("timer", help="Record a duration")
    p_timer.add_argument("--name", required=True)
    p_timer.add_argument("--seconds", type=float, required=True)
    p_timer.add_argument("--tags", default=None)

    # Counter
    p_count = sub.add_parser("counter", help="Increment a counter")
    p_count.add_argument("--name", required=True)
    p_count.add_argument("--increment", type=float, default=1)

    # Error
    p_err = sub.add_parser("error", help="Record an error")
    p_err.add_argument("--name", required=True)
    p_err.add_argument("--message", default="")

    # Gauge
    p_gauge = sub.add_parser("gauge", help="Set a gauge value")
    p_gauge.add_argument("--name", required=True)
    p_gauge.add_argument("--value", type=float, required=True)

    # Dashboard
    sub.add_parser("dashboard", help="Show metrics dashboard")

    # View
    p_view = sub.add_parser("view", help="View metrics")
    p_view.add_argument("--name", default=None)
    p_view.add_argument("--period", choices=["day", "week", "all"], default="day")

    # Export
    p_exp = sub.add_parser("export", help="Export metrics")
    p_exp.add_argument("--format", choices=["json", "csv"], default="json")
    p_exp.add_argument("--period", choices=["day", "week", "all"], default="all")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "record":
        tags = json.loads(args.tags) if args.tags else None
        entry = record(args.name, "event", args.value, tags)
        print(f"Recorded: {entry['name']} = {entry.get('value', 1)}")

    elif args.command == "timer":
        tags = json.loads(args.tags) if args.tags else None
        entry = record(args.name, "timer", args.seconds, tags)
        print(f"Timer: {entry['name']} = {args.seconds}s")

    elif args.command == "counter":
        entry = record(args.name, "counter", args.increment)
        print(f"Counter: {entry['name']} += {args.increment}")

    elif args.command == "error":
        entry = record(args.name, "error", message=args.message)
        print(f"Error: {entry['name']} — {args.message}")

    elif args.command == "gauge":
        entry = record(args.name, "gauge", args.value)
        print(f"Gauge: {entry['name']} = {args.value}")

    elif args.command == "dashboard":
        dashboard()

    elif args.command == "view":
        view_entries(name=args.name, period=args.period)

    elif args.command == "export":
        export_metrics(fmt=args.format, period=args.period)


if __name__ == "__main__":
    main()
