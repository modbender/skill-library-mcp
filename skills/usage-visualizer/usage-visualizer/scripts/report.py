#!/usr/bin/env python3
"""
Generate usage and cost reports - text/JSON format with cache discount info
"""
import argparse
import json
import os
import sys
import yaml
from datetime import datetime, timedelta
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from store import UsageStore
from calc_cost import get_pricing


def load_config(config_path: str = "config/config.yaml") -> Dict:
    """Load configuration"""
    paths_to_try = [
        config_path,
        os.path.join(os.path.dirname(os.path.dirname(__file__)), config_path),
        os.path.expanduser("~/.llm-cost-monitor/config.yaml"),
    ]
    for path in paths_to_try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
    return {"providers": {}, "budget": {}, "storage": {}}


def get_date_range(period: str) -> tuple:
    """Get start and end dates for a period"""
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    
    if period == "today":
        return today_str, today_str
    elif period == "yesterday":
        yesterday = today - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")
    elif period == "week":
        week_ago = today - timedelta(days=7)
        return week_ago.strftime("%Y-%m-%d"), today_str
    elif period == "month":
        month_ago = today - timedelta(days=30)
        return month_ago.strftime("%Y-%m-%d"), today_str
    else:
        return today_str, today_str


def fmt_cost(cost: float) -> str:
    if cost >= 1:
        return f"${cost:.2f}"
    return f"${cost:.4f}"


def fmt_tokens(t: int) -> str:
    if t >= 1_000_000:
        return f"{t/1_000_000:.1f}M"
    elif t >= 1_000:
        return f"{t/1_000:.1f}K"
    return str(t)


def calc_cache_savings(tokens_summary: dict) -> dict:
    """Calculate cache savings - how much saved with 90% discount on cache reads"""
    cache_read = tokens_summary.get("cache_read_tokens", 0)
    cache_write = tokens_summary.get("cache_creation_tokens", 0)
    
    if cache_read == 0 and cache_write == 0:
        return {"read_savings": 0, "write_cost": 0, "total_savings": 0}
    
    # Estimate: without cache, would pay full input price
    # With cache read at 90% discount, savings = cache_read * 90% of average input price
    avg_input_price = 3.0 / 1_000_000  # Rough average $3/1M
    read_savings = cache_read * avg_input_price * 0.9
    write_cost = cache_write * avg_input_price * 1.25  # Cache write is 125% of regular
    
    return {
        "read_savings": read_savings,
        "write_cost": write_cost,
        "total_savings": read_savings - write_cost
    }


def print_report(period: str, config: Dict):
    """Print usage report in text format"""
    storage_path = config.get("storage", {}).get("path", "~/.llm-cost-monitor")
    store = UsageStore(storage_path)
    
    start_date, end_date = get_date_range(period)
    
    # Get data
    total_cost = store.get_total_cost(start_date, end_date)
    by_provider = store.get_cost_by_provider(start_date, end_date)
    by_model = store.get_cost_by_model(start_date, end_date)
    tokens_summary = store.get_tokens_summary(start_date, end_date)
    budget_limit = config.get("budget", {}).get("monthly_limit", 0)
    
    # Cache savings
    cache_savings = calc_cache_savings(tokens_summary)
    
    date_label = {"today": "Today", "yesterday": "Yesterday", "week": "This Week", "month": "This Month"}.get(period, period)
    
    print(f"\n💰 LLM Cost Report - {date_label}")
    print("=" * 50)
    print(f"Period: {start_date} to {end_date}")
    print(f"\nTotal Cost: {fmt_cost(total_cost)}")
    print(f"Total Tokens: {fmt_tokens(tokens_summary['total_tokens'])}")
    
    # Token breakdown
    print(f"\n📊 Token Breakdown:")
    print(f"   Input:  {fmt_tokens(tokens_summary['input_tokens'])}")
    print(f"   Output: {fmt_tokens(tokens_summary['output_tokens'])}")
    
    if tokens_summary.get("cache_read_tokens", 0) > 0 or tokens_summary.get("cache_creation_tokens", 0) > 0:
        print(f"   Cache R: {fmt_tokens(tokens_summary.get('cache_read_tokens', 0))}")
        print(f"   Cache W: {fmt_tokens(tokens_summary.get('cache_creation_tokens', 0))}")
        print(f"   💡 Cache Savings: {fmt_cost(cache_savings['total_savings'])}")
    
    # By provider
    if by_provider:
        print(f"\n📊 By Provider:")
        for provider, cost in sorted(by_provider.items(), key=lambda x: x[1], reverse=True):
            pct = (cost / total_cost * 100) if total_cost > 0 else 0
            print(f"  • {provider}: {fmt_cost(cost)} ({pct:.0f}%)")
    
    # By model
    if by_model:
        print(f"\n📈 By Model (Top 10):")
        for model, cost in sorted(by_model.items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = (cost / total_cost * 100) if total_cost > 0 else 0
            print(f"  • {model}: {fmt_cost(cost)} ({pct:.0f}%)")
    
    # Budget
    if budget_limit > 0:
        pct = (total_cost / budget_limit * 100) if budget_limit > 0 else 0
        status = "✅" if pct < 80 else "⚠️" if pct < 100 else "🔴"
        print(f"\n🎯 Budget: {fmt_cost(total_cost)} / {fmt_cost(budget_limit)} ({pct:.0f}%) {status}")
    
    # Unknown models
    unknown = [m for m in by_model.keys() if get_pricing(m) is None]
    if unknown:
        print(f"\n⚠️ Note: Showing real cost from sessions (no local pricing): {', '.join(unknown)}")
    
    print()


def print_json(period: str, config: Dict):
    """Print report as JSON"""
    storage_path = config.get("storage", {}).get("path", "~/.llm-cost-monitor")
    store = UsageStore(storage_path)
    
    start_date, end_date = get_date_range(period)
    
    total_cost = store.get_total_cost(start_date, end_date)
    by_provider = store.get_cost_by_provider(start_date, end_date)
    by_model = store.get_cost_by_model(start_date, end_date)
    tokens_summary = store.get_tokens_summary(start_date, end_date)
    cache_savings = calc_cache_savings(tokens_summary)
    
    output = {
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "total_cost": round(total_cost, 6),
        "tokens": {
            "input": tokens_summary.get("input_tokens", 0),
            "output": tokens_summary.get("output_tokens", 0),
            "cache_read": tokens_summary.get("cache_read_tokens", 0),
            "cache_write": tokens_summary.get("cache_creation_tokens", 0),
            "total": tokens_summary.get("total_tokens", 0)
        },
        "cache_savings": {
            "read_savings": round(cache_savings["read_savings"], 4),
            "write_cost": round(cache_savings["write_cost"], 4),
            "total_savings": round(cache_savings["total_savings"], 4)
        },
        "by_provider": {k: round(v, 4) for k, v in by_provider.items()},
        "by_model": {k: round(v, 4) for k, v in by_model.items()}
    }
    
    budget_limit = config.get("budget", {}).get("monthly_limit", 0)
    if budget_limit > 0:
        output["budget"] = {
            "limit": budget_limit,
            "used": round(total_cost, 4),
            "percentage": round(total_cost / budget_limit * 100, 1)
        }
    
    print(json.dumps(output, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Generate LLM cost reports")
    parser.add_argument("--period", type=str, choices=["today", "yesterday", "week", "month"],
                       default="today", help="Report period")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--text", action="store_true", help="Output as text (default)")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Config file path")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    if args.json:
        print_json(args.period, config)
    else:
        print_report(args.period, config)


if __name__ == "__main__":
    main()
