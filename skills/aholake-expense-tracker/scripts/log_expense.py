#!/usr/bin/env python3
"""
Log daily expenses to markdown files organized by month.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path


def get_expense_file(year_month: str, workspace_path: str = None) -> Path:
    """Get the path to the expense file for a given month."""
    if workspace_path is None:
        workspace_path = Path.home() / ".openclaw" / "workspace"
    else:
        workspace_path = Path(workspace_path)
    
    expenses_dir = workspace_path / "expenses"
    expenses_dir.mkdir(exist_ok=True)
    
    return expenses_dir / f"{year_month}.md"


def init_expense_file(file_path: Path, year_month: str):
    """Initialize a new expense file with headers."""
    content = f"""# Expenses - {year_month}

| Date | Category | Amount (VND) | Description | Tags |
|------|----------|-------------|-------------|------|
"""
    file_path.write_text(content)


def log_expense(amount: float, category: str, description: str = "", tags: str = "", 
                date: str = None, workspace_path: str = None):
    """Log an expense entry."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    year_month = date[:7]  # YYYY-MM
    file_path = get_expense_file(year_month, workspace_path)
    
    # Initialize file if it doesn't exist
    if not file_path.exists():
        init_expense_file(file_path, year_month)
    
    # Format amount with thousand separators
    amount_str = f"{amount:,.0f}"
    
    # Create expense entry
    entry = f"| {date} | {category} | {amount_str} | {description} | {tags} |\n"
    
    # Append to file
    with file_path.open("a") as f:
        f.write(entry)
    
    print(f"✓ Logged expense: {amount_str} VND ({category})")
    print(f"  File: {file_path}")
    
    return str(file_path)


def get_monthly_summary(year_month: str, workspace_path: str = None) -> dict:
    """Get summary of expenses for a month."""
    file_path = get_expense_file(year_month, workspace_path)
    
    if not file_path.exists():
        return {"total": 0, "by_category": {}, "count": 0}
    
    content = file_path.read_text()
    lines = content.strip().split("\n")[3:]  # Skip header
    
    total = 0
    by_category = {}
    count = 0
    
    for line in lines:
        if not line.strip() or line.startswith("|---"):
            continue
        
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 3:
            continue
        
        try:
            amount = float(parts[2].replace(",", ""))
            category = parts[1]
            
            total += amount
            by_category[category] = by_category.get(category, 0) + amount
            count += 1
        except (ValueError, IndexError):
            continue
    
    return {
        "total": total,
        "by_category": by_category,
        "count": count,
        "file": str(file_path)
    }


def main():
    parser = argparse.ArgumentParser(description="Log daily expenses")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log an expense")
    log_parser.add_argument("amount", type=float, help="Amount in VND")
    log_parser.add_argument("category", help="Expense category")
    log_parser.add_argument("--description", "-d", default="", help="Description")
    log_parser.add_argument("--tags", "-t", default="", help="Tags (comma-separated)")
    log_parser.add_argument("--date", help="Date (YYYY-MM-DD, defaults to today)")
    log_parser.add_argument("--workspace", help="Workspace path")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Get monthly summary")
    summary_parser.add_argument("year_month", nargs="?", help="Year-month (YYYY-MM, defaults to current month)")
    summary_parser.add_argument("--workspace", help="Workspace path")
    summary_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.command == "log":
        log_expense(
            args.amount,
            args.category,
            args.description,
            args.tags,
            args.date,
            args.workspace
        )
    
    elif args.command == "summary":
        year_month = args.year_month or datetime.now().strftime("%Y-%m")
        summary = get_monthly_summary(year_month, args.workspace)
        
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n📊 Expense Summary - {year_month}")
            print(f"   Total: {summary['total']:,.0f} VND")
            print(f"   Transactions: {summary['count']}")
            print(f"\n   By Category:")
            for cat, amount in sorted(summary['by_category'].items(), key=lambda x: -x[1]):
                print(f"   • {cat}: {amount:,.0f} VND")
            print(f"\n   File: {summary.get('file', 'N/A')}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
