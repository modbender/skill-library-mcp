# Beancount Query Language (BQL)

## Official Documentation

- **Query Language Reference**: http://furius.ca/beancount/doc/query
- **Beancount Documentation**: https://beancount.github.io/docs/index.html

## Overview

The Beancount Query Language (BQL) is SQL-like syntax for querying Beancount data. It can be used:
- In the `bean-query` command-line tool
- In Fava's Query page
- In saved `query` directives in Beancount files

## Basic Query Structure

```sql
SELECT <columns>
FROM <table>
WHERE <condition>
GROUP BY <columns>
ORDER BY <columns> <ASC|DESC>
LIMIT <number>
```

## Tables

BQL queries operate on virtual tables generated from your Beancount data:

- **entries**: All directives (transactions, balances, etc.)
- **postings**: Individual postings from transactions
- **balances**: Account balances at specific points in time

Most queries use implicit tables based on the SELECT clause.

## Common Query Patterns

### Monthly Expenses by Category

```sql
SELECT
  year, month,
  account,
  sum(position) AS total
WHERE
  account ~ 'Expenses:'
  AND year = 2024
GROUP BY year, month, account
ORDER BY year, month, total DESC
```

### Income vs Expenses

```sql
SELECT
  year, month,
  sum(position) WHERE account ~ 'Income:' AS income,
  sum(position) WHERE account ~ 'Expenses:' AS expenses,
  sum(position) WHERE account ~ 'Income:' OR account ~ 'Expenses:' AS net
GROUP BY year, month
ORDER BY year, month
```

### Net Worth Over Time

```sql
SELECT
  year, month,
  sum(convert(position, 'USD')) AS net_worth
WHERE
  account_sortkey(account) < 3  -- Assets and Liabilities only
GROUP BY year, month
ORDER BY year, month
```

### Top Expenses by Category

```sql
SELECT
  account,
  sum(convert(position, 'USD')) AS amount
WHERE
  account ~ 'Expenses:'
  AND year = 2024
GROUP BY account
ORDER BY amount DESC
LIMIT 10
```

### Tagged Transactions

```sql
SELECT
  date, payee, narration,
  sum(convert(position, 'USD')) AS amount
WHERE
  'vacation' IN tags
  AND year = 2024
ORDER BY date
```

### Linked Transactions

```sql
SELECT
  date, payee, narration, account,
  position
WHERE
  'invoice-123' IN links
ORDER BY date
```

### Account Balance at Date

```sql
SELECT
  sum(convert(position, 'USD')) AS balance
WHERE
  account = 'Assets:Bank:Checking'
  AND date <= 2024-01-31
```

### Transactions Between Dates

```sql
SELECT
  date, payee, narration, account, position
WHERE
  account = 'Expenses:Food:Groceries'
  AND date >= 2024-01-01
  AND date <= 2024-01-31
ORDER BY date
```

### Investment Performance

```sql
SELECT
  account,
  sum(convert(position, 'USD', date)) AS market_value,
  sum(convert(cost(position), 'USD')) AS book_value,
  sum(convert(position, 'USD', date)) - sum(convert(cost(position), 'USD')) AS unrealized_gains
WHERE
  account ~ 'Assets:Investments:'
GROUP BY account
```

### Payee Summary

```sql
SELECT
  payee,
  count(*) AS transactions,
  sum(convert(position, 'USD')) WHERE account ~ 'Expenses:' AS total_spent
WHERE
  payee != ''
GROUP BY payee
ORDER BY total_spent DESC
LIMIT 20
```

### Expense Breakdown by Payee

```sql
SELECT
  payee,
  account,
  sum(convert(position, 'USD')) AS amount
WHERE
  account ~ 'Expenses:'
  AND year = 2024
GROUP BY payee, account
ORDER BY amount DESC
```

### Monthly Savings Rate

```sql
SELECT
  year, month,
  sum(position) WHERE account ~ 'Income:' AS income,
  sum(position) WHERE account ~ 'Expenses:' AS expenses,
  (sum(position) WHERE account ~ 'Income:') + 
  (sum(position) WHERE account ~ 'Expenses:') AS savings
WHERE
  year = 2024
GROUP BY year, month
ORDER BY year, month
```

### Cash Flow by Month

```sql
SELECT
  year, month,
  sum(position) WHERE account ~ 'Assets:' AS asset_changes,
  sum(position) WHERE account ~ 'Liabilities:' AS liability_changes
GROUP BY year, month
ORDER BY year, month
```

## Query Functions

### Aggregation Functions

- **sum(field)**: Sum of values
- **count(*)**: Count rows
- **first(field)**: First value
- **last(field)**: Last value
- **min(field)**: Minimum value
- **max(field)**: Maximum value

### Conversion Functions

**convert(position, 'CURRENCY')**
Converts position to specified currency at historical rates:
```sql
sum(convert(position, 'USD'))
```

**convert(position, 'CURRENCY', date)**
Converts at specific date:
```sql
sum(convert(position, 'USD', date))  -- Use market value at transaction date
```

**cost(position)**
Gets cost basis instead of market value:
```sql
sum(convert(cost(position), 'USD'))  -- Original purchase price
```

### Special Functions

**account_sortkey(account)**
Returns sort order of account by type (Assets=1, Liabilities=2, Equity=3, Income=4, Expenses=5):
```sql
WHERE account_sortkey(account) < 3  -- Only Assets and Liabilities
```

## Column Names

Common columns you can query:

- **date**: Transaction date
- **account**: Account name
- **payee**: Payee name
- **narration**: Transaction description
- **position**: Amount with currency
- **year**: Year from date
- **month**: Month from date (1-12)
- **day**: Day from date (1-31)
- **tags**: Set of tags
- **links**: Set of links

## Filtering (WHERE Clause)

### Exact Match
```sql
WHERE account = 'Assets:Bank:Checking'
WHERE payee = 'Grocery Store'
WHERE year = 2024
```

### Regex Match
```sql
WHERE account ~ 'Expenses:'          -- Starts with Expenses:
WHERE account ~ 'Food'                -- Contains Food
WHERE payee ~ '^Amazon'               -- Payee starts with Amazon
```

### Date Filtering
```sql
WHERE date >= 2024-01-01
WHERE date <= 2024-12-31
WHERE year = 2024
WHERE month = 6
WHERE year = 2024 AND month IN (6, 7, 8)  -- Summer months
```

### Tag/Link Filtering
```sql
WHERE 'vacation' IN tags
WHERE 'invoice-123' IN links
WHERE ANY_META('trip') = 'Europe-2024'
```

### Logical Operators
```sql
WHERE account ~ 'Expenses:' AND year = 2024
WHERE account = 'Assets:Checking' OR account = 'Assets:Savings'
WHERE NOT account ~ 'Income:'
```

### Nested Conditions
```sql
WHERE (account ~ 'Expenses:Food' OR account ~ 'Expenses:Dining')
  AND year = 2024
```

## Grouping (GROUP BY)

Group results by one or more columns:

```sql
GROUP BY account                    -- By account
GROUP BY year, month               -- By time period
GROUP BY payee, account            -- By payee and account
GROUP BY year, account             -- By year and account
```

## Sorting (ORDER BY)

```sql
ORDER BY date                       -- Ascending (oldest first)
ORDER BY date DESC                  -- Descending (newest first)
ORDER BY amount DESC                -- Largest first
ORDER BY year, month               -- Multiple columns
ORDER BY account ASC, amount DESC  -- Mixed directions
```

## Limiting Results (LIMIT)

```sql
LIMIT 10                           -- Top 10 results
LIMIT 50                           -- Top 50 results
```

## Conditional Aggregation

Sum only rows matching a condition:

```sql
SELECT
  sum(position) WHERE account ~ 'Income:' AS total_income,
  sum(position) WHERE account ~ 'Expenses:Food' AS food_expenses
```

## Advanced Patterns

### Year-over-Year Comparison

```sql
SELECT
  year,
  sum(position) WHERE account ~ 'Expenses:' AS expenses
GROUP BY year
ORDER BY year
```

### Quarterly Analysis

```sql
SELECT
  year,
  CASE
    WHEN month <= 3 THEN 'Q1'
    WHEN month <= 6 THEN 'Q2'
    WHEN month <= 9 THEN 'Q3'
    ELSE 'Q4'
  END AS quarter,
  sum(position) AS total
WHERE account ~ 'Expenses:'
GROUP BY year, quarter
ORDER BY year, quarter
```

### Running Balance

```sql
SELECT
  date,
  sum(position) AS daily_balance
WHERE
  account = 'Assets:Bank:Checking'
GROUP BY date
ORDER BY date
```

### Expense Categories as Percentage

```sql
SELECT
  account,
  sum(position) AS amount,
  sum(position) / (
    SELECT sum(position) 
    FROM postings 
    WHERE account ~ 'Expenses:' AND year = 2024
  ) * 100 AS percentage
WHERE
  account ~ 'Expenses:'
  AND year = 2024
GROUP BY account
ORDER BY amount DESC
```

### Average Transaction Size by Payee

```sql
SELECT
  payee,
  count(*) AS num_transactions,
  sum(position) AS total,
  sum(position) / count(*) AS avg_transaction
WHERE
  account ~ 'Expenses:'
  AND payee != ''
GROUP BY payee
HAVING count(*) >= 5  -- Only payees with 5+ transactions
ORDER BY total DESC
```

## Tips for Effective Queries

### Start Simple
Begin with a basic query and add complexity:
1. SELECT what you need
2. Add WHERE to filter
3. Add GROUP BY to aggregate
4. Add ORDER BY to sort
5. Test and refine

### Use Regex Wisely
- `~` for pattern matching
- `^` for start of string
- `$` for end of string
- `.*` for any characters

### Currency Conversion
Always use `convert()` when dealing with multiple currencies:
```sql
sum(convert(position, 'USD'))  -- Not just sum(position)
```

### Comment Your Queries
Use comments to document complex queries:
```sql
-- Monthly expense breakdown for 2024
-- Groups by category and shows percentage of total
SELECT ...
```

### Save Useful Queries
Save frequently-used queries as directives:
```beancount
2024-01-01 query "monthly-breakdown" "
  SELECT year, month, account, sum(position)
  WHERE account ~ 'Expenses:'
  GROUP BY year, month, account
"
```

### Test with LIMIT
When developing queries, use LIMIT to see sample results quickly:
```sql
SELECT * FROM postings LIMIT 10  -- Quick preview
```

## Query Performance

For large ledgers:
- Filter by date early (use WHERE year = 2024)
- Use specific account patterns (WHERE account = 'exact' is faster than WHERE account ~ 'pattern')
- Limit results when exploring data
- Consider splitting queries into smaller time ranges

## Common Errors

**"No implicit table"**: Add explicit columns to SELECT
```sql
-- Wrong: SELECT * WHERE account ~ 'Expenses:'
-- Right: SELECT date, account, position WHERE account ~ 'Expenses:'
```

**Currency mixing**: Use convert() for multi-currency queries
```sql
-- Wrong: sum(position)
-- Right: sum(convert(position, 'USD'))
```

**Regex syntax**: Remember to use ~ not LIKE
```sql
-- Wrong: WHERE account LIKE 'Expenses:%'
-- Right: WHERE account ~ 'Expenses:'
```
