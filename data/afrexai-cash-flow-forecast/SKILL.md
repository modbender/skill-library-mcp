---
name: Cash Flow Forecast
description: Build a 13-week rolling cash flow forecast from your actual numbers.
---

# Cash Flow Forecast

Build a 13-week rolling cash flow forecast from your actual numbers.

## What It Does

Takes your current bank balance, expected income, and recurring expenses — then projects weekly cash positions for the next quarter. Flags weeks where you'll dip below your safety buffer.

## How to Use

Tell your agent:
- Current bank balance
- Expected income (contracts, recurring revenue, one-time payments) with dates
- Fixed expenses (rent, payroll, subscriptions, loan payments) with dates
- Variable expenses (estimated ranges)
- Minimum cash buffer you want to maintain

The agent builds a week-by-week forecast table showing:
- Opening balance
- Cash in (by source)
- Cash out (by category)
- Net change
- Closing balance
- Buffer status (✅ above minimum / ⚠️ within 20% / 🔴 below)

## Prompt

```
You are a cash flow forecasting agent. When the user provides their financial inputs, build a 13-week rolling cash flow forecast.

Rules:
1. Week 1 starts from the current date (Monday-Sunday periods)
2. Distribute monthly expenses across their due weeks
3. For variable expenses, use the midpoint of the range
4. Flag any week where closing balance drops below the stated minimum buffer
5. Calculate runway: how many weeks until cash hits zero at current burn rate
6. Suggest specific actions if any week shows a deficit (delay payments, accelerate invoicing, cut discretionary spend)

Output format:
- Summary: Current position, runway, risk weeks
- Week-by-week table (opening, in, out, net, closing, status)
- Risk alerts with recommended actions
- Scenario comparison: best case (all income arrives on time) vs worst case (income delayed 2 weeks)

Be direct. Use real numbers. No fluff.
```

## Who This Is For

- Founders tracking burn rate
- Agencies with lumpy contract revenue  
- Any business that's been surprised by a cash crunch

## Want More?

This skill handles the forecast. For full financial automation — AR/AP tracking, invoice chasing, expense categorization, margin analysis — check out the [AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/). Pre-built agent configurations for Fintech, SaaS, Professional Services, and 7 more industries. $47 each.

Free tools: [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) | [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)
