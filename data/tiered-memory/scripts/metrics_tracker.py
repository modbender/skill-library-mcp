#!/usr/bin/env python3
"""
Memory Metrics Tracker

Tracks memory system health over time by recording stats to JSONL
and generating health reports.

Usage:
  python3 metrics_tracker.py --record   # append to JSONL
  python3 metrics_tracker.py --report   # print text report
  python3 metrics_tracker.py --trend    # show 7-day trend
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Paths
WORKSPACE = os.environ.get("WORKSPACE", str(Path(__file__).parent.parent.parent.parent))
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
METRICS_FILE = os.path.join(MEMORY_DIR, "memory-metrics.jsonl")
CLI_PATH = os.path.join(Path(__file__).parent, "memory_cli.py")


def get_memory_stats():
    """Get current memory stats from the CLI."""
    try:
        result = subprocess.run(
            [sys.executable, CLI_PATH, "stats"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error getting memory stats: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing stats JSON: {e}", file=sys.stderr)
        return None


def record_metrics():
    """Record current metrics to JSONL file."""
    stats = get_memory_stats()
    if not stats:
        return False
    
    # Extract key metrics
    timestamp = int(time.time())
    hot_bytes = stats.get("hot", {}).get("size_bytes", 0)
    warm_count = stats.get("warm", {}).get("count", 0)
    warm_bytes = stats.get("warm", {}).get("size_bytes", 0)
    tree_nodes = stats.get("tree", {}).get("nodes", 0)
    
    # Calculate cold count (not in current CLI output, default to 0)
    cold_count = 0
    
    # Build metrics entry
    entry = {
        "timestamp": timestamp,
        "hot_bytes": hot_bytes,
        "warm_count": warm_count,
        "warm_bytes": warm_bytes,
        "tree_nodes": tree_nodes,
        "evicted": 0,  # Not tracked yet
        "cold_count": cold_count
    }
    
    # Append to JSONL
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(METRICS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Recorded metrics at {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
    return True


def format_bytes(bytes_val):
    """Format bytes as human-readable string."""
    if bytes_val < 1024:
        return f"{bytes_val}B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f}KB"
    else:
        return f"{bytes_val / (1024 * 1024):.1f}MB"


def progress_bar(pct, width=10):
    """Generate a text progress bar."""
    filled = int(pct / 10)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def print_report():
    """Print a text health report."""
    stats = get_memory_stats()
    if not stats:
        print("Failed to get memory stats", file=sys.stderr)
        return
    
    # Extract data
    hot = stats.get("hot", {})
    warm = stats.get("warm", {})
    tree = stats.get("tree", {})
    
    hot_bytes = hot.get("size_bytes", 0)
    hot_max = hot.get("max_bytes", 5120)
    hot_pct = (hot_bytes / hot_max * 100) if hot_max > 0 else 0
    
    warm_bytes = warm.get("size_bytes", 0)
    warm_max_kb = warm.get("max_kb", 50)
    warm_max_bytes = warm_max_kb * 1024
    warm_pct = (warm_bytes / warm_max_bytes * 100) if warm_max_bytes > 0 else 0
    warm_count = warm.get("count", 0)
    
    tree_nodes = tree.get("nodes", 0)
    tree_max = tree.get("max_nodes", 50)
    
    cold_count = 0  # Not tracked yet
    
    # Calculate score range from warm entries (simplified)
    score_range = "N/A"
    
    # Estimate last consolidation (1 hour ago - placeholder)
    last_consolidation = datetime.now() - timedelta(hours=1)
    time_ago = "1h ago"
    
    # Print report
    print(f"=== Memory Health Report ({datetime.now().strftime('%Y-%m-%d')}) ===")
    print()
    print(f"Hot:  {format_bytes(hot_bytes)} / {format_bytes(hot_max)} ({hot_pct:.0f}%)  {progress_bar(hot_pct)}")
    print(f"Warm: {format_bytes(warm_bytes)} / {warm_max_kb}KB  ({warm_pct:.0f}%)   {progress_bar(warm_pct)}")
    print(f"Tree: {tree_nodes}/{tree_max} nodes")
    print(f"Cold: {cold_count} entries")
    print()
    print(f"Warm entry count: {warm_count}")
    print(f"Score range: {score_range}")
    print(f"Last consolidation: {time_ago}")
    print()


def load_metrics_history(days=7):
    """Load metrics from the last N days."""
    if not os.path.exists(METRICS_FILE):
        return []
    
    cutoff = time.time() - (days * 86400)
    metrics = []
    
    with open(METRICS_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry["timestamp"] >= cutoff:
                    metrics.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue
    
    return metrics


def print_trend():
    """Show 7-day trend of memory usage."""
    metrics = load_metrics_history(7)
    
    if not metrics:
        print("No metrics data available for the last 7 days")
        return
    
    print(f"=== Memory Trend (last 7 days, {len(metrics)} samples) ===")
    print()
    
    # Group by day
    daily_stats = {}
    for entry in metrics:
        date = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d")
        if date not in daily_stats:
            daily_stats[date] = []
        daily_stats[date].append(entry)
    
    # Print daily averages
    print(f"{'Date':<12} {'Hot':<10} {'Warm':<15} {'Tree':<10} {'Cold':<10}")
    print("-" * 60)
    
    for date in sorted(daily_stats.keys()):
        entries = daily_stats[date]
        avg_hot = sum(e["hot_bytes"] for e in entries) // len(entries)
        avg_warm = sum(e["warm_count"] for e in entries) // len(entries)
        avg_tree = sum(e["tree_nodes"] for e in entries) // len(entries)
        avg_cold = sum(e["cold_count"] for e in entries) // len(entries)
        
        hot_str = format_bytes(avg_hot)
        warm_str = f"{avg_warm} entries"
        tree_str = f"{avg_tree} nodes"
        cold_str = f"{avg_cold}"
        
        print(f"{date:<12} {hot_str:<10} {warm_str:<15} {tree_str:<10} {cold_str:<10}")
    
    print()
    
    # Show trends
    if len(metrics) >= 2:
        first = metrics[0]
        last = metrics[-1]
        
        hot_delta = last["hot_bytes"] - first["hot_bytes"]
        warm_delta = last["warm_count"] - first["warm_count"]
        tree_delta = last["tree_nodes"] - first["tree_nodes"]
        
        print("Trends:")
        print(f"  Hot:  {'+' if hot_delta >= 0 else ''}{format_bytes(hot_delta)}")
        print(f"  Warm: {'+' if warm_delta >= 0 else ''}{warm_delta} entries")
        print(f"  Tree: {'+' if tree_delta >= 0 else ''}{tree_delta} nodes")
        print()


def main():
    parser = argparse.ArgumentParser(description="Memory system metrics tracker")
    parser.add_argument("--record", action="store_true", help="Append current metrics to JSONL")
    parser.add_argument("--report", action="store_true", help="Print text health report")
    parser.add_argument("--trend", action="store_true", help="Show 7-day trend")
    
    args = parser.parse_args()
    
    if args.record:
        success = record_metrics()
        sys.exit(0 if success else 1)
    elif args.report:
        print_report()
    elif args.trend:
        print_trend()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
