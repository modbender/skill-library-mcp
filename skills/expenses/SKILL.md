---
name: Expenses
description: Build a personal expense tracking system for daily spending, shared costs, business expenses, and project budgets.
metadata: {"clawdbot":{"emoji":"💸","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions spending money → offer to log expense
- Different contexts need different tracking → adapt to their use case
- Surface patterns when asked → where is money going?
- Create `~/expenses/` as workspace

## Use Case Discovery
Ask how they'll use expense tracking:
- Personal spending: "where does my money go?"
- Shared costs: roommates, couples, group trips
- Business/freelance: billable expenses, tax deductions
- Work reimbursement: expenses to claim from employer
- Project budget: renovation, wedding, specific goal
- Travel: trip-specific spending

## Expense Entry Basics
- Amount and currency
- Date
- What: brief description
- Category: food, transport, entertainment, etc.
- Payment method: cash, card, account (optional)
- Receipt photo if needed

## Personal Spending
Track to understand patterns:
- Categories that matter to you
- Weekly/monthly totals by category
- Trends over time: spending more on dining out?
- No judgment — awareness is the goal

## Shared Expenses
Track who paid, who owes:
- Expense + who paid + split between whom
- Running balance: who owes whom how much
- Settle up periodically: "I owe you €45"
- Handle unequal splits: 60/40, by item

## Business Expenses
Track for billing or taxes:
- Client/project attribution
- Billable vs non-billable
- Receipt storage critical — link or embed
- Category for tax deduction type
- Mileage if applicable

## Work Reimbursement
Track what employer owes you:
- Status: pending, submitted, reimbursed
- Submission date
- Receipt attached
- Reimbursement received date
- Monthly report generation

## Project Budget
Track spending against a budget:
- Project: kitchen renovation, wedding, vacation
- Budget amount set upfront
- Running total vs budget: "€3,400 of €10,000 spent"
- Category breakdown within project
- Flag when approaching limit

## Travel Expenses
Trip-specific tracking:
- All expenses tagged to trip
- Daily spending if relevant
- By category: lodging, food, activities, transport
- Currency conversion if international
- Per-person if group travel
- Post-trip summary

## File Structure
```
~/expenses/
├── daily/
│   └── 2024-03.md
├── shared/
│   └── roommates.md
├── business/
│   └── 2024-q1.md
├── trips/
│   └── japan-2024.md
├── projects/
│   └── kitchen-reno.md
└── categories.md
```

## Category System
- Keep categories broad: 10-15 max
- Common: food, transport, housing, utilities, entertainment, health, shopping
- Customize to what matters: "coffee" separate if tracking that
- Consistent naming — "restaurants" not sometimes "dining"

## Entry Formats
Quick daily: "€45 groceries"
Detailed: amount, date, category, description, receipt
Shared: amount, paid by, split between, category
Business: amount, client, category, receipt, billable

## What To Surface
- "You've spent €X this month on dining"
- "Coffee spending up 40% vs last month"
- "John owes you €89 from shared expenses"
- "Kitchen project: €2,100 remaining in budget"
- "€450 in unreimbursed work expenses"

## Progressive Enhancement
- Week 1: log expenses as they happen
- Week 2: add categories, see patterns
- Month 2: compare months, spot trends
- Ongoing: adjust categories to what's useful

## Receipt Management
- Photo immediately — paper receipts fade
- Link to expense entry
- Store in expense folder or dedicated receipts folder
- Filename: date-vendor-amount.jpg
- Business expenses: retention period awareness

## Reporting
- Monthly summary by category
- Trend comparison: this month vs last
- Shared: balance summary, settlement suggestion
- Business: quarterly for taxes
- Project: spend vs budget status

## What NOT To Suggest
- Complex budgeting before spending is tracked
- Linking bank accounts — manual has value
- Obsessive categorization — broad categories work
- Guilt about spending — data, not judgment

## Multi-Currency
- Log in currency spent
- Note exchange rate if tracking
- Convert for totals if needed
- Travel especially: mixed currencies normal

## Integration Points
- Budget: expenses feed into budget tracking
- Invoices: billable expenses to clients
- Taxes: business expense categories
- Trips: travel-specific tracking
