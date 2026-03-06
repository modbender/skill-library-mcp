#!/usr/bin/env python3
"""
Beancount Analysis Helper Script

Provides common financial analysis queries for Beancount files.
Run this script with a beancount file to get quick insights.

Usage:
    python analyze_beancount.py <beancount_file> [options]

Options:
    --net-worth              Calculate current net worth
    --monthly-expenses       Show monthly expenses breakdown
    --savings-rate           Calculate savings rate
    --top-expenses N         Show top N expense categories (default: 10)
    --year YYYY              Filter by specific year
    --month MM               Filter by specific month
    --account PATTERN        Filter by account pattern
"""

import sys
import argparse
from datetime import datetime
from decimal import Decimal
from collections import defaultdict

try:
    from beancount import loader
    from beancount.core import data, getters, convert, realization
    from beancount.query import query
    from beancount.core.number import D
except ImportError:
    print("Error: beancount package not installed.")
    print("Install with: pip install beancount")
    sys.exit(1)


def load_beancount_file(filename):
    """Load and validate a Beancount file."""
    entries, errors, options = loader.load_file(filename)
    
    if errors:
        print(f"⚠️  Found {len(errors)} errors in the file:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
        print()
    
    return entries, options


def calculate_net_worth(entries, options):
    """Calculate current net worth (Assets - Liabilities)."""
    operating_currency = options.get('operating_currency', ['USD'])[0]
    
    real_root = realization.realize(entries)
    
    assets = realization.get(real_root, 'Assets')
    liabilities = realization.get(real_root, 'Liabilities')
    
    assets_balance = assets.balance.reduce(convert.get_units) if assets else {}
    liabilities_balance = liabilities.balance.reduce(convert.get_units) if liabilities else {}
    
    # Convert to operating currency
    assets_total = sum(
        pos.units.number for pos in assets_balance.get_positions()
        if pos.units.currency == operating_currency
    )
    
    liabilities_total = sum(
        pos.units.number for pos in liabilities_balance.get_positions()
        if pos.units.currency == operating_currency
    )
    
    net_worth = assets_total + liabilities_total  # Liabilities are negative
    
    return {
        'assets': assets_total,
        'liabilities': abs(liabilities_total),
        'net_worth': net_worth,
        'currency': operating_currency
    }


def calculate_monthly_expenses(entries, options, year=None, month=None):
    """Calculate expenses by month and category."""
    operating_currency = options.get('operating_currency', ['USD'])[0]
    monthly_data = defaultdict(lambda: defaultdict(Decimal))
    
    for entry in entries:
        if not isinstance(entry, data.Transaction):
            continue
        
        # Filter by year/month if specified
        if year and entry.date.year != year:
            continue
        if month and entry.date.month != month:
            continue
        
        period = f"{entry.date.year}-{entry.date.month:02d}"
        
        for posting in entry.postings:
            if posting.account.startswith('Expenses:'):
                if posting.units.currency == operating_currency:
                    # Get top-level expense category
                    parts = posting.account.split(':')
                    category = parts[1] if len(parts) > 1 else 'Other'
                    monthly_data[period][category] += posting.units.number
    
    return dict(monthly_data)


def calculate_savings_rate(entries, options, year=None):
    """Calculate savings rate (Income - Expenses) / Income."""
    operating_currency = options.get('operating_currency', ['USD'])[0]
    
    total_income = Decimal(0)
    total_expenses = Decimal(0)
    
    for entry in entries:
        if not isinstance(entry, data.Transaction):
            continue
        
        if year and entry.date.year != year:
            continue
        
        for posting in entry.postings:
            if posting.units.currency == operating_currency:
                if posting.account.startswith('Income:'):
                    total_income -= posting.units.number  # Income is negative
                elif posting.account.startswith('Expenses:'):
                    total_expenses += posting.units.number
    
    if total_income == 0:
        return None
    
    savings = total_income - total_expenses
    savings_rate = (savings / total_income) * 100
    
    return {
        'income': total_income,
        'expenses': total_expenses,
        'savings': savings,
        'savings_rate': savings_rate,
        'currency': operating_currency
    }


def get_top_expenses(entries, options, n=10, year=None):
    """Get top N expense categories."""
    operating_currency = options.get('operating_currency', ['USD'])[0]
    expenses_by_account = defaultdict(Decimal)
    
    for entry in entries:
        if not isinstance(entry, data.Transaction):
            continue
        
        if year and entry.date.year != year:
            continue
        
        for posting in entry.postings:
            if posting.account.startswith('Expenses:'):
                if posting.units.currency == operating_currency:
                    expenses_by_account[posting.account] += posting.units.number
    
    # Sort by amount descending
    sorted_expenses = sorted(
        expenses_by_account.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return sorted_expenses[:n]


def format_currency(amount, currency='USD'):
    """Format amount as currency."""
    return f"{currency} {amount:,.2f}"


def print_net_worth(entries, options):
    """Print net worth report."""
    result = calculate_net_worth(entries, options)
    
    print("\n" + "="*50)
    print("NET WORTH SUMMARY")
    print("="*50)
    print(f"Assets:      {format_currency(result['assets'], result['currency'])}")
    print(f"Liabilities: {format_currency(result['liabilities'], result['currency'])}")
    print("-" * 50)
    print(f"Net Worth:   {format_currency(result['net_worth'], result['currency'])}")
    print("="*50 + "\n")


def print_monthly_expenses(entries, options, year=None):
    """Print monthly expenses report."""
    monthly_data = calculate_monthly_expenses(entries, options, year=year)
    operating_currency = options.get('operating_currency', ['USD'])[0]
    
    print("\n" + "="*70)
    print(f"MONTHLY EXPENSES BREAKDOWN{' - ' + str(year) if year else ''}")
    print("="*70)
    
    for period in sorted(monthly_data.keys()):
        print(f"\n{period}:")
        print("-" * 70)
        
        categories = monthly_data[period]
        total = sum(categories.values())
        
        # Sort by amount
        for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total * 100) if total > 0 else 0
            print(f"  {category:30} {format_currency(amount, operating_currency):>15}  ({percentage:5.1f}%)")
        
        print("-" * 70)
        print(f"  {'TOTAL':30} {format_currency(total, operating_currency):>15}")
    
    print("="*70 + "\n")


def print_savings_rate(entries, options, year=None):
    """Print savings rate report."""
    result = calculate_savings_rate(entries, options, year=year)
    
    if result is None:
        print("\n⚠️  No income data found. Cannot calculate savings rate.\n")
        return
    
    print("\n" + "="*50)
    print(f"SAVINGS RATE{' - ' + str(year) if year else ''}")
    print("="*50)
    print(f"Income:       {format_currency(result['income'], result['currency'])}")
    print(f"Expenses:     {format_currency(result['expenses'], result['currency'])}")
    print(f"Savings:      {format_currency(result['savings'], result['currency'])}")
    print("-" * 50)
    print(f"Savings Rate: {result['savings_rate']:.2f}%")
    
    # Provide interpretation
    rate = result['savings_rate']
    if rate < 5:
        interpretation = "Critical - Limited financial resilience"
    elif rate < 10:
        interpretation = "Below average - Vulnerable to emergencies"
    elif rate < 20:
        interpretation = "Average - Building foundation"
    elif rate < 30:
        interpretation = "Good - Strong financial position"
    elif rate < 50:
        interpretation = "Excellent - Accelerated wealth building"
    else:
        interpretation = "Exceptional - Early retirement potential"
    
    print(f"Assessment:   {interpretation}")
    print("="*50 + "\n")


def print_top_expenses(entries, options, n=10, year=None):
    """Print top expense categories."""
    top_expenses = get_top_expenses(entries, options, n=n, year=year)
    operating_currency = options.get('operating_currency', ['USD'])[0]
    
    print("\n" + "="*70)
    print(f"TOP {n} EXPENSE CATEGORIES{' - ' + str(year) if year else ''}")
    print("="*70)
    
    total = sum(amount for _, amount in top_expenses)
    
    for i, (account, amount) in enumerate(top_expenses, 1):
        percentage = (amount / total * 100) if total > 0 else 0
        print(f"{i:2}. {account:45} {format_currency(amount, operating_currency):>15}  ({percentage:5.1f}%)")
    
    print("-" * 70)
    print(f"    {'TOTAL':45} {format_currency(total, operating_currency):>15}")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Beancount financial data',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('filename', help='Beancount file to analyze')
    parser.add_argument('--net-worth', action='store_true', help='Calculate net worth')
    parser.add_argument('--monthly-expenses', action='store_true', help='Show monthly expenses')
    parser.add_argument('--savings-rate', action='store_true', help='Calculate savings rate')
    parser.add_argument('--top-expenses', type=int, nargs='?', const=10, metavar='N',
                       help='Show top N expense categories (default: 10)')
    parser.add_argument('--year', type=int, help='Filter by year')
    parser.add_argument('--all', action='store_true', help='Run all reports')
    
    args = parser.parse_args()
    
    # Load Beancount file
    print(f"\n📊 Loading {args.filename}...")
    entries, options = load_beancount_file(args.filename)
    print(f"✅ Loaded {len(entries)} entries\n")
    
    # If no specific report requested, show all
    if not any([args.net_worth, args.monthly_expenses, args.savings_rate, args.top_expenses is not None]) or args.all:
        args.net_worth = True
        args.monthly_expenses = True
        args.savings_rate = True
        args.top_expenses = 10
    
    # Generate requested reports
    if args.net_worth:
        print_net_worth(entries, options)
    
    if args.savings_rate:
        print_savings_rate(entries, options, year=args.year)
    
    if args.top_expenses is not None:
        print_top_expenses(entries, options, n=args.top_expenses, year=args.year)
    
    if args.monthly_expenses:
        print_monthly_expenses(entries, options, year=args.year)


if __name__ == '__main__':
    main()
