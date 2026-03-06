# Credit Cards

## How credit cards work in Actual Budget

Credit card accounts are on-budget accounts with a negative balance. Actual treats them like any other account — the negative balance is subtracted from your positive deposit account balances to give your total on-budget funds.

When you make a credit card purchase and categorize it, the money comes from that budget category (just like a debit card purchase). The only difference is the timing of when the actual cash leaves your checking account (when you pay the credit card bill).

**Key insight:** If every credit card purchase is categorized to a funded budget category, you will always have enough money to pay the bill. The budget already accounted for the spending.

## Strategy: Paying in Full (Within the Budget)

Use this when you pay off your credit card statement every month.

### Rules

- Never over-budget. Only budget funds you actually have
- Check your category balance before spending
- Enter purchase transactions promptly
- Cover all overspending by moving money between categories
- Reconcile accounts at least monthly
- Pay at least your statement balance before the due date

### Setup

1. Confirm the account is a credit card (not checking/savings) before creating it.

2. Create the credit card as an on-budget account with a negative starting balance. Include account type in the name:

```bash
fscl accounts create "Chase Credit 5736" --balance -35.00
```

3. No special budget category needed — each purchase uses your regular expense categories

### Monthly workflow

1. Throughout the month, categorize every credit card purchase to a funded category
2. When the statement arrives, note the New Balance
3. Reconcile the account
4. Pay the statement balance as a linked transfer from checking:

```bash
# Add/import the payment on checking
fscl transactions add <checking-acct-id> --date 2026-02-15 --amount -213.15 \
  --payee "CHASE PAYMENT" --notes "Statement payment"

# Convert matching entries into linked transfers by setting payee to the transfer payee
# (find <chase-transfer-payee-id> via "fscl payees list", where transfer_acct=<chase-acct-id>)
fscl rules create '{
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    {"field": "account", "op": "is", "value": "<checking-acct-id>"},
    {"field": "imported_payee", "op": "contains", "value": "CHASE PAYMENT"}
  ],
  "actions": [
    {"field": "payee", "op": "set", "value": "<chase-transfer-payee-id>"}
  ]
}'
fscl rules run --dry-run
fscl rules run
```

## Strategy: Carrying Debt

Use this when you have a credit card balance you cannot pay in full. The goal is to pay it off safely without incurring more debt.

### Setup

1. Create a "Credit Card Debt" category group:

```bash
fscl categories create-group "Credit Card Debt"
```

2. Create a debt category for each card carrying debt:

```bash
fscl categories create "Citi Card Debt" --group <debt-group-id>
fscl categories create "DEMO Card Debt" --group <debt-group-id>
```

3. Enable rollover overspending on each debt category:

```bash
fscl month set-carryover 2026-02 <citi-debt-cat-id> true
fscl month set-carryover 2026-02 <demo-debt-cat-id> true
```

4. Create the credit card account with the total amount owed as the starting balance, categorized to the debt category. Include account type in the name:

```bash
fscl accounts create "Citibank Credit 4455" --balance -2590.00
```

The starting balance transaction should be categorized to the debt category.

### Why rollover is needed

Negative credit card account balances are already subtracted from your available on-budget funds. Without rollover, the negative debt category balance would also be deducted from "To Budget" — double-counting the debt. Rollover prevents this.

### Monthly workflow (card with debt, no new purchases)

1. At the start of the month, budget the expected minimum payment to the debt category:

```bash
fscl month set 2026-02 <citi-debt-cat-id> 90.00
```

2. If you have extra money after funding all expenses, add it to the debt category to pay down faster:

```bash
fscl month set 2026-02 <citi-debt-cat-id> 290.00  # 90 minimum + 200 extra
```

3. When the statement arrives, enter interest and fees as a transaction categorized to the debt category:

```bash
fscl transactions add <citi-acct-id> --date 2026-02-10 --amount -64.00 \
  --payee "Citibank" --category <citi-debt-cat-id> --notes "Interest charge"
```

4. Make the payment as a linked transfer from checking:

```bash
fscl transactions add <checking-acct-id> --date 2026-02-15 --amount -290.00 \
  --payee "CITIBANK PAYMENT" --notes "CC payment"

# Rule converts payee text to the card transfer payee ID
fscl rules create '{
  "stage": null,
  "conditionsOp": "and",
  "conditions": [
    {"field": "account", "op": "is", "value": "<checking-acct-id>"},
    {"field": "imported_payee", "op": "contains", "value": "CITIBANK PAYMENT"}
  ],
  "actions": [
    {"field": "payee", "op": "set", "value": "<citi-transfer-payee-id>"}
  ]
}'
fscl rules run --dry-run
fscl rules run
```

### Monthly workflow (card with debt AND new purchases)

If you must use a card that has existing debt:

1. Categorize new purchases to regular funded budget categories (staying Within the Budget)
2. When the statement arrives, enter interest/fees to the debt category
3. Reconcile the account
4. Calculate payment:
   - **Payment = New Purchases - Return Credits + Uncleared Total + Budgeted Column**
   - Or equivalently: **Account Balance - Debt Category Balance** (using absolute values)
5. The minimum payment must be at least the statement minimum

### Paying off the highest interest first

When carrying debt on multiple cards:
- Budget minimum payments for all cards
- After funding all necessary expenses, add extra to the highest-interest card
- Once the highest-interest card is paid off, redirect that extra payment to the next highest
- Use only one card for new purchases and pay it in full monthly

### Important notes

- All credit card accounts should be **on-budget** (not off-budget)
- Include account type in the account name (for example, `Chase Credit 5736`) so account context stays clear in future chats
- You cannot change an off-budget account to on-budget — set it correctly from the start
- Only set a credit card as off-budget if there will be no new purchases and the account will be closed once paid off
- A credit limit is not an invitation to spend it
- If you lose your grace period due to late payment, you'll incur interest from purchase date on all new purchases until you pay in full for several consecutive months
