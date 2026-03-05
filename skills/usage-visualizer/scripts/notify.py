#!/usr/bin/env python3
"""
Notification output for LLM Cost Monitor
Outputs formatted messages for different channels
OpenClaw's message tool handles actual delivery
"""
import argparse
import json
import sys


def format_for_channel(data: dict, channel: str) -> str:
    """Format notification data for specific channel"""
    
    # Build common message
    total_cost = data.get("total_cost", 0)
    period = data.get("period", "today")
    tokens = data.get("tokens", {})
    cache_savings = data.get("cache_savings", {})
    
    if channel == "feishu":
        # Feishu: use text with basic formatting
        lines = [
            f"💰 LLM 成本报告 - {period}",
            f"总费用: ${total_cost:.2f}",
            f"Token: {tokens.get('total', 0):,}",
        ]
        if cache_savings.get("total_savings", 0) > 0:
            lines.append(f"💡 Cache节省: ${cache_savings['total_savings']:.2f}")
        return "\n".join(lines)
    
    elif channel == "telegram":
        # Telegram: Markdown format
        lines = [
            f"💰 *LLM Cost Report - {period}*",
            f"Total: ${total_cost:.2f}",
            f"Tokens: {tokens.get('total', 0):,}",
        ]
        if cache_savings.get("total_savings", 0) > 0:
            lines.append(f"💡 Cache: ${cache_savings['total_savings']:.2f}")
        return "\n".join(lines)
    
    elif channel == "discord":
        # Discord: Basic with emoji
        lines = [
            f"💰 **LLM Cost Report - {period}**",
            f"Total: ${total_cost:.2f}",
            f"Tokens: {tokens.get('total', 0):,}",
        ]
        if cache_savings.get("total_savings", 0) > 0:
            lines.append(f"💡 Cache Savings: ${cache_savings['total_savings']:.2f}")
        return "\n".join(lines)
    
    else:
        # Default: plain text
        return f"LLM Cost Report - {period}: ${total_cost:.2f}"


def main():
    parser = argparse.ArgumentParser(description="Format notification for channel")
    parser.add_argument("--json", help="JSON input from report.py")
    parser.add_argument("--channel", "-c", default="feishu", 
                       choices=["feishu", "telegram", "discord", "console"],
                       help="Target channel")
    parser.add_argument("--period", "-p", default="today", help="Period name")
    
    args = parser.parse_args()
    
    if args.json:
        try:
            data = json.loads(args.json)
        except:
            print("Invalid JSON input", file=sys.stderr)
            sys.exit(1)
    else:
        # Build minimal data from args
        data = {"period": args.period, "total_cost": 0, "tokens": {}, "cache_savings": {}}
    
    output = format_for_channel(data, args.channel)
    print(output)


if __name__ == "__main__":
    main()
