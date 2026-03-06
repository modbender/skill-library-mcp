#!/usr/bin/env python3
"""Natural language query parser and executor for transaction data."""

import argparse
import json
import re
import sys

from db import ensure_db_ready, get_connection, get_all_categories
from utils import format_currency, resolve_time_reference


# Aggregation keywords — ordered from most specific to least specific.
# More specific patterns (avg, max, min, list, count) are checked before the
# general "sum" fallback so that phrases like "average spending" don't
# incorrectly match "spending" → sum first.
AGG_PATTERNS = [
    ("avg", r"\b(average|avg|mean|typical)\b"),
    ("max", r"\b(largest|biggest|highest|most expensive|max)\b"),
    ("min", r"\b(smallest|cheapest|least expensive|min|lowest)\b"),
    ("list", r"\b(list|show|display|details|breakdown)\b"),
    ("count", r"\b(how many|count|number of)\b"),
    ("sum", r"\b(total|sum|how much|spent|spend|spending|earned|income)\b"),
]

# Time reference patterns
TIME_PATTERNS = [
    r"(this month|current month)",
    r"(last month|previous month)",
    r"(this year|current year|ytd)",
    r"(last year|previous year)",
    r"(this week|current week)",
    r"(last week|previous week)",
    r"(today|yesterday)",
    r"(last\s+\d+\s+(?:day|week|month|year)s?)",
    r"(january|february|march|april|may|june|july|august|september|october|november|december)"
    r"(?:\s+\d{4})?",
    r"(jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)(?:\s+\d{4})?",
    r"(\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2})",
]


def parse_query(query_text, category_names):
    """Parse a natural language query into structured components."""
    text = query_text.lower().strip()

    # Detect aggregation type
    agg_type = "sum"  # default
    for agg, pattern in AGG_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            agg_type = agg
            break

    # Detect time reference
    time_ref = None
    for pattern in TIME_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            time_ref = m.group(0).strip()
            break

    start_date, end_date = None, None
    if time_ref:
        start_date, end_date = resolve_time_reference(time_ref)

    # If no time reference found, default to this month
    if not start_date:
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

    # Detect category
    category = None
    for cat in category_names:
        # Match full category name or common aliases
        aliases = {
            "groceries": ["grocery", "groceries", "food", "supermarket"],
            "dining": ["dining", "restaurants", "restaurant", "eating out", "food delivery"],
            "transport": ["transport", "transportation", "gas", "uber", "lyft", "transit", "commute"],
            "utilities": ["utilities", "utility", "bills", "electric", "internet", "phone"],
            "subscriptions": ["subscriptions", "subscription", "streaming", "netflix", "spotify"],
            "shopping": ["shopping", "retail", "amazon", "online shopping", "clothes"],
            "healthcare": ["healthcare", "health", "medical", "pharmacy", "doctor"],
            "entertainment": ["entertainment", "fun", "movies", "travel", "hotels"],
            "income": ["income", "salary", "earnings", "deposits", "refunds"],
            "uncategorized": ["uncategorized", "unknown", "other"],
        }
        cat_aliases = aliases.get(cat, [cat])
        for alias in cat_aliases:
            if alias in text:
                category = cat
                break
        if category:
            break

    # Detect merchant
    merchant = None
    merchant_match = re.search(r"(?:at|from|to|for)\s+([a-zA-Z][\w\s&'-]+?)(?:\s+(?:in|during|for|last|this)|$)", text)
    if merchant_match:
        potential = merchant_match.group(1).strip()
        # Don't treat time references or categories as merchants
        if potential.lower() not in (
            "last month", "this month", "this year", "last year",
            "this week", "last week", "today", "yesterday"
        ) and potential.lower() not in category_names:
            merchant = potential

    # Detect limit for list queries
    limit = None
    limit_match = re.search(r"(?:top|first|last|recent)\s+(\d+)", text)
    if limit_match:
        limit = int(limit_match.group(1))
    elif agg_type == "list":
        limit = 20  # default limit for list queries

    return {
        "aggregation": agg_type,
        "start_date": start_date,
        "end_date": end_date,
        "time_reference": time_ref,
        "category": category,
        "merchant": merchant,
        "limit": limit,
    }


def execute_query(parsed, db_path=None):
    """Execute a parsed query against the database."""
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    base_query = """
        SELECT t.*, c.name as category_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    """
    params = []

    if parsed.get("start_date"):
        base_query += " AND t.date >= ?"
        params.append(parsed["start_date"])
    if parsed.get("end_date"):
        base_query += " AND t.date <= ?"
        params.append(parsed["end_date"])
    if parsed.get("category"):
        base_query += " AND c.name = ?"
        params.append(parsed["category"])
    if parsed.get("merchant"):
        base_query += " AND (t.description LIKE ? OR t.original_description LIKE ?)"
        merchant_pat = f"%{parsed['merchant']}%"
        params.extend([merchant_pat, merchant_pat])

    # Only consider spending (negative amounts) unless querying income
    is_income_query = parsed.get("category") == "income"
    if not is_income_query:
        base_query += " AND t.amount < 0"

    agg = parsed.get("aggregation", "sum")

    if agg == "sum":
        query = f"SELECT COALESCE(SUM(ABS(t.amount)), 0) as total, COUNT(*) as count FROM ({base_query}) t"
        # Need category join in subquery already
        query = f"""
            SELECT COALESCE(SUM(ABS(sub.amount)), 0) as total, COUNT(*) as count
            FROM ({base_query}) sub
        """
        row = conn.execute(query, params).fetchone()
        result = {
            "type": "sum",
            "total": round(row["total"], 2),
            "total_formatted": format_currency(row["total"]),
            "transaction_count": row["count"],
        }

    elif agg == "count":
        query = f"SELECT COUNT(*) as count FROM ({base_query}) sub"
        row = conn.execute(query, params).fetchone()
        result = {
            "type": "count",
            "count": row["count"],
        }

    elif agg == "avg":
        query = f"SELECT COALESCE(AVG(ABS(sub.amount)), 0) as avg_amount, COUNT(*) as count FROM ({base_query}) sub"
        row = conn.execute(query, params).fetchone()
        result = {
            "type": "avg",
            "average": round(row["avg_amount"], 2),
            "average_formatted": format_currency(row["avg_amount"]),
            "transaction_count": row["count"],
        }

    elif agg == "max":
        query = f"{base_query} ORDER BY ABS(t.amount) DESC LIMIT 1"
        row = conn.execute(query, params).fetchone()
        if row:
            result = {
                "type": "max",
                "amount": abs(round(row["amount"], 2)),
                "amount_formatted": format_currency(abs(row["amount"])),
                "description": row["description"],
                "date": row["date"],
                "category": row["category_name"],
            }
        else:
            result = {"type": "max", "amount": 0, "message": "No transactions found"}

    elif agg == "min":
        query = f"{base_query} ORDER BY ABS(t.amount) ASC LIMIT 1"
        row = conn.execute(query, params).fetchone()
        if row:
            result = {
                "type": "min",
                "amount": abs(round(row["amount"], 2)),
                "amount_formatted": format_currency(abs(row["amount"])),
                "description": row["description"],
                "date": row["date"],
                "category": row["category_name"],
            }
        else:
            result = {"type": "min", "amount": 0, "message": "No transactions found"}

    elif agg == "list":
        limit = parsed.get("limit", 20)
        query = f"{base_query} ORDER BY t.date DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        result = {
            "type": "list",
            "count": len(rows),
            "transactions": [
                {
                    "date": row["date"],
                    "description": row["description"],
                    "amount": round(row["amount"], 2),
                    "amount_formatted": format_currency(abs(row["amount"])),
                    "category": row["category_name"],
                }
                for row in rows
            ],
        }

    else:
        result = {"type": "error", "message": f"Unknown aggregation type: {agg}"}

    # Add query metadata
    result["query"] = {
        "time_range": f"{parsed.get('start_date', 'all')} to {parsed.get('end_date', 'now')}",
        "category": parsed.get("category", "all"),
        "merchant": parsed.get("merchant"),
    }

    conn.close()
    return result


def run_query(query_text, db_path=None):
    """Parse and execute a natural language query."""
    ensure_db_ready(db_path)
    conn = get_connection(db_path)
    categories = get_all_categories(conn)
    category_names = [cat["name"] for cat in categories]
    conn.close()

    parsed = parse_query(query_text, category_names)
    result = execute_query(parsed, db_path)

    return {"success": True, "parsed_query": parsed, "result": result}


def main():
    parser = argparse.ArgumentParser(description="Query transaction data with natural language")
    parser.add_argument("query", nargs="?", help="Natural language query")
    parser.add_argument("--db", help="Database path override")
    args = parser.parse_args()

    if not args.query:
        print(json.dumps({"success": False, "error": "No query provided"}))
        sys.exit(1)

    result = run_query(args.query, db_path=args.db)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
