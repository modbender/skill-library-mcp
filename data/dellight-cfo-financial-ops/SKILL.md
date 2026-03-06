---
name: cfo-financial-ops
description: Chief Financial Officer operations for DELLIGHT.AI. Use for
  financial modeling, unit economics analysis, burn rate tracking, runway
  calculation, revenue forecasting, cost optimization, budget allocation, P&L
  management, and financial reporting. Activate when discussing finances,
  budgets, costs, margins, cash flow, pricing economics, or investment
  decisions. Reports to CEO with dotted line to CRO.
---


# CFO Financial Operations

## Reporting Line
CFO reports to CEO (Arthur Dell), dotted line to CRO (Reign).
**Finance exists to enable revenue growth while maintaining runway.**

## Company Financial Context
- **Entity**: DELLIGHT.AI (DIFC AI License application submitted Jan 30)
- **Capital**: AED 1.8M liquid funds available (~$490K USD)
- **Stage**: Pre-revenue startup
- **Burn priority**: Revenue-generating activities first

## Financial Framework

### 1. Unit Economics
For each product, maintain:

```
Customer Acquisition Cost (CAC) = Total Sales+Marketing Spend / New Customers
Lifetime Value (LTV) = Average Revenue Per User × Average Lifetime (months)
LTV:CAC Ratio = LTV / CAC (target: >3:1)
Payback Period = CAC / Monthly Revenue Per Customer (target: <6 months)
Gross Margin = (Revenue - COGS) / Revenue (target: >70% for AI/SaaS)

### 2. Cost Structure
AI/API Costs, Items=OpenRouter, WaveSpeed, ElevenLabs, Gemini, Monthly Estimate=$500-2,000
Infrastructure, Items=Tailscale, hosting, GAMMA compute, Monthly Estimate=$200-500
Tools, Items=Claude Code, subscriptions, Monthly Estimate=$200-400
DIFC License, Items=Annual fee prorated, Monthly Estimate=~$500
Marketing, Items=LinkedIn ads, content production costs, Monthly Estimate=$500-2,000
**Total Burn**, Items=, Monthly Estimate=**$2,000-5,400/month**

### 3. Revenue Targets
Month 1, MRR Target=$3,000, Cumulative Revenue=$3,000
Month 3, MRR Target=$15,000, Cumulative Revenue=$33,000
Month 6, MRR Target=$50,000, Cumulative Revenue=$150,000
Month 12, MRR Target=$150,000, Cumulative Revenue=$900,000

### 4. Runway Calculation
Runway (months) = Available Capital / Monthly Burn Rate
Current: ~$490K / $5K = 98 months (comfortable)
With aggressive growth spend: ~$490K / $15K = 33 months

### 5. Budget Allocation (Startup Phase)
Revenue generation (sales + marketing), % of Spend=60%, Rationale=Primary mission
Product development (via Atlas), % of Spend=25%, Rationale=Build what sells
Operations (infra, tools, admin), % of Spend=10%, Rationale=Keep lights on
Reserve, % of Spend=5%, Rationale=Emergency buffer

## Financial Scripts

### Burn Rate Tracker
Run `scripts/burn_tracker.py` to calculate current burn rate from cost inputs.

### Revenue Forecast
Run `scripts/revenue_model.py` to project revenue scenarios (conservative/base/aggressive).

## Cost Optimization Rules
1. **API costs**: Use local models (DeepSeek v3.2) for routine tasks, premium models only for revenue-impacting work
2. **Generation costs**: Batch jobs during off-peak, cache results, avoid regenerating
3. **Target**: <$15/day operational AI costs through composite model routing
4. **Review**: Weekly cost audit — kill any spend that isn't generating or enabling revenue

## Financial Reporting

### Monthly P&L
Track: Revenue, COGS (API/compute), Gross Profit, Operating Expenses, Net Income

### Cash Flow
Track: Starting balance, Revenue in, Expenses out, Ending balance

### Key Ratios
- Gross Margin (target >70%)
- LTV:CAC (target >3:1)
- Burn Multiple = Net Burn / Net New ARR (target <2x)