# Budgeting Concepts

Envelope budgeting mechanics, category strategy, and special scenarios for Actual Budget.

## Category Templates

Use these as starting points. Adapt based on what the user tells you about their life. Don't create categories they won't use — you can always add more later.

### Single person, renting

```
Housing:          Rent, Utilities, Internet, Renter's Insurance
Food:             Groceries, Dining Out, Coffee
Transportation:   Gas/Transit, Car Insurance, Car Maintenance, Parking
Personal:         Clothing, Personal Care, Health/Medical, Subscriptions
Lifestyle:        Entertainment, Hobbies, Gifts
Financial:        Savings, Emergency Fund, Investments
Income:           Salary, Side Income
```

### Single person, homeowner

Add to the above:
```
Housing:          Mortgage, Property Tax, HOA, Home Insurance, Home Maintenance
```
Remove: Rent, Renter's Insurance

### Couple, shared budget

```
Housing:          Rent/Mortgage, Utilities, Internet, Insurance
Shared Living:    Groceries, Household Supplies, Dining Out
Transportation:   Gas/Transit, Car Insurance, Maintenance
Kids (if any):    Childcare, School, Activities, Kids Clothing
Personal - [Name A]: Clothing, Personal Care, Hobbies, Fun Money
Personal - [Name B]: Clothing, Personal Care, Hobbies, Fun Money
Financial:        Emergency Fund, Savings Goals, Investments
Debt (if any):    [Card Name] Debt
Income:           [Name A] Income, [Name B] Income, Partner Contributions
```

### Freelancer / variable income

Add:
```
Business:         Equipment, Software, Professional Services, Business Travel
Taxes:            Estimated Taxes, Tax Prep
```

Key difference: Budget conservatively using the lowest expected monthly income. In good months, put extra toward savings or taxes.

## Category Management

### Category groups

Categories are organized into groups.

```bash
# Create a group
fscl categories create-group "Fixed Expenses"

# Create categories in the group
fscl categories create "Rent" --group <group-id>
fscl categories create "Utilities" --group <group-id>
fscl categories create "Internet" --group <group-id>
```

### Merging categories

If you have duplicate or redundant categories, delete one and transfer its transactions:

```bash
# Move all "Foods" transactions to "Food", then delete "Foods"
fscl categories delete <foods-id> --transfer-to <food-id> --yes
```

### Income categories

Create income categories in the income group:

```bash
fscl categories create "Salary" --group <income-group-id> --income
fscl categories create "Freelance" --group <income-group-id> --income
```

## Month Setup

The fastest way to set up a new month is to copy from the previous month:

```bash
fscl month copy 2026-01 2026-02
```

Alternatively, use `month draft` + `month apply` for selective editing, or templates for automated budgeting.

## Goal Templates

Use category-level templates to automate month setup.

```bash
# Generate editable template draft
fscl month templates draft
# Edit templates.json (add/update template arrays)
fscl month templates apply --dry-run
fscl month templates apply

# Validate + apply for the month
fscl month templates check
fscl month templates run 2026-03
```

## Income Handling

When you receive income:

- It becomes immediately available to budget (appears in "Available Funds" / "To Budget")
- If you don't budget it this month, it rolls over to next month
- Common strategy: "hold" current month's income for next month's budget, so you're always budgeting with last month's income

Using fscl, income shows up as a positive-amount transaction categorized to an income category.

## Overspending

When you overspend in a category (balance goes negative):

- **Default behavior:** The negative balance is automatically deducted from next month's "To Budget" amount, and the category balance resets to zero
- This means overspending reduces your ability to budget next month
- To handle it: move money from another category to cover the overspent amount, or accept that next month will have less to budget

### Rollover overspending (carryover)

Sometimes you want to keep a negative balance across months (e.g., tracking reimbursable expenses). Enable per-category:

```bash
fscl month set-carryover 2026-02 <category-id> true
```

When rollover is enabled, the negative balance stays in the category instead of being deducted from "To Budget."

## Returns and Reimbursements

### Returns

A return is not income — it goes back to the category you originally spent from. Enter the return as a positive-amount transaction with the same category:

```bash
fscl transactions add <acct-id> --date 2026-02-10 --amount 32.99 \
  --payee "Amazon" --category <clothing-cat-id> --notes "Sandals return"
```

This restores $32.99 to the Clothing category balance.

### Reimbursements

For reimbursable expenses (business travel, shared costs):

1. Create a dedicated category (e.g., "Business Expenses")
2. **Option A: Pre-fund** — Budget money into the category before spending. True zero-budget approach.
3. **Option B: Carry negative** — Let the category go negative, enable rollover overspending, and refill when reimbursed.

```bash
# Create category and enable carryover
fscl categories create "Business Expenses" --group <group-id>
fscl month set-carryover 2026-02 <biz-exp-cat-id> true

# Spend (category goes negative if not pre-funded)
fscl transactions add <acct-id> --date 2026-02-05 --amount -150.00 \
  --payee "Hotel" --category <biz-exp-cat-id> --notes "Client trip"

# Receive reimbursement (positive amount, same category)
fscl transactions add <acct-id> --date 2026-02-20 --amount 150.00 \
  --payee "Employer" --category <biz-exp-cat-id> --notes "Trip reimbursement"
```

## Joint Accounts

### Shared budget (recommended for committed couples)

Both partners use the same budget file. Sync via an Actual Budget server so both can access it.

Setup:
1. Create a joint checking account
2. Use the shared budget on a synced server
3. Create a "Partner Personal Spending" category (with rollover) for tracking personal purchases made on the shared account
4. Track income contributions via a "Partners Contributions" income category

### Personal budget with shared account

Track your partner's contributions in your own budget:

1. Create the joint account on-budget
2. Your transfers to the joint account don't need a category (on-budget to on-budget transfer)
3. Your partner's deposits are categorized as income (use a "Partner Contribution" income category)
4. Budget the full bill amounts in shared expense categories

### Contribution strategy

For proportional contributions based on income:
- If Partner A earns $4,000/month and Partner B earns $6,000/month
- Total = $10,000. Partner A contributes 40%, Partner B contributes 60%
- If shared expenses are $3,000/month: A pays $1,200, B pays $1,800
