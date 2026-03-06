---
name: afrexai-sales-funnel-engine
description: "Design, build, optimize, and scale sales funnels for any business model. Use when mapping customer journeys, diagnosing conversion leaks, building landing pages, designing email sequences, setting up attribution, A/B testing funnel stages, or scaling paid acquisition. Covers B2B, B2C, SaaS, services, ecommerce, and hybrid funnels. Trigger on: sales funnel, conversion funnel, funnel optimization, lead funnel, why aren't people buying, funnel audit, landing page, email sequence, conversion rate, customer journey, pipeline conversion, funnel metrics."
---

# Sales Funnel Engine

Complete system for designing, measuring, optimizing, and scaling sales funnels across any business model.

---

## Phase 1: Funnel Architecture Assessment

Before building or optimizing, assess current state.

### Funnel Health Check (answer each, score 0-2)

```yaml
funnel_health:
  clarity:
    - question: "Can you describe your funnel stages in under 30 seconds?"
    - question: "Do you know your conversion rate at every stage?"
    - question: "Can you name your #1 funnel leak right now?"
  measurement:
    - question: "Do you track stage-by-stage conversion weekly?"
    - question: "Do you know your CAC and LTV?"
    - question: "Do you have attribution set up?"
  optimization:
    - question: "Have you A/B tested in the last 30 days?"
    - question: "Do you have automated nurture sequences?"
    - question: "Do you review funnel metrics weekly?"
  # Score: 0-6 = Critical, 7-12 = Developing, 13-18 = Mature
```

### Business Model → Funnel Type Decision Matrix

| Business Model | Primary Funnel | Avg Deal Size | Sales Cycle | Automation Level |
|---|---|---|---|---|
| SaaS < $50/mo | Product-Led Growth | Low | Days | 95% automated |
| SaaS $50-500/mo | Hybrid (PLG + Sales) | Medium | 1-4 weeks | 70% automated |
| SaaS > $500/mo | Sales-Led | High | 1-6 months | 40% automated |
| Services < $5K | High-Touch Light | Medium | 1-2 weeks | 60% automated |
| Services $5K-50K | Consultative | High | 2-8 weeks | 30% automated |
| Services > $50K | Enterprise | Very High | 3-12 months | 20% automated |
| Ecommerce < $50 | Direct Response | Low | Minutes | 98% automated |
| Ecommerce $50-500 | Considered Purchase | Medium | Days-weeks | 85% automated |
| Info Products | Launch/Evergreen | Low-Medium | Days | 90% automated |
| Marketplace | Two-Sided | Varies | Varies | 80% automated |

---

## Phase 2: Funnel Blueprint Design

### Universal 7-Stage Framework

```
ATTRACT → CAPTURE → NURTURE → CONVERT → ACTIVATE → RETAIN → EXPAND
```

Every business uses these stages. The tactics, timing, and automation level vary by model.

### Funnel Blueprint YAML Template

```yaml
funnel:
  name: "[Product/Service] Sales Funnel"
  model: "product-led | sales-led | hybrid | direct-response | launch"
  target_customer:
    icp: "[Ideal Customer Profile - one sentence]"
    pain: "[Primary pain point they're trying to solve]"
    awareness_level: "unaware | problem-aware | solution-aware | product-aware | most-aware"
    budget_range: "$X - $Y"
    decision_maker: "[Title/role]"
    buying_trigger: "[What event makes them search for a solution NOW]"
  
  stages:
    attract:
      channels: []  # ranked by expected ROI
      content_types: []
      budget_monthly: "$X"
      target_volume: "X visitors/month"
    
    capture:
      mechanism: "free trial | lead magnet | demo request | consultation | quiz | webinar"
      offer: "[What they get in exchange for contact info]"
      form_fields: []  # minimum viable — every field reduces conversion 10-25%
      target_rate: "X% of visitors"
    
    nurture:
      sequence_type: "email | retargeting | content | community | multi-channel"
      touchpoints: X
      duration: "X days"
      target_rate: "X% to next stage"
    
    convert:
      mechanism: "self-checkout | sales call | proposal | demo | trial expiry"
      pricing_page: true | false
      social_proof: []
      risk_reversal: "[guarantee, trial, refund policy]"
      target_rate: "X%"
    
    activate:
      first_value_target: "X minutes to aha moment"
      onboarding_type: "self-serve | guided | white-glove"
      success_milestones: []
      target_rate: "X% complete onboarding in Y days"
    
    retain:
      check_in_cadence: "weekly | biweekly | monthly | quarterly"
      value_reminder: "[how you show ROI to customer]"
      health_signals: []
      churn_prevention: []
      target_rate: "X% monthly retention"
    
    expand:
      upsell_triggers: []
      cross_sell_products: []
      referral_program: true | false
      target_rate: "X% expansion revenue"
```

---

## Phase 3: Stage-by-Stage Tactics & Templates

### Stage 1: ATTRACT — Get the Right Eyeballs

**Channel Selection Framework** (score each 1-5):

| Factor | Weight | Question |
|---|---|---|
| Audience presence | 5x | Is your ICP actively using this channel? |
| Intent level | 4x | Are they searching for solutions (high intent) or browsing (low intent)? |
| CAC potential | 3x | What's the realistic cost per qualified visitor? |
| Scalability | 2x | Can you 10x spend without diminishing returns? |
| Your advantage | 2x | Do you have unfair advantage here (expertise, network, content)? |
| Time to results | 1x | How fast can you validate this channel? |

**Channel Playbook by Intent Level:**

**High intent (searching for solution):**
- Google Search Ads — target "[problem] solution", "[competitor] alternative"
- SEO — target "[problem] how to", "best [solution category]"
- G2/Capterra/review sites — be listed where buyers compare
- Partner referrals — leverage trust from complementary products

**Medium intent (evaluating options):**
- LinkedIn Ads — target by job title + company size + industry
- Content marketing — thought leadership, comparison guides, case studies
- Webinars — demonstrate expertise live
- YouTube — how-to videos solving their problem

**Low intent (building awareness):**
- Social media organic — build brand, share insights
- Podcasts — guest appearances reaching target audience
- Community building — own the conversation in your niche
- Display/social ads — retarget website visitors only (cold display rarely works)

**Rule: Start with ONE high-intent channel. Master it. Then add ONE medium-intent channel. Never run more than 3 channels simultaneously until each is profitable.**

### Stage 2: CAPTURE — Convert Visitors to Leads

**Lead Magnet Selection by Awareness Level:**

| Awareness Level | Best Lead Magnets | Why It Works |
|---|---|---|
| Unaware | Quiz, assessment, calculator | Diagnoses their problem |
| Problem-aware | Checklist, cheatsheet, template | Quick tactical value |
| Solution-aware | Comparison guide, case study | Helps them evaluate |
| Product-aware | Free trial, demo, consultation | Let them experience it |
| Most-aware | Discount, bonus, limited offer | Remove final friction |

**Landing Page Template (7 sections, in order):**

```
1. HEADLINE: [Outcome they want] + [Timeframe or mechanism]
   Formula: "Get [Result] Without [Pain] in [Timeframe]"
   Example: "Close 3x More Deals Without Cold Calling in 90 Days"

2. SUBHEADLINE: Expand on the mechanism or address skepticism
   Example: "Our AI sales assistant handles prospecting so you focus on closing"

3. SOCIAL PROOF BAR: Logos, "Trusted by X companies", star rating
   Rule: Show proof BEFORE explaining the product

4. PROBLEM AGITATION: 3-5 bullet points of pain they recognize
   Start each with "Tired of..." or "Frustrated by..." or "Still..."
   
5. SOLUTION: What you offer (features → benefits)
   Rule: Every feature needs a "so that..." benefit
   Template: "[Feature] so you can [benefit] which means [outcome]"

6. PROOF: Case study, testimonial, or data point
   Formula: "[Name/Company] achieved [specific result] in [timeframe]"
   
7. CTA: One clear action
   Rules:
   - Button text = outcome, not action ("Get My Free Plan" not "Submit")
   - Reduce form to minimum fields (name + email for lead magnets)
   - Add micro-commitment copy below button ("No credit card required")
```

**Landing Page Conversion Benchmarks:**

| Traffic Source | Good | Great | World-Class |
|---|---|---|---|
| Paid search | 3-5% | 5-8% | 8-12% |
| Paid social | 2-4% | 4-6% | 6-10% |
| Organic search | 2-3% | 3-5% | 5-8% |
| Email | 5-10% | 10-15% | 15-25% |
| Referral | 3-5% | 5-10% | 10-20% |
| Direct | 3-5% | 5-8% | 8-15% |

### Stage 3: NURTURE — Build Trust Over Time

**Email Nurture Sequence Templates:**

#### Sequence A: Education-First (for problem-aware leads)

```yaml
nurture_sequence:
  trigger: "Lead magnet download"
  goal: "Move to demo/trial request"
  
  email_1:
    delay: "immediate"
    subject: "Your [lead magnet] + a quick question"
    purpose: "Deliver asset + ask about their biggest challenge"
    cta: "Reply with your #1 challenge"
    
  email_2:
    delay: "+2 days"
    subject: "The [cost of inaction] most [ICPs] don't see"
    purpose: "Agitate the problem with data/story"
    cta: "Read the full case study"
    
  email_3:
    delay: "+2 days"
    subject: "How [similar company] solved [exact problem]"
    purpose: "Social proof — detailed case study"
    cta: "See how they did it"
    
  email_4:
    delay: "+3 days"
    subject: "[First name], quick thought on your [problem area]"
    purpose: "Personalized insight based on their industry/role"
    cta: "Want me to show you how this applies to you?"
    
  email_5:
    delay: "+3 days"
    subject: "The 3 things that actually move the needle on [outcome]"
    purpose: "Framework/methodology — position expertise"
    cta: "Try it free / Book a call"
    
  email_6:
    delay: "+4 days"
    subject: "Is [problem] still on your plate?"
    purpose: "Direct ask — are they ready?"
    cta: "Book 15 min — I'll show you exactly how we'd help"
```

#### Sequence B: Trial Conversion (for product-aware leads on free trial)

```yaml
trial_sequence:
  trigger: "Free trial started"
  goal: "Activate → Convert to paid"
  urgency: "trial_length"
  
  email_1:
    delay: "immediate"
    subject: "You're in! Here's your fastest path to [result]"
    purpose: "Onboarding — guide to aha moment"
    cta: "Complete this 5-minute setup"
    
  email_2:
    delay: "+1 day"
    subject: "Did you try [key feature]?"
    purpose: "Feature highlight — the thing that hooks people"
    cta: "Try it now (takes 2 minutes)"
    
  email_3:
    delay: "+3 days"
    subject: "[Name], you've unlocked [achievement]"
    purpose: "Celebrate progress + show value"
    cta: "See your results so far"
    
  email_4:
    delay: "+5 days (behavioral)"
    # If active: "Power users do this next..."
    # If inactive: "Need help getting started?"
    purpose: "Behavioral fork — active vs inactive"
    
  email_5:
    delay: "-3 days before trial end"
    subject: "Your trial ends in 3 days — here's what you'd lose"
    purpose: "Loss aversion — show what they've built/achieved"
    cta: "Upgrade now to keep your [data/setup/progress]"
    
  email_6:
    delay: "-1 day before trial end"
    subject: "Last day — [specific thing they used] goes away tomorrow"
    purpose: "Final urgency with specific value at risk"
    cta: "Keep your account"
```

#### Sequence C: High-Touch Nurture (for sales-led, post-discovery call)

```yaml
sales_nurture:
  trigger: "Discovery call completed, no close"
  goal: "Move to proposal/close"
  
  email_1:
    delay: "+1 hour"
    subject: "Summary from our conversation"
    purpose: "Recap + next steps + timeline"
    include: "Their stated problem, your proposed solution, 3 next steps"
    
  email_2:
    delay: "+3 days"
    subject: "Relevant to our conversation — [specific insight]"
    purpose: "Add value — article, case study, or data point relevant to THEIR situation"
    
  email_3:
    delay: "+5 days"
    subject: "[Competitor/peer company] just did this..."
    purpose: "Social proof / competitive pressure (ethical)"
    
  email_4:
    delay: "+7 days"
    subject: "Quick question about [their stated timeline]"
    purpose: "Re-engage on THEIR timeline/urgency"
    
  email_5:
    delay: "+14 days"
    subject: "Still thinking about [problem]?"
    purpose: "Check in — offer new angle or updated offer"
```

### Stage 4: CONVERT — Close the Deal

**Pricing Page Optimization Checklist:**

- [ ] Lead with annual pricing (show monthly as more expensive)
- [ ] Highlight recommended tier visually (border, badge, different color)
- [ ] Show 3 tiers maximum (decoy pricing: cheap/recommended/premium)
- [ ] Feature comparison table below pricing cards
- [ ] FAQ section addressing top 5 objections
- [ ] Social proof near CTA (logos, testimonial, user count)
- [ ] Risk reversal above or below CTA (guarantee, trial, refund)
- [ ] CTA button text = outcome ("Start Growing" not "Buy Now")
- [ ] Annual savings shown as dollar amount ("Save $240/year")
- [ ] Enterprise/custom option for high-value prospects

**Objection Handling Matrix:**

| Objection | Type | Response Framework |
|---|---|---|
| "Too expensive" | Price | Reframe to cost of inaction. "What does NOT solving this cost you per month?" |
| "Need to think about it" | Stall | Identify the real blocker. "What specifically would you want to think through?" |
| "Need to check with [person]" | Authority | Offer to present to them. "Want me to join a call with [person]?" |
| "We're using [competitor]" | Status quo | Contrast specifically. "What made you look at alternatives?" |
| "Not the right time" | Timing | Anchor to their timeline. "When does this become urgent?" |
| "Can you do a discount?" | Price | Trade, don't discount. "I can do X if you commit to annual/sign by Friday" |
| "We tried something similar" | Trust | Acknowledge + differentiate. "What went wrong? Here's how we're different..." |

**Conversion Rate Benchmarks by Funnel Type:**

| Conversion Point | B2B SaaS | B2C SaaS | Services | Ecommerce |
|---|---|---|---|---|
| Visit → Lead | 2-5% | 3-7% | 3-8% | 1-3% |
| Lead → MQL | 15-30% | 20-40% | 20-35% | N/A |
| MQL → SQL | 30-50% | N/A | 40-60% | N/A |
| SQL → Opportunity | 50-70% | N/A | 50-70% | N/A |
| Opportunity → Close | 20-35% | N/A | 25-40% | N/A |
| Trial → Paid | 5-15% | 3-10% | N/A | N/A |
| Cart → Purchase | N/A | N/A | N/A | 65-75% |
| Visit → Purchase | N/A | N/A | N/A | 2-4% |

### Stage 5: ACTIVATE — First Value Fast

**Time-to-Value Framework:**

```yaml
activation:
  aha_moment:
    definition: "[The specific moment the customer FEELS the value]"
    # Examples:
    # CRM: "When they see their first pipeline report"
    # Analytics: "When they see their first dashboard with real data"
    # AI tool: "When it generates something they'd actually use"
    
  steps_to_aha:
    - step: "[Action 1]"
      target_time: "X minutes"
      help_needed: "tooltip | video | human"
    - step: "[Action 2]"
      target_time: "X minutes"
    - step: "[Action 3 = AHA]"
      target_time: "X minutes"
  
  total_target: "< 10 minutes for self-serve, < 1 day for enterprise"
  
  activation_metric: "[What you measure to confirm they activated]"
  # Examples: "Completed setup wizard", "Imported first data", "Sent first campaign"
  
  benchmark: "80%+ of new users should activate within [timeframe]"
```

**Onboarding Anti-Patterns:**
- Asking users to configure everything before showing value (setup ≠ activation)
- Showing ALL features at once (progressive disclosure beats feature dumps)
- No follow-up for users who don't activate within 48 hours
- Same onboarding for all user types (segment by use case/role)
- No clear "you're done" signal (users don't know when setup is complete)

### Stage 6: RETAIN — Keep Them Paying

**Retention Diagnostic Decision Tree:**

```
Is monthly churn > 5%?
├── YES → Is activation rate < 80%?
│   ├── YES → Problem is onboarding. Fix activation first.
│   └── NO → Is NPS < 30?
│       ├── YES → Product-market fit issue. Talk to churned customers.
│       └── NO → Is churn concentrated in specific segment?
│           ├── YES → Wrong ICP. Tighten acquisition targeting.
│           └── NO → Check: pricing too high? Support too slow? Better competitor?
└── NO → Focus on expansion revenue instead of churn reduction.
```

**Retention Lever Ranking (by impact):**

1. **Product quality** — Does it actually solve the problem? (highest impact)
2. **Activation** — Did they reach the aha moment?
3. **Habit formation** — Is it embedded in their workflow?
4. **Switching costs** — How much would it cost to leave? (data, integrations, training)
5. **Community** — Do they feel belonging?
6. **Support quality** — When things break, how fast do you fix?
7. **Pricing perception** — Do they feel they're getting a deal?

### Stage 7: EXPAND — Grow Revenue Per Customer

**Expansion Revenue Signals:**

```yaml
upsell_signals:
  usage_based:
    - "Hitting plan limits (seats, storage, API calls)"
    - "Using product daily (high engagement = high willingness to pay more)"
    - "Multiple team members using it"
  outcome_based:
    - "Achieved stated ROI goal"
    - "Renewed without negotiating price"
    - "Referred another customer"
  timing_based:
    - "90 days post-activation (relationship established)"
    - "Annual renewal approaching (natural pricing conversation)"
    - "Business growing (more revenue = more budget)"
```

**Net Revenue Retention (NRR) Benchmarks:**

| NRR | Rating | What It Means |
|---|---|---|
| < 90% | Critical | Losing revenue faster than expanding |
| 90-100% | Below average | Treading water |
| 100-110% | Good | Growing without new customers |
| 110-130% | Great | Strong expansion motion |
| 130%+ | World-class | Customers spending significantly more over time |

---

## Phase 4: Funnel Diagnostics & Optimization

### Funnel Audit Checklist (run monthly)

```yaml
funnel_audit:
  date: "YYYY-MM-DD"
  
  traffic:
    total_visitors: X
    by_channel: {}
    trend: "up | flat | down"
    cost_per_visitor: "$X"
  
  capture:
    leads_generated: X
    visitor_to_lead_rate: "X%"
    best_converting_page: "[URL]"
    worst_converting_page: "[URL]"
    action: "[What to test/improve]"
  
  nurture:
    leads_in_nurture: X
    email_open_rate: "X%"
    email_click_rate: "X%"
    nurture_to_opportunity_rate: "X%"
    action: "[What to test/improve]"
  
  conversion:
    opportunities: X
    win_rate: "X%"
    avg_deal_size: "$X"
    sales_cycle_days: X
    action: "[What to test/improve]"
  
  activation:
    new_customers: X
    activation_rate: "X%"
    time_to_value: "X days"
    action: "[What to test/improve]"
  
  retention:
    monthly_churn: "X%"
    nrr: "X%"
    action: "[What to test/improve]"
  
  overall:
    cac: "$X"
    ltv: "$X"
    ltv_cac_ratio: "X:1"  # Target: > 3:1
    payback_months: X  # Target: < 12
    biggest_leak: "[Stage with worst conversion]"
    this_month_focus: "[ONE thing to fix]"
```

### A/B Testing Protocol

**What to test (by stage, ranked by impact):**

| Stage | High-Impact Tests | Expected Lift |
|---|---|---|
| Capture | Headline, CTA button text, form length | 20-50% |
| Capture | Lead magnet type, social proof placement | 10-30% |
| Nurture | Subject lines, send time, email length | 10-25% |
| Nurture | Sequence length, content type | 5-20% |
| Convert | Pricing display, guarantee copy, testimonial | 10-40% |
| Convert | Checkout flow steps, payment options | 5-20% |
| Activate | Onboarding steps, first-run experience | 15-40% |

**Test Rules:**
1. Only test ONE variable at a time
2. Need 100+ conversions per variant for statistical significance
3. Run for minimum 2 weeks (avoid day-of-week bias)
4. Decide significance threshold BEFORE running (p < 0.05 standard)
5. If test is inconclusive after 4 weeks, the difference is too small to matter — move on

**Statistical Significance Quick Reference:**

| Conversions/variant | Minimum detectable difference |
|---|---|
| 100 | ~20% relative change |
| 250 | ~13% relative change |
| 500 | ~9% relative change |
| 1,000 | ~6% relative change |
| 5,000 | ~3% relative change |

---

## Phase 5: Funnel Economics & Attribution

### Unit Economics Calculator

```yaml
unit_economics:
  revenue:
    avg_deal_size: "$X"
    avg_customer_lifetime_months: X
    monthly_expansion_rate: "X%"
    ltv: "$X"  # = avg_deal_size × lifetime × (1 + expansion)
  
  costs:
    monthly_ad_spend: "$X"
    leads_per_month: X
    cost_per_lead: "$X"  # = ad_spend / leads
    lead_to_customer_rate: "X%"
    cac: "$X"  # = cost_per_lead / conversion_rate
    
    cogs_per_customer_monthly: "$X"
    support_cost_per_customer_monthly: "$X"
    total_cost_per_customer: "$X"
  
  health:
    ltv_cac_ratio: "X:1"
    # < 1:1 = Losing money on every customer
    # 1-3:1 = Unprofitable or break-even
    # 3-5:1 = Healthy
    # > 5:1 = Under-investing in growth (or CAC unrealistically low)
    
    payback_months: X
    # < 6 = Excellent
    # 6-12 = Good
    # 12-18 = Acceptable for enterprise
    # > 18 = Dangerous
    
    gross_margin: "X%"
    # SaaS target: 70-85%
    # Services target: 50-70%
    # Ecommerce target: 30-50%
```

### Attribution Models

| Model | How It Works | Best For |
|---|---|---|
| Last touch | 100% credit to final touchpoint | Simple funnels, direct response |
| First touch | 100% credit to first touchpoint | Understanding acquisition channels |
| Linear | Equal credit to all touchpoints | Short sales cycles |
| Time decay | More credit to recent touchpoints | Long sales cycles |
| U-shaped | 40% first, 40% last, 20% middle | B2B with clear entry/close points |
| W-shaped | 30% first, 30% lead creation, 30% close, 10% middle | Complex B2B funnels |
| Data-driven | ML-based multi-touch | High volume (1000+ conversions/month) |

**Rule: Start with last-touch. Add first-touch for comparison. Only invest in multi-touch attribution when you have 500+ monthly conversions across 3+ channels.**

---

## Phase 6: Complete Funnel Templates

### Template 1: B2B SaaS Product-Led Growth

```
Content/SEO → Free Signup → Self-Serve Onboarding → Activation → 
Usage-Based Upgrade Prompt → Paid Conversion → CSM Assignment (high-tier) → 
Expansion/Upsell
```

Key metrics: Sign-up rate, activation rate (Day 1/7/30), free-to-paid conversion, NRR
Key automation: Onboarding emails, usage-based triggers, upgrade prompts
Human touch: CSM for enterprise tier, sales for upgrade conversations

### Template 2: B2B Services / Consulting

```
LinkedIn/Referral/Content → Lead Magnet Download → Email Nurture → 
Discovery Call Request → Discovery Call → Proposal → Negotiation → 
Close → Onboarding Call → Delivery → Review/Testimonial → Referral/Repeat
```

Key metrics: Lead-to-call rate, call-to-proposal rate, proposal-to-close rate, referral rate
Key automation: Email nurture, scheduling, follow-up reminders
Human touch: Discovery call, proposal, delivery, QBRs

### Template 3: Ecommerce / Direct-to-Consumer

```
Paid Social/Search → Product Page → Add to Cart → Checkout → 
Post-Purchase Email → Review Request → Repeat Purchase / Subscription → 
Referral
```

Key metrics: CTR, add-to-cart rate, cart abandonment rate, AOV, repeat purchase rate
Key automation: Cart abandonment emails (3-sequence), post-purchase flow, win-back
Human touch: Customer service (reactive only)

### Template 4: Info Product / Course Launch

```
Content/Social → Webinar Registration → Webinar Attendance → 
Open Cart (limited time) → Purchase → Course Delivery → 
Community Access → Upsell (next course/coaching)
```

Key metrics: Registration rate, show-up rate, webinar-to-purchase rate, completion rate
Key automation: Registration sequence, reminder sequence, cart open/close sequence
Human touch: Live webinar, community engagement, coaching calls

### Template 5: Enterprise / Complex B2B

```
Account Research → Multi-Thread Outreach → Champion Identified → 
Discovery Meeting → Technical Evaluation → Business Case → 
Executive Sponsor Alignment → Procurement → Legal → Close → 
Implementation → Go-Live → QBR → Expansion
```

Key metrics: Meetings booked, pipeline created, win rate, deal velocity, expansion revenue
Key automation: Account research, outreach sequencing, meeting scheduling
Human touch: Nearly everything post-first-meeting

---

## Phase 7: Advanced Funnel Strategies

### Multi-Funnel Architecture

Most mature businesses run 3-5 funnels simultaneously:

```yaml
funnel_portfolio:
  primary:
    name: "Core product funnel"
    purpose: "Main revenue driver"
    optimization_priority: 1
    
  secondary:
    name: "Upsell/expansion funnel"
    purpose: "Grow existing customer revenue"
    optimization_priority: 2
    
  acquisition:
    name: "Content/community funnel"
    purpose: "Build audience for primary funnel"
    optimization_priority: 3
    
  reactivation:
    name: "Win-back funnel"
    purpose: "Recover churned customers"
    optimization_priority: 4
    # Win-back is 5-25x cheaper than new acquisition
    
  referral:
    name: "Customer referral funnel"
    purpose: "Turn customers into acquisition channel"
    optimization_priority: 5
```

### Funnel Stacking (Advanced)

Layer funnels where one's output feeds another's input:

```
Free content → Email list → Free tool/trial → Paid product → 
Premium tier → Done-for-you service → Strategic advisory
```

Each level qualifies buyers for the next. Revenue per customer grows 10-100x from bottom to top.

### Dark Funnel Awareness

40-70% of the buyer journey is invisible ("dark funnel"):
- Slack/Discord conversations you can't track
- Word-of-mouth recommendations
- Internal forwarding of your content
- Podcast mentions
- Social media DMs

**How to account for dark funnel:**
- Add "How did you hear about us?" to every conversion point (open text, not dropdown)
- Track branded search volume over time (proxy for dark funnel growth)
- Ask during discovery calls: "What made you reach out today?"
- Monitor community mentions (Reddit, Twitter, forums)

---

## Phase 8: Funnel Quality Scoring

### 100-Point Funnel Quality Rubric

| Dimension | Weight | 0-2 (Weak) | 3-4 (Adequate) | 5 (Strong) |
|---|---|---|---|---|
| Stage definition | 15 | Vague stages, unclear transitions | Most stages defined | Every stage defined with clear entry/exit criteria |
| Measurement | 20 | No metrics tracked | Some metrics, inconsistent | Every stage measured weekly with benchmarks |
| Conversion rates | 15 | Below benchmarks at most stages | At benchmark for most stages | Above benchmark, improving trend |
| Automation | 10 | All manual | Key sequences automated | Full automation with behavioral triggers |
| Content quality | 10 | Generic, no personalization | Segmented by audience | Personalized, A/B tested, continuously improved |
| Economics | 15 | LTV:CAC < 3:1 or unknown | LTV:CAC 3-5:1 | LTV:CAC > 5:1 with improving trend |
| Optimization cadence | 10 | No regular review | Monthly review | Weekly metrics review + monthly A/B tests |
| Attribution | 5 | No attribution | Single-touch | Multi-touch with channel ROI visibility |

**Scoring: multiply dimension weight × score (0-5). Max = 500. Divide by 5 for 0-100.**

- 0-40: Funnel needs complete redesign
- 41-60: Foundation exists, major gaps to fix
- 61-75: Functional funnel with optimization opportunities
- 76-90: Strong funnel, focus on incremental gains
- 91-100: World-class, focus on scaling

---

## Phase 9: Edge Cases & Difficult Situations

### Funnel Won't Convert (Good Traffic, No Sales)
1. Check traffic quality first — are you attracting your ICP? (Look at bounce rate by source)
2. Survey visitors who don't convert: "What stopped you from [action]?"
3. Record session replays (Hotjar/FullStory) — where do people get stuck?
4. Test radically different offer (not just tweaks — fundamentally different value prop)

### High Acquisition, High Churn
- Acquisition and retention are different problems. Don't optimize one hoping the other improves.
- Common cause: marketing promises don't match product reality
- Fix: align messaging with actual product experience. Under-promise, over-deliver.

### Sales Cycle Too Long
- Map every step from first touch to close. Remove any step that doesn't add value.
- Identify the "stuck" stage — where do deals stall?
- Common fix: bring the demo/proof earlier in the funnel (don't hide value behind calls)

### Can't Afford Paid Acquisition
- Start with organic: SEO + community + partnerships. CAC = time, not money.
- Build referral into product design (viral loops, invite-only, share features)
- Use content to capture high-intent search traffic

### Two-Sided Marketplace
- You need TWO funnels — one for supply, one for demand
- Start with the harder side first (usually supply)
- Use "come for the tool, stay for the network" strategy (single-player mode)

### Seasonal Business
- Plan campaigns 6-8 weeks before peak season
- Build email list during off-season (lead magnets related to peak-season needs)
- Use off-season for product improvement and content creation

---

## Phase 10: Weekly Funnel Review

### 15-Minute Weekly Review Template

```yaml
weekly_review:
  date: "YYYY-MM-DD"
  
  top_of_funnel:
    visitors: X
    vs_last_week: "+/- X%"
    best_channel: "[channel]"
    
  middle_of_funnel:
    new_leads: X
    conversion_rate: "X%"
    active_in_nurture: X
    
  bottom_of_funnel:
    new_customers: X
    revenue: "$X"
    win_rate: "X%"
    
  health:
    biggest_leak: "[stage]"
    leak_severity: "critical | moderate | minor"
    
  action:
    this_week_focus: "[ONE thing to improve]"
    test_running: "[Current A/B test, if any]"
    test_result: "[Last test result]"
```

---

## Natural Language Commands

Use these to interact with the Sales Funnel Engine:

| Command | What It Does |
|---|---|
| "Design a funnel for [business type]" | Creates complete funnel blueprint from template |
| "Audit my funnel" | Runs full diagnostic with recommendations |
| "My [stage] conversion is [X%], help" | Diagnoses specific stage and suggests fixes |
| "Write a nurture sequence for [scenario]" | Generates email sequence with templates |
| "Build a landing page for [offer]" | Creates 7-section landing page copy |
| "Calculate my funnel economics" | Runs unit economics with health assessment |
| "What should I A/B test next?" | Prioritizes tests by expected impact |
| "Compare funnel models for [business]" | Recommends funnel type with reasoning |
| "Set up attribution for [channels]" | Recommends attribution model and setup |
| "Review my funnel metrics" | Generates weekly review template with analysis |
| "Fix my [specific problem]" | Diagnoses and provides action plan |
| "Create a funnel for [specific product at $X]" | End-to-end funnel with economics |
