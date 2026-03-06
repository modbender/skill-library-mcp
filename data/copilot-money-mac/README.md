# Copilot Money Skill

A Claude Code skill for querying personal finance data from the [Copilot Money](https://copilot.money) Mac app.

## What It Does

This skill enables Claude to access and analyze your financial data stored locally by Copilot Money, including:

- Transaction history and spending patterns
- Account balances over time
- Category-based expense analysis
- Recurring transaction definitions (rent, subscriptions, etc.)
- Budget amounts and investment data

## Requirements

- macOS with Copilot Money app installed
- Copilot Money must have synced data locally (the app stores data in SQLite and Firestore LevelDB cache)

## Example Uses

- "How much did I spend on restaurants last month?"
- "Show me my largest transactions this year"
- "What's my monthly spending trend?"
- "Find all Amazon purchases"

## Data Locations

**SQLite Database** (transactions, balances):
```
~/Library/Group Containers/group.com.copilot.production/database/CopilotDB.sqlite
```

**Firestore LevelDB Cache** (recurring names, budgets, investments):
```
~/Library/Containers/com.copilot.production/Data/Library/Application Support/firestore/__FIRAPP_DEFAULT/copilot-production-22904/main/*.ldb
```

## Privacy Note

All data stays local - this skill queries the local databases directly on your Mac. No data is sent to external services.
