"""
Finance Tracker — Report Generation
Creates beautiful, readable spending reports
"""

from datetime import datetime, timedelta
from typing import Optional

try:
    from .storage import FinanceStorage, get_storage
    from .categories import get_emoji, get_name
except ImportError:
    from storage import FinanceStorage, get_storage
    from categories import get_emoji, get_name


def generate_report(
    period: str = "month",
    storage: Optional[FinanceStorage] = None
) -> str:
    """
    Generate a spending report for the given period.
    
    Args:
        period: 'today', 'week', 'month', 'year', or 'all'
        storage: Optional storage instance
    
    Returns:
        Formatted report string
    """
    if storage is None:
        storage = get_storage()
    
    # Determine days to look back
    days_map = {
        "today": 1,
        "day": 1,
        "week": 7,
        "month": 30,
        "year": 365,
        "all": None
    }
    
    days = days_map.get(period.lower(), 30)
    
    # Get period title
    now = datetime.now()
    if period == "today" or period == "day":
        title = f"📊 Today's Spending ({now.strftime('%b %d, %Y')})"
    elif period == "week":
        title = f"📊 This Week's Spending"
    elif period == "month":
        title = f"📊 This Month's Spending"
    elif period == "year":
        title = f"📊 This Year's Spending"
    else:
        title = f"📊 All-Time Spending"
    
    # Get stats
    stats = storage.get_stats(days=days)
    currency = storage.get_currency()
    
    if stats["count"] == 0:
        return f"{title}\n━━━━━━━━━━━━━━━━━━━━━\n\n📭 No transactions found for this period."
    
    # Build report
    lines = [
        title,
        "━━━━━━━━━━━━━━━━━━━━━",
        f"💵 Total: {stats['total']:,} {currency}",
        ""
    ]
    
    # Category breakdown
    for category, data in stats["by_category"].items():
        emoji = get_emoji(category)
        amount = data["amount"]
        count = data["count"]
        pct = (amount / stats["total"]) * 100
        
        lines.append(f"{emoji} {category.capitalize()}: {amount:,} {currency} ({pct:.1f}%)")
    
    lines.append("")
    lines.append(f"📝 {stats['count']} transactions")
    lines.append(f"📈 Average: {stats['average']:,} {currency}")
    
    return "\n".join(lines)


def list_recent(
    n: int = 5,
    storage: Optional[FinanceStorage] = None
) -> str:
    """
    List recent transactions.
    
    Args:
        n: Number of transactions to show
        storage: Optional storage instance
    
    Returns:
        Formatted list string
    """
    if storage is None:
        storage = get_storage()
    
    transactions = storage.get_transactions(limit=n)
    currency = storage.get_currency()
    
    if not transactions:
        return "📭 No transactions yet.\n\nAdd one: finance add 50000 \"coffee\""
    
    lines = [f"📝 Recent Transactions (last {len(transactions)}):", ""]
    
    for tx in transactions:
        emoji = get_emoji(tx["category"])
        date = datetime.fromisoformat(tx["date"]).strftime("%m/%d %H:%M")
        amount = f"{tx['amount']:,}"
        
        lines.append(f"  {date}  {emoji} {amount} {currency} — {tx['description']}")
    
    return "\n".join(lines)


def search_transactions(
    query: str,
    storage: Optional[FinanceStorage] = None
) -> str:
    """
    Search transactions and return formatted results.
    
    Args:
        query: Search query
        storage: Optional storage instance
    
    Returns:
        Formatted search results
    """
    if storage is None:
        storage = get_storage()
    
    results = storage.search(query)
    currency = storage.get_currency()
    
    if not results:
        return f"🔍 No transactions found matching '{query}'"
    
    total = sum(tx["amount"] for tx in results)
    
    lines = [
        f"🔍 Search: '{query}'",
        f"Found {len(results)} transactions (total: {total:,} {currency})",
        ""
    ]
    
    for tx in results[:10]:  # Limit to 10 results
        emoji = get_emoji(tx["category"])
        date = datetime.fromisoformat(tx["date"]).strftime("%m/%d")
        
        lines.append(f"  {date}  {emoji} {tx['amount']:,} — {tx['description']}")
    
    if len(results) > 10:
        lines.append(f"\n  ... and {len(results) - 10} more")
    
    return "\n".join(lines)
