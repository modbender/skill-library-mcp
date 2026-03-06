#!/usr/bin/env python3
"""
Agent Metrics - Observability for AI Agents
v1.0.3

Track calls, errors, latency, and resource usage (with psutil)
"""

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

try:
    import psutil
except ImportError:
    print("ERROR: psutil library not installed", file=sys.stderr)
    print("Run: pip install psutil", file=sys.stderr)
    sys.exit(1)

METRICS_FILE = "agent_metrics.json"


def load_metrics():
    """Load metrics from file"""
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    return {
        "start_time": time.time(),
        "calls": [],
        "errors": [],
        "latency": [],
        "custom": []
    }


def save_metrics(metrics):
    """Save metrics to file"""
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)


def record_call(label):
    """Record an API call"""
    metrics = load_metrics()
    metrics["calls"].append({
        "label": label,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    save_metrics(metrics)
    print(f"[OK] Call recorded: {label}")


def record_error(label, details=""):
    """Record an error with optional stack trace"""
    metrics = load_metrics()
    # Get stack trace if no details provided
    stack_trace = ""
    if not details:
        stack_trace = traceback.format_exc()
    metrics["errors"].append({
        "label": label,
        "details": details or "No details",
        "stack_trace": stack_trace[:2000] if stack_trace else "",  # Limit to 2000 chars
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    save_metrics(metrics)
    print(f"[ERR] Error recorded: {label} - {details}")


def get_resource_usage():
    """Get current resource usage via psutil"""
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "memory_used_mb": mem.used / (1024 * 1024),
            "disk_percent": disk.percent,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


def record_latency(label, value):
    """Record latency in milliseconds"""
    metrics = load_metrics()
    metrics["latency"].append({
        "label": label,
        "value": float(value),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    save_metrics(metrics)
    print(f"⏱ Latency recorded: {label} = {value}ms")


def show_dashboard():
    """Show metrics dashboard"""
    metrics = load_metrics()
    
    total_calls = len(metrics["calls"])
    total_errors = len(metrics["errors"])
    error_rate = (total_errors / total_calls * 100) if total_calls > 0 else 0
    
    latencies = [l["value"] for l in metrics["latency"]]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    uptime = time.time() - metrics["start_time"]
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    
    # Count labels
    label_counts = {}
    for call in metrics["calls"]:
        label = call["label"]
        label_counts[label] = label_counts.get(label, 0) + 1
    
    top_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print("\n" + "=" * 47)
    print("| AGENT METRICS DASHBOARD".center(43) + " |")
    print("=" * 47)
    print(f"| Total Calls:     {total_calls:,}".ljust(46) + " |")
    print(f"| Total Errors:    {total_errors:,}".ljust(46) + " |")
    print(f"| Error Rate:      {error_rate:.2f}%".ljust(46) + " |")
    print(f"| Avg Latency:     {avg_latency:.0f}ms".ljust(46) + " |")
    print(f"| Uptime:          {hours}h {minutes}m".ljust(46) + " |")
    print("=" * 47)
    print("| Top Labels:".ljust(46) + " |")
    for label, count in top_labels:
        pct = (count / total_calls * 100) if total_calls > 0 else 0
        print(f"|   {label[:18]:<18} {count:>5} ({pct:.1f}%)".ljust(46) + " |")
    print("=" * 47 + "\n")


def show_summary():
    """Show metrics summary"""
    metrics = load_metrics()
    
    print("\n--- METRICS SUMMARY ---")
    print(f"Total Calls: {len(metrics['calls'])}")
    print(f"Total Errors: {len(metrics['errors'])}")
    
    if metrics["errors"]:
        print("\nRecent Errors:")
        for err in metrics["errors"][-5:]:
            print(f"  - {err['label']}: {err['details']}")
    
    latencies = [l["value"] for l in metrics["latency"]]
    if latencies:
        print(f"\nLatency Stats:")
        print(f"  Min: {min(latencies):.0f}ms")
        print(f"  Max: {max(latencies):.0f}ms")
        print(f"  Avg: {sum(latencies)/len(latencies):.0f}ms")


def export_metrics(format="json", output="metrics.json"):
    """Export metrics to file"""
    metrics = load_metrics()
    
    if format == "json":
        with open(output, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"[OK] Exported to {output}")
    elif format == "csv":
        import csv
        with open(output, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["type", "label", "value", "details", "timestamp"])
            
            for call in metrics["calls"]:
                writer.writerow(["call", call["label"], "", "", call["timestamp"]])
            
            for err in metrics["errors"]:
                writer.writerow(["error", err["label"], "", err["details"], err["timestamp"]])
            
            for lat in metrics["latency"]:
                writer.writerow(["latency", lat["label"], lat["value"], "", lat["timestamp"]])
        
        print(f"[OK] Exported to {output}")


def show_resources():
    """Show current resource usage"""
    usage = get_resource_usage()
    if "error" in usage:
        print(f"[ERR] Resource monitoring error: {usage['error']}")
        return
    
    print("\n--- RESOURCE USAGE ---")
    print(f"CPU:        {usage['cpu_percent']:.1f}%")
    print(f"Memory:     {usage['memory_percent']:.1f}% ({usage['memory_used_mb']:.0f} MB used)")
    print(f"Disk:       {usage['disk_percent']:.1f}%")
    print(f"Timestamp:  {usage['timestamp']}")


def reset_metrics():
    """Reset all metrics"""
    metrics = {
        "start_time": time.time(),
        "calls": [],
        "errors": [],
        "latency": [],
        "custom": []
    }
    save_metrics(metrics)
    print("[OK] Metrics reset")


def cmd_record(args):
    if args.type == "call":
        record_call(args.label)
    elif args.type == "error":
        record_error(args.label, args.details or "")
    elif args.type == "latency":
        if not args.value:
            print("ERROR: --value required for latency", file=sys.stderr)
            sys.exit(1)
        record_latency(args.label, args.value)
    else:
        print(f"Unknown type: {args.type}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Agent Metrics - Observability for AI Agents")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # record
    rec_parser = subparsers.add_parser("record", help="Record a metric")
    rec_parser.add_argument("--type", required=True, choices=["call", "error", "latency", "custom"], help="Metric type")
    rec_parser.add_argument("--label", required=True, help="Label/name")
    rec_parser.add_argument("--value", help="Value (for latency)")
    rec_parser.add_argument("--details", help="Details (for errors)")
    
    # dashboard
    subparsers.add_parser("dashboard", help="Show dashboard")
    
    # summary
    subparsers.add_parser("summary", help="Show summary")
    
    # export
    exp_parser = subparsers.add_parser("export", help="Export metrics")
    exp_parser.add_argument("--format", default="json", choices=["json", "csv"], help="Export format")
    exp_parser.add_argument("--output", default="metrics.json", help="Output file")
    
    # resources
    subparsers.add_parser("resources", help="Show resource usage (CPU, memory, disk)")
    
    # reset
    subparsers.add_parser("reset", help="Reset all metrics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    handlers = {
        "record": lambda: cmd_record(args),
        "dashboard": show_dashboard,
        "summary": show_summary,
        "export": lambda: export_metrics(args.format, args.output),
        "resources": show_resources,
        "reset": reset_metrics
    }
    
    handlers[args.command]()


if __name__ == "__main__":
    main()


