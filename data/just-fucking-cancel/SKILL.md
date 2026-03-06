---
name: just-fucking-cancel
version: 1.2.0
description: Find and cancel unwanted subscriptions by analyzing bank transactions. Detects recurring charges, calculates annual waste, and provides cancel URLs. CSV-based analysis with optional Plaid integration for ClawdBot users.
author: ClawdBot
attribution: Originally created by rohunvora (https://github.com/rohunvora/just-fucking-cancel)
category: finance
tags:
  - subscriptions
  - cancel
  - money-saving
  - finance
  - budgeting
  - recurring-charges
  - personal-finance
env:
  - name: PLAID_CLIENT_ID
    description: Plaid client ID for transaction access (optional - only needed for Plaid integration)
    required: false
  - name: PLAID_SECRET
    description: Plaid secret key (optional - only needed for Plaid integration)
    required: false
  - name: PLAID_ACCESS_TOKEN
    description: User's Plaid access token for their connected bank account (optional)
    required: false
triggers:
  - cancel subscriptions
  - audit subscriptions
  - find recurring charges
  - what am I paying for
  - subscription cleanup
  - save money
---

# Just Fucking Cancel

Analyze transactions, categorize subscriptions, generate HTML audit, help cancel.

## How It Works

This skill analyzes your transaction history to find recurring charges (subscriptions), helps you categorize them, and provides direct cancel URLs. **No automated cancellation** - you control every action.

```
Transaction Data → Pattern Detection → User Categorization → HTML Audit → Cancel URLs
```

## Triggers

- "cancel subscriptions", "audit subscriptions"
- "find recurring charges", "what am I paying for"
- "subscription audit", "clean up subscriptions"

## Data Sources

### Option A: CSV Upload (Recommended - Fully Local)

Upload a transaction CSV from your bank. **All processing happens locally** - no data leaves your machine.

Supported formats:
- **Apple Card**: Wallet → Card Balance → Export
- **Chase**: Accounts → Download activity → CSV
- **Amex**: Statements & Activity → Download → CSV
- **Citi**: Account Details → Download Transactions
- **Bank of America**: Activity → Download → CSV
- **Capital One**: Transactions → Download
- **Mint / Copilot**: Transactions → Export

### Option B: Plaid Integration (ClawdBot Only)

If you have ClawdBot with Plaid connected, transactions can be pulled automatically.

**Important**: This requires Plaid credentials and sends data to Plaid's servers:
- `PLAID_CLIENT_ID` - Your Plaid client ID
- `PLAID_SECRET` - Your Plaid secret key
- `PLAID_ACCESS_TOKEN` - Access token for the bank connection

**Privacy note**: When using Plaid, transaction data is transmitted to Plaid's API. CSV analysis is fully local.

## Workflow

### 1. Get Transactions
- CSV: User uploads file, analyzed locally
- Plaid: Pull last 6-12 months via API (requires credentials)

### 2. Analyze Recurring Charges
- Detect same merchant, similar amounts, monthly/annual patterns
- Flag subscription-like charges (streaming, SaaS, memberships)
- Calculate charge frequency and total annual cost

### 3. Categorize with User
For each subscription, ask user to categorize:
- **Cancel** - Stop immediately
- **Investigate** - Needs decision (unsure, trapped in contract)
- **Keep** - Intentional, continue paying

Ask in batches of 5-10 to avoid overwhelming.

### 4. Generate HTML Audit
Create interactive HTML report with:
- Summary: subscriptions found, total waste, potential savings
- Sections: Cancelled / Needs Decision / Keeping
- Privacy toggle to blur service names
- Dark mode support

### 5. Provide Cancel URLs
For each service to cancel:
1. Look up direct cancel URL from [common-services.md](references/common-services.md)
2. Provide URL to user - **user navigates manually**
3. Include dark pattern warnings and tips

**No automated browser interaction** - this skill provides URLs and guidance only. You control the actual cancellation.

## HTML Structure

Three sections, auto-hide when empty:
- **Cancelled** (green badge, strikethrough) - Done items
- **Needs Decision** (orange badge) - Has checkboxes for selection
- **Keeping** (grey badge) - Reference only

Features:
- Floating copy button for selected items
- Privacy toggle blurs service names
- Collapsible sections
- Dark mode support

## Cancellation Tips

See [common-services.md](references/common-services.md) for:
- Direct cancel URLs for 50+ services
- Dark pattern warnings (gym contracts, phone-only)
- Retention script responses
- Credit card dispute backup

## Privacy Summary

| Data Source | Where Processed | Data Leaves Device? |
|-------------|-----------------|---------------------|
| CSV Upload | Local only | No |
| Plaid API | Plaid servers | Yes (to Plaid) |

## Related

- `plaid` - Bank account connection
- `ynab` - Budget tracking
- `copilot` - Financial insights
