"""
Finance Tracker — Trend Analysis
Find patterns in spending and income over time
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List, Dict, Any, Tuple

try:
    from .storage import get_storage
    from .categories import get_emoji
except ImportError:
    from storage import get_storage
    from categories import get_emoji


def analyze_trends(days: int = 90) -> str:
    """
    Analyze spending trends over the given period.
    Returns insights about patterns.
    """
    storage = get_storage()
    transactions = storage.get_transactions(days=days)
    currency = storage.get_currency()
    
    if len(transactions) < 5:
        return "📊 Need more data for trend analysis.\n\nKeep tracking expenses for a few weeks!"
    
    lines = [
        f"📊 Spending Trends (last {days} days)",
        "━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]
    
    # === DAILY AVERAGES ===
    total = sum(tx["amount"] for tx in transactions)
    daily_avg = total // days
    lines.append(f"📅 Daily Average: {daily_avg:,} {currency}")
    lines.append(f"📅 Weekly Average: {daily_avg * 7:,} {currency}")
    lines.append(f"📅 Monthly Average: {daily_avg * 30:,} {currency}")
    lines.append("")
    
    # === DAY OF WEEK PATTERNS ===
    by_weekday = defaultdict(list)
    for tx in transactions:
        dt = datetime.fromisoformat(tx["date"])
        weekday = dt.strftime("%A")
        by_weekday[weekday].append(tx["amount"])
    
    weekday_avgs = {}
    for day, amounts in by_weekday.items():
        weekday_avgs[day] = sum(amounts) // len(amounts) if amounts else 0
    
    if weekday_avgs:
        max_day = max(weekday_avgs, key=weekday_avgs.get)
        min_day = min(weekday_avgs, key=weekday_avgs.get)
        
        lines.append("📆 Day of Week Patterns:")
        lines.append(f"   📈 Highest spending: {max_day} ({weekday_avgs[max_day]:,} avg)")
        lines.append(f"   📉 Lowest spending: {min_day} ({weekday_avgs[min_day]:,} avg)")
        lines.append("")
    
    # === CATEGORY TRENDS ===
    by_category = defaultdict(lambda: {"total": 0, "count": 0})
    for tx in transactions:
        cat = tx["category"]
        by_category[cat]["total"] += tx["amount"]
        by_category[cat]["count"] += 1
    
    sorted_cats = sorted(by_category.items(), key=lambda x: x[1]["total"], reverse=True)
    
    lines.append("🏷️ Top Categories:")
    for cat, data in sorted_cats[:5]:
        emoji = get_emoji(cat)
        pct = (data["total"] / total * 100) if total > 0 else 0
        lines.append(f"   {emoji} {cat}: {data['total']:,} {currency} ({pct:.1f}%)")
    lines.append("")
    
    # === LARGEST EXPENSES ===
    sorted_tx = sorted(transactions, key=lambda x: x["amount"], reverse=True)[:3]
    
    lines.append("💸 Biggest Expenses:")
    for tx in sorted_tx:
        emoji = get_emoji(tx["category"])
        date = datetime.fromisoformat(tx["date"]).strftime("%m/%d")
        lines.append(f"   {date} {emoji} {tx['amount']:,} — {tx['description']}")
    
    # === INSIGHTS ===
    lines.append("")
    lines.append("💡 Insights:")
    
    # Find if any category is growing
    if len(sorted_cats) > 0:
        top_cat = sorted_cats[0][0]
        top_pct = (sorted_cats[0][1]["total"] / total * 100) if total > 0 else 0
        
        if top_pct > 40:
            lines.append(f"   ⚠️ {get_emoji(top_cat)} {top_cat.capitalize()} is {top_pct:.0f}% of spending")
        
        if daily_avg > 100000:  # Arbitrary threshold
            lines.append(f"   📈 High daily spending: {daily_avg:,} {currency}/day")
    
    return "\n".join(lines)


def compare_periods(period1_days: int = 30, period2_days: int = 30) -> str:
    """
    Compare spending between two periods.
    Period 1 is the recent period, Period 2 is before that.
    """
    storage = get_storage()
    currency = storage.get_currency()
    
    now = datetime.now()
    
    # Get transactions for both periods
    all_tx = storage.get_transactions()
    
    cutoff1 = now.timestamp() - (period1_days * 86400)
    cutoff2 = cutoff1 - (period2_days * 86400)
    
    period1_tx = [tx for tx in all_tx if tx["timestamp"] >= cutoff1]
    period2_tx = [tx for tx in all_tx if cutoff2 <= tx["timestamp"] < cutoff1]
    
    total1 = sum(tx["amount"] for tx in period1_tx)
    total2 = sum(tx["amount"] for tx in period2_tx)
    
    if total2 == 0:
        change = 100 if total1 > 0 else 0
    else:
        change = ((total1 - total2) / total2) * 100
    
    lines = [
        "📊 Period Comparison",
        "━━━━━━━━━━━━━━━━━━━━━",
        f"📅 This period ({period1_days} days): {total1:,} {currency}",
        f"📅 Last period ({period2_days} days): {total2:,} {currency}",
        ""
    ]
    
    if change > 0:
        lines.append(f"📈 Spending UP {change:.1f}%")
    elif change < 0:
        lines.append(f"📉 Spending DOWN {abs(change):.1f}%")
    else:
        lines.append("➡️ Spending unchanged")
    
    return "\n".join(lines)


def get_budget_status(daily_budget: int) -> str:
    """
    Check spending against a daily budget.
    """
    storage = get_storage()
    currency = storage.get_currency()
    
    # Get today's spending
    today_tx = storage.get_transactions(days=1)
    today_total = sum(tx["amount"] for tx in today_tx)
    
    # Get this week's spending
    week_tx = storage.get_transactions(days=7)
    week_total = sum(tx["amount"] for tx in week_tx)
    week_budget = daily_budget * 7
    
    lines = [
        "💰 Budget Status",
        "━━━━━━━━━━━━━━━━━━━━━",
        f"📅 Daily Budget: {daily_budget:,} {currency}",
        ""
    ]
    
    # Today
    today_pct = (today_total / daily_budget * 100) if daily_budget > 0 else 0
    remaining = daily_budget - today_total
    
    if today_pct <= 50:
        status = "✅"
    elif today_pct <= 100:
        status = "⚠️"
    else:
        status = "🚨"
    
    lines.append(f"{status} Today: {today_total:,} / {daily_budget:,} ({today_pct:.0f}%)")
    
    if remaining > 0:
        lines.append(f"   💵 Remaining: {remaining:,}")
    else:
        lines.append(f"   🚨 Over budget by: {abs(remaining):,}")
    
    lines.append("")
    
    # Week
    week_pct = (week_total / week_budget * 100) if week_budget > 0 else 0
    week_remaining = week_budget - week_total
    
    if week_pct <= 70:
        status = "✅"
    elif week_pct <= 100:
        status = "⚠️"
    else:
        status = "🚨"
    
    lines.append(f"{status} This Week: {week_total:,} / {week_budget:,} ({week_pct:.0f}%)")
    
    return "\n".join(lines)
