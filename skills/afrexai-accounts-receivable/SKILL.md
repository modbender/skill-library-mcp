# Accounts Receivable Manager

Automate AR workflows: aging analysis, collection prioritization, payment follow-ups, cash application, and bad debt forecasting.

## What It Does

1. **AR Aging Report** — Bucket outstanding invoices by 0-30, 31-60, 61-90, 90+ days with risk scoring
2. **Collection Priority Queue** — Rank overdue accounts by amount × days × risk for optimal follow-up order
3. **Payment Reminder Drafts** — Generate professional escalation emails (friendly → firm → final notice → collections)
4. **Cash Application Matching** — Match incoming payments to open invoices with variance handling
5. **Bad Debt Forecasting** — Predict write-offs using historical payment patterns and aging trends
6. **DSO Tracking** — Calculate Days Sales Outstanding with trend analysis and benchmarks by industry

## How to Use

Tell your agent what you need:

- "Run an AR aging analysis for our open invoices"
- "Prioritize our collection queue — what should we chase first?"
- "Draft a 60-day overdue reminder for [client name]"
- "Our DSO is 47 days — how does that compare to SaaS benchmarks?"
- "Forecast bad debt exposure for Q1"

## AR Aging Buckets

| Bucket | Risk Level | Action |
|--------|-----------|--------|
| Current (0-30) | Low | Monitor |
| 31-60 days | Medium | Friendly reminder |
| 61-90 days | High | Escalation call + written notice |
| 90+ days | Critical | Final demand → collections/write-off review |

## Collection Priority Formula

```
Priority Score = (Invoice Amount × 0.4) + (Days Overdue × 0.3) + (Customer Risk Score × 0.3)
```

Customer Risk Score (1-10) based on:
- Payment history (avg days to pay)
- Number of past-due invoices
- Credit limit utilization
- Industry default rates

## Payment Reminder Escalation

### Day 1 (Invoice Due)
Subject: Invoice #[NUM] — Payment Due Today
Tone: Friendly, informational

### Day 7 (1 Week Overdue)
Subject: Friendly Reminder — Invoice #[NUM] Past Due
Tone: Warm but clear

### Day 30 (1 Month Overdue)
Subject: Payment Required — Invoice #[NUM] Now 30 Days Past Due
Tone: Professional, firm

### Day 60 (2 Months Overdue)
Subject: Urgent — Invoice #[NUM] Significantly Overdue
Tone: Serious, mention late fees / service impact

### Day 90+ (Final Notice)
Subject: Final Notice — Invoice #[NUM] Requires Immediate Payment
Tone: Formal, mention collections referral

## DSO Benchmarks by Industry

| Industry | Good DSO | Average DSO | Poor DSO |
|----------|----------|-------------|----------|
| SaaS / Software | <30 | 30-45 | >60 |
| Professional Services | <35 | 35-55 | >70 |
| Manufacturing | <40 | 40-60 | >75 |
| Construction | <45 | 45-70 | >90 |
| Healthcare | <35 | 35-50 | >65 |

## Bad Debt Forecasting Model

Estimate write-off probability by aging bucket:
- Current: 1-2% default rate
- 31-60 days: 5-8%
- 61-90 days: 15-25%
- 90-120 days: 30-50%
- 120+ days: 50-80%

Apply to outstanding amounts for expected loss provision.

## Cash Application Rules

1. **Exact match** — Payment amount matches one open invoice exactly
2. **Combination match** — Payment matches sum of multiple invoices
3. **Short payment** — Payment < invoice amount → flag for dispute/deduction review
4. **Overpayment** — Payment > invoice → apply to oldest open balance or issue credit
5. **Unidentified** — No match found → hold in suspense, research within 48 hours

## Output Format

When generating AR reports, include:
- Total AR outstanding
- Aging distribution ($ and %)
- Top 10 overdue accounts by priority score
- DSO current vs. 3-month trend
- Estimated bad debt exposure
- Recommended actions (who to call, what to send)

---

## Take It Further

This skill handles AR analysis and workflows. For full financial operations automation:

- **[AI Agent Context Packs](https://afrexai-cto.github.io/context-packs/)** — Industry-specific agent configs for Fintech, Professional Services, SaaS, and more ($47 each)
- **[AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)** — Find where your business is losing money to manual processes
- **[Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)** — Get your AI agent configured in minutes

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — operational AI for businesses that run on results, not hype.
