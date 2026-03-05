#!/usr/bin/env python3
"""Budget CRUD and status checks."""

import argparse
import json
import sys
from datetime import datetime

from dateutil.relativedelta import relativedelta

from db import ensure_db_ready, get_connection, get_category_id, get_all_categories
from utils import format_currency


def set_budget(category_name, amount, period="monthly", db_path=None):
    """Set or update a budget for a category."""
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    cat_id = get_category_id(conn, category_name)
    if cat_id is None:
        conn.close()
        return {"success": False, "error": f"Category not found: {category_name}"}

    if period not in ("monthly", "yearly"):
        conn.close()
        return {"success": False, "error": f"Invalid period: {period}. Use 'monthly' or 'yearly'"}

    if amount <= 0:
        conn.close()
        return {"success": False, "error": "Budget amount must be positive"}

    # Upsert budget
    existing = conn.execute(
        "SELECT id FROM budgets WHERE category_id = ? AND period = ?",
        (cat_id, period),
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE budgets SET amount = ?, updated_at = datetime('now') WHERE id = ?",
            (amount, existing["id"]),
        )
        action = "updated"
    else:
        conn.execute(
            "INSERT INTO budgets (category_id, amount, period) VALUES (?, ?, ?)",
            (cat_id, amount, period),
        )
        action = "created"

    conn.commit()
    conn.close()

    return {
        "success": True,
        "action": action,
        "category": category_name,
        "amount": amount,
        "amount_formatted": format_currency(amount),
        "period": period,
    }


def delete_budget(category_name, period="monthly", db_path=None):
    """Delete a budget for a category."""
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    cat_id = get_category_id(conn, category_name)
    if cat_id is None:
        conn.close()
        return {"success": False, "error": f"Category not found: {category_name}"}

    result = conn.execute(
        "DELETE FROM budgets WHERE category_id = ? AND period = ?",
        (cat_id, period),
    )
    conn.commit()
    conn.close()

    if result.rowcount > 0:
        return {"success": True, "message": f"Deleted {period} budget for {category_name}"}
    return {"success": True, "message": f"No {period} budget found for {category_name}"}


def list_budgets(db_path=None):
    """List all budgets."""
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    rows = conn.execute("""
        SELECT b.*, c.name as category_name
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        ORDER BY c.name, b.period
    """).fetchall()

    budgets = []
    for row in rows:
        budgets.append({
            "category": row["category_name"],
            "amount": row["amount"],
            "amount_formatted": format_currency(row["amount"]),
            "period": row["period"],
        })

    conn.close()
    return {"success": True, "budgets": budgets, "count": len(budgets)}


def check_budget_status(category_name=None, period="monthly", db_path=None, reference_date=None):
    """Check budget status for one or all categories.

    Args:
        reference_date: Optional datetime to use instead of today (useful for
                        checking past periods or in tests).
    """
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    today = reference_date or datetime.now()

    if period == "monthly":
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = ((today.replace(day=1) + relativedelta(months=1)) - relativedelta(days=1)).strftime("%Y-%m-%d")
        period_label = today.strftime("%B %Y")
    else:
        start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        end_date = today.replace(month=12, day=31).strftime("%Y-%m-%d")
        period_label = str(today.year)

    # Get budgets
    budget_query = """
        SELECT b.*, c.name as category_name
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.period = ?
    """
    budget_params = [period]

    if category_name:
        budget_query += " AND c.name = ?"
        budget_params.append(category_name)

    budgets = conn.execute(budget_query, budget_params).fetchall()

    if not budgets:
        conn.close()
        msg = f"No {period} budgets found"
        if category_name:
            msg += f" for {category_name}"
        return {"success": True, "statuses": [], "message": msg}

    statuses = []
    for budget in budgets:
        # Get spending for this category in the period
        spent_row = conn.execute("""
            SELECT COALESCE(SUM(ABS(t.amount)), 0) as spent, COUNT(*) as tx_count
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.name = ?
              AND t.date >= ?
              AND t.date <= ?
              AND t.amount < 0
        """, (budget["category_name"], start_date, end_date)).fetchone()

        spent = round(spent_row["spent"], 2)
        budget_amount = budget["amount"]
        remaining = round(budget_amount - spent, 2)
        pct_used = round((spent / budget_amount * 100), 1) if budget_amount > 0 else 0

        if pct_used > 100:
            status = "exceeded"
        elif pct_used > 80:
            status = "warning"
        else:
            status = "ok"

        statuses.append({
            "category": budget["category_name"],
            "budget": budget_amount,
            "budget_formatted": format_currency(budget_amount),
            "spent": spent,
            "spent_formatted": format_currency(spent),
            "remaining": remaining,
            "remaining_formatted": format_currency(remaining),
            "percent_used": pct_used,
            "status": status,
            "transaction_count": spent_row["tx_count"],
            "period": period,
            "period_label": period_label,
        })

    conn.close()

    # Sort: exceeded first, then warning, then ok
    status_order = {"exceeded": 0, "warning": 1, "ok": 2}
    statuses.sort(key=lambda s: (status_order.get(s["status"], 3), -s["percent_used"]))

    return {"success": True, "statuses": statuses, "period": period, "period_label": period_label}


def main():
    parser = argparse.ArgumentParser(description="Manage budgets")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Set budget
    set_parser = subparsers.add_parser("set", help="Set a budget")
    set_parser.add_argument("category", help="Category name")
    set_parser.add_argument("amount", type=float, help="Budget amount")
    set_parser.add_argument("--period", choices=["monthly", "yearly"],
                            default="monthly", help="Budget period")
    set_parser.add_argument("--db", help="Database path override")

    # Delete budget
    del_parser = subparsers.add_parser("delete", help="Delete a budget")
    del_parser.add_argument("category", help="Category name")
    del_parser.add_argument("--period", choices=["monthly", "yearly"],
                            default="monthly", help="Budget period")
    del_parser.add_argument("--db", help="Database path override")

    # List budgets
    list_parser = subparsers.add_parser("list", help="List all budgets")
    list_parser.add_argument("--db", help="Database path override")

    # Check status
    status_parser = subparsers.add_parser("status", help="Check budget status")
    status_parser.add_argument("--category", help="Category name (all if not specified)")
    status_parser.add_argument("--period", choices=["monthly", "yearly"],
                               default="monthly", help="Budget period")
    status_parser.add_argument("--db", help="Database path override")

    args = parser.parse_args()

    if args.command == "set":
        result = set_budget(args.category, args.amount, args.period, db_path=args.db)
    elif args.command == "delete":
        result = delete_budget(args.category, args.period, db_path=args.db)
    elif args.command == "list":
        result = list_budgets(db_path=args.db)
    elif args.command == "status":
        result = check_budget_status(category_name=args.category,
                                     period=args.period, db_path=args.db)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
