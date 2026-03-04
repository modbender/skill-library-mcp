#!/usr/bin/env python3
"""Monthly/yearly report generator with JSON, text, and HTML output."""

import argparse
import json
import sys
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from tabulate import tabulate

from db import ensure_db_ready, get_connection
from utils import format_currency


def generate_report(month=None, year=None, period="monthly", output_format="json", db_path=None):
    """Generate a spending report."""
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    today = datetime.now()

    if period == "monthly":
        if month and year:
            start = datetime(year, month, 1)
        elif month:
            start = datetime(today.year, month, 1)
        elif year:
            start = datetime(year, today.month, 1)
        else:
            start = today.replace(day=1)
        end = (start + relativedelta(months=1)) - timedelta(days=1)
        period_label = start.strftime("%B %Y")

        # Previous period for comparison
        prev_start = start - relativedelta(months=1)
        prev_end = start - timedelta(days=1)
        prev_label = prev_start.strftime("%B %Y")
    else:
        if year:
            start = datetime(year, 1, 1)
        else:
            start = datetime(today.year, 1, 1)
        end = datetime(start.year, 12, 31)
        period_label = str(start.year)

        prev_start = datetime(start.year - 1, 1, 1)
        prev_end = datetime(start.year - 1, 12, 31)
        prev_label = str(start.year - 1)

    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    prev_start_str = prev_start.strftime("%Y-%m-%d")
    prev_end_str = prev_end.strftime("%Y-%m-%d")

    # Total spending (negative amounts)
    spending_row = conn.execute("""
        SELECT COALESCE(SUM(ABS(amount)), 0) as total, COUNT(*) as count
        FROM transactions
        WHERE date >= ? AND date <= ? AND amount < 0
    """, (start_str, end_str)).fetchone()

    total_spending = round(spending_row["total"], 2)
    tx_count = spending_row["count"]

    # Total income (positive amounts)
    income_row = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
        FROM transactions
        WHERE date >= ? AND date <= ? AND amount > 0
    """, (start_str, end_str)).fetchone()

    total_income = round(income_row["total"], 2)
    net = round(total_income - total_spending, 2)

    # By category breakdown
    category_rows = conn.execute("""
        SELECT c.name as category, COALESCE(SUM(ABS(t.amount)), 0) as total,
               COUNT(*) as count
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.date >= ? AND t.date <= ? AND t.amount < 0
        GROUP BY c.name
        ORDER BY total DESC
    """, (start_str, end_str)).fetchall()

    categories = []
    for row in category_rows:
        pct = round((row["total"] / total_spending * 100), 1) if total_spending > 0 else 0
        categories.append({
            "category": row["category"],
            "total": round(row["total"], 2),
            "total_formatted": format_currency(row["total"]),
            "count": row["count"],
            "percent": pct,
        })

    # Top merchants
    merchant_rows = conn.execute("""
        SELECT description, COALESCE(SUM(ABS(amount)), 0) as total, COUNT(*) as count
        FROM transactions
        WHERE date >= ? AND date <= ? AND amount < 0
        GROUP BY description
        ORDER BY total DESC
        LIMIT 10
    """, (start_str, end_str)).fetchall()

    top_merchants = [
        {
            "merchant": row["description"],
            "total": round(row["total"], 2),
            "total_formatted": format_currency(row["total"]),
            "count": row["count"],
        }
        for row in merchant_rows
    ]

    # Largest transactions
    largest_rows = conn.execute("""
        SELECT t.date, t.description, ABS(t.amount) as amount, c.name as category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.date >= ? AND t.date <= ? AND t.amount < 0
        ORDER BY ABS(t.amount) DESC
        LIMIT 5
    """, (start_str, end_str)).fetchall()

    largest = [
        {
            "date": row["date"],
            "description": row["description"],
            "amount": round(row["amount"], 2),
            "amount_formatted": format_currency(row["amount"]),
            "category": row["category"],
        }
        for row in largest_rows
    ]

    # Previous period comparison
    prev_spending = conn.execute("""
        SELECT COALESCE(SUM(ABS(amount)), 0) as total
        FROM transactions
        WHERE date >= ? AND date <= ? AND amount < 0
    """, (prev_start_str, prev_end_str)).fetchone()["total"]

    prev_spending = round(prev_spending, 2)
    if prev_spending > 0:
        change_pct = round(((total_spending - prev_spending) / prev_spending) * 100, 1)
        change_direction = "increased" if change_pct > 0 else "decreased" if change_pct < 0 else "unchanged"
    else:
        change_pct = 0
        change_direction = "no previous data"

    # Budget compliance
    budget_rows = conn.execute("""
        SELECT b.amount as budget, c.name as category,
               COALESCE(
                   (SELECT SUM(ABS(t2.amount))
                    FROM transactions t2
                    WHERE t2.category_id = b.category_id
                      AND t2.date >= ? AND t2.date <= ?
                      AND t2.amount < 0), 0
               ) as spent
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.period = ?
    """, (start_str, end_str, period)).fetchall()

    budget_compliance = []
    for row in budget_rows:
        spent = round(row["spent"], 2)
        budget = row["budget"]
        pct = round((spent / budget * 100), 1) if budget > 0 else 0
        status = "exceeded" if pct > 100 else "warning" if pct > 80 else "ok"
        budget_compliance.append({
            "category": row["category"],
            "budget": budget,
            "budget_formatted": format_currency(budget),
            "spent": spent,
            "spent_formatted": format_currency(spent),
            "percent_used": pct,
            "status": status,
        })

    report = {
        "period": period_label,
        "date_range": {"start": start_str, "end": end_str},
        "summary": {
            "total_spending": total_spending,
            "total_spending_formatted": format_currency(total_spending),
            "total_income": total_income,
            "total_income_formatted": format_currency(total_income),
            "net": net,
            "net_formatted": format_currency(net),
            "transaction_count": tx_count,
        },
        "by_category": categories,
        "top_merchants": top_merchants,
        "largest_transactions": largest,
        "trends": {
            "previous_period": prev_label,
            "previous_spending": prev_spending,
            "previous_spending_formatted": format_currency(prev_spending),
            "change_percent": change_pct,
            "change_direction": change_direction,
        },
        "budget_compliance": budget_compliance,
    }

    conn.close()

    if output_format == "json":
        return report
    elif output_format == "text":
        return format_text_report(report)
    elif output_format == "html":
        return format_html_report(report)
    else:
        return report


def format_text_report(report):
    """Format report as readable text using tabulate."""
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"  Financial Report: {report['period']}")
    lines.append(f"  {report['date_range']['start']} to {report['date_range']['end']}")
    lines.append(f"{'='*60}")
    lines.append("")

    s = report["summary"]
    lines.append("SUMMARY")
    lines.append(f"  Total Spending:  {s['total_spending_formatted']}")
    lines.append(f"  Total Income:    {s['total_income_formatted']}")
    lines.append(f"  Net:             {s['net_formatted']}")
    lines.append(f"  Transactions:    {s['transaction_count']}")
    lines.append("")

    # Trends
    t = report["trends"]
    lines.append("TRENDS")
    lines.append(f"  vs {t['previous_period']}: {t['change_direction']} {abs(t['change_percent'])}%")
    lines.append(f"  Previous spending: {t['previous_spending_formatted']}")
    lines.append("")

    # By category
    if report["by_category"]:
        lines.append("SPENDING BY CATEGORY")
        cat_table = [
            [c["category"].title(), c["total_formatted"], f"{c['percent']}%", c["count"]]
            for c in report["by_category"]
        ]
        lines.append(tabulate(cat_table, headers=["Category", "Amount", "%", "Txns"],
                              tablefmt="simple"))
        lines.append("")

    # Top merchants
    if report["top_merchants"]:
        lines.append("TOP MERCHANTS")
        merch_table = [
            [m["merchant"], m["total_formatted"], m["count"]]
            for m in report["top_merchants"]
        ]
        lines.append(tabulate(merch_table, headers=["Merchant", "Amount", "Txns"],
                              tablefmt="simple"))
        lines.append("")

    # Largest transactions
    if report["largest_transactions"]:
        lines.append("LARGEST TRANSACTIONS")
        large_table = [
            [l["date"], l["description"], l["amount_formatted"], l["category"] or ""]
            for l in report["largest_transactions"]
        ]
        lines.append(tabulate(large_table, headers=["Date", "Description", "Amount", "Category"],
                              tablefmt="simple"))
        lines.append("")

    # Budget compliance
    if report["budget_compliance"]:
        lines.append("BUDGET STATUS")
        budget_table = [
            [b["category"].title(), b["budget_formatted"], b["spent_formatted"],
             f"{b['percent_used']}%", b["status"].upper()]
            for b in report["budget_compliance"]
        ]
        lines.append(tabulate(budget_table,
                              headers=["Category", "Budget", "Spent", "Used", "Status"],
                              tablefmt="simple"))
        lines.append("")

    return "\n".join(lines)


def format_html_report(report):
    """Format report as HTML."""
    s = report["summary"]
    t = report["trends"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Report - {report['period']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #1a1a2e; border-bottom: 2px solid #16213e; padding-bottom: 10px; }}
        h2 {{ color: #16213e; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 15px; margin: 20px 0; }}
        .card {{ background: white; padding: 20px; border-radius: 8px;
                 box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card .label {{ font-size: 0.85em; color: #666; text-transform: uppercase; }}
        .card .value {{ font-size: 1.5em; font-weight: bold; color: #1a1a2e; margin-top: 5px; }}
        .card .value.positive {{ color: #27ae60; }}
        .card .value.negative {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; background: white;
                 border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #16213e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
        tr:hover td {{ background: #f8f9fa; }}
        .status-ok {{ color: #27ae60; font-weight: bold; }}
        .status-warning {{ color: #f39c12; font-weight: bold; }}
        .status-exceeded {{ color: #e74c3c; font-weight: bold; }}
        .trend {{ font-size: 0.9em; color: #666; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>Financial Report: {report['period']}</h1>
    <p>{report['date_range']['start']} to {report['date_range']['end']}</p>

    <div class="summary">
        <div class="card">
            <div class="label">Total Spending</div>
            <div class="value negative">{s['total_spending_formatted']}</div>
        </div>
        <div class="card">
            <div class="label">Total Income</div>
            <div class="value positive">{s['total_income_formatted']}</div>
        </div>
        <div class="card">
            <div class="label">Net</div>
            <div class="value {'positive' if s['net'] >= 0 else 'negative'}">{s['net_formatted']}</div>
        </div>
        <div class="card">
            <div class="label">Transactions</div>
            <div class="value">{s['transaction_count']}</div>
        </div>
    </div>

    <p class="trend">vs {t['previous_period']}: spending {t['change_direction']} {abs(t['change_percent'])}%
       (was {t['previous_spending_formatted']})</p>
"""

    # By category table
    if report["by_category"]:
        html += "    <h2>Spending by Category</h2>\n    <table>\n"
        html += "        <tr><th>Category</th><th>Amount</th><th>%</th><th>Transactions</th></tr>\n"
        for c in report["by_category"]:
            html += f"        <tr><td>{c['category'].title()}</td><td>{c['total_formatted']}</td>"
            html += f"<td>{c['percent']}%</td><td>{c['count']}</td></tr>\n"
        html += "    </table>\n"

    # Top merchants
    if report["top_merchants"]:
        html += "    <h2>Top Merchants</h2>\n    <table>\n"
        html += "        <tr><th>Merchant</th><th>Amount</th><th>Transactions</th></tr>\n"
        for m in report["top_merchants"]:
            html += f"        <tr><td>{m['merchant']}</td><td>{m['total_formatted']}</td>"
            html += f"<td>{m['count']}</td></tr>\n"
        html += "    </table>\n"

    # Largest transactions
    if report["largest_transactions"]:
        html += "    <h2>Largest Transactions</h2>\n    <table>\n"
        html += "        <tr><th>Date</th><th>Description</th><th>Amount</th><th>Category</th></tr>\n"
        for l in report["largest_transactions"]:
            html += f"        <tr><td>{l['date']}</td><td>{l['description']}</td>"
            html += f"<td>{l['amount_formatted']}</td><td>{l['category'] or ''}</td></tr>\n"
        html += "    </table>\n"

    # Budget compliance
    if report["budget_compliance"]:
        html += "    <h2>Budget Status</h2>\n    <table>\n"
        html += "        <tr><th>Category</th><th>Budget</th><th>Spent</th><th>Used</th><th>Status</th></tr>\n"
        for b in report["budget_compliance"]:
            status_class = f"status-{b['status']}"
            html += f"        <tr><td>{b['category'].title()}</td><td>{b['budget_formatted']}</td>"
            html += f"<td>{b['spent_formatted']}</td><td>{b['percent_used']}%</td>"
            html += f"<td class=\"{status_class}\">{b['status'].upper()}</td></tr>\n"
        html += "    </table>\n"

    html += """
</body>
</html>"""

    return html


def main():
    parser = argparse.ArgumentParser(description="Generate financial reports")
    parser.add_argument("--month", type=int, choices=range(1, 13),
                        help="Month (1-12)")
    parser.add_argument("--year", type=int, help="Year")
    parser.add_argument("--period", choices=["monthly", "yearly"],
                        default="monthly", help="Report period")
    parser.add_argument("--format", choices=["json", "text", "html"],
                        default="json", dest="output_format", help="Output format")
    parser.add_argument("--db", help="Database path override")
    args = parser.parse_args()

    result = generate_report(
        month=args.month,
        year=args.year,
        period=args.period,
        output_format=args.output_format,
        db_path=args.db,
    )

    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
