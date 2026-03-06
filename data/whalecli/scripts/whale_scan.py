#!/usr/bin/env python3
"""
WhaleWatch CLI agent wrapper.

Quick scan/stream interface for OpenClaw agents.
Requires: uv pip install whalecli

Usage:
    uv run python scripts/whale_scan.py scan --chain ETH --hours 4
    uv run python scripts/whale_scan.py stream --chain ETH --interval 60
    uv run python scripts/whale_scan.py check --chain ETH  # quick bullish/bearish signal
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys


def run_whalecli(*args: str, timeout: int = 30) -> dict:
    """Run whalecli with given args, return parsed JSON output."""
    cmd = ["whalecli", *args, "--format", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    if result.returncode == 2:
        try:
            error = json.loads(result.stderr)
            print(f"API error: {error.get('message', result.stderr)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"API error: {result.stderr}", file=sys.stderr)
        sys.exit(2)

    if result.returncode == 3:
        print(f"Network error: {result.stderr}", file=sys.stderr)
        sys.exit(3)

    if not result.stdout.strip():
        return {"wallets": [], "alerts_triggered": 0}

    return json.loads(result.stdout)


def cmd_scan(args: argparse.Namespace) -> None:
    """Run a whale scan and print results."""
    scan_args = ["scan", "--chain", args.chain, "--hours", str(args.hours)]
    if args.threshold:
        scan_args.extend(["--threshold", str(args.threshold)])

    data = run_whalecli(*scan_args)
    print(json.dumps(data, indent=2))


def cmd_check(args: argparse.Namespace) -> None:
    """Quick bullish/bearish signal check."""
    data = run_whalecli("scan", "--chain", args.chain, "--hours", str(args.hours))

    summary = data.get("summary", {})
    acc = summary.get("accumulating", 0)
    dist = summary.get("distributing", 0)
    avg_score = summary.get("avg_score", 0)

    if acc > dist and avg_score >= 60:
        signal = "BULLISH"
        emoji = "🟢"
    elif dist > acc and avg_score >= 60:
        signal = "BEARISH"
        emoji = "🔴"
    else:
        signal = "NEUTRAL"
        emoji = "⚪"

    result = {
        "signal": signal,
        "accumulating": acc,
        "distributing": dist,
        "avg_score": avg_score,
        "chain": args.chain,
        "hours": args.hours,
    }

    print(f"{emoji} Whale signal: {signal} ({acc} accumulating, {dist} distributing, avg score {avg_score})")
    print(json.dumps(result))


def cmd_stream(args: argparse.Namespace) -> None:
    """Stream whale alerts (JSONL)."""
    cmd = [
        "whalecli", "stream",
        "--chain", args.chain,
        "--interval", str(args.interval),
    ]
    if args.threshold:
        cmd.extend(["--threshold", str(args.threshold)])

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
        for line in proc.stdout:  # type: ignore[union-attr]
            line = line.strip()
            if line:
                print(line)
    except KeyboardInterrupt:
        print("\nStream stopped.", file=sys.stderr)
        if proc:
            proc.terminate()


def main() -> None:
    parser = argparse.ArgumentParser(description="WhaleWatch agent wrapper")
    sub = parser.add_subparsers(dest="command", required=True)

    # scan
    p_scan = sub.add_parser("scan", help="Run whale scan")
    p_scan.add_argument("--chain", default="ETH", choices=["ETH", "BTC", "HL", "ALL"])
    p_scan.add_argument("--hours", type=int, default=24)
    p_scan.add_argument("--threshold", type=int, default=None)
    p_scan.set_defaults(func=cmd_scan)

    # check (quick signal)
    p_check = sub.add_parser("check", help="Quick bullish/bearish signal")
    p_check.add_argument("--chain", default="ETH", choices=["ETH", "BTC", "HL", "ALL"])
    p_check.add_argument("--hours", type=int, default=4)
    p_check.set_defaults(func=cmd_check)

    # stream
    p_stream = sub.add_parser("stream", help="Stream whale alerts")
    p_stream.add_argument("--chain", default="ETH", choices=["ETH", "BTC", "HL", "ALL"])
    p_stream.add_argument("--interval", type=int, default=60)
    p_stream.add_argument("--threshold", type=int, default=None)
    p_stream.set_defaults(func=cmd_stream)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
