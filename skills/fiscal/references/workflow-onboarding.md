# Workflow: New Budget Onboarding

Guide the user through setting up their first budget. This is a conversation — ask questions, explain decisions, and take action on their behalf.

## Step 1: Understand Their Situation

Ask these questions (adapt based on what they volunteer):

1. **Accounts:** "What accounts do you have? For each one, tell me institution, account type (checking/savings/credit card), last 4 digits or nickname, and current balance."
2. **Income:** "What's your monthly take-home pay? If it varies, use your lowest typical month."
3. **Fixed expenses:** "What bills are the same every month? (rent, insurance, subscriptions, car payment, etc.)"
4. **Debt:** "Are you carrying any credit card balances you can't pay off in full this month?"
5. **Lifestyle:** Use their answers to infer a persona (single renter, homeowner, couple, freelancer) for category template selection.

Don't ask everything at once — start with accounts and income, then drill into expenses as you build the budget. If any account type is unclear, ask a follow-up before creating accounts.

## Step 2: Create Accounts

Create every account they mention. Use negative balances for credit cards (the amount owed).

Normalize account names to include account type so future sessions stay unambiguous:

- `<Institution> <Type> <Last4-or-nickname>`
- Examples: `Chase Checking 5736`, `Ally Savings 1120`, `AmEx Credit 1008`

```bash
fscl accounts create-batch '[
  {"name": "Chase Checking 5736", "balance": "3500.00"},
  {"name": "Ally Savings 1120", "balance": "12000.00"},
  {"name": "Chase Credit 8891", "balance": "-840.00"}
]'
```

Credit cards must be on-budget (the default). If they have credit card debt they can't pay in full, see [credit-cards.md](credit-cards.md) for the debt tracking setup (rollover category + carryover flag).

## Step 3: Set Up Categories

Select a template from [budgeting.md](budgeting.md) based on their persona. Adapt it — remove categories they won't use, add ones they mention.

```bash
# Create groups
fscl categories create-group "Fixed Expenses"
fscl categories create-group "Food"
fscl categories create-group "Transportation"
fscl categories create-group "Personal"
fscl categories create-group "Savings & Goals"

# Generate full tree draft, then edit
fscl categories draft
# Edit categories.json:
# - top-level rows are category groups; nested rows are categories (not nested categories)
# - add rows without id to create groups/categories
# - change name on rows with id to rename
# - move category rows between groups to reassign
fscl categories apply --dry-run
fscl categories apply
```

Present the proposed categories to the user before creating: "Based on what you've told me, here's how I'd organize your budget. Does this look right?"

## Step 4: Set Initial Budget Amounts

Use their income and fixed expenses to build the first budget. As a starting point, apply the 50/30/20 split:

| Bucket | % of Income | What goes here |
|---|---|---|
| **Needs** | 50% | Housing, utilities, groceries, insurance, transportation |
| **Wants** | 30% | Dining, entertainment, subscriptions, hobbies |
| **Savings** | 20% | Emergency fund, savings goals, extra debt payments |

Start with known fixed expenses (rent, insurance, car payment). Subtract from income to see what's left for variable categories. Budget variable categories conservatively. Put the remainder toward savings.

```bash
fscl month draft <current-month>
# Edit the draft — set amount for each category as a decimal string (e.g. "500.00")
fscl month apply <current-month>
```

Present a summary before applying: "Here's your budget for February — does this look right?"

Tell the user: **"This is a starting point. After a month of tracking actual spending, we'll adjust based on real numbers."**

Verify the budget:

```bash
fscl month show <current-month> --json
```

## Step 5: Import Transactions

Ask: "Do you have any bank export files? Most banks let you download OFX, QFX, or CSV files from the last few months. This helps us see where your money has been going."

If they don't have files yet, give them directions:
- "Log into each bank account online"
- "Look for 'Download Transactions' or 'Export' — choose OFX or QFX if available, CSV as fallback"
- "Download the last 1-2 months"
- "Come back with the files and I'll import them"

If they have files:

```bash
# Preview first
fscl transactions import <account-id> <file> --dry-run --report

# Import
fscl transactions import <account-id> <file> --report
```

For CSV files that need column mapping, see [import-guide.md](import-guide.md).

## Step 6: Process Imported Transactions

After import, clean up in this order — payees first, then categorize, then rules:

```bash
# 1. Run any existing rules
fscl rules run --and-commit

# 2. Review uncategorized transactions for messy payee names
fscl transactions uncategorized --json

# 3. Clean payees — rename ugly bank names, merge duplicates
fscl payees update <id> --name "Whole Foods"
fscl payees merge <clean-id> <duplicate-id-1> <duplicate-id-2>

# 4. Categorize remaining uncategorized transactions
fscl transactions categorize draft
# Fill in category IDs in categorize.json using _meta context
# Do not hand-create categorize.json; edit the file generated by the draft command
fscl transactions categorize apply

# 5. Create rules for recurring payees so future imports auto-categorize
fscl rules draft
# Add new rules (rows without id), update existing (rows with id)
fscl rules apply
fscl rules run --and-commit
```

For rule creation patterns (pre-stage payee cleanup + default-stage categorization), see [rules.md](rules.md).

Report results to the user: "I imported 47 transactions. 39 were auto-categorized by rules. I categorized 6 more and need your input on 2."

## What's Next

Once setup is complete, tell the user:
- "Your budget is set up! Going forward, import new transactions periodically and I'll help categorize them."
- "At the start of each month, we'll review your spending and set the next month's budget."
- "The more transactions you import, the smarter the rules get — eventually most categorization happens automatically."
