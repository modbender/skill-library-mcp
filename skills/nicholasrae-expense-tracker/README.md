# 💰 Expense Tracker Skill

Track, categorize, and budget personal expenses through natural conversation. Just tell your AI what you spent — it handles the rest.

## What It Does

- **Natural language logging** — "spent $45 at Costco" just works
- **Auto-categorization** — matches vendors to 16 categories using keyword lists
- **Budget tracking** — set monthly limits, get warned when you're close
- **Reports** — weekly and monthly spending summaries with trends
- **Refunds & corrections** — handles negative amounts, edits, and deletions
- **Smart parsing** — understands "yesterday", split bills, approximate amounts

## Quick Start

### 1. Install

Copy the `expense-tracker/` folder into your OpenClaw `skills/` directory:

```
skills/expense-tracker/
├── SKILL.md              # AI instructions (don't edit unless customizing)
├── README.md             # This file
├── references/
│   ├── categories.json   # Category definitions + keyword matching
│   └── budgets.json      # Monthly budget limits (edit this!)
├── scripts/
│   ├── add-expense.sh    # Add expense to ledger
│   ├── query.sh          # Query/filter expenses
│   └── budget-check.sh   # Check spending vs budget
├── templates/
│   ├── weekly-report.md  # Weekly report template
│   └── monthly-report.md # Monthly report template
└── expenses/
    └── ledger.json       # Your data (auto-created on first expense)
```

### 2. Requirements

- **macOS or Linux** (bash scripts)
- **jq** — JSON processor. Install with `brew install jq` (macOS) or `apt install jq` (Linux)
- **bc** — calculator (pre-installed on macOS and most Linux distros)

### 3. First-Time Setup

1. **Set your budgets** — Edit `references/budgets.json` to match your spending:
   - Adjust category limits to your lifestyle
   - Set `income` to your monthly take-home pay (enables savings rate in reports)
   - The defaults are for a single US adult (~$5,300/month total)

2. **Start logging** — Just tell your AI what you spent:
   ```
   You: spent $45 at Costco
   AI:  ✅ Expense #1: $45.00 at Costco (Groceries) on 2026-02-17
   ```

That's it. No database to set up, no accounts to create. Your data lives in `expenses/ledger.json` as plain JSON.

## Usage Examples

### Logging Expenses
```
"spent $45 at Costco"
"grabbed lunch for $18 at Chipotle yesterday"
"Netflix $15.99"
"filled up the tank, 55 bucks at Shell"
"$120 electric bill"
"dropped $200 at Target for birthday stuff"
```

### Refunds & Reimbursements
```
"got a $35 refund from Amazon"
"work reimbursed me $45 for lunch"
```

### Checking Spending
```
"how much have I spent this month?"
"what did I spend on food?"
"show me last week's expenses"
"how's my budget looking?"
```

### Reports
```
"weekly report"
"how'd February go?"
"compare this month to last month"
```

### Budget Management
```
"set my dining budget to $400"
"how much is left in my grocery budget?"
```

## Categories

The skill comes with 16 categories pre-configured with keyword matching:

| Category | Example Merchants |
|----------|------------------|
| Groceries | Costco, Trader Joe's, Whole Foods, Safeway |
| Dining | Chipotle, Starbucks, DoorDash, restaurants |
| Gas/Transport | Shell, Chevron, Uber, Lyft, parking |
| Subscriptions | Netflix, Spotify, Adobe, iCloud |
| Health/Fitness | CVS, Planet Fitness, doctor, pharmacy |
| Entertainment | AMC, concerts, Steam, tickets |
| Shopping | Amazon, Target, Best Buy, clothing |
| Utilities | Electric, internet, phone bill |
| Housing | Rent, mortgage, HOA, repairs |
| Personal Care | Haircut, salon, dry cleaning |
| Education | Courses, books, Udemy, tuition |
| Gifts | Birthday, holiday, donations |
| Travel | Flights, hotels, Airbnb, rental car |
| Insurance | Health/auto/life insurance premiums |
| Pets | Vet, Petco, pet food, grooming |
| Miscellaneous | ATM, fees, anything uncategorized |

Edit `references/categories.json` to add your own keywords or categories.

## Budget Alerts

The skill proactively warns you when spending approaches budget limits:

| Usage | Alert |
|-------|-------|
| < 50% | No alert |
| 50–79% | Informational |
| 80–99% | ⚠️ Warning |
| ≥ 100% | 🔴 Over budget |

## Your Data

All expense data is stored locally in `expenses/ledger.json`. It's plain JSON — easy to back up, export, or migrate. No cloud, no accounts, no tracking.

### Backup

```bash
cp skills/expense-tracker/expenses/ledger.json ~/expense-backup.json
```

### Export to CSV

```bash
jq -r '.[] | [.id, .date, .amount, .category, .vendor, .notes] | @csv' \
  skills/expense-tracker/expenses/ledger.json > expenses.csv
```

## Customization

- **Add categories**: Edit `references/categories.json` — add new category objects with keywords
- **Adjust budgets**: Edit `references/budgets.json` — change limits anytime
- **Report style**: Edit templates in `templates/` — the AI uses these as guides for formatting

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "jq not found" | Install: `brew install jq` |
| Wrong category | Say "move that to Entertainment" — AI will recategorize |
| Duplicate entry | Say "delete expense #12" or "cancel the last one" |
| Budget seems off | Check `references/budgets.json` — ensure `total_limit` matches sum of category limits |

---

## Want Your Entire AI Stack Set Up Like This?

This skill is one piece of a fully automated personal AI system — morning briefs, smart dashboards, fleet monitoring, trading bots, notification digests, and more.

**I'll build and customize the whole thing for you.**

👉 [nickrae.net](https://nickrae.net) — See the full stack and book a setup call.

---

**Built by [Nick Rae](https://nickrae.net)** · Pilot · Builder · Maker  
**License:** MIT  
**Version:** 1.0.0  
**Compatibility:** macOS, Linux | Requires jq, bash
