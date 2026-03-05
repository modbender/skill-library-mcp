---
name: expense-tracker
description: Track daily expenses in structured markdown files organized by month. Use when the user wants to log spending, view expense summaries, analyze spending patterns, or manage personal finance tracking. Supports categories, tags, and monthly summaries.
---

# Expense Tracker

Log and track daily expenses in markdown files organized by month.

## Quick Start

### Log an expense

```bash
python3 scripts/log_expense.py log <amount> <category> [--description "text"] [--tags "tag1,tag2"] [--date YYYY-MM-DD]
```

Examples:

```bash
# Simple expense
python3 scripts/log_expense.py log 45000 Coffee

# With description
python3 scripts/log_expense.py log 250000 Dining --description "Lunch with team"

# With tags
python3 scripts/log_expense.py log 500000 Shopping --tags "clothes,sale" --description "New shirt"

# Specify date (for backdating)
python3 scripts/log_expense.py log 1200000 Vehicle --description "Gas" --date 2026-02-15
```

### View monthly summary

```bash
# Current month
python3 scripts/log_expense.py summary

# Specific month
python3 scripts/log_expense.py summary 2026-02

# JSON output (for parsing)
python3 scripts/log_expense.py summary 2026-02 --json
```

## File Organization

Expenses are stored in `expenses/` directory at workspace root:

```
expenses/
├── 2026-01.md
├── 2026-02.md
└── 2026-03.md
```

Each file contains a markdown table:

```markdown
# Expenses - 2026-02

| Date | Category | Amount (VND) | Description | Tags |
|------|----------|-------------|-------------|------|
| 2026-02-17 | Coffee | 45,000 | | |
| 2026-02-17 | Dining | 250,000 | Lunch with team | |
| 2026-02-17 | Shopping | 500,000 | New shirt | clothes,sale |
```

## Categories

See `references/categories.md` for common expense categories. Use existing categories or create custom ones as needed.

Common categories:
- **Housing** - Rent, utilities, home expenses
- **Vehicle** - Gas, maintenance, parking
- **Dining** - Restaurants, food delivery
- **Coffee** - Cafes, coffee shops
- **Shopping** - Clothes, electronics, general purchases
- **Entertainment** - Movies, games, hobbies
- **Healthcare** - Medicine, doctor visits
- **Subscriptions** - Netflix, Spotify, gym, apps
- **Savings** - Investments, emergency fund
- **Debt Payment** - Loans, credit cards
- **Miscellaneous** - Other expenses

## Workflow Examples

### Log daily expenses from conversation

When the user mentions spending money:

```bash
# User: "Just paid 35k for coffee"
python3 scripts/log_expense.py log 35000 Coffee

# User: "Grabbed lunch for 120k at Phở 24"
python3 scripts/log_expense.py log 120000 Dining --description "Phở 24"

# User: "Filled up gas, 400k"
python3 scripts/log_expense.py log 400000 Vehicle --description "Gas"
```

### Monthly review

```bash
# Get summary
python3 scripts/log_expense.py summary 2026-02

# Read the expense file to see details
cat expenses/2026-02.md
```

### Analyze spending patterns

```bash
# Get JSON for analysis
python3 scripts/log_expense.py summary 2026-02 --json

# Compare multiple months
python3 scripts/log_expense.py summary 2026-01 --json > jan.json
python3 scripts/log_expense.py summary 2026-02 --json > feb.json
```

## Tips

- **Batch logging**: User can tell you multiple expenses at once, log them all
- **Category consistency**: Use the same category names to enable accurate summaries
- **Tags for filtering**: Use tags for subcategories (e.g., "work", "weekend", "urgent")
- **Descriptions**: Add context that helps identify the expense later
- **Regular reviews**: Suggest monthly summaries to track spending patterns

## Integration with Financial Goals

When tracking expenses, consider:

1. **Budget tracking**: Compare monthly totals to target budget
2. **Spending patterns**: Identify high-spend categories
3. **Emergency fund**: Track savings progress
4. **Debt reduction**: Monitor debt payment progress
5. **Financial ratios**: Calculate expenses as % of income

## Script Reference

### log_expense.py

**Commands:**
- `log` - Add an expense entry
- `summary` - View monthly summary

**Arguments (log):**
- `amount` - Amount in VND (required)
- `category` - Category name (required)
- `--description/-d` - Optional description
- `--tags/-t` - Optional comma-separated tags
- `--date` - Optional date (YYYY-MM-DD, defaults to today)
- `--workspace` - Optional workspace path (defaults to ~/.openclaw/workspace)

**Arguments (summary):**
- `year_month` - Optional YYYY-MM (defaults to current month)
- `--json` - Output as JSON
- `--workspace` - Optional workspace path

**Output:**
- Creates/updates markdown files in `expenses/` directory
- Prints confirmation with file location
- Summary shows total, count, and breakdown by category
