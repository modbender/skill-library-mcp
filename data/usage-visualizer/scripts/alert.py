#!/usr/bin/env python3
"""
Budget alerts for LLM Cost Monitor
"""
import argparse
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from store import UsageStore


def check_budget(
    store: UsageStore,
    budget_usd: float,
    period: str = "today",
    provider: str = None,
    mode: str = "exit"  # "exit" (exit code 2 on breach) or "warn" (just warn)
) -> dict:
    """
    Check if usage exceeds budget
    
    Args:
        store: UsageStore instance
        budget_usd: Budget in USD
        period: "today", "yesterday", "week", "month"
        provider: Optional provider filter
        mode: "exit" or "warn"
    
    Returns:
        dict with keys: exceeded (bool), cost (float), budget (float), message (str)
    """
    today = datetime.now()
    
    if period == "today":
        start_date = end_date = today.strftime("%Y-%m-%d")
        period_name = "today"
    elif period == "yesterday":
        yesterday = today - timedelta(days=1)
        start_date = end_date = yesterday.strftime("%Y-%m-%d")
        period_name = "yesterday"
    elif period == "week":
        start_date = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        period_name = "last 7 days"
    elif period == "month":
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        period_name = "this month"
    else:
        raise ValueError(f"Unknown period: {period}")
    
    # Get cost
    cost = store.get_total_cost(start_date, end_date, provider)
    
    # Check if exceeded
    exceeded = cost > budget_usd
    
    # Format message
    provider_str = f" ({provider})" if provider else ""
    
    if exceeded:
        pct_over = ((cost - budget_usd) / budget_usd) * 100
        message = f"⚠️ ALERT: {period_name}{provider_str} cost ${cost:.2f} exceeded budget ${budget_usd:.2f} by {pct_over:.1f}%"
    else:
        pct_left = ((budget_usd - cost) / budget_usd) * 100
        message = f"✅ {period_name}{provider_str} cost ${cost:.2f} is within budget ${budget_usd:.2f} ({pct_left:.1f}% remaining)"
    
    return {
        "exceeded": exceeded,
        "cost": cost,
        "budget": budget_usd,
        "period": period_name,
        "provider": provider,
        "message": message,
        "exit_code": 2 if exceeded and mode == "exit" else 0
    }


def main():
    parser = argparse.ArgumentParser(description="Budget alert for LLM usage")
    parser.add_argument("--budget-usd", type=float, required=True, help="Budget threshold in USD")
    parser.add_argument("--period", type=str, default="today", 
                       choices=["today", "yesterday", "week", "month"],
                       help="Period to check")
    parser.add_argument("--provider", type=str, help="Filter by provider")
    parser.add_argument("--mode", type=str, default="exit",
                       choices=["exit", "warn"],
                       help="Action on breach: 'exit' (exit code 2) or 'warn' (just print)")
    
    args = parser.parse_args()
    
    store = UsageStore()
    
    result = check_budget(
        store,
        budget_usd=args.budget_usd,
        period=args.period,
        provider=args.provider,
        mode=args.mode
    )
    
    print(result["message"])
    
    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
