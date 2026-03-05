---
name: accountsos
description: AI-native accounting for UK micro-businesses. Use when the user wants to track transactions, manage VAT, check deadlines, or do any bookkeeping for a UK limited company.
compatibility: Requires ACCOUNTSOS_API_KEY environment variable. Works on all platforms. Network access required to accounts-os.com API.
metadata:
  author: thriveventurelabs
  version: "1.2.0"
  homepage: https://accounts-os.com
  openclaw:
    category: finance
    api_base: https://accounts-os.com
    requires:
      env: ["ACCOUNTSOS_API_KEY"]
---

# AccountsOS

AI-native accounting. Your agent runs the books so your human doesn't have to.

**Base URL:** `https://accounts-os.com/api/mcp`

## What is AccountsOS?

AccountsOS is accounting infrastructure for AI agents. Built for UK micro-businesses (Ltd companies, sole traders):

- **Transaction tracking** — Income, expenses, categorized automatically
- **VAT management** — Calculate returns, track what's owed
- **Deadline alerts** — Corporation tax, VAT, confirmation statements
- **Document storage** — Receipts, invoices, contracts
- **AI categorization** — Smart category suggestions for every transaction

No spreadsheets. No manual entry. Just tell your agent what happened.

## Quick Start (For AI Agents)

### 1. Get API Key

**Option A: Self-Signup (recommended)** — Create an account yourself with one request:

```bash
curl -X POST https://accounts-os.com/api/agent-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "founder@example.com",
    "company_name": "Acme Ltd",
    "full_name": "Jane Smith"
  }'
```

Response includes `api_key` for immediate use. Your human gets a welcome email to claim the account.

**Option B: Manual** — Your human signs up at https://accounts-os.com and generates an API key from the dashboard.

```bash
export ACCOUNTSOS_API_KEY="sk_live_..."
```

### 2. Check the Books

```bash
# Get recent transactions
curl -X POST https://accounts-os.com/api/mcp \
  -H "Authorization: Bearer $ACCOUNTSOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "tool", "name": "get_transactions", "arguments": {"limit": 10}}'
```

### 3. Record a Transaction

```bash
curl -X POST https://accounts-os.com/api/mcp \
  -H "Authorization: Bearer $ACCOUNTSOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "tool",
    "name": "create_transaction",
    "arguments": {
      "date": "2026-02-01",
      "description": "Client payment - Website project",
      "amount": 2500.00,
      "direction": "in"
    }
  }'
```

### 4. Check VAT Position

```bash
curl -X POST https://accounts-os.com/api/mcp \
  -H "Authorization: Bearer $ACCOUNTSOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "tool", "name": "get_vat_summary", "arguments": {}}'
```

---

## API Reference

AccountsOS uses an MCP-style API. All requests go to `/api/mcp` with a JSON body specifying the tool or resource.

### Authentication

```bash
Authorization: Bearer your_api_key
Content-Type: application/json
```

### Tools (Actions)

**Get transactions:**
```json
{
  "type": "tool",
  "name": "get_transactions",
  "arguments": {
    "from_date": "2026-01-01",
    "to_date": "2026-01-31",
    "direction": "in",
    "limit": 50
  }
}
```

**Get balance:**
```json
{
  "type": "tool",
  "name": "get_balance",
  "arguments": {"account_id": "optional"}
}
```

**Get VAT summary:**
```json
{
  "type": "tool",
  "name": "get_vat_summary",
  "arguments": {"quarter": "Q4 2025"}
}
```

**Get deadlines:**
```json
{
  "type": "tool",
  "name": "get_deadlines",
  "arguments": {"include_completed": false}
}
```

**Create transaction:**
```json
{
  "type": "tool",
  "name": "create_transaction",
  "arguments": {
    "date": "2026-02-01",
    "description": "AWS hosting - January",
    "amount": 127.50,
    "direction": "out",
    "category_id": "optional",
    "vat_rate": 20,
    "notes": "Monthly infrastructure"
  }
}
```

Directions: `in` (income) or `out` (expense)

**Update transaction:**
```json
{
  "type": "tool",
  "name": "update_transaction",
  "arguments": {
    "transaction_id": "uuid",
    "category_id": "new_category",
    "notes": "Updated notes"
  }
}
```

**AI categorization:**
```json
{
  "type": "tool",
  "name": "categorize_transaction",
  "arguments": {"transaction_id": "uuid"}
}
```

Returns suggested category based on description and historical patterns.

**List categories:**
```json
{
  "type": "tool",
  "name": "list_categories",
  "arguments": {"type": "expense"}
}
```

Types: `income`, `expense`, `asset`, `liability`, `equity`

**Create deadline:**
```json
{
  "type": "tool",
  "name": "create_deadline",
  "arguments": {
    "type": "VAT Return",
    "due_date": "2026-02-07",
    "notes": "Q4 2025 VAT"
  }
}
```

**Search documents:**
```json
{
  "type": "tool",
  "name": "search_documents",
  "arguments": {
    "query": "invoice",
    "type": "receipt"
  }
}
```

**Upload document:**
```json
{
  "type": "tool",
  "name": "upload_document",
  "arguments": {
    "file_name": "receipt.pdf",
    "file_data": "base64_encoded_data",
    "document_type": "receipt"
  }
}
```

**Get Director's Loan Account balance:**
```json
{
  "type": "tool",
  "name": "get_dla_balance",
  "arguments": {
    "limit": 10
  }
}
```

Returns DLA balance with S455 tax warnings if the account is overdrawn.

**Get invoices:**
```json
{
  "type": "tool",
  "name": "get_invoices",
  "arguments": {
    "status": "all",
    "contact_id": "optional"
  }
}
```

Status options: `draft`, `sent`, `paid`, `overdue`, `cancelled`, `all`
Returns invoices with summary of outstanding and overdue amounts.

**Create deadline:**
```json
{
  "type": "tool",
  "name": "create_deadline",
  "arguments": {
    "type": "VAT Return",
    "due_date": "2026-02-07",
    "notes": "Q4 2025 VAT"
  }
}
```

### Agent Self-Signup

**POST /api/agent-signup** — No authentication required.

Create an account and get an API key in one request:

```json
{
  "email": "founder@example.com",
  "company_name": "Acme Ltd",
  "full_name": "Jane Smith",
  "entity_type": "ltd"
}
```

Required: `email`, `company_name`
Optional: `full_name`, `entity_type` (default: `ltd`)

Entity types: `ltd`, `plc`, `llp`, `sole_trader`, `partnership`, `cic`, `charity`, `overseas`, `other`

Response:
```json
{
  "api_key": "sk_live_...",
  "company_id": "uuid",
  "user_id": "uuid",
  "trial_ends_at": "2026-02-22T...",
  "api_base": "https://accounts-os.com/api/mcp",
  "message": "Account created. Store this API key — it will not be shown again."
}
```

The API key has `read` + `write` scopes. 14-day free trial. Human receives a welcome email.

Returns `409` if the email is already registered.

---

### Scopes

API keys support three permission levels:

- **read** — Query transactions, balances, deadlines, documents, invoices, DLA
- **write** — Create/update transactions, documents, deadlines (includes read)
- **admin** — Manage company settings (includes write)

Your API key's scope is configured in the dashboard. Requests beyond your scope return a 403 error.

### Resources (Read-only)

**Company info:**
```json
{
  "type": "resource",
  "uri": "accountsos://company"
}
```

**Recent transactions:**
```json
{
  "type": "resource",
  "uri": "accountsos://transactions"
}
```

---

## Use Cases for Agents

### Daily Bookkeeping
Your human mentions expenses throughout the day? Log them:

```python
# Human: "Just paid £45 for the Figma subscription"
accountsos.create_transaction(
    date=today,
    description="Figma subscription - monthly",
    amount=45.00,
    direction="out"
)
# AI auto-categorizes as "Software & Subscriptions"
```

### Invoice Follow-up
Track what's owed:

```python
# Check unpaid invoices
transactions = accountsos.get_transactions(
    direction="in",
    status="pending"
)
for t in transactions:
    if t.days_overdue > 14:
        # Alert human or draft follow-up email
        notify(f"Invoice {t.description} is {t.days_overdue} days overdue")
```

### VAT Prep
Quarterly VAT? Already calculated:

```python
vat = accountsos.get_vat_summary(quarter="Q4 2025")
print(f"VAT owed: £{vat.amount_owed}")
print(f"Due: {vat.due_date}")
# Surface to human before deadline
```

### Deadline Monitoring
Never miss a filing:

```python
deadlines = accountsos.get_deadlines()
for d in deadlines:
    if d.days_until < 7:
        alert(f"⚠️ {d.type} due in {d.days_until} days")
```

### Expense Categorization
New transaction? Categorize it:

```python
# Get AI suggestion
suggestion = accountsos.categorize_transaction(transaction_id)
if suggestion.confidence > 0.8:
    accountsos.update_transaction(transaction_id, {
        "category_id": suggestion.category_id
    })
```

---

## Add to Your Heartbeat

```markdown
## AccountsOS (daily or weekly)

### Daily
- Check for new transactions needing categorization
- Log any expenses human mentioned today

### Weekly
- Review uncategorized transactions
- Check upcoming deadlines (next 14 days)
- Summarize week's P&L if human asks

### Quarterly
- Generate VAT summary
- Surface filing deadlines
- Remind human to review before submission
```

---

## UK-Specific Features

| Feature | Details |
|---------|---------|
| VAT schemes | Standard, Flat Rate, Cash Accounting |
| Tax years | April-April alignment |
| Deadlines | CT600, VAT, Confirmation Statement |
| Categories | HMRC-aligned expense categories |

Built for UK Ltd companies and sole traders. Knows the rules so you don't have to.

---

## Example: Weekly Finance Check

```python
import os
import requests
from datetime import datetime, timedelta

API_URL = "https://accounts-os.com/api/mcp"
headers = {
    "Authorization": f"Bearer {os.environ['ACCOUNTSOS_API_KEY']}",
    "Content-Type": "application/json"
}

def call_tool(name, args={}):
    resp = requests.post(API_URL, headers=headers, json={
        "type": "tool", "name": name, "arguments": args
    })
    return resp.json()["result"]

# 1. Check balance
balance = call_tool("get_balance")
print(f"💰 Current balance: £{balance['amount']}")

# 2. This week's transactions
week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
transactions = call_tool("get_transactions", {"from_date": week_ago})
income = sum(t["amount"] for t in transactions if t["direction"] == "in")
expenses = sum(t["amount"] for t in transactions if t["direction"] == "out")
print(f"📈 Week: +£{income} / -£{expenses}")

# 3. Upcoming deadlines
deadlines = call_tool("get_deadlines")
urgent = [d for d in deadlines if d["days_until"] < 14]
if urgent:
    print(f"⚠️ {len(urgent)} deadlines in next 2 weeks")
    for d in urgent:
        print(f"  - {d['type']}: {d['due_date']}")

# 4. VAT position
vat = call_tool("get_vat_summary")
print(f"🧾 VAT owed: £{vat['amount_owed']}")
```

---

## Links

- **App:** https://accounts-os.com
- **Support:** hello@accounts-os.com

---

## Your Human's Financial Copilot

Most people hate bookkeeping. They forget receipts, miss deadlines, panic at tax time.

You don't forget. You don't panic. You just log, categorize, and surface what matters.

Be the agent that makes finances boring (in a good way).

---

Built by [Thrive Venture Labs](https://thriveventurelabs.com)
