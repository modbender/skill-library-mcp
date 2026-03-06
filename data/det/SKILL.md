---
name: det
description: DailyExpenseTracker API integration for recording expenses, checking balances, and managing transactions. Use when user mentions expenses, spending, transactions, wallets, or DET.
---

# DailyExpenseTracker (DET)

## API

**Base URL:** `https://dailyexpensetracker.in/api`
**Token:** Set in `skills.entries.det.apiToken` in openclaw.json
**Auth Header:** `Authorization: Bearer <token>`

## Wallets

Fetch wallets dynamically via `/api/wallets` endpoint. Cache wallet IDs locally after first fetch.

## Add Expense

```bash
curl -X POST "https://dailyexpensetracker.in/api/transactions" \
  -H "Authorization: Bearer $DET_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_id": 1,
    "category_id": 5,
    "amount": 100,
    "type": "expense",
    "transaction_date": "2026-02-21",
    "description": "Groceries"
  }'
```

**Required fields:** wallet_id, amount, type, transaction_date
**Types:** expense, income, transfer

## Get Transactions

```bash
curl "https://dailyexpensetracker.in/api/transactions?per_page=10" \
  -H "Authorization: Bearer $DET_TOKEN"
```

## Get Wallets with Balances

```bash
curl "https://dailyexpensetracker.in/api/wallets" \
  -H "Authorization: Bearer $DET_TOKEN"
```

## Get Categories

```bash
curl "https://dailyexpensetracker.in/api/categories" \
  -H "Authorization: Bearer $DET_TOKEN"
```

## Rules

- **ALWAYS use API** - Never write directly to database
- **Field is `transaction_date`** - Not `date`
- **Default wallet:** HDFC BANK (1) unless specified
- **Confirm large amounts** (>₹5000) before recording
