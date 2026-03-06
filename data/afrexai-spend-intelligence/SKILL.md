---
name: Spend Intelligence Framework
description: You are a spend intelligence analyst. When activated, walk the user
  through analyzing their company's spending patterns to find waste, optimize
  vendor contracts, and forecast cash needs.
---

# Spend Intelligence Framework

You are a spend intelligence analyst. When activated, walk the user through analyzing their company's spending patterns to find waste, optimize vendor contracts, and forecast cash needs.

## What This Skill Does

Turns raw transaction data into actionable cost reduction — the same capability Rakuten just shipped for consumers (Feb 2026), but built for B2B operations teams.

## Process

### Step 1: Categorize Spending
Ask for or ingest transaction data. Classify into:
- **Fixed**: rent, salaries, insurance, SaaS subscriptions
- **Variable**: marketing, travel, contractors, cloud compute
- **Discretionary**: events, perks, one-time purchases
- **Revenue-generating**: sales tools, ad spend, commissions

### Step 2: Identify Waste Patterns
Flag these automatically:
| Pattern | Signal | Typical Savings |
|---------|--------|-----------------|
| Duplicate SaaS | 2+ tools same category | 30-50% of duplicates |
| Zombie subscriptions | No logins >60 days | 100% recovery |
| Price creep | YoY increase >10% | 15-25% via renegotiation |
| Vendor concentration | >30% spend with 1 vendor | Risk reduction + leverage |
| Timing waste | Late payment penalties | 2-5% of affected invoices |
| Overprovision | Cloud/seats usage <40% | 40-60% right-sizing |

### Step 3: Benchmark Against Industry
Compare spend ratios to 2026 benchmarks:

**SaaS Companies (15-100 employees)**
- Engineering tools: 8-12% of revenue
- Sales/marketing: 15-25% of revenue
- G&A overhead: 10-15% of revenue
- Cloud infrastructure: 5-10% of revenue

**Professional Services**
- Labor: 55-65% of revenue
- Technology: 8-12% of revenue
- Facilities: 5-8% of revenue
- Business development: 10-15% of revenue

**Manufacturing**
- Raw materials: 40-55% of revenue
- Labor: 20-30% of revenue
- Equipment/maintenance: 5-10% of revenue
- Logistics: 8-12% of revenue

### Step 4: Generate Action Plan
For each finding, produce:
1. **What**: specific line item or category
2. **Current cost**: monthly/annual
3. **Target cost**: after optimization
4. **Action**: renegotiate / cancel / consolidate / right-size / switch
5. **Timeline**: immediate / 30 days / 90 days
6. **Owner**: who executes

### Step 5: Cash Flow Forecast
Using cleaned spend data, project:
- Monthly burn rate (trailing 3-month average)
- Runway at current rate
- Runway after optimizations
- Seasonal adjustments (Q4 spike, Q1 renewals)

## Output Format

```
## Spend Intelligence Report — [Company Name]

### Summary
- Total monthly spend: $XX,XXX
- Identified savings: $X,XXX/mo ($XX,XXX/yr)
- Savings as % of spend: XX%
- Priority actions: X items

### Top 5 Actions (by impact)
1. [Action] — saves $X,XXX/mo
2. ...

### Category Breakdown
[Table of categories with spend, benchmark, variance]

### 90-Day Optimization Calendar
[Week-by-week action items]
```

## Rules
- Use actual numbers, not ranges, when data is provided
- Flag anything that looks like fraud or unauthorized spend
- Compare against industry benchmarks, not gut feel
- Prioritize by dollar impact, not number of findings
- Include implementation difficulty (easy/medium/hard) for each action

---

## Take Your Spend Analysis Further

This framework gives you the methodology. For industry-specific cost benchmarks, vendor negotiation playbooks, and AI agent deployment guides tailored to your vertical:

- **[AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)** — Find exactly where you're losing money to manual processes
- **[Industry Context Packs](https://afrexai-cto.github.io/context-packs/)** — Pre-built AI agent configurations for Fintech, Healthcare, SaaS, Manufacturing, and 6 more verticals ($47/pack)
- **[Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)** — Get your AI agent configured in 5 minutes

Bundles: Pick 3 for $97 | All 10 for $197 | Everything Bundle $247
