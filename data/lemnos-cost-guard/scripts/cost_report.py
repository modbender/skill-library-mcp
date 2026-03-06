#!/usr/bin/env python3
"""
cost_report.py — Generate cost summary from daily logs.
Usage: python3 cost_report.py [--days 1] [--budget 5.00] [--format brief|full]
"""
import json, argparse, os, glob
from datetime import datetime, timezone, timedelta
from collections import defaultdict

LOG_DIR = os.path.join(os.path.dirname(__file__), "../../logs")

def load_logs(days=1):
    entries = []
    for i in range(days):
        date_str = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        log_file = os.path.join(LOG_DIR, f"cost-{date_str}.jsonl")
        if os.path.exists(log_file):
            with open(log_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
    return entries

def report(days=1, budget=5.00, fmt="brief"):
    entries = load_logs(days)

    if not entries:
        print(f"No cost data found for last {days} day(s).")
        return

    total_cost = sum(e["cost_usd"] for e in entries)
    total_input = sum(e["input_tokens"] for e in entries)
    total_output = sum(e["output_tokens"] for e in entries)
    avg_ratio = round(total_input / max(total_output, 1), 1)
    budget_pct = (total_cost / budget) * 100

    # Top tasks by cost
    by_task = defaultdict(float)
    for e in entries:
        by_task[e["task"]] += e["cost_usd"]
    top_tasks = sorted(by_task.items(), key=lambda x: x[1], reverse=True)[:5]

    # Alert flags
    over_500k = [e for e in entries if e["input_tokens"] > 500_000]
    bloat_calls = [e for e in entries if e["ratio"] > 50]

    if fmt == "brief":
        status = "🔴 OVER BUDGET" if budget_pct >= 100 else ("⚠️ WARNING" if budget_pct >= 80 else "✅ OK")
        print(f"COST SUMMARY (last {days}d): ${total_cost:.2f} / ${budget:.2f} ({budget_pct:.0f}%) {status}")
        print(f"Tokens: {total_input:,} in / {total_output:,} out | ratio {avg_ratio}:1 | {len(entries)} calls")
        if over_500k:
            print(f"⚠️  {len(over_500k)} call(s) exceeded 500K input tokens")
        if bloat_calls:
            print(f"⚠️  {len(bloat_calls)} call(s) had >50:1 input:output ratio")
    else:
        print(f"\n{'='*50}")
        print(f"COST REPORT — Last {days} Day(s)")
        print(f"{'='*50}")
        print(f"Total Cost:    ${total_cost:.4f}")
        print(f"Daily Budget:  ${budget:.2f}")
        print(f"Budget Used:   {budget_pct:.1f}% {'🔴 OVER' if budget_pct >= 100 else '⚠️ WARNING' if budget_pct >= 80 else '✅ OK'}")
        print(f"Total Calls:   {len(entries)}")
        print(f"Input Tokens:  {total_input:,}")
        print(f"Output Tokens: {total_output:,}")
        print(f"Avg I/O Ratio: {avg_ratio}:1")
        print(f"\nTop Tasks by Cost:")
        for task, cost in top_tasks:
            print(f"  ${cost:.4f}  {task}")
        if over_500k:
            print(f"\n🔴 Large Calls (>500K input):")
            for e in over_500k:
                print(f"  {e['ts'][:16]} | {e['task']} | {e['input_tokens']:,} tokens | ${e['cost_usd']:.4f}")
        if bloat_calls:
            print(f"\n⚠️  Context Bloat Calls (>50:1 ratio):")
            for e in bloat_calls:
                print(f"  {e['ts'][:16]} | {e['task']} | ratio {e['ratio']}:1")
        print(f"\nModel Routing Suggestions:")
        high_ratio = [e for e in entries if e["ratio"] > 100 and e["cost_usd"] < 0.01]
        if high_ratio:
            print(f"  {len(high_ratio)} simple task(s) could use Haiku (~75% cheaper)")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--budget", type=float, default=5.00)
    parser.add_argument("--format", choices=["brief", "full"], default="brief")
    args = parser.parse_args()
    report(args.days, args.budget, args.format)
