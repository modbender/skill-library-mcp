# Workflow: Budget Maintenance

The budget is established and the user is using it day-to-day. Handle their requests and run the monthly cycle.

## Monthly Cycle

The complete monthly routine. Run these steps when the user imports new transactions or at the start of a new month.

### 1. Import Transactions

```bash
fscl transactions import <account-id> <file> --report
```

For CSV files with custom columns, see [import-guide.md](import-guide.md). Always preview first with `--dry-run` if it's a new format.

### 2. Run Rules

```bash
fscl rules run --and-commit
```

### 3. Clean Up Payees

Review uncategorized transactions for messy or duplicate payee names:

```bash
fscl transactions uncategorized --json
fscl payees update <id> --name "Clean Name"
fscl payees merge <target-id> <dup-ids...>
```

### 4. Categorize Remaining

```bash
fscl transactions categorize draft
# Fill in category IDs using _meta context
# Do not create categorize.json manually; edit the generated draft file
fscl transactions categorize apply
```

### 5. Create Rules for New Patterns

Any payee appearing 2+ times with the same category should get a rule. See [rules.md](rules.md).

```bash
fscl rules draft
# Add new rules (no id), update existing (with id)
fscl rules apply
fscl rules run --and-commit
```

### 6. Review Budget

```bash
fscl month status --compare 3 --json
fscl month status --only over --json
```

Lead with what matters:
1. Categories that are overspent or near limit
2. Total spent vs total budgeted
3. "To Budget" amount
4. Trends compared to previous months

### 7. Adjust Budget

Move money between categories to cover overages:

```bash
fscl month set <month> <overspent-cat> <new-amount>
fscl month set <month> <surplus-cat> <reduced-amount>
```

Or use draft/apply for bulk changes:

```bash
fscl month draft <month>
# Edit amounts
fscl month apply <month>
```

### 8. New Month Setup

```bash
# Apply templates if configured
fscl month templates check
fscl month templates run <next-month>

# Or draft/apply manually
fscl month draft <next-month>
fscl month apply <next-month>

# Optional: end-of-month cleanup
fscl month cleanup <prev-month>
```

## Common Scenarios

### "How am I doing this month?"

For a quick health check, use compact status: `fscl status --compact --json`. For a full review:

```bash
fscl month status --month <current> --compare 3 --json
fscl month status --month <current> --only over --json
fscl transactions uncategorized --json
```

Present a summary:
> **February Budget Check-in**
> - Spent $2,340 of $3,200 (73%) with 2 weeks left
> - **Watch out:** Dining Out at $185 of $200 (92%)
> - **On track:** Groceries at $290 of $500 (58%)
> - **Under budget:** Transportation at $45 of $150 (30%)
> - 3 uncategorized transactions need attention
> - Compared to the last 3 months, dining spending is up 15%

### "I overspent on [category]"

1. Check how much they're over
2. Find categories with surplus: `fscl month show <month> --json`
3. Suggest a transfer: "You're $45 over on Dining. Entertainment has $80 left. Want me to move $45?"
4. If no surplus anywhere, explain the overspending will reduce next month's available budget
5. After handling it, consider if the budget needs a permanent adjustment

### "I just got paid"

1. Check if the income transaction was imported or needs manual entry
2. Show updated "To Budget" amount
3. If following a month-ahead strategy, this income funds next month's budget
4. If not month-ahead yet, allocate to current month's underfunded categories

### "I want to save for [goal]"

1. Create a savings category: `fscl categories create "Vacation Fund" --group <savings-group-id>`
2. Calculate monthly contribution: goal amount / months
3. Budget it: `fscl month set <month> <vacation-id> 300.00`
4. Track and report progress each month: "You've saved $900 of $3,000 (30%). At $300/month, you'll reach it by November."

### "I returned something"

Enter as a positive-amount transaction in the original expense category — this restores the category balance:

```bash
fscl transactions add <acct-id> --date <date> --amount 32.99 \
  --payee "Amazon" --category <clothing-id> --notes "Return"
```

### "Import my bank transactions"

See [import-guide.md](import-guide.md). Always preview with `--dry-run` first. For CSV files, ask what the columns mean and use `--csv-date-col`, `--csv-amount-col`, `--csv-payee-col` to map them.

### Credit card questions

See [credit-cards.md](credit-cards.md).

### Shared expenses

See [budgeting.md](budgeting.md) for joint account and partner contribution strategies.

### "My balance doesn't match the bank"

When fscl's account balance differs from the user's bank balance:

1. Check the account balance with a cutoff date matching the bank statement: `fscl accounts balance <id> --cutoff <statement-date> --json`
2. Compare to the bank's statement balance
3. If they differ, common causes:
   - **Pending transactions:** Bank shows pending charges not yet imported — wait for them to clear and re-import
   - **Duplicate import:** Same file imported twice — find and delete duplicates: `fscl transactions list <id> --start <date> --end <date> --json`
   - **Missing transactions:** Manual entries not recorded — add them with `fscl transactions add`
   - **Wrong amount:** A transaction was entered incorrectly — fix with `fscl transactions edit draft` / `edit apply`
4. After fixing, verify: `fscl accounts balance <id> --json`

## Proactive Monitoring

Flag these issues without being asked:

**Immediate:**
- Overspent categories (negative balance)
- Large uncategorized transactions (>$100)
- Negative "To Budget" (over-budgeted)
- Overdue schedules

**Monthly:**
- Categories consistently over/under budget for 2-3 months → suggest permanent adjustment
- Unused categories (2+ months with $0 spent) → suggest removal
- Payees appearing 3+ times without a rule → create one
- Duplicate payees → merge

**Quarterly:**
- Spending trends across months (use [query-library.md](query-library.md) for trend queries)
- Savings goal progress
- Debt paydown progress (if applicable)
