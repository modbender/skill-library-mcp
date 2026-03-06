---
name: budget-tracker
description: Track agent spending, set budgets and alerts, and prevent surprise bills. Use when the agent needs to log expenses, check remaining budget, set spending limits, or get cost summaries. Essential for autonomous agents with real money.
user-invocable: true
metadata: {"openclaw": {"emoji": "💰", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Budget Tracker

Track every cent your agent spends. Set hard limits. Get alerts before you blow your budget.

## Why This Exists

Autonomous agents with access to APIs, domains, and services can rack up unexpected bills. This skill gives you a financial safety net — log every transaction, enforce spending limits, and always know exactly where you stand.

## Commands

### Log a transaction
```bash
python3 {baseDir}/scripts/budget.py log --amount 10.00 --merchant "Namecheap" --category "domain" --note "arcself.com registration"
```

### Check balance
```bash
python3 {baseDir}/scripts/budget.py balance
```

### View spending summary
```bash
python3 {baseDir}/scripts/budget.py summary
```

### View recent transactions
```bash
python3 {baseDir}/scripts/budget.py history --limit 10
```

### Set budget limit
```bash
python3 {baseDir}/scripts/budget.py set-budget --total 200.00
```

### Set alert threshold (warn when balance drops below this)
```bash
python3 {baseDir}/scripts/budget.py set-alert --threshold 50.00
```

### Check if a purchase is safe
```bash
python3 {baseDir}/scripts/budget.py check --amount 25.00
```

### Export to CSV
```bash
python3 {baseDir}/scripts/budget.py export --format csv
```

## Data Storage

Budget data is stored in `~/.openclaw/budget-tracker/budget.json` by default. Override with `--data-dir /path/to/dir`.

The JSON structure:
```json
{
  "budget": {"total": 200.00, "alert_threshold": 50.00},
  "transactions": [
    {
      "id": "txn_001",
      "timestamp": "2026-02-15T14:00:00Z",
      "amount": 10.00,
      "merchant": "Namecheap",
      "category": "domain",
      "note": "arcself.com"
    }
  ]
}
```

## Categories

Use consistent categories: `domain`, `hosting`, `api`, `tool`, `subscription`, `marketing`, `other`.

## Alerts

When balance drops below the alert threshold, the skill outputs a warning. When a purchase would exceed the remaining budget, it blocks and warns.

## Tips

- Log transactions immediately after spending — don't batch them
- Use `check` before any purchase to verify budget safety
- Run `summary` at the start of each day for awareness
- Set `--alert-threshold` to 25% of your total budget
