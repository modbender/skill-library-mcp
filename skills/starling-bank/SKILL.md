---
name: starling-bank
description: Manage Starling Bank accounts via the starling-bank-mcp server. Check balances, list transactions, create payees, make payments, manage savings goals, and track spending. Use when the user asks about their bank balance, transactions, payments, savings, direct debits, standing orders, or any Starling Bank operation. Requires the starling-bank-mcp npm package and a Starling personal access token.
---

# Starling Bank

Manage Starling Bank accounts through mcporter + starling-bank-mcp.

## Setup

### 1. Install the MCP server

```bash
npm i -g starling-bank-mcp
```

### 2. Get a Personal Access Token

Create one at https://developer.starlingbank.com/ (Personal Access Token with required scopes).

### 3. Configure mcporter

```bash
mcporter config add starling \
  --command "node $(npm root -g)/starling-bank-mcp/dist/main.js" \
  --env STARLING_BANK_ACCESS_TOKEN="YOUR_TOKEN"
```

### 4. Verify

```bash
mcporter list starling --schema
```

## Quick Reference

### Account basics

```bash
# List accounts (get accountUid and default categoryUid)
mcporter call starling.accounts_list

# Get balance
mcporter call starling.account_balance_get accountUid=ACCOUNT_UID

# Get account holder info
mcporter call starling.account_holder_get

# Get sort code / account number
mcporter call starling.account_identifiers_get accountUid=ACCOUNT_UID
```

### Transactions

```bash
# List transactions (ISO 8601 timestamps required)
mcporter call starling.transactions_list \
  accountUid=ACCOUNT_UID \
  categoryUid=CATEGORY_UID \
  minTransactionTimestamp=2026-01-01T00:00:00.000Z \
  maxTransactionTimestamp=2026-01-31T23:59:59.999Z

# Get single transaction detail
mcporter call starling.feed_item_get \
  accountUid=ACCOUNT_UID \
  categoryUid=CATEGORY_UID \
  feedItemUid=FEED_ITEM_UID
```

### Payments

```bash
# List payees
mcporter call starling.payees_list

# Create payee
mcporter call starling.payee_create \
  payeeName="John Smith" \
  payeeType=INDIVIDUAL \
  accountIdentifier=12345678 \
  bankIdentifier=608371 \
  bankIdentifierType=SORT_CODE \
  countryCode=GB

# Make payment (amount in minor units / pence)
mcporter call starling.payment_create \
  accountUid=ACCOUNT_UID \
  categoryUid=CATEGORY_UID \
  destinationPayeeAccountUid=PAYEE_ACCOUNT_UID \
  reference="Payment ref" \
  --args '{"amount":{"currency":"GBP","minorUnits":1000}}'
```

### Savings Goals

```bash
# List goals
mcporter call starling.savings_goals_list accountUid=ACCOUNT_UID

# Create goal
mcporter call starling.savings_goal_create \
  accountUid=ACCOUNT_UID name="Emergency Fund" currency=GBP \
  --args '{"target":{"currency":"GBP","minorUnits":100000}}'

# Deposit into goal
mcporter call starling.savings_goal_deposit \
  accountUid=ACCOUNT_UID savingsGoalUid=GOAL_UID \
  --args '{"amount":{"currency":"GBP","minorUnits":5000}}'

# Withdraw from goal
mcporter call starling.savings_goal_withdraw \
  accountUid=ACCOUNT_UID savingsGoalUid=GOAL_UID \
  --args '{"amount":{"currency":"GBP","minorUnits":5000}}'
```

### Other

```bash
# Direct debits
mcporter call starling.direct_debits_list accountUid=ACCOUNT_UID

# Standing orders
mcporter call starling.standing_orders_list \
  accountUid=ACCOUNT_UID categoryUid=CATEGORY_UID

# Cards
mcporter call starling.cards_list

# Lock/unlock card
mcporter call starling.card_lock_update cardUid=CARD_UID enabled=false
```

## Workflow: First-Time Setup

1. Run `accounts_list` to get `accountUid` and `defaultCategory` (categoryUid)
2. Save these IDs — they're needed for most operations
3. Run `account_balance_get` to verify access works
4. Store account details in your memory/config for future use

## Notes

- All amounts are in **minor units** (pence). £10.50 = 1050
- Timestamps must be **ISO 8601** format: `2026-02-17T00:00:00.000Z`
- `categoryUid` = the `defaultCategory` from `accounts_list` for main account transactions
- Balance fields: `clearedBalance` (settled), `effectiveBalance` (including pending)
- See [references/api-details.md](references/api-details.md) for full tool schemas
