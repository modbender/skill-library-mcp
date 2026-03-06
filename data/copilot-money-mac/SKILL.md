---
name: copilot-money
description: Query and analyze personal finance data from the Copilot Money Mac app. Use when the user asks about their spending, transactions, account balances, budgets, or financial trends from Copilot Money.
---

# Copilot Money

Query local data from the Copilot Money Mac app to analyze transactions, spending patterns, account balances, investments, and budgets. Data is stored in both SQLite (transactions, balances) and Firestore LevelDB cache (recurring names, budgets, investments).

## Database Location

```
~/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite
```

## Schema

### Transactions Table

Primary table for all financial transactions.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| date | DATE | Transaction date |
| name | TEXT | Merchant/transaction name |
| original_name | TEXT | Raw name from bank |
| amount | DOUBLE | Transaction amount (positive = expense) |
| iso_currency_code | TEXT | Currency (e.g., "USD") |
| account_id | TEXT | Linked account reference |
| category_id | TEXT | Category reference |
| pending | BOOLEAN | Whether transaction is pending |
| recurring | BOOLEAN | Whether transaction is recurring |
| recurring_id | TEXT | Links to recurring definition (see Firestore) |
| user_note | TEXT | User-added notes |
| user_deleted | BOOLEAN | Soft-deleted by user |

### accountDailyBalance Table

Daily balance snapshots per account.

| Column | Type | Description |
|--------|------|-------------|
| date | TEXT | Snapshot date |
| account_id | TEXT | Account reference |
| current_balance | DOUBLE | Balance on that date |
| available_balance | DOUBLE | Available balance |

## Firestore Cache (LevelDB)

Additional data is stored in **Firestore's local LevelDB cache**, not in the SQLite database.

**Location:**
```
~/Library/Containers/com.copilot.production/Data/Library/Application Support/firestore/__FIRAPP_DEFAULT/copilot-production-22904/main/*.ldb
```

### Collections

| Collection | Description |
|------------|-------------|
| `items` | Linked bank accounts/institutions |
| `investment_prices` | Historical security prices |
| `investment_performance` | TWR (time-weighted return) per holding |
| `investment_splits` | Stock split history |
| `securities` | Stock/fund metadata |
| `users/.../budgets` | Budget definitions (amount, category_id) |
| `users/.../recurrings` | Recurring transaction definitions |
| `amazon` | Amazon order matching data |

### Recurring Definitions

| Field | Description |
|-------|-------------|
| name | Display name (e.g., "Water / Sewer", "Rent") |
| match_string | Transaction name to match (e.g., "CHECK PAID") |
| plaid_category_id | Category ID for the recurring |
| state | "active" or "inactive" |

### Data Not in SQLite

- **Recurring names** - human-readable names like "Rent", "Netflix"
- **Budget amounts** - monthly budget per category
- **Investment data** - holdings, prices, performance, splits
- **Account/institution names** - Chase, Fidelity, etc.
- **Category names** - Restaurants, Travel, Groceries, etc.

### Extracting Data from LevelDB

**List all recurring names:**
```bash
for f in ~/Library/Containers/com.copilot.production/Data/Library/Application\ Support/firestore/__FIRAPP_DEFAULT/copilot-production-22904/main/*.ldb; do
  strings "$f" 2>/dev/null | grep -B10 "^state$" | grep -A1 "^name$" | grep -v "^name$" | grep -v "^--$"
done | sort -u | grep -v "^$"
```

**List all collections:**
```bash
for f in ~/Library/Containers/com.copilot.production/Data/Library/Application\ Support/firestore/__FIRAPP_DEFAULT/copilot-production-22904/main/*.ldb; do
  strings "$f" 2>/dev/null
done | grep -oE "documents/[a-z_]+/" | sort | uniq -c | sort -rn
```

**Find category names:**
```bash
for f in ~/Library/Containers/com.copilot.production/Data/Library/Application\ Support/firestore/__FIRAPP_DEFAULT/copilot-production-22904/main/*.ldb; do
  strings "$f" 2>/dev/null
done | grep -iE "^(groceries|restaurants|shopping|entertainment|travel|transportation|utilities)$" | sort -u
```

## Common Queries

### Recent Transactions
```sql
SELECT date, name, amount, category_id
FROM Transactions
WHERE user_deleted = 0
ORDER BY date DESC
LIMIT 20;
```

### Monthly Spending Summary
```sql
SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
FROM Transactions
WHERE amount > 0 AND user_deleted = 0
GROUP BY month
ORDER BY month DESC;
```

### Spending by Category
```sql
SELECT category_id, SUM(amount) as total, COUNT(*) as count
FROM Transactions
WHERE amount > 0 AND user_deleted = 0 AND date >= date('now', '-30 days')
GROUP BY category_id
ORDER BY total DESC;
```

### Search Transactions
```sql
SELECT date, name, amount
FROM Transactions
WHERE name LIKE '%SEARCH_TERM%' AND user_deleted = 0
ORDER BY date DESC;
```

### List Recurring Transactions
```sql
SELECT DISTINCT name, recurring_id
FROM Transactions
WHERE recurring = 1 AND user_deleted = 0
ORDER BY name;
```

## Usage

Use `sqlite3` to query the database:

```bash
sqlite3 ~/Library/Group\ Containers/group.com.copilot.production/database/CopilotDB.sqlite "YOUR_QUERY"
```

For formatted output:
```bash
sqlite3 -header -column ~/Library/Group\ Containers/group.com.copilot.production/database/CopilotDB.sqlite "YOUR_QUERY"
```

## Notes

- Category IDs are opaque strings - group by them for analysis (names are in Firestore cache)
- Amounts are positive for expenses, negative for income
- Filter `user_deleted = 0` to exclude deleted transactions
- Both databases are actively used by the app; read-only access is safe
- SQLite has `recurring_id` linking to Firestore recurring definitions
- Use `strings` on LevelDB files to extract human-readable data from Firestore cache
