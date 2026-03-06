---
name: Partnership & Channel Revenue Engine
description: Turn partnerships from handshake deals into a systematic revenue
  machine. This is the complete playbook for finding, qualifying, structuring,
  launching, and scaling partner-driven growth — whether ...
---

# Partnership & Channel Revenue Engine

Turn partnerships from handshake deals into a systematic revenue machine. This is the complete playbook for finding, qualifying, structuring, launching, and scaling partner-driven growth — whether you're building integration partnerships, reseller channels, affiliate programs, or strategic alliances.

---

## Phase 1 — Partnership Strategy & ICP

Before reaching out to anyone, define what a great partner looks like.

### Partnership Type Decision Matrix

| Type | Best When | Revenue Model | Complexity | Time to Revenue |
|------|-----------|---------------|------------|-----------------|
| **Integration/Tech** | Products complement each other | Revenue share 10-30% | High | 3-6 months |
| **Reseller/VAR** | Partner has your buyer's trust | Wholesale discount 20-40% | Medium | 1-3 months |
| **Referral** | Low-commitment entry point | Per-lead fee or % of first deal | Low | 2-4 weeks |
| **Affiliate** | Large audience, digital product | 15-40% commission | Low | 1-2 weeks |
| **Co-Sell** | Enterprise deals, both logos help | Split varies by contribution | High | 3-6 months |
| **White-Label/OEM** | Partner wants your tech under their brand | License + per-seat/usage fee | Very High | 6-12 months |
| **Co-Marketing** | Shared audience, content leverage | No direct rev (pipeline gen) | Low | 2-4 weeks |
| **Strategic/JV** | Market entry, new geography | Equity or profit share | Very High | 6-18 months |

**Selection rule:** Start with Referral or Affiliate (fast wins, prove concept), then graduate to Integration or Reseller (real revenue), then Strategic (market expansion).

### Ideal Partner Profile (IPP)

```yaml
ideal_partner_profile:
  company:
    size: "50-500 employees"  # or revenue range
    stage: "Series B+ or profitable"
    geography: "US, UK, EU"
    industries: ["SaaS", "Professional Services"]
  
  audience_overlap:
    serves_our_icp: true  # Their customers = our target buyers
    complementary_not_competitive: true
    audience_size_minimum: 5000  # customers or active users
  
  capability:
    has_sales_team: true  # for reseller; optional for referral
    technical_integration_capacity: "medium"  # for tech partnerships
    marketing_team_exists: true  # for co-marketing
    partner_program_experience: "any"  # bonus if they've partnered before
  
  alignment:
    brand_quality: "matches or exceeds ours"
    values_compatible: true
    growth_trajectory: "stable or growing"
    executive_sponsorship_likely: true
  
  anti_signals:  # Disqualify if any are true
    - "Direct competitor or building competing feature"
    - "Declining revenue / layoffs > 20%"
    - "Known for partner-unfriendly behavior"
    - "Regulatory risk that could impact us"
    - "Single decision-maker who's leaving"
```

### Partner Scoring (0-100)

| Dimension | Weight | 1-5 Scale Criteria |
|-----------|--------|---------------------|
| **Audience Fit** | 25% | 1=no overlap, 3=partial overlap, 5=exact ICP match |
| **Revenue Potential** | 25% | 1=<$5K/yr, 3=$25-50K/yr, 5=$100K+/yr |
| **Brand Alignment** | 15% | 1=risky brand, 3=neutral, 5=prestigious/trusted |
| **Execution Capability** | 20% | 1=no team/resources, 3=some capacity, 5=dedicated partner team |
| **Strategic Value** | 15% | 1=transactional only, 3=market insight, 5=opens new market segment |

**Score = (Audience×5 + Revenue×5 + Brand×3 + Execution×4 + Strategic×3) = max 100**

- **80-100:** Tier 1 — white-glove onboarding, dedicated partner manager
- **60-79:** Tier 2 — standard enablement, quarterly reviews
- **40-59:** Tier 3 — self-serve resources, annual check-in
- **<40:** Pass — politely decline or defer

---

## Phase 2 — Partner Discovery & Research

### 8 Discovery Channels (ranked by quality)

1. **Existing customer referrals** — "Which tools do you use alongside ours?" — highest-quality signal
2. **Integration marketplace analysis** — Browse Zapier, HubSpot, Salesforce AppExchange for adjacent tools
3. **Competitor's partner pages** — Who partners with competitors? They understand the value prop
4. **Industry conference sponsor lists** — Companies investing in visibility = partnership-ready
5. **LinkedIn Sales Navigator** — Search by company, filter by "partnerships" or "business development" in title
6. **G2/Capterra category adjacency** — Same category buyers also buy from these vendors
7. **VC portfolio overlap** — Same investors often encourage portfolio partnerships
8. **Inbound requests** — Track who reaches out; signal of natural demand

### Research Brief Template

```yaml
partner_research:
  company: "Acme Corp"
  website: "https://acme.com"
  what_they_do: "Project management for construction firms"
  
  audience:
    customer_count: "~2,000 companies"
    target_segment: "Mid-market construction ($10M-$200M revenue)"
    geographic_focus: "US, expanding to UK"
    overlap_with_our_icp: "HIGH — 60% of their customers match our target"
  
  product:
    core_product: "Cloud PM platform"
    pricing: "$99-499/mo per company"
    integrations: ["QuickBooks", "Procore", "Slack"]
    api_available: true
    gaps_we_fill: "No AI automation, no document analysis"
  
  business:
    funding: "Series B, $40M raised"
    revenue_estimate: "$15M ARR"
    growth: "Growing ~40% YoY"
    team_size: 180
    partner_program_exists: false  # Opportunity to be first!
  
  key_people:
    partnership_lead: "Jane Smith, VP Business Development"
    product_lead: "Mike Johnson, CPO"
    ceo: "Sarah Williams"
    linkedin_urls:
      - "https://linkedin.com/in/janesmith"
      - "https://linkedin.com/in/mikejohnson"
  
  competitive_intel:
    partners_with: ["QuickBooks", "DocuSign"]
    missing_partners: "No AI/automation partner"
    competitor_partnerships: "Rival Corp partners with BuildBot AI"
  
  partnership_angle: "Integration: our AI reads their project docs, automates compliance checks"
  estimated_annual_value: "$75K (rev share on 200 conversions)"
  risk_factors: ["May build in-house", "CEO reportedly difficult"]
  
  outreach_strategy:
    warm_intro_available: "Yes — mutual investor, also customer X knows their VP"
    first_touch: "Warm intro via investor → meeting with VP BD"
    hook: "Their competitor already has AI partner; they're falling behind"
```

---

## Phase 3 — Outreach & First Meeting

### Outreach Sequence (5 touches over 3 weeks)

**Touch 1 — Day 1: Warm Intro or Cold Email**

Subject: `{Mutual connection} suggested I reach out — {their company} + {your company}`

```
Hi {Name},

{Mutual connection} mentioned you're exploring ways to help {their customers} 
with {problem area}. We've been building {brief description} and {X} of our 
customers already use {their product} alongside ours.

Quick thought: a {partnership type} between us could help your customers 
{specific outcome — e.g., "cut compliance review time by 60%"} without you 
building anything new.

Worth a 20-minute call this week?

{Signature}
```

**Touch 2 — Day 4: Value-Add Follow-up**

```
Hi {Name},

Following up — I put together a quick analysis of how {their product} users 
could benefit from {your capability}. [Attach 1-pager or link]

The overlap between our customer bases is stronger than I expected — 
{specific data point}.

Happy to walk through it whenever works.
```

**Touch 3 — Day 8: Social Proof**

```
Quick update — {similar company} just launched a similar partnership with us 
and saw {metric — e.g., "23% increase in customer retention"} in the first 
quarter. 

Their {role} said: "{brief quote}."

Think this could work for {their company} too. Free Thursday?
```

**Touch 4 — Day 14: Light Nudge**

```
Hi {Name} — wanted to bump this up. We're formalizing our partner program 
this quarter and have {X} spots for launch partners who get priority 
integration support and co-marketing.

Should I include {their company}?
```

**Touch 5 — Day 21: Break-up**

```
Hi {Name} — I'll assume the timing isn't right. Totally understand.

If partnerships ever become a priority, we'd love to explore this. 
I'll check back in {timeframe — e.g., "Q3"}.

In the meantime, {useful resource — guide, report, or intro to someone helpful}.
```

### First Meeting Agenda (30 min)

```
0-5 min:  Rapport + confirm agenda
5-10 min: THEM — their business, customers, growth priorities
10-15 min: US — brief overview, why we think there's a fit
15-20 min: THE OPPORTUNITY — specific partnership model, mutual benefits
20-25 min: LOGISTICS — next steps, who else should be involved
25-30 min: COMMITMENT — agree on timeline for follow-up/decision
```

**Questions to ask:**
1. "What's your biggest growth priority this quarter?"
2. "How do your customers currently solve {problem we address}?"
3. "Have you done partnerships before? What worked/didn't?"
4. "Who internally would need to sign off on a partnership?"
5. "What would make this a no-brainer for you?"

**Red flags in first meeting:**
- They can't articulate who their customer is → unclear audience
- "We'll need to run this by legal" as first response → bureaucracy-heavy
- No questions about your product → not genuinely interested
- Immediately jump to "what's your commission?" → transactional mindset only

---

## Phase 4 — Deal Structure & Commercials

### Revenue Share Models

| Model | Use When | Typical Range | Tracking Method |
|-------|----------|---------------|-----------------|
| **% of revenue** | Ongoing SaaS referrals | 15-30% of MRR for 12-24 months | UTM + referral code |
| **Flat fee per lead** | High volume, lower quality | $50-500 per qualified lead | CRM attribution |
| **Flat fee per deal** | Clear conversion events | $500-5,000 per closed deal | Promo code or UTM |
| **Tiered commission** | Incentivize volume | 15% for 1-10, 20% for 11-25, 25% for 26+ | Dashboard tracking |
| **Revenue share (mutual)** | Integration partnership | 10-20% both directions | API usage + attribution |
| **License fee** | White-label/OEM | $X per seat per month | Usage metering |
| **Hybrid** | Complex deals | Base fee + performance bonus | Combined tracking |

### Deal Economics Calculator

```
Partner Deal Economics:
  Expected referrals per month: [X]
  Average deal size (ACV): $[Y]
  Close rate on partner leads: [Z]%
  Commission rate: [W]%
  
  Monthly partner revenue: X × Y × (Z/100) = $[A]
  Monthly commission paid: A × (W/100) = $[B]
  Net revenue after commission: A - B = $[C]
  
  Partner CAC: (onboarding cost + enablement time) / expected deals in Year 1
  Partner LTV: average monthly net revenue × average partner lifespan (months)
  
  HEALTHY IF:
  - Partner LTV / Partner CAC > 3:1
  - Net margin on partner deals > 40%
  - Partner-sourced CAC < direct CAC
  - Commission < customer LTV × 25%
```

### Partnership Agreement Checklist

```
MUST INCLUDE:
□ Partnership type and scope (what's included, what's excluded)
□ Revenue share / commission structure with payment terms
□ Attribution method and tracking technology
□ Minimum commitments (if any — e.g., X referrals/quarter to maintain tier)
□ Exclusivity terms (usually NON-exclusive; exclusive = premium tier only)
□ Term length and renewal (12 months auto-renew is standard)
□ Termination clause (30-60 days notice, what happens to in-flight deals)
□ IP and brand usage rights (logo, name, marketing materials)
□ Data sharing and privacy (what data is exchanged, GDPR/CCPA compliance)
□ SLAs for integration support or lead response time
□ Dispute resolution (mediation before litigation)
□ Non-compete / non-solicit (narrow and reasonable)
□ Confidentiality / NDA
□ Insurance requirements (if applicable)

NICE TO INCLUDE:
□ Joint marketing commitments (X co-branded pieces per quarter)
□ MDF (Market Development Funds) availability
□ Partner advisory board participation
□ Early access to product roadmap
□ Escalation contacts for both sides
```

---

## Phase 5 — Partner Enablement & Launch

### Partner Onboarding Checklist (First 14 Days)

```
DAY 1-3: SETUP
□ Signed agreement received and countersigned
□ Partner portal access provisioned
□ Referral/tracking link generated and tested
□ Partner contact added to CRM with "Partner" tag
□ Welcome email sent with all resources
□ Kick-off call scheduled

DAY 4-7: ENABLEMENT
□ Product deep-dive session (60 min — record it)
□ Sales enablement materials shared:
  - One-pager (partner version)
  - Battle card vs. competitors
  - Demo script / walkthrough
  - FAQ document (20+ common questions)
  - Pricing guide with partner-specific terms
□ Co-branded landing page live (if applicable)
□ Partner's team trained on positioning and qualification

DAY 8-14: ACTIVATION
□ First joint pipeline review
□ First co-marketing piece planned (webinar, blog, case study)
□ Partner makes first referral or introduction
□ Feedback collected on enablement materials
□ 14-day check-in call completed
□ Partner added to monthly partner newsletter
```

### Partner Enablement Kit

| Asset | Purpose | Update Frequency |
|-------|---------|------------------|
| **Partner One-Pager** | Quick overview for partner's sales team | Quarterly |
| **Battle Card** | Positioning vs. competitors | Monthly |
| **Demo Script** | Step-by-step demo walkthrough | Per release |
| **FAQ Document** | 20+ common objections + answers | Monthly |
| **Case Studies** | Social proof by industry/use case | As available |
| **Email Templates** | Pre-written intro emails partners can use | Quarterly |
| **Co-branded Deck** | Joint presentation for prospects | Per partner |
| **Integration Guide** | Technical setup documentation | Per release |
| **ROI Calculator** | Shareable tool for partner's prospects | Quarterly |
| **Commission Dashboard** | Real-time earnings tracking | Always live |

### Launch Playbook

```
WEEK 1: Soft Launch
- Partner's internal team briefed
- Test referral flow end-to-end
- First 3-5 warm intros from partner's network

WEEK 2-3: Controlled Launch
- Co-branded announcement blog post
- Email to partner's customer base (segmented)
- Social media cross-promotion
- Webinar or live demo (target: 50+ registrants)

WEEK 4+: Full Launch
- Integration listed on both marketplaces
- Paid co-marketing (if budget allows)
- Case study from first joint customer
- Press release (if strategic partnership)
```

---

## Phase 6 — Partner Management & Growth

### Partner Health Score (0-100, monthly)

| Metric | Weight | Scoring |
|--------|--------|---------|
| **Referral Volume** | 25% | 1=0 refs, 3=meets target, 5=exceeds 2x |
| **Lead Quality** | 20% | 1=<10% close rate, 3=matches avg, 5=>2x avg close rate |
| **Engagement** | 20% | 1=unresponsive, 3=attends QBRs, 5=proactive co-marketing |
| **Revenue Generated** | 25% | 1=<$1K/mo, 3=meets forecast, 5=exceeds 2x |
| **Relationship Strength** | 10% | 1=single contact, 3=multiple stakeholders, 5=executive sponsor |

**Score = weighted sum × 4 = max 100**

- **80-100:** Champion — invest more, expand scope
- **60-79:** Healthy — maintain cadence, look for growth
- **40-59:** At risk — diagnose issues, intervention plan
- **<40:** Declining — honest conversation, consider winding down

### Quarterly Business Review (QBR) Template

```
## Partner QBR: {Partner Name} — {Quarter}

### Performance Summary
- Referrals sent: {X} (target: {Y})
- Deals closed: {X} (target: {Y})
- Revenue generated: ${X} (target: ${Y})
- Commission paid: ${X}
- Partner health score: {X}/100

### What Worked
- {Top performing initiative}
- {Successful co-marketing effort}

### What Didn't
- {Underperforming area}
- {Blocked initiative and why}

### Next Quarter Plan
- Revenue target: ${X} (+{Y}% growth)
- Key initiatives:
  1. {Initiative — owner — deadline}
  2. {Initiative — owner — deadline}
  3. {Initiative — owner — deadline}
- Co-marketing commitment: {X pieces}
- Enablement needs: {Training, new materials, etc.}

### Open Issues
- {Issue — owner — target resolution date}

### Executive Alignment
- {Any strategic changes to discuss}
```

### Partner Lifecycle Stages

```
PROSPECT → EVALUATING → ONBOARDING → RAMPING → PRODUCING → SCALING → STRATEGIC
   ↓          ↓            ↓            ↓           ↓          ↓          ↓
 Research   Pitch &     14-day       First 90    Steady     Expand     Deep
 & score    negotiate   checklist    days ramp   state      scope      collab
```

**Stage-specific actions:**

| Stage | Key Action | Success Metric | Typical Duration |
|-------|-----------|----------------|------------------|
| Prospect | Research + score | Score >60 | 1-2 weeks |
| Evaluating | Pitch + negotiate terms | Signed agreement | 2-4 weeks |
| Onboarding | Enablement + training | Completion of 14-day checklist | 2 weeks |
| Ramping | First referrals + support | First closed deal | 30-90 days |
| Producing | Consistent referral flow | Meets monthly targets | Ongoing |
| Scaling | Expand scope, co-sell | Revenue growing QoQ | 6+ months |
| Strategic | JVs, co-build, exclusivity | Board-level relationship | 12+ months |

---

## Phase 7 — Channel Program Design

### Program Tiers

```yaml
partner_program:
  tiers:
    - name: "Referral Partner"
      requirements:
        annual_revenue: "$0+"
        certifications: 0
        quarterly_reviews: false
      benefits:
        commission: "15%"
        support: "Email only"
        marketing: "Listed in partner directory"
        training: "Self-serve portal"
        
    - name: "Silver Partner"
      requirements:
        annual_revenue: "$25K+"
        certifications: 1
        quarterly_reviews: true
      benefits:
        commission: "20%"
        support: "Dedicated Slack channel"
        marketing: "Co-branded landing page + 1 webinar/quarter"
        training: "Live training sessions"
        mdf: "$2,500/quarter"
        
    - name: "Gold Partner"
      requirements:
        annual_revenue: "$100K+"
        certifications: 2
        quarterly_reviews: true
      benefits:
        commission: "25%"
        support: "Dedicated partner manager"
        marketing: "Full co-marketing program"
        training: "Custom enablement"
        mdf: "$10,000/quarter"
        early_access: true
        advisory_board: true
        
    - name: "Platinum Partner"
      requirements:
        annual_revenue: "$250K+"
        certifications: 3
        quarterly_reviews: true
        executive_sponsor: true
      benefits:
        commission: "30%"
        support: "Named SE + partner manager"
        marketing: "Joint press releases + events"
        training: "On-site enablement"
        mdf: "$25,000/quarter"
        product_input: "Roadmap influence"
        exclusivity_option: true
```

### Partner Certification Program

```
LEVEL 1 — Foundations (self-paced, 2 hours)
- Product overview and positioning
- Target customer profile
- Basic demo skills
- Quiz: 80% to pass

LEVEL 2 — Practitioner (instructor-led, half day)
- Advanced product deep-dive
- Objection handling workshop
- Live demo practice with feedback
- Role-play exercise: 3 scenarios

LEVEL 3 — Expert (hands-on, full day)
- Technical integration workshop
- Solution architecture for top use cases
- Co-selling methodology
- Build a custom demo
- Present to panel for certification
```

---

## Phase 8 — Metrics & Reporting

### Partner Program Dashboard

```yaml
weekly_metrics:
  pipeline:
    new_partner_leads: {X}
    partners_in_evaluation: {X}
    partners_onboarding: {X}
    active_partners: {X}
    churned_partners_this_month: {X}
  
  performance:
    total_referrals_this_week: {X}
    qualified_referrals: {X}
    deals_closed_via_partners: {X}
    partner_sourced_revenue: "${X}"
    commission_paid: "${X}"
    net_partner_revenue: "${X}"
  
  efficiency:
    partner_sourced_vs_direct_cac: "{X}% lower"
    partner_deal_close_rate: "{X}%"
    average_partner_deal_size: "${X}"
    time_to_first_referral: "{X} days"
    partner_activation_rate: "{X}%"  # % of signed partners who refer in 90 days
  
  health:
    avg_partner_health_score: "{X}/100"
    partners_at_risk: {X}
    nps_from_partners: {X}

monthly_review:
  - Top 5 partners by revenue
  - Bottom 5 active partners (intervention needed?)
  - New partners added vs churned
  - Partner-sourced % of total revenue (target: 20-30%)
  - Co-marketing ROI
  - Enablement material usage stats
```

### Key Benchmarks

| Metric | Poor | Good | Great |
|--------|------|------|-------|
| Partner activation rate (first referral in 90 days) | <30% | 50-70% | >70% |
| Partner-sourced deal close rate | <10% | 20-30% | >30% |
| Partner-sourced CAC vs direct | Same or higher | 20-40% lower | >40% lower |
| Partner-sourced revenue % | <10% | 15-25% | >25% |
| Average time to first referral | >90 days | 30-60 days | <30 days |
| Partner NPS | <30 | 40-60 | >60 |
| Commission as % of partner revenue | >35% | 20-30% | <20% |
| Partner churn rate (annual) | >30% | 15-25% | <15% |

---

## Phase 9 — Advanced Strategies

### Co-Sell Motion (Enterprise Deals)

```
1. IDENTIFY: Partner flags opportunity where both products needed
2. QUALIFY: Joint discovery call — both teams present
3. PLAN: Mutual Action Plan with shared milestones
4. DEMO: Integrated demo showing combined value
5. PROPOSE: Joint proposal — single contract or coordinated pricing
6. NEGOTIATE: Lead partner runs point; support partner advises
7. CLOSE: Coordinated signing and onboarding
8. SUCCEED: Joint customer success plan
```

**Co-sell rules:**
- Lead partner = whoever has the stronger existing relationship
- Revenue split agreed BEFORE first joint meeting
- One partner manages the deal; other provides air cover
- Weekly joint stand-ups during active deals
- Shared CRM view or weekly pipeline email

### Affiliate Program at Scale

```yaml
affiliate_program:
  tracking: "First-click attribution, 90-day cookie"
  commission_structure:
    one_time: "30% of first payment"
    recurring: "20% for 12 months"
    
  tiers:
    starter: { monthly_sales: "0-5", commission: "20%" }
    pro: { monthly_sales: "6-20", commission: "25%" }
    elite: { monthly_sales: "21+", commission: "30%", bonus: "$500/mo" }
  
  assets_provided:
    - Banner ads (5 sizes)
    - Email swipe copy (5 variations)
    - Social media posts (10 templates)
    - Landing page (co-branded, personalized link)
    - Video testimonials for embedding
  
  rules:
    - No brand bidding on paid search
    - No coupon/deal sites without approval
    - Honest representation required
    - FTC disclosure mandatory
    
  payment: "Monthly, NET-30, minimum $100 payout"
  platform: "PartnerStack / FirstPromoter / custom"
```

### Partner Ecosystem Flywheel

```
More Partners → More Integrations → Better Product → More Customers
     ↑                                                        ↓
More Revenue ← Higher Retention ← More Value ← More Use Cases
```

**Flywheel accelerators:**
1. **Partner marketplace** — customers discover partners naturally
2. **Integration templates** — reduce time-to-integrate from months to days
3. **Partner API** — self-serve technical onboarding
4. **Success stories** — each win attracts 2-3 similar partners
5. **Partner events** — annual summit builds community

---

## Phase 10 — Edge Cases & Difficult Situations

### When a Partner Isn't Performing

```
Step 1: Data review — is it volume, quality, or conversion?
Step 2: Honest conversation — "We committed to X referrals/quarter. 
        We're at Y. What's blocking you?"
Step 3: Enablement check — do they have what they need? Re-train if needed
Step 4: 30-day improvement plan with specific targets
Step 5: If no improvement → move to self-serve tier or mutual wind-down
```

### When Partners Compete with Each Other

- Segment by geography, vertical, or deal size
- "First to register the deal" wins (deal registration system)
- Transparent rules, consistently enforced
- If conflict: mediating conversation, not email threads

### When a Partner Wants Exclusivity

- Only grant for specific geography or vertical, never global
- Require minimum revenue commitment (2x what they'd get non-exclusive)
- Time-bound (12 months, reviewed annually)
- Performance clause: exclusivity revoked if targets missed by >30%

### When You're the Smaller Partner

- Lead with specific value you bring (niche expertise, technical capability)
- Propose a pilot (3 months, limited scope, clear success metrics)
- Make it zero-effort for them (you build the integration, you create the materials)
- Find an internal champion who benefits personally (quota relief, innovation credit)

### International Partnerships

- Respect local business customs (relationship speed varies by culture)
- Contracts: specify governing law and currency
- Consider local partner for market entry vs. direct
- Tax implications: withholding on cross-border commissions
- Language: translate key enablement materials

### When to Kill a Partnership

Red flags that mean it's over:
- Partner actively sends leads to competitor
- Reputational damage to your brand
- Legal/compliance violations
- Negative ROI after 6+ months of effort
- Relationship has become adversarial

**Exit gracefully:** 30-60 day notice, honor existing pipeline, write a professional transition plan, leave the door open for the future.

---

## Natural Language Commands

```
"Research [company] as potential partner"
→ Builds full research brief from web data

"Score [company] as a partner"
→ Runs 5-dimension scoring, returns tier recommendation

"Draft outreach to [name] at [company] about [partnership type]"
→ Generates personalized 5-touch sequence

"Create partner agreement outline for [company] — [type] partnership"
→ Generates deal structure with commercial terms

"Build enablement kit for [partner name]"
→ Creates one-pager, FAQ, battle card, email templates

"Run QBR prep for [partner name]"
→ Pulls metrics, generates QBR document

"Partner health check — all active partners"
→ Scores all partners, flags at-risk, suggests actions

"Design partner program tiers"
→ Generates tier structure with requirements and benefits

"Calculate deal economics: [referrals/mo] referrals at [ACV] ACV, [rate]% commission"
→ Returns full economics including Partner LTV/CAC

"Compare partnership types for [goal]"
→ Decision matrix based on your specific situation

"Plan co-marketing campaign with [partner]"
→ Generates campaign plan with timeline and assets

"Draft partner newsletter for this month"
→ Compiles updates, wins, new resources for partner base
```

---

## ⚡ Level Up

This skill gives you the complete partnership playbook. For industry-specific partner strategies, deal structures, and vertical-specific outreach sequences:

**[AfrexAI Context Packs — $47](https://afrexai-cto.github.io/context-packs/)**

- **SaaS Pack** — SaaS-specific channel partner strategies and integration playbooks
- **Professional Services Pack** — Referral network and subcontractor partnership frameworks
- **Manufacturing Pack** — Distributor and supply chain partner methodologies
- **Construction Pack** — Subcontractor and vendor partnership systems

## 🔗 More Free Skills by AfrexAI

- `afrexai-lead-hunter` — Automated lead generation & enrichment
- `afrexai-sales-playbook` — Complete B2B sales system
- `afrexai-negotiation-mastery` — Deal negotiation frameworks
- `afrexai-proposal-engine` — Winning proposal methodology
- `afrexai-competitive-intel` — Competitive intelligence system

**[Browse all AfrexAI skills →](https://afrexai-cto.github.io/context-packs/)**
