---
name: Startup Fundraising Engine
slug: afrexai-startup-fundraising
version: 1.0.0
description: Complete startup fundraising system — from pre-seed to Series B. Investor targeting, pitch deck construction, term sheet negotiation, due diligence preparation, and cap table management.
tags: fundraising, startup, venture-capital, pitch-deck, term-sheet, investors, seed, series-a
---

# Startup Fundraising Engine ⚡

Complete fundraising operating system for founders raising pre-seed through Series B. Covers investor targeting, pitch construction, outreach, term sheet negotiation, due diligence preparation, and cap table management.

**Zero dependencies. Pure methodology.**

---

## Phase 1: Fundraising Readiness Assessment

### 8-Signal Quick Health Check

Score each 0-2 (0 = not ready, 1 = partially, 2 = ready):

| Signal | Question | Score |
|--------|----------|-------|
| Traction | Do you have measurable growth metrics? | /2 |
| Market | Can you articulate a $1B+ market bottoms-up? | /2 |
| Team | Do you have a founding team that can execute? | /2 |
| Product | Is there a working product or clear prototype? | /2 |
| Story | Can you explain the opportunity in 60 seconds? | /2 |
| Unit Economics | Do you know CAC, LTV, margins (or reasonable projections)? | /2 |
| Use of Funds | Do you have a clear 18-month plan for the capital? | /2 |
| Timing | Is now the right time to raise (runway, market, traction)? | /2 |

**Score interpretation:**
- 14-16: Ready to raise. Start immediately.
- 10-13: Almost ready. Fix gaps in 2-4 weeks, then launch.
- 6-9: Not ready. Build more traction first. Raising now will damage your reputation.
- 0-5: Too early. Focus on product and initial customers.

### Fundraising Strategy Brief

```yaml
fundraising_brief:
  company_name: ""
  stage: "" # pre-seed | seed | series-a | series-b
  current_arr_or_mrr: ""
  growth_rate_mom: "" # month-over-month
  team_size: 0
  months_of_runway: 0
  target_raise: "" # dollar amount
  target_valuation: "" # pre-money
  use_of_funds:
    engineering: "" # percentage + headcount
    sales_marketing: ""
    operations: ""
    runway_extension: ""
  timeline:
    start_date: ""
    target_close: "" # aim for 8-12 weeks
  key_metrics:
    customers: 0
    revenue: ""
    growth_rate: ""
    retention: ""
    burn_rate: ""
```

### Stage-Appropriate Raise Guide

| Stage | Typical Raise | Pre-Money Valuation | What You Need | Investor Type |
|-------|--------------|---------------------|---------------|---------------|
| Pre-seed | $250K-$1M | $2M-$6M | Idea + team + early signal | Angels, pre-seed funds |
| Seed | $1M-$4M | $6M-$15M | MVP + early traction + some revenue | Seed funds, angels |
| Series A | $5M-$20M | $20M-$60M | PMF + $1M+ ARR + clear GTM | Series A VCs |
| Series B | $15M-$50M | $60M-$200M | Scaling + $5M+ ARR + unit economics | Growth VCs |

### Raise-or-Don't Decision Framework

**Raise NOW if:**
- You have <6 months runway AND strong metrics
- A clear use of funds would unlock 3-5x growth
- Market timing is favorable (hot sector, strong VC appetite)
- You have warm investor interest

**DON'T raise if:**
- You can bootstrap to profitability in 6-12 months
- Metrics aren't strong enough (raising on weak numbers = bad terms)
- You're raising because "everyone else is" (worst reason)
- You haven't talked to 10+ potential investors informally first

---

## Phase 2: Investor Targeting & Pipeline

### Investor Selection Criteria

Score each potential investor 1-5:

| Dimension | Weight | What to Look For |
|-----------|--------|-----------------|
| Stage fit | 25% | Do they invest at your stage? Check recent deals, not website claims |
| Sector fit | 25% | Have they invested in your space? Adjacent counts |
| Check size | 15% | Does your raise match their typical check? |
| Value-add | 15% | What beyond money? Intros, expertise, brand? |
| Portfolio conflict | 10% | Any competitive portfolio companies? |
| Reputation | 10% | Founder references? How do they behave in downturns? |

### Target List Architecture

```yaml
investor_target:
  name: ""
  firm: ""
  title: ""
  email: ""
  linkedin: ""
  twitter: ""
  
  fit_score: 0 # 1-30 (sum of weighted dimensions)
  
  stage_focus: "" # pre-seed | seed | series-a | series-b | multi-stage
  sector_focus: [] # fintech, saas, health, etc.
  typical_check: "" # $500K-$2M
  recent_deals: [] # last 3-5 investments
  
  warm_path: "" # who can intro you?
  connection_strength: "" # strong | medium | weak | cold
  
  status: "" # researching | outreach | meeting | dd | term-sheet | pass | closed
  last_contact: ""
  next_action: ""
  notes: ""
```

### Pipeline Sizing Rules

| Round Size | Target Investors | Expected Meetings | Expected Term Sheets |
|------------|-----------------|-------------------|---------------------|
| Pre-seed ($500K) | 30-50 | 15-25 | 1-3 |
| Seed ($2M) | 50-80 | 25-40 | 2-4 |
| Series A ($10M) | 40-60 | 20-30 | 1-3 |
| Series B ($25M) | 20-40 | 10-20 | 1-2 |

**Conversion benchmarks:**
- Cold outreach → meeting: 5-10%
- Warm intro → meeting: 30-50%
- Meeting → second meeting: 30-40%
- Second meeting → term sheet: 10-20%
- Term sheet → close: 70-90%

### Tiering Strategy

**Tier 1 (Dream investors, 5-8):** Your ideal lead investors. Don't pitch them first — practice on Tier 3.

**Tier 2 (Strong fit, 15-20):** Good stage/sector fit. Many will become your actual lead.

**Tier 3 (Practice + optionality, 20-30):** Reasonable fit. Use for pitch practice and creating momentum.

**Tier 4 (Followers, 10-20):** Angels, smaller funds. Good for filling out the round after lead is set.

**CRITICAL RULE:** Pitch Tier 3 first (weeks 1-2), then Tier 2 (weeks 2-3), then Tier 1 (weeks 3-4). By the time you hit your dream investors, your pitch is sharp and you may already have term sheets.

---

## Phase 3: Pitch Deck Construction

### The 12-Slide Framework

Every great pitch deck follows this structure. Each slide has ONE job.

#### Slide 1: Title
- Company name + one-line description
- Your name, title, contact
- "We help [customer] do [outcome] by [how]"

#### Slide 2: Problem
- Paint the pain. Make the investor FEEL it.
- Use a specific story or example, not abstract stats
- "Today, [persona] struggles with [specific pain]"
- Show the cost of the problem (time, money, opportunity)

#### Slide 3: Solution
- Your product in 2-3 sentences
- Screenshot or demo GIF (visual > words)
- Focus on the "magic moment" — the thing that makes people say "wow"
- DO NOT list features. Show the transformation.

#### Slide 4: Why Now
- What changed that makes this possible/necessary TODAY?
- Technology shift? Regulatory change? Behavior change? Market timing?
- This is the most underrated slide. Nail it.

#### Slide 5: Market Size
- TAM → SAM → SOM (bottoms-up, NOT top-down)
- Show your math: [# of target customers] × [annual contract value] = SAM
- SAM should be $1B+ for VC-scale
- Show the growth trajectory of the market

#### Slide 6: Product / How It Works
- 3-step process or simple diagram
- Make it feel inevitable and obvious
- If you need more than 3 steps, simplify

#### Slide 7: Traction
- THE most important slide after Seed stage
- Revenue graph (up and to the right)
- Key metrics: ARR, MRR growth, customers, retention, NPS
- Logos of notable customers
- If pre-revenue: waitlist, LOIs, pilot results, engagement metrics

#### Slide 8: Business Model
- How you make money (clearly)
- Pricing model + unit economics
- ACV, gross margin, LTV/CAC, payback period
- Expansion revenue potential

#### Slide 9: Competition
- 2x2 matrix (NOT a feature comparison table)
- Your axes should be the dimensions where you win
- Show why you're in the top-right quadrant
- Mention "why not just use X?" for the obvious alternatives

#### Slide 10: Team
- Founder photos + relevant experience
- Why THIS team for THIS problem?
- Highlight: domain expertise, previous exits, technical depth
- Key hires made + key hires planned

#### Slide 11: The Ask
- How much you're raising
- Use of funds (3-4 categories max)
- What milestones this gets you to
- "This round gets us to [milestone] which positions us for [next round]"

#### Slide 12: Appendix (optional)
- Detailed financials
- Product roadmap
- Additional metrics
- Customer testimonials

### Pitch Deck Quality Checklist

- [ ] Total slides: 10-15 (12 ideal)
- [ ] Each slide has ONE key message
- [ ] Can be understood in 3 minutes without narration
- [ ] Fonts are readable at projection size (24pt minimum)
- [ ] Consistent design (colors, fonts, layout)
- [ ] No walls of text (max 30 words per slide)
- [ ] Traction slide has real numbers, not vanity metrics
- [ ] Market size is bottoms-up with shown math
- [ ] Ask is specific (amount + use of funds + milestones)
- [ ] Team slide shows founder-market fit

### The 60-Second Elevator Pitch

```
[Company] helps [specific customer] solve [specific problem].

Today, [customer] has to [painful current state], which costs them [quantified pain].

We built [solution] — a [category] that [key differentiator]. 

In [timeframe], we've [best traction metric]. We're growing [growth rate].

We're raising [amount] to [key milestone]. [Firm name] would be a great fit because [specific reason].
```

---

## Phase 4: Outreach & Meeting Strategy

### Warm Introduction Template

**To the connector:**
```
Hi [Name],

I'm raising a [seed/Series A] round for [Company] — we're [one-line description].

We've [best traction metric] and growing [rate]. I noticed [Investor Name] at [Firm] recently invested in [similar company] and thought there could be a strong fit.

Would you be comfortable making an intro? I've drafted a forwardable blurb below.

[Forwardable blurb — 3-4 sentences about the company, traction, what you're raising]

Really appreciate it either way.
```

### Cold Outreach Template (last resort)

```
Subject: [Company] — [one compelling metric]

Hi [Investor first name],

[One sentence about why you're reaching out to THEM specifically — recent investment, blog post, tweet].

I'm building [Company] — [one-line description]. We're at [best metric] and growing [rate] MoM.

Would love 20 minutes to share what we're seeing in [market]. Happy to work around your schedule.

[Your name]
[Company] | [website]
```

**Cold outreach rules:**
- NEVER send identical emails to multiple investors
- Reference something specific about THEM (shows research)
- Lead with your BEST metric
- Keep under 100 words
- Send Tuesday-Thursday, 8-10 AM their timezone

### First Meeting (30 min) Playbook

**Structure:**
- 0-2 min: Rapport + agenda setting
- 2-15 min: Walk through pitch (abbreviated — they've seen the deck)
- 15-25 min: Q&A (this is where the real evaluation happens)
- 25-28 min: Your questions for them
- 28-30 min: Next steps

**Your questions for them (ask 2-3):**
1. "What would you need to see to get conviction on this?"
2. "What's your typical decision timeline?"
3. "How do you typically work with portfolio companies post-investment?"
4. "What's your current fund deployment status?"
5. "Who else on your team would be involved in the decision?"

**After the meeting (within 2 hours):**
- Send thank you + any materials they requested
- Note their concerns — address in follow-up
- Update your CRM with status + next action

### Investor Objection Response Framework

| Objection | What They Mean | How to Respond |
|-----------|---------------|----------------|
| "Too early for us" | Traction insufficient | "What metrics would signal the right time?" (plants seed for future) |
| "Not in our thesis" | Sector/model mismatch | Accept gracefully. Ask for referrals to better-fit investors |
| "Valuation is too high" | They see risk you don't | "What comparable deals have you seen? Let's discuss what drives our thinking" |
| "We need to see more traction" | Interested but not convinced | "Happy to share monthly updates. What metric matters most to you?" |
| "Let me discuss with partners" | Could be real or polite pass | "Great. When's your next partner meeting? I'll send a follow-up brief" |
| "We just invested in a competitor" | True conflict | Move on. Ask if they know investors who'd be interested |
| "The market is too small" | Your TAM story isn't convincing | Reframe with bottoms-up math. Show expansion potential |
| "What's your moat?" | Worried about defensibility | Network effects, data advantages, switching costs, brand. Be specific |

---

## Phase 5: Financial Model & Projections

### 3-Statement Model Essentials

Investors expect a 3-5 year financial model. Keep it simple but defensible.

```yaml
financial_model:
  revenue_assumptions:
    current_arr: ""
    growth_rate_year1: "" # conservative
    growth_rate_year2: ""
    growth_rate_year3: ""
    acv: ""
    new_customers_per_month: ""
    churn_rate_annual: ""
    expansion_rate: ""
    
  cost_assumptions:
    cogs_percentage: "" # target <30% for SaaS
    engineering_headcount: [] # by quarter
    sales_headcount: []
    g_and_a_headcount: []
    avg_salary_eng: ""
    avg_salary_sales: ""
    marketing_spend_percentage: "" # of revenue
    
  key_outputs:
    gross_margin: "" # target >70% SaaS
    burn_rate_monthly: ""
    runway_months: ""
    breakeven_date: ""
    arr_at_next_raise: ""
```

### Revenue Projection Rules

1. **Bottom-up only.** [# sales reps] × [deals/rep/month] × [ACV] = revenue. NOT "if we get 1% of the market."
2. **Show your assumptions.** Every number should trace back to a testable assumption.
3. **Three scenarios.** Conservative (60% probability), Base (30%), Optimistic (10%). Present Base, have Conservative ready.
4. **Growth rate benchmarks:**

| ARR | Good Growth | Great Growth | Exceptional |
|-----|------------|--------------|-------------|
| $0-$1M | 15% MoM | 20% MoM | 30%+ MoM |
| $1M-$5M | 2.5x YoY | 3x YoY | 4x+ YoY |
| $5M-$20M | 2x YoY | 2.5x YoY | 3x+ YoY |
| $20M+ | 60% YoY | 80% YoY | 100%+ YoY |

### Unit Economics Deep Dive

```yaml
unit_economics:
  ltv:
    arpu_monthly: 0
    gross_margin: 0.0  # percentage
    churn_monthly: 0.0  # percentage
    formula: "ARPU × Gross Margin / Monthly Churn"
    result: 0
    
  cac:
    total_sales_marketing_spend: 0  # last quarter
    new_customers_acquired: 0  # last quarter
    formula: "S&M Spend / New Customers"
    result: 0
    
  ltv_to_cac_ratio: 0  # target >3x
  cac_payback_months: 0  # target <18 months
  
  health_check:
    ltv_cac_above_3x: false
    payback_under_18_months: false
    gross_margin_above_70: false
    net_dollar_retention_above_100: false
```

**Health benchmarks (SaaS):**
| Metric | Poor | OK | Good | Great |
|--------|------|-----|------|-------|
| LTV:CAC | <2x | 2-3x | 3-5x | >5x |
| CAC Payback | >24mo | 18-24mo | 12-18mo | <12mo |
| Gross Margin | <60% | 60-70% | 70-80% | >80% |
| Net Revenue Retention | <90% | 90-100% | 100-120% | >120% |
| Logo Churn (annual) | >15% | 10-15% | 5-10% | <5% |

---

## Phase 6: Term Sheet Negotiation

### Key Term Sheet Components

```yaml
term_sheet:
  economics:
    pre_money_valuation: ""
    investment_amount: ""
    post_money_valuation: ""  # pre + investment
    price_per_share: ""
    shares_issued: ""
    
  control:
    board_seats:
      founders: 0
      investors: 0
      independent: 0
    protective_provisions: [] # list of investor veto rights
    
  liquidation:
    preference: "" # 1x non-participating (standard) | 1x participating | 2x
    participation_cap: "" # if participating
    
  anti_dilution: "" # broad-based weighted average (standard) | full ratchet (bad)
  
  pro_rata_rights: true  # investors right to maintain ownership %
  
  vesting:
    founder_vesting: "" # 4 years, 1 year cliff (standard)
    acceleration: "" # single trigger | double trigger | none
    
  other:
    option_pool: "" # 10-15% post-money (negotiate pre vs post)
    drag_along: true
    right_of_first_refusal: true
    information_rights: true
    no_shop_period: "" # 30-60 days typical
```

### Term Sheet Red Flags 🚩

| Term | Standard | Acceptable | Red Flag |
|------|----------|------------|----------|
| Liquidation preference | 1x non-participating | 1x participating with 3x cap | >1x or uncapped participating |
| Anti-dilution | Broad-based weighted average | Narrow-based weighted average | Full ratchet |
| Board composition | Founder majority early stage | Equal (2-2-1 with independent) | Investor majority at seed |
| Option pool | 10% post-money | 10-15% pre-money | >20% pre-money |
| Vesting acceleration | Double-trigger | Single-trigger for CEO only | No acceleration |
| No-shop period | 30 days | 45 days | >60 days |
| Protective provisions | Standard (sale, new round, debt) | Expanded but reasonable | Veto on hiring, spending >$X |
| Pay-to-play | None at seed | Reasonable at Series A+ | Punitive conversion terms |

### Negotiation Playbook

**Rule 1: Optimize for valuation LAST.** The order of importance:
1. Amount raised (enough runway for 18-24 months)
2. Board composition (maintain founder control early)
3. Liquidation preferences (1x non-participating)
4. Anti-dilution protection (broad-based weighted average)
5. Valuation (important but not #1)

**Rule 2: Get multiple term sheets.** BATNA is everything. Even one competing offer changes the dynamic completely.

**Rule 3: Negotiate the option pool.** If they want 15% post-money, that dilutes YOU more than them. Push for smaller pool or post-money sizing.

**Rule 4: Understand the math.**
```
Founder ownership = 1 - (investor_shares + option_pool) / total_shares
Example: $5M pre + $2M raise + 10% pool
- Post-money: $7M
- Investor owns: $2M / $7M = 28.6%
- Pool: 10%
- Founders: 61.4%

With 15% pool pre-money:
- "Pre-money" is really $5M - 15% = $4.25M effective
- Investor owns: $2M / $6.25M = 32%
- Pool: 15%
- Founders: 53% ← see the difference?
```

**Rule 5: Get a good lawyer.** Don't negotiate term sheets yourself. Startup lawyers (Cooley, Wilson Sonsini, Gunderson, Orrick) know what's standard. Budget $15-30K for a priced round.

### Word-for-Word Negotiation Scripts

**On valuation:**
"We've seen comparable companies at our stage and traction level — [example 1], [example 2] — raise at [X] to [Y] pre-money. Given our [specific metric that's strong], we believe [your number] reflects fair value. What's driving your thinking on valuation?"

**On option pool:**
"We're happy with a 10% pool — that covers our hiring plan for the next 18 months. A 15% pool pre-money effectively reduces our valuation by [$ amount]. Could we either reduce the pool to 10% or calculate it post-money?"

**On liquidation preference:**
"We'd prefer standard 1x non-participating. Participating preferred with a cap could work, but uncapped participation significantly changes the economics for founders and early employees in moderate outcomes."

**On board seats:**
"At this stage, we think a 3-person board with 2 founders + 1 investor makes sense. We'd love your input and governance, but founder control is important to us while we're still finding our groove."

---

## Phase 7: Due Diligence Preparation

### DD Readiness Checklist

Prepare these BEFORE you start fundraising. Scrambling during DD kills deals.

#### Corporate Documents
- [ ] Certificate of incorporation (Delaware C-Corp preferred)
- [ ] Bylaws
- [ ] Board minutes (all meetings)
- [ ] Stockholder agreements
- [ ] Cap table (fully diluted, option grants, vesting schedules)
- [ ] 83(b) election filings for all founders
- [ ] State registrations / qualifications

#### Financial
- [ ] Financial statements (last 2 years + YTD)
- [ ] Bank statements (last 12 months)
- [ ] Tax returns (federal + state, last 2 years)
- [ ] Revenue by customer (concentration analysis)
- [ ] Accounts receivable aging
- [ ] Budget vs actuals
- [ ] Financial model (3-5 year projections)

#### IP & Technology
- [ ] Patent filings / applications
- [ ] Trademark registrations
- [ ] IP assignment agreements (ALL employees + contractors)
- [ ] Open source usage audit
- [ ] Technology architecture overview
- [ ] Security audit / SOC 2 status

#### Team & HR
- [ ] Employee list with titles, start dates, compensation
- [ ] Employment agreements (all employees)
- [ ] Contractor agreements (all contractors)
- [ ] Option grant schedule
- [ ] Benefits summary
- [ ] Key person dependencies

#### Legal
- [ ] Customer contracts (template + material contracts)
- [ ] Vendor agreements (material)
- [ ] Pending / threatened litigation
- [ ] Regulatory compliance status
- [ ] Privacy policy + terms of service
- [ ] Insurance policies

#### Metrics
- [ ] Monthly revenue / ARR waterfall (last 12+ months)
- [ ] Cohort retention data
- [ ] Unit economics (LTV, CAC, payback)
- [ ] Pipeline / bookings data
- [ ] NPS / customer satisfaction data
- [ ] Churn analysis by cohort

### Data Room Organization

```
📁 Data Room/
├── 📁 1-Corporate/
│   ├── Certificate_of_Incorporation.pdf
│   ├── Bylaws.pdf
│   ├── Board_Minutes/
│   └── Cap_Table_[date].xlsx
├── 📁 2-Financial/
│   ├── Financial_Statements/
│   ├── Tax_Returns/
│   ├── Bank_Statements/
│   └── Financial_Model_[date].xlsx
├── 📁 3-IP_Technology/
│   ├── IP_Assignments/
│   ├── Architecture_Overview.pdf
│   └── Security_Audit.pdf
├── 📁 4-Team_HR/
│   ├── Org_Chart.pdf
│   ├── Employment_Agreements/
│   └── Option_Grants.xlsx
├── 📁 5-Legal/
│   ├── Customer_Contracts/
│   ├── Vendor_Agreements/
│   └── Insurance_Policies/
├── 📁 6-Metrics/
│   ├── Monthly_Metrics_Dashboard.xlsx
│   ├── Cohort_Analysis.xlsx
│   └── Pipeline_Report.xlsx
└── 📁 7-Pitch_Materials/
    ├── Pitch_Deck_[date].pdf
    ├── Executive_Summary.pdf
    └── Product_Demo_Link.md
```

---

## Phase 8: Cap Table Management

### Cap Table Fundamentals

```yaml
cap_table:
  company: ""
  date: ""
  total_authorized_shares: 10000000
  
  common_stock:
    - holder: "Founder 1"
      shares: 0
      vesting: "4yr/1yr cliff"
      vested_shares: 0
      percentage: 0.0
    - holder: "Founder 2"
      shares: 0
      vesting: "4yr/1yr cliff"
      vested_shares: 0
      percentage: 0.0
      
  preferred_stock:
    - round: "Seed"
      investor: ""
      shares: 0
      price_per_share: 0.0
      amount_invested: 0
      percentage: 0.0
      liquidation_preference: "1x non-participating"
      
  option_pool:
    total_reserved: 0
    granted: 0
    exercised: 0
    available: 0
    percentage_of_fully_diluted: 0.0
    
  fully_diluted_shares: 0  # common + preferred + all options
```

### Dilution Math Every Founder Must Know

**Round-by-round dilution example:**

| Event | Founders | Seed Investor | Option Pool | Series A |
|-------|----------|---------------|-------------|----------|
| Formation | 100% | - | - | - |
| Option pool (10%) | 90% | - | 10% | - |
| Seed ($2M at $8M pre) | 72% | 20% | 8% | - |
| Option pool refresh (+5%) | 68.4% | 19% | 12.6% | - |
| Series A ($10M at $40M pre) | 54.7% | 15.2% | 10.1% | 20% |

**Key insight:** After a typical Seed + Series A, founders often own 50-60%. This is NORMAL. The goal isn't to minimize dilution — it's to maximize the value of your remaining shares.

**$100M exit at 55% ownership = $55M. $500M exit at 40% ownership = $200M.** Take the dilution that unlocks the bigger outcome.

### Pro-Rata Rights

Pro-rata rights let existing investors maintain their ownership percentage in future rounds.

**When it matters:** If a Seed investor has 15% and doesn't participate pro-rata in Series A, they get diluted to ~12%. With pro-rata, they invest enough to maintain 15%.

**Founder impact:** More pro-rata participation = less room for new investors = potential conflict. Manage this by setting clear allocation frameworks.

---

## Phase 9: Fundraising Process Management

### The Fundraising Sprint (8-12 Week Framework)

**Weeks 1-2: Preparation**
- Finalize pitch deck
- Build financial model
- Set up data room
- Build target list (50-80 investors)
- Write outreach templates
- Request warm intros (takes 1-2 weeks to materialize)

**Weeks 3-4: Tier 3 + Early Tier 2 Meetings**
- Practice pitch with 10-15 investors
- Refine based on questions and feedback
- Identify common objections, prepare responses
- Update deck based on learnings

**Weeks 5-6: Tier 1 + Tier 2 Meetings**
- Pitch your dream investors with a polished deck
- Create urgency with momentum ("we have 3 partner meetings next week")
- Share any early interest/term sheets (carefully)

**Weeks 7-8: Term Sheets + Negotiation**
- Receive and compare term sheets
- Negotiate key terms
- Check investor references (CRITICAL — call 3-5 portfolio founders)
- Select lead investor

**Weeks 9-12: Close**
- Finalize legal docs with lawyers
- Fill remaining allocation (angels, smaller checks)
- Wire transfer + board setup
- Announce (if desired)

### Weekly Pipeline Dashboard

```yaml
fundraising_pipeline:
  week: 0
  date: ""
  
  funnel:
    total_targets: 0
    outreach_sent: 0
    meetings_scheduled: 0
    meetings_completed: 0
    second_meetings: 0
    partner_meetings: 0
    term_sheets: 0
    
  conversion_rates:
    outreach_to_meeting: 0.0
    meeting_to_second: 0.0
    second_to_partner: 0.0
    partner_to_ts: 0.0
    
  momentum_signals:
    - "" # "3 partner meetings scheduled for next week"
    
  concerns:
    - "" # "Common pushback on market size"
    
  next_week_actions:
    - ""
```

### Follow-Up Cadence

| After | Action | Template |
|-------|--------|----------|
| First meeting | Thank you + materials | Send within 2 hours |
| 1 week | Follow-up + update | Share new metric or customer win |
| 2 weeks | Check-in | "Wanted to share [progress]" |
| Monthly | Investor update | Send to all investors in pipeline |
| Pass | Graceful accept | Ask for referrals + add to update list |

### Monthly Investor Update Template

```
Subject: [Company] — [Month] Update: [headline metric]

Hi [Name],

Quick update on [Company]:

📈 Key Metrics
• ARR: $X (+Y% MoM)
• Customers: X (+Y new)
• [Key operational metric]: X

🏆 Wins
• [Biggest win this month]
• [Second win]

🔥 Challenges
• [Honest challenge — shows self-awareness]

🎯 Next Month
• [Key goal 1]
• [Key goal 2]

We're raising [amount] — happy to chat if this is interesting.

Best,
[Name]
```

**Investor update rules:**
- Send monthly, even before you're raising
- Be honest about challenges (builds trust)
- Keep under 200 words
- Include 1-2 specific metrics with trajectory
- Send to everyone — passed investors sometimes come back

---

## Phase 10: Post-Close & Governance

### First 30 Days After Close

- [ ] Set up board meeting cadence (quarterly)
- [ ] Send announcement to team, customers, press (if desired)
- [ ] Update cap table and legal docs
- [ ] Set up board reporting package
- [ ] Have 1:1 onboarding with each board member
- [ ] Begin hiring per use-of-funds plan
- [ ] Set up monthly investor update cadence

### Board Meeting Template

```yaml
board_meeting:
  date: ""
  duration: "90 minutes"
  
  agenda:
    - topic: "CEO Update"
      duration: "15 min"
      content: "High-level strategy, key decisions, morale"
      
    - topic: "Financial Review"
      duration: "15 min"
      content: "Revenue, burn, runway, budget vs actual"
      
    - topic: "Product & Metrics"
      duration: "15 min"
      content: "Key metrics, product roadmap, customer feedback"
      
    - topic: "Deep Dive Topic"
      duration: "20 min"
      content: "One strategic topic for board input (GTM, hiring, partnerships)"
      
    - topic: "Open Discussion"
      duration: "15 min"
      content: "Board member questions, concerns, opportunities"
      
    - topic: "Closed Session"
      duration: "10 min"
      content: "Exec compensation, sensitive matters"
```

### Board Package (Send 3 Days Before Meeting)

| Section | Contents |
|---------|----------|
| Executive Summary | 1-page: wins, challenges, key decisions, help needed |
| Financial Dashboard | P&L, balance sheet, cash flow, runway, burn |
| Metrics Dashboard | ARR, growth, retention, pipeline, conversion |
| Product Update | Shipped features, roadmap, key customer feedback |
| Team Update | Headcount, open roles, notable hires/departures |
| Strategic Decisions | 1-2 topics requiring board input or approval |

---

## Phase 11: Alternative Fundraising Strategies

### SAFE Notes (Pre-Seed / Seed)

**When to use:** Pre-seed and seed when speed matters more than precision.

| SAFE Type | Best For | Watch Out |
|-----------|----------|-----------|
| Valuation Cap only | Most common. Sets maximum conversion price | Cap IS your effective valuation |
| Discount only | Rare. X% discount to next round price | Risky — no ceiling on conversion price |
| Cap + Discount | Best protection for investors | Most dilutive for founders |
| MFN (Most Favored Nation) | Very early, no valuation signal | Converts at best terms given to any investor |

**SAFE best practices:**
- Use Y Combinator standard SAFE (don't modify)
- Post-money SAFEs are now standard (clearer dilution math)
- Stack no more than $2-3M in SAFEs before pricing a round
- Track ALL SAFEs in your cap table (they WILL convert)

### Revenue-Based Financing

**When to use:** You have revenue but don't want to give up equity.

| Provider | Typical Terms | Best For |
|----------|--------------|---------|
| Pipe | Advance on ARR | SaaS with annual contracts |
| Clearco | % of revenue repayment | E-commerce, DTC |
| Lighter Capital | Revenue share | SaaS $200K-$5M ARR |
| Traditional bank | Venture debt | Post-Series A |

### Venture Debt

**When to use:** Extend runway between equity rounds without dilution.

- Typical terms: 2-3 year term, interest + warrants (0.5-2% of equity)
- Usually available after Series A (sometimes Seed)
- DON'T use venture debt as a substitute for equity — use it as a supplement
- Rule: Never take venture debt that represents >25% of your last equity raise

---

## Quality Scoring

### 100-Point Fundraising Readiness Rubric

| Dimension | Weight | Score (0-10) |
|-----------|--------|-------------|
| Traction & Metrics | 20% | /10 |
| Pitch & Story | 15% | /10 |
| Financial Model | 15% | /10 |
| Team & Founder-Market Fit | 15% | /10 |
| Market Opportunity | 10% | /10 |
| Data Room Readiness | 10% | /10 |
| Investor Pipeline Quality | 10% | /10 |
| Legal & Corporate Structure | 5% | /10 |

**Weighted score = Σ (weight × score × 10)**

| Score | Grade | Action |
|-------|-------|--------|
| 85-100 | A | Launch fundraise immediately |
| 70-84 | B | Fix 1-2 gaps, launch in 2 weeks |
| 55-69 | C | Significant work needed (4-6 weeks) |
| 40-54 | D | Major gaps — build more traction first |
| 0-39 | F | Not ready. Focus on product-market fit |

---

## Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Raising too early (weak metrics) | Build traction first. Bad first impressions are permanent |
| 2 | Raising too little (12 months runway) | Raise for 18-24 months. Fundraising takes longer than expected |
| 3 | No warm intros (all cold outreach) | Network for 6 months before you need to raise |
| 4 | Pitching dream investors first | Practice on Tier 3, then work up to Tier 1 |
| 5 | Optimizing only for valuation | Terms matter more. 1x non-participating > higher valuation with participating |
| 6 | No BATNA (only one term sheet) | Run a parallel process. Multiple term sheets = leverage |
| 7 | Ignoring investor references | Call 3-5 portfolio founders. Ask about behavior in bad times |
| 8 | Sloppy data room | Prepare everything before you start. Scrambling kills momentum |
| 9 | Top-down market sizing | Bottom-up always. Show your math |
| 10 | Not sending investor updates | Monthly updates to all investors, even those who passed |

---

## Edge Cases

### First-Time Founder
- Lean on advisors who've raised before
- Consider an accelerator (YC, Techstars) for credibility + network
- Accept slightly lower valuation for a great investor with strong brand
- Double your timeline estimates — everything takes longer the first time

### Down Round
- Try alternatives first: bridge round, extension, venture debt
- If unavoidable: negotiate pay-to-play provisions (forces all investors to participate)
- Communicate proactively with existing investors — no surprises
- Reframe the narrative: "We're resetting to grow sustainably"

### Bootstrapped → First Raise
- Lead with your profitability story (rare and valuable)
- You have MASSIVE leverage — you don't NEED the money
- Negotiate from strength: higher valuation, better terms, board control
- Consider raising a small round ($1-2M) to test the VC relationship

### Founder Solo (No Co-Founder)
- Address it head-on: "I'm looking for my #2 — this round funds that search"
- Show strong advisors / early team members
- Demonstrate extreme execution velocity as proof you can recruit
- Consider finding a co-founder before raising (strongest signal)

### International Founder (Non-US)
- Incorporate in Delaware (non-negotiable for US VCs)
- Use Stripe Atlas, Clerky, or Firstbase for setup
- Consider US-based angels first for credibility
- Time zone overlap with US investors matters — schedule accordingly

---

## Natural Language Commands

When this skill is active, the agent responds to:

1. "Assess my fundraising readiness" → Run Phase 1 assessment
2. "Build my investor target list" → Phase 2 pipeline creation
3. "Review my pitch deck" → Phase 3 quality checklist
4. "Draft investor outreach" → Phase 4 templates
5. "Build my financial model" → Phase 5 projections
6. "Analyze this term sheet" → Phase 6 red flag analysis
7. "Prepare my data room" → Phase 7 checklist
8. "Calculate dilution for [amount] at [valuation]" → Phase 8 math
9. "Plan my fundraising sprint" → Phase 9 timeline
10. "Prepare my board meeting" → Phase 10 package
11. "Compare SAFE vs priced round" → Phase 11 alternatives
12. "Score my fundraising readiness" → Quality rubric

---

*Built by AfrexAI — Autonomous AI agents for business growth.*

*⚡ Level up your fundraising with industry-specific context:*
*[AfrexAI Context Packs — $47](https://afrexai-cto.github.io/context-packs/) — SaaS, Fintech, Healthcare, and 7 more verticals.*

*🔗 More free skills by AfrexAI:*
- `afrexai-founder-os` — Complete founder operating system
- `afrexai-investor-engine` — Investment analysis from the investor side
- `afrexai-pricing-strategy` — Pricing optimization
- `afrexai-business-model-engine` — Business model design
- `afrexai-saas-billing-engine` — SaaS billing & subscription management
