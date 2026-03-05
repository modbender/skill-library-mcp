---
name: afrexai-startup-metrics-engine
model: default
version: 1.0.0
description: >
  Complete startup metrics command center — from raw data to investor-ready dashboards.
  Covers every stage (pre-seed to Series B+), every model (SaaS, marketplace, consumer, 
  hardware), with diagnostic frameworks, benchmark databases, and board-ready reporting.
tags: [startup, metrics, saas, kpis, unit-economics, growth, fundraising, investor, dashboard, arr, mrr, churn, ltv, cac]
---

# Startup Metrics Command Center

Your complete system for tracking, diagnosing, and communicating startup health — not just formulas, but the *thinking* behind what to measure, when, and what to do when numbers go wrong.

---

## Phase 1: Metrics Architecture

### Step 1 — Identify Your Model & Stage

Before tracking anything, classify yourself:

**Business Model:**
```yaml
model_type:
  saas:
    sub_type: # self-serve | sales-led | PLG | hybrid
    pricing: # per-seat | usage-based | flat | tiered
    contract: # monthly | annual | multi-year
  marketplace:
    type: # managed | unmanaged | SaaS-enabled
    unit: # GMV | take-rate | transaction
  consumer:
    type: # subscription | ad-supported | freemium | transactional
    engagement_model: # DAU/MAU | session-based | content
  hardware_plus_software:
    type: # device + subscription | IoT | embedded
```

**Stage (determines what matters):**

| Stage | ARR Range | North Star Focus | Board Cares About |
|-------|-----------|-------------------|-------------------|
| Pre-seed | $0-$50K | Engagement + retention signal | Problem-solution fit evidence |
| Seed | $50K-$500K | Cohort retention + early revenue | Product-market fit signals |
| Series A | $500K-$3M | Growth efficiency + unit economics | LTV:CAC, NDR, growth rate |
| Series B | $3M-$15M | Scalability + operating leverage | Rule of 40, magic number, burn multiple |
| Growth | $15M+ | Capital efficiency + market share | Net margins, NRR, competitive moat |

### Step 2 — Build Your Metric Stack

**Layer 1: Health Vitals (track daily)**
```
- Revenue: MRR, ARR, net new MRR
- Growth: MoM growth rate, WoW for early stage
- Retention: Logo churn rate, revenue churn rate
- Cash: Monthly burn, runway in months
```

**Layer 2: Efficiency (track weekly)**
```
- Unit economics: CAC, LTV, LTV:CAC ratio, payback months
- Sales: Pipeline coverage, win rate, sales cycle length
- Product: Activation rate, feature adoption, NPS/CSAT
- Team: Revenue per employee, quota attainment
```

**Layer 3: Strategic (track monthly)**
```
- NDR (Net Dollar Retention)
- Burn multiple
- Rule of 40 score
- Magic number
- Cohort analysis curves
```

---

## Phase 2: The Complete Formula Reference

### Revenue Metrics

```
MRR = Σ(active_subscriptions × monthly_price)
ARR = MRR × 12

Net New MRR = New MRR + Expansion MRR - Churned MRR - Contraction MRR

MRR Components:
  new_mrr:         First-time customer revenue this month
  expansion_mrr:   Upsell + cross-sell from existing customers
  churned_mrr:     Revenue lost from customers who left
  contraction_mrr: Revenue lost from downgrades (customer stayed)
  reactivation_mrr: Revenue from returning churned customers

MoM Growth = (MRR_current - MRR_previous) / MRR_previous
CMGR (Compound Monthly Growth Rate) = (MRR_end / MRR_start)^(1/months) - 1
```

**Why CMGR > MoM:** Monthly growth is noisy. CMGR smooths 6-12 month periods for real trend.

### Unit Economics

```
CAC = Total_Sales_Marketing_Spend / New_Customers_Acquired
  - Include: salaries, commissions, tools, ads, events, content costs
  - Exclude: product/engineering, CS (post-sale)
  - Time-lag adjustment: match spend to cohort it generated (typically 1-3 month lag)

Blended CAC vs Channel CAC:
  blended_cac = total_spend / total_new_customers
  channel_cac = channel_spend / channel_new_customers
  # Always track both — blended hides channel problems

LTV = ARPU × Gross_Margin% × Average_Customer_Lifetime
  # Or: LTV = ARPU × Gross_Margin% × (1 / Monthly_Churn_Rate)
  # Cap at 5 years for conservative estimates

LTV:CAC Ratio — THE ratio:
  > 5.0  → Under-investing in growth (spend more!)
  3.0-5.0 → Excellent efficiency
  1.5-3.0 → Healthy but watch payback period
  1.0-1.5 → Marginal — fix churn or reduce CAC
  < 1.0  → Burning cash per customer — STOP and fix

CAC Payback = CAC / (Monthly_ARPU × Gross_Margin%)
  < 6 months  → Elite (PLG companies)
  6-12 months → Great
  12-18 months → Acceptable for enterprise
  > 18 months → Danger zone (unless >130% NDR)
```

### Retention & Churn

```
Logo Churn Rate = Customers_Lost / Customers_Start_of_Period
Revenue Churn Rate = MRR_Lost / MRR_Start_of_Period
  # Revenue churn > logo churn = losing big customers (very bad)
  # Revenue churn < logo churn = losing small customers (less bad)

Net Dollar Retention (NDR) = (Starting_MRR + Expansion - Contraction - Churn) / Starting_MRR
  > 130% → World-class (Snowflake, Twilio territory)
  110-130% → Excellent
  100-110% → Good
  90-100% → Acceptable but concerning
  < 90% → Leaky bucket — growth can't outrun churn

Gross Dollar Retention (GDR) = (Starting_MRR - Contraction - Churn) / Starting_MRR
  # NDR without expansion — shows your floor
  > 90% → Sticky product
  80-90% → Normal for SMB
  < 80% → Product or market problem
```

### Growth Efficiency

```
Burn Multiple = Net_Burn / Net_New_ARR
  < 1.0 → Amazing (rare at early stage)
  1.0-1.5 → Great
  1.5-2.0 → Good
  2.0-3.0 → Mediocre
  > 3.0 → Bad — inefficient growth

Rule of 40 = Revenue_Growth_Rate% + Profit_Margin%
  > 40 → Healthy SaaS (IPO-ready)
  # Example: 60% growth + -20% margin = 40 ✓
  # Example: 20% growth + 20% margin = 40 ✓

Magic Number = Net_New_ARR_This_Quarter / Sales_Marketing_Spend_Last_Quarter
  > 1.0 → Efficient, invest more in S&M
  0.5-1.0 → OK, optimize before scaling
  < 0.5 → Inefficient — fix before spending more

Hype Ratio = Valuation / ARR
  # Reality check on fundraising expectations
  # Median SaaS multiples: 6-12x ARR (varies by growth + retention)
```

### Cash & Runway

```
Monthly Burn = Total_Monthly_Expenses - Total_Monthly_Revenue
Gross Burn = Total_Monthly_Expenses (ignoring revenue)
Net Burn = Gross_Burn - Revenue

Runway = Cash_Balance / Monthly_Net_Burn
  > 18 months → Comfortable
  12-18 months → Start planning next raise
  6-12 months → Urgently fundraising
  < 6 months → Default alive or dead calculation needed

Default Alive? = Can_Current_Growth_Rate_Make_Revenue > Expenses_Before_Cash_Runs_Out
  # Paul Graham's test — if growing, project the intersection
```

### Sales Efficiency

```
Sales Cycle Length = Avg_Days(First_Touch → Closed_Won)
Pipeline Coverage = Total_Pipeline_Value / Revenue_Target
  # Need 3-4x for predictable revenue
  
Win Rate = Deals_Won / Total_Deals_in_Stage
  By stage: SQL→Opp (30-40%), Opp→Proposal (50-60%), Proposal→Close (60-70%)

ACV (Annual Contract Value) = Total_Contract_Value / Contract_Years
ASP (Average Selling Price) = Total_Revenue / Deals_Closed

Quota Attainment = Actual_Bookings / Quota_Target
  # Healthy org: 60-70% of reps hitting quota

Sales Efficiency = Net_New_ARR / Fully_Loaded_Sales_Cost
  > 1.0 → Scalable
```

---

## Phase 3: Diagnostic Framework — PULSE Method

When a metric is off, don't just report it — diagnose it.

### P — Pattern Recognition
```
Questions:
- Is this a trend (3+ months) or a blip (1 month)?
- Is it seasonal or structural?
- Did it change gradually or suddenly?
- Which cohorts/segments are affected?
```

### U — Upstream Tracing
```
Every metric has upstream drivers. Trace back:

Revenue declining? →
  ├── New MRR down? → Lead volume? → Conversion rate? → Channel performance?
  ├── Expansion down? → Upsell attempts? → Product adoption? → CSM activity?
  └── Churn up? → Which segment? → Voluntary vs involuntary? → Reasons?

CAC increasing? →
  ├── Spend up? → Which channels? → CPM/CPC changes?
  ├── Volume same but cost up? → Market saturation? → Competition?
  └── Conversion down? → Funnel stage? → Lead quality? → Sales process?
```

### L — Leverage Point
```
Find the highest-impact intervention:
- Which single metric, if improved 10%, would cascade the most?
- What's the cheapest/fastest fix vs highest-impact fix?
- Score: Impact (1-5) × Feasibility (1-5) × Speed (1-5)
```

### S — So-What Translation
```
Convert metric into business language:
- "Churn increased 2%" → "We'll lose $X00K ARR this year at this rate"
- "CAC payback is 18 months" → "Each new customer is cash-negative for 1.5 years"
- "NDR is 95%" → "Even with zero new sales, we shrink 5% annually"
```

### E — Experiment Design
```yaml
diagnostic_experiment:
  hypothesis: "[Metric] is declining because [upstream cause]"
  test: "[Specific action] for [time period]"
  success_metric: "[Metric] improves by [X%] within [timeframe]"
  sample: "[Segment/cohort to test on]"
  kill_criteria: "Stop if [negative signal] within [days]"
```

---

## Phase 4: Cohort Analysis — The Truth Machine

Aggregate metrics lie. Cohorts tell the truth.

### Revenue Cohort Table
```
Track each monthly cohort's MRR over time:

         Month 0   Month 1   Month 3   Month 6   Month 12
Jan '25  $50K      $48K      $45K      $42K      $38K
Feb '25  $55K      $53K      $50K      $48K      —
Mar '25  $60K      $58K      $57K      $56K      —
Apr '25  $45K      $44K      $43K      —         —

Reading this:
- Jan cohort retained 76% at month 12 → mediocre
- Mar cohort retained 93% at month 3 → improving! What changed?
- Apr cohort started smaller but retention looks good
```

### Engagement Cohort (Non-Revenue Signal)
```yaml
cohort_engagement:
  week_1_activation: # % completing key action within 7 days
  week_4_habit: # % using product 3+ days in week 4
  month_3_retention: # % still active at 90 days
  
  # Leading indicators of revenue retention
  # If engagement drops, revenue follows 1-3 months later
```

### Cohort Red Flags
```
🚩 Each new cohort retains worse → product-market fit eroding
🚩 Large cohorts churn more → scaling quality issues
🚩 Specific channel cohorts churn fast → bad-fit leads
🚩 Expansion only in old cohorts → pricing/packaging problem
```

---

## Phase 5: Board & Investor Reporting

### Monthly Investor Update Template
```yaml
investor_update:
  subject: "[Company] — [Month] Update: [One-line headline]"
  
  # 1. TL;DR (3 bullets max)
  highlights:
    - "ARR: $X (+Y% MoM) — [context]"
    - "Key win: [biggest achievement]"
    - "Challenge: [biggest problem + what you're doing]"
  
  # 2. Key Metrics Table
  metrics:
    arr: {current: "", prior_month: "", delta: ""}
    mrr: {current: "", growth_mom: ""}
    customers: {total: "", new: "", churned: ""}
    ndr: ""
    burn_rate: ""
    runway_months: ""
    cash_balance: ""
    
  # 3. What Happened (5-7 bullets)
  wins: []
  challenges: []
  
  # 4. What's Next (3-5 bullets)
  next_month_priorities: []
  
  # 5. Asks (be specific!)
  asks:
    - intro: "Looking for intro to [person/company] for [reason]"
    - advice: "Would love 15 min on [specific topic]"
    - hiring: "Seeking [role] — know anyone?"
```

### Board Deck Metric Slides

**Slide 1: Business Health Dashboard**
```
ARR: $___     MoM: ___%     NDR: ___%
Customers: ___  New: ___    Churned: ___
Runway: ___ months          Burn Multiple: ___

Traffic light: 🟢 On track | 🟡 Watch | 🔴 Action needed
```

**Slide 2: Revenue Waterfall**
```
Starting MRR:     $___
+ New:            $___
+ Expansion:      $___
- Contraction:    $___
- Churn:          $___
= Ending MRR:     $___
```

**Slide 3: Unit Economics**
```
CAC: $___  →  LTV: $___  →  LTV:CAC: ___x
Payback: ___ months
Blended vs top channel efficiency
```

---

## Phase 6: Model-Specific Metrics

### SaaS Additions
```
Quick Ratio = (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)
  > 4.0 → Very healthy growth
  2.0-4.0 → Good
  1.0-2.0 → Sustainable but slow
  < 1.0 → Shrinking

Logo-to-Revenue Retention Gap:
  If logo retention 85% but revenue retention 95% → upsell compensates
  If logo retention 85% and revenue retention 85% → no expansion = problem

Expansion Revenue % = Expansion MRR / Total New MRR
  > 30% → Healthy at scale
  # Best SaaS: expansion > new revenue (Twilio was 170% NDR)
```

### Marketplace Additions
```
GMV (Gross Merchandise Value) = Total value of transactions on platform
Take Rate = Platform Revenue / GMV
  5-15% → Typical for most marketplaces
  15-30% → Managed/full-service marketplaces
  
Supply-side metrics:
  supply_liquidity = listings_with_transaction / total_listings
  time_to_first_match = avg_days_from_listing_to_sale
  
Demand-side metrics:
  search_to_fill = completed_transactions / searches
  repeat_purchase_rate = returning_buyers / total_buyers
```

### Consumer/PLG Additions
```
DAU/MAU Ratio:
  > 50% → Exceptional (messaging apps)
  25-50% → Strong habit (social, productivity)
  10-25% → Good (media, entertainment)
  < 10% → Weak engagement

Viral Coefficient (K-factor) = Invites_per_User × Conversion_Rate
  > 1.0 → Viral growth (each user brings >1 new user)
  0.5-1.0 → Amplified growth
  < 0.5 → Not viral — need paid acquisition

Free-to-Paid Conversion:
  PLG benchmark: 2-5% of free users convert
  Freemium benchmark: 1-3%
  Enterprise self-serve: 5-15%

Time to Value = Time from signup to "aha moment"
  # Reduce this aggressively — strongest lever for activation
```

---

## Phase 7: Metric Manipulation Red Flags

### Vanity vs Real Metrics

| Vanity (Avoid) | Real (Track) |
|----------------|--------------|
| Total signups | Activated users (completed key action) |
| Page views | Engaged sessions (>2 min or action taken) |
| "Pipeline" | Qualified pipeline (met ICP criteria) |
| Gross revenue | Net revenue (after refunds + credits) |
| Total customers | Active customers (logged in last 30d) |
| Downloads | WAU/MAU |
| "Partnerships" | Revenue from partnerships |

### Common Manipulation Tactics to Watch

```
🚩 Counting annual contracts as MRR at signing (vs. monthly recognition)
🚩 Excluding "one-time" churns from churn rate
🚩 Using gross revenue instead of net
🚩 Measuring CAC without fully-loaded costs
🚩 Cherry-picking best cohort as "representative"
🚩 Counting reactivations as new customers
🚩 Using "committed ARR" (signed but not live)
🚩 Trailing-12-month NDR when recent cohorts are worse
```

---

## Phase 8: Action Playbooks

### When CAC Is Too High
```
1. Audit channel efficiency — kill bottom 20% channels
2. Improve activation rate (reduces wasted spend)
3. Increase conversion at each funnel stage (+10% each = compound effect)
4. Shift mix: more organic/PLG, less paid
5. Reduce sales cycle length (lower cost per deal)
6. Tighten ICP — stop selling to bad-fit customers
```

### When Churn Is Too High
```
1. Segment: which customers churn? (Size, channel, use case)
2. Time: when do they churn? (Month 1-3 = onboarding, 6-12 = value, 12+ = competition)
3. Reason: exit survey + CS interviews (top 3 reasons)
4. Fix activation if month 1-3 churn
5. Fix value delivery if month 6-12 churn
6. Fix switching cost / competitive moat if 12+ churn
```

### When Growth Stalls
```
1. Check: is TAM exhausted in current segment? → Expand to adjacent
2. Check: conversion rates declining? → Product or message fatigue
3. Check: CAC rising with flat volume? → Channel saturation
4. Check: expansion revenue flat? → Packaging/pricing problem
5. Check: sales cycle lengthening? → Market conditions or competition
```

### When Raising Capital
```
Metrics investors care about BY STAGE:

Pre-seed: Engagement, retention curves, market size
Seed: MoM growth (15%+), retention cohorts, early unit economics
Series A: $1M+ ARR, 3x+ YoY growth, LTV:CAC > 3, NDR > 100%
Series B: $5M+ ARR, path to Rule of 40, burn multiple < 2, sales efficiency
```

---

## Quick Commands

- "Set up metrics for [stage] [model] startup" → Full metric stack recommendation
- "Diagnose [metric]" → PULSE diagnostic framework
- "Build investor update for [month]" → Template with guidance
- "Cohort analysis on [data]" → Retention curve analysis
- "Compare us to benchmarks" → Gap analysis vs stage-appropriate benchmarks
- "What metrics for Series [A/B] raise?" → Investor-ready checklist
- "Calculate unit economics from [data]" → Full LTV, CAC, payback analysis
- "Red flag check" → Scan metrics for warning signs
- "Board deck metrics" → Generate slide-ready metric views

---

## Edge Cases

### Multi-Product Companies
Track metrics per product line AND blended. Watch for cross-subsidization where one product's margins mask another's losses.

### Usage-Based Pricing
MRR is estimated, not contracted. Track committed vs consumed. Expansion is automatic (usage growth), so NDR is naturally higher — compare to usage-based peers, not seat-based.

### Negative Churn via Price Increases
If NDR > 100% only because of price increases (not organic expansion), this is fragile. Separate price-driven vs usage-driven expansion.

### Very Early Stage (Pre-Revenue)
Track leading indicators: activation rate, engagement frequency, NPS, waitlist growth, organic traffic, time-to-value. Revenue metrics come later — don't force them.

### Seasonal Businesses
Use YoY comparisons, not MoM. Adjust cohort analysis for seasonal patterns. Build seasonal forecast models.

---

*Built by AfrexAI — turning data into revenue.*
