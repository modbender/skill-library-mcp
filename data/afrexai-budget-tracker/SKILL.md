---
name: Budget & Expense Tracker — AI Agent Financial Command Center
description: Track every dollar, enforce budgets, spot spending patterns, and
  build wealth — all through natural conversation with your AI agent.
---

# Budget & Expense Tracker — AI Agent Financial Command Center

Track every dollar, enforce budgets, spot spending patterns, and build wealth — all through natural conversation with your AI agent.

## How It Works

You talk to your agent naturally: "I spent $45 on groceries" or "How much did I spend on food this month?" The agent maintains a local JSON ledger, enforces your budgets, and gives you weekly/monthly financial intelligence.

---

## 1. Setup — Your Financial Profile

On first use, create `budget-profile.json` in your workspace:

```json
{
  "currency": "USD",
  "monthlyIncome": 5000,
  "payDays": [1, 15],
  "fiscalMonthStart": 1,
  "categories": {
    "housing": { "budget": 1500, "essential": true },
    "food": { "budget": 600, "essential": true, "subcategories": ["groceries", "dining", "delivery", "coffee"] },
    "transport": { "budget": 300, "essential": true, "subcategories": ["fuel", "public", "rideshare", "parking"] },
    "utilities": { "budget": 200, "essential": true, "subcategories": ["electric", "water", "internet", "phone"] },
    "health": { "budget": 200, "essential": true, "subcategories": ["gym", "medical", "supplements"] },
    "entertainment": { "budget": 200, "essential": false, "subcategories": ["streaming", "games", "events", "hobbies"] },
    "shopping": { "budget": 300, "essential": false, "subcategories": ["clothes", "electronics", "home", "gifts"] },
    "education": { "budget": 100, "essential": false, "subcategories": ["books", "courses", "subscriptions"] },
    "savings": { "budget": 500, "essential": true, "target": "emergency-fund" },
    "misc": { "budget": 100, "essential": false }
  },
  "alerts": {
    "budgetWarning": 0.75,
    "budgetCritical": 0.90,
    "unusualSpend": 2.0,
    "dailyMax": 200
  },
  "goals": []
}
```

Customize categories, budgets, and subcategories to your life. The agent adapts to whatever structure you define.

---

## 2. The Ledger — Transaction Format

All transactions live in `budget-ledger.json`:

```json
{
  "transactions": [
    {
      "id": "tx_20260213_001",
      "date": "2026-02-13",
      "type": "expense",
      "amount": 45.67,
      "category": "food",
      "subcategory": "groceries",
      "description": "Weekly shop at Aldi",
      "merchant": "Aldi",
      "paymentMethod": "debit",
      "tags": ["weekly", "essentials"],
      "recurring": false,
      "note": ""
    }
  ],
  "recurringRules": [],
  "metadata": {
    "lastUpdated": "2026-02-13T10:30:00Z",
    "transactionCount": 1,
    "ledgerVersion": "1.0"
  }
}
```

### Transaction ID Convention
`tx_YYYYMMDD_NNN` — date + sequential number. Never reuse IDs.

---

## 3. Natural Language Parsing

When a user says something about money, parse it into a transaction:

### Parsing Rules

| User says | Extracted |
|-----------|-----------|
| "spent $45 on groceries" | expense, $45, food/groceries |
| "paid rent $1500" | expense, $1500, housing |
| "got paid $2500" | income, $2500, salary |
| "uber $12" | expense, $12, transport/rideshare |
| "Netflix $15.99 monthly" | expense, $15.99, entertainment/streaming, recurring |
| "coffee $5" | expense, $5, food/coffee |
| "sent mom $200" | expense, $200, misc (ask: gift or loan?) |
| "returned shoes got $80 back" | refund, $80, shopping/clothes |

### Ambiguity Resolution
- If category is unclear, make your best guess AND confirm: "Logged $45 under food/groceries — correct?"
- If amount is missing, ask: "How much was that?"
- If "monthly" or "every week" mentioned, create a recurring rule
- "Returned" or "refund" = negative expense (credit)
- "Lent" vs "borrowed" — always clarify direction

### Recurring Transactions
When a user mentions recurring expenses, create a rule:

```json
{
  "id": "rec_001",
  "description": "Netflix subscription",
  "amount": 15.99,
  "category": "entertainment",
  "subcategory": "streaming",
  "frequency": "monthly",
  "dayOfMonth": 15,
  "active": true,
  "lastApplied": "2026-02-15"
}
```

On each budget check, auto-apply any recurring transactions that are due.

---

## 4. Budget Enforcement Engine

### Real-Time Budget Checks

After EVERY expense logged, run this check:

```
1. Calculate total spent in category this month
2. Compare to budget limit
3. Calculate percentage used
4. Check days remaining in month
5. Calculate daily budget remaining
6. Trigger alerts if needed
```

### Alert Levels

| Level | Trigger | Response |
|-------|---------|----------|
| 🟢 On track | < 75% budget, proportional to month progress | Silent (log only) |
| 🟡 Warning | 75-90% budget used | "Heads up — you've used 78% of your $600 food budget with 18 days left. That's $3.67/day remaining." |
| 🔴 Critical | > 90% budget used | "⚠️ Food budget is at 92% ($552/$600) with 12 days left. Only $4/day remaining. Consider cooking at home this week." |
| 🚨 Over budget | > 100% | "🚨 You're $47 over your $600 food budget. Total: $647. This eats into your savings target." |
| ⚡ Unusual | Single transaction > 2x average for category | "That $89 coffee purchase seems unusual — your average is $5.20. Correct amount?" |

### Pace Tracking (Smart Budget Intelligence)

Don't just track totals — track spending PACE:

```
Days elapsed this month: 13
Days remaining: 15
Budget: $600
Spent so far: $380
Daily pace: $29.23/day (spending)
Sustainable pace: $21.43/day (budget / total days)
Remaining pace: $14.67/day (remaining budget / remaining days)

Verdict: Spending 37% faster than sustainable. Will exceed budget by ~$160 at current pace.
```

This is MORE useful than just "you spent X of Y" because it predicts the future.

---

## 5. Savings Goals

### Goal Structure

```json
{
  "id": "goal_001",
  "name": "Emergency Fund",
  "targetAmount": 10000,
  "currentAmount": 3500,
  "deadline": "2026-12-31",
  "priority": "high",
  "contributions": [
    { "date": "2026-02-01", "amount": 500, "note": "Monthly auto-save" }
  ],
  "autoContribute": {
    "enabled": true,
    "amount": 500,
    "frequency": "monthly",
    "dayOfMonth": 1
  }
}
```

### Goal Intelligence

When checking goals, calculate:
- **On track?** Compare current savings rate to required rate
- **Projected completion:** At current rate, when will goal be hit?
- **Acceleration options:** "If you save $100 more/month, you'll hit your goal 2 months early"
- **Surplus allocation:** If under budget this month, suggest putting surplus toward goals

---

## 6. Reports & Intelligence

### Weekly Summary (run every Sunday or on demand)

```
📊 Week of Feb 7-13, 2026

💸 Spent: $487.23
💰 Income: $2,500.00
📈 Net: +$2,012.77

Top categories:
  🏠 Housing: $375 (rent proration)
  🍔 Food: $112.23 (18.7% of budget used, on track)

⚡ Unusual: $0 flagged
🎯 Goals: Emergency Fund 35% → 40% (+$500)
💡 Insight: Food spending down 12% vs last week. Nice work.
```

### Monthly Report (run on 1st of each month)

```
📊 January 2026 — Full Report

INCOME:         $5,000.00
EXPENSES:       $3,847.23
NET SAVINGS:    $1,152.77 (23.1% savings rate)

BUDGET PERFORMANCE:
  ✅ Housing:      $1,500 / $1,500 (100%) — on budget
  ✅ Food:         $534 / $600 (89%) — $66 under
  ✅ Transport:    $187 / $300 (62%) — $113 under
  ⚠️ Shopping:     $342 / $300 (114%) — $42 OVER
  ✅ Entertainment: $156 / $200 (78%) — $44 under

CATEGORY TRENDS (vs last month):
  📈 Food: +8% ($534 vs $495)
  📉 Transport: -23% ($187 vs $243) — nice!
  📈 Shopping: +37% ($342 vs $250) — watch this

SAVINGS GOALS:
  🎯 Emergency Fund: $4,000 / $10,000 (40%) — on track for Aug completion
  🎯 Vacation: $800 / $2,000 (40%) — on track

TOP MERCHANTS:
  1. Aldi — $178 (12 visits)
  2. Amazon — $156 (8 orders)
  3. Shell — $89 (6 fills)

💡 INSIGHTS:
  • Shopping was 14% over budget — 3 Amazon orders on Feb 8 totaled $120
  • You saved $113 on transport (worked from home more?)
  • At current savings rate ($1,153/mo), emergency fund complete by August
  • Consider moving $66 food surplus → vacation goal
```

### Year-to-Date Dashboard (on demand)

```
📊 2026 YTD (Jan-Feb)

Total Income:    $10,000
Total Expenses:  $7,694
Total Saved:     $2,306 (23.1% rate)
Goal Progress:   Emergency Fund 40%, Vacation 40%

Best month: January (24.2% savings rate)
Worst category: Shopping (avg 107% of budget)
Most improved: Transport (-15% trend)
```

---

## 7. Smart Insights Engine

Beyond basic tracking, provide ACTIONABLE intelligence:

### Spending Patterns
- **Day-of-week analysis:** "You spend 40% more on weekends. Saturday average: $67 vs weekday $23"
- **Merchant loyalty:** "You've been to Starbucks 18 times this month. A home coffee setup pays for itself in 3 weeks."
- **Category creep:** "Shopping has increased 15% each of the last 3 months. Projected: $450 next month."

### Optimization Suggestions
- **Subscription audit:** "You have 6 streaming services ($78/mo). Used Netflix 20 times, Disney+ once. Consider canceling Disney+."
- **Budget rebalancing:** "You've been under transport budget for 3 months. Consider reducing to $200 and moving $100 to savings."
- **Cash flow timing:** "Your biggest expenses hit on the 1st-5th. Consider moving some to the 15th paycheck cycle."

### Financial Health Score (0-100)

Calculate monthly:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Savings rate | 30% | 20%+ = 100, 10-20% = 70, 5-10% = 40, <5% = 10 |
| Budget adherence | 25% | All under = 100, 1 over = 80, 2-3 over = 50, 4+ = 20 |
| Goal progress | 20% | On track = 100, slightly behind = 60, way behind = 20 |
| Expense stability | 15% | Low variance = 100, moderate = 60, volatile = 20 |
| Debt-free spending | 10% | No credit used = 100, some = 50, heavy = 10 |

Score interpretation:
- 90-100: 💪 Excellent — wealth building mode
- 70-89: 👍 Good — minor optimizations possible
- 50-69: ⚠️ Fair — specific areas need attention
- Below 50: 🚨 Needs work — create an action plan

---

## 8. Commands Reference

| Command | What it does |
|---------|-------------|
| "I spent $X on Y" | Log expense |
| "Got paid $X" | Log income |
| "Budget check" | Show all budgets vs actuals with pace |
| "Weekly summary" | This week's report |
| "Monthly report" | Full month analysis |
| "How much on food?" | Category deep-dive |
| "Set food budget to $500" | Update budget |
| "Add goal: Vacation $2000 by June" | Create savings goal |
| "Save $200 toward vacation" | Log goal contribution |
| "Financial health" | Calculate health score |
| "Unusual spending?" | Flag outliers |
| "Subscription audit" | List recurring + usage |
| "Compare to last month" | Month-over-month trends |
| "Export CSV" | Export ledger for spreadsheets |
| "Undo last" | Remove last transaction |

---

## 9. Data Management

### File Locations
- `budget-profile.json` — Your financial profile and budgets
- `budget-ledger.json` — All transactions
- `budget-goals.json` — Savings goals and contributions
- `budget-recurring.json` — Recurring transaction rules

### CSV Export Format
When user asks to export:
```csv
Date,Type,Amount,Category,Subcategory,Description,Merchant,Tags
2026-02-13,expense,45.67,food,groceries,Weekly shop,Aldi,"weekly,essentials"
```

### Backup
Periodically remind users to back up their ledger. Offer to commit to git if workspace is a repo.

### Privacy
All data stays local. No external APIs. No cloud sync. Your money data never leaves your machine.

---

## 10. Edge Cases

- **Split transactions:** "Dinner $80, split with friend" → Log $40 as your share
- **Foreign currency:** "Spent €50 in Paris" → Convert at current rate, note original currency
- **Cash back / rewards:** Track as income subcategory "cashback"
- **Transfers between accounts:** Don't count as expense or income — log as "transfer" type
- **Shared expenses:** Tag with "shared" and note who owes what
- **Tax deductible:** Tag with "tax-deductible" for year-end filtering
- **Returns within same month:** Net against the category. Cross-month: log as refund income.
- **Variable income:** If income varies, use 3-month rolling average for budget calculations
