# Proposal Engine — Win More Deals

Turn discovery calls into winning proposals. Full lifecycle: qualify → scope → price → write → present → close.

## When to Use

- Client says "send me a proposal"
- After a discovery call or meeting
- Responding to an RFP/RFI
- Creating a statement of work (SOW)
- Pricing a new project or retainer

## 1. Pre-Proposal Qualification (Don't Waste Time)

Before writing anything, score the opportunity:

### BANT-Plus Framework

```yaml
qualification:
  budget:
    score: 0-3  # 0=unknown, 1=below range, 2=in range, 3=confirmed+funded
    notes: ""
  authority:
    score: 0-3  # 0=no access, 1=influencer only, 2=decision maker involved, 3=signer in room
    notes: ""
  need:
    score: 0-3  # 0=nice-to-have, 1=want, 2=need, 3=urgent/painful
    notes: ""
  timeline:
    score: 0-3  # 0=someday, 1=this quarter, 2=this month, 3=this week/ASAP
    notes: ""
  competition:
    score: 0-3  # 0=3+ competitors, 1=2 competitors, 2=1 competitor, 3=sole source
    notes: ""
  champion:
    score: 0-3  # 0=no internal advocate, 1=passive, 2=active, 3=actively selling for you
    notes: ""
  total: 0     # Sum of all scores. Max=18
```

**Decision matrix:**
| Score | Action |
|-------|--------|
| 14-18 | Full custom proposal — invest heavily |
| 10-13 | Standard proposal with light customization |
| 6-9 | Template proposal or decline politely |
| 0-5 | Decline — not qualified. Send a polite "not a fit" email |

### Disqualification Signals (Walk Away)
- They want a proposal before a real conversation
- "We're just getting quotes" (you're column fodder)
- No budget conversation allowed
- Decision maker won't attend any meeting
- Timeline is "whenever" with no urgency driver
- They want you to do unpaid strategy work in the proposal

## 2. Discovery Extraction

After a discovery call, extract these into structured notes:

```yaml
discovery:
  client:
    company: ""
    industry: ""
    size: ""  # employees, revenue range
    decision_makers:
      - name: ""
        role: ""
        priorities: []
        communication_style: ""  # analytical, driver, expressive, amiable
  
  situation:
    current_state: ""
    trigger_event: ""  # What happened that made them look for help NOW?
    previous_attempts: []  # What have they tried? Why didn't it work?
    constraints: []  # Budget, timeline, technical, political, regulatory
  
  desired_outcome:
    primary_goal: ""
    success_metrics: []  # How will they measure success? Get NUMBERS.
    dream_state: ""  # "If this goes perfectly, what does it look like in 12 months?"
    fears: []  # What are they afraid will go wrong?
  
  decision_process:
    steps: []  # "What happens between receiving our proposal and starting?"
    stakeholders: []  # Who else weighs in?
    timeline: ""
    budget_range: ""
    competing_options: []
  
  value_drivers:
    revenue_impact: ""  # Will this make them money? How much?
    cost_savings: ""  # Will this save them money? How much?
    risk_reduction: ""  # What risks does this eliminate?
    strategic_value: ""  # How does this advance their bigger goals?
```

**Key rule:** If you can't fill in `success_metrics` with numbers, you don't have enough discovery. Go back and ask.

## 3. Pricing Strategy

### Cost-Plus Pricing (Floor)
```
Hours × Rate + Materials + Buffer = Floor Price
Never price below this. It's your minimum, not your target.
```

### Value-Based Pricing (Target)
```
Client's expected value from the project = X
Your price should be 10-20% of X
If X = $500K revenue increase, price = $50K-$100K
```

### Three-Tier Pricing (Always Present Options)

**Always offer exactly 3 options.** Anchoring psychology makes the middle option feel like the best deal.

```yaml
pricing_tiers:
  good:
    name: ""  # e.g., "Foundation", "Essential", "Starter"
    price: 0
    description: "Solves the core problem"
    includes:
      - "Core deliverable 1"
      - "Core deliverable 2"
    excludes:
      - "Everything in Better/Best"
    timeline: ""
    best_for: "Budget-conscious, clear scope, minimal customization"
    
  better:
    name: ""  # e.g., "Growth", "Professional", "Recommended"  
    price: 0  # 1.5-2.5x of Good
    description: "Core + optimization + support"
    includes:
      - "Everything in Good"
      - "Additional deliverable 1"
      - "Additional deliverable 2"
      - "30 days support"
    timeline: ""
    best_for: "Best value — most clients choose this"
    recommended: true  # Mark this one visually
    
  best:
    name: ""  # e.g., "Enterprise", "Premium", "Partnership"
    price: 0  # 2-4x of Good
    description: "Full transformation + ongoing partnership"
    includes:
      - "Everything in Better"
      - "Premium deliverable 1"
      - "Premium deliverable 2"  
      - "90 days support"
      - "Quarterly reviews"
    timeline: ""
    best_for: "Maximum results, full partnership"
```

**Pricing rules:**
1. Never show hourly rates — price the outcome, not the time
2. Good option should still be profitable (don't create a loss leader)
3. Better option is your target — design it to be obviously the best value
4. Best option is the anchor — makes Better look reasonable
5. Use round numbers ending in 0 or 5 (not $12,347)
6. Annual/retainer pricing: show monthly equivalent AND total (monthly feels smaller)

### Payment Terms

```yaml
payment_terms:
  project:  # For fixed-scope projects
    deposit: "50% on signing"
    milestone_1: "25% on [milestone]"
    final: "25% on delivery + approval"
    late_fee: "1.5%/month after 30 days"
    
  retainer:  # For ongoing work
    billing: "Monthly, billed in advance"
    minimum_term: "3 months"
    unused_hours: "Do not roll over"
    overage_rate: "$X/hour"
    cancellation: "30 days written notice"
    
  saas:  # For software/platform
    billing: "Annual (2 months free) or monthly"
    payment_method: "Credit card on file"
    refund_policy: "30-day money-back guarantee"
```

## 4. Proposal Structure

### The Winning Formula

Every proposal follows this arc: **Mirror → Solve → Prove → Ask**

```
1. Their World (Mirror)     — Show you understand their situation
2. The Gap (Problem)        — Articulate what's broken/missing
3. The Bridge (Solution)    — Your approach to closing the gap
4. The Proof (Evidence)     — Why you specifically can deliver
5. The Path (Plan)          — How you'll get there, step by step
6. The Investment (Pricing) — Three options, value-framed
7. The Ask (Next Steps)     — Exactly what happens when they say yes
```

### Section-by-Section Guide

#### Cover Page
```
[Client Logo] + [Your Logo]
"[Project Name]: [Outcome-Focused Subtitle]"
Prepared for: [Decision Maker Name], [Title]
Prepared by: [Your Name], [Title]
Date: [Date]
Valid until: [Date + 30 days]
Confidential
```

#### 1. Executive Summary (1 page max)

Write this LAST but put it FIRST. The decision maker may only read this page.

Template:
```
[Client] is facing [specific challenge] that is costing approximately 
[quantified impact — dollars, hours, risk]. After [discovery call/meeting], 
we understand that your priority is [primary goal] by [timeline].

We propose [one-sentence solution] that will [primary outcome + metric]. 
Based on [similar project/experience], we expect [specific result] 
within [timeframe].

Three engagement options are detailed below, ranging from $[Good price] 
to $[Best price]. We recommend [Better option name] for the optimal 
balance of speed, thoroughness, and value.

Next step: [specific action] by [date].
```

**Rules:**
- No jargon. Write at 8th grade reading level.
- Include at least one number (cost of inaction, expected ROI, timeline).
- Name the decision maker. This is personal.

#### 2. Understanding Your Situation (Mirror)

Restate what you learned in discovery. Use their exact words where possible.

```
Current state: [What they told you about today]
Trigger: [Why they're looking for help NOW]
Impact: [What this problem is costing them — quantified]
Previous attempts: [What they've tried, why it fell short]
Desired outcome: [What success looks like — in THEIR words]
```

**Why this works:** When prospects see their own words reflected back accurately, trust skyrockets. They think "these people actually listened."

#### 3. Proposed Solution

Structure: What → Why → How

```
What we'll deliver:
- [Deliverable 1]: [One sentence on what it is and why it matters]
- [Deliverable 2]: [One sentence]
- [Deliverable 3]: [One sentence]

Why this approach:
- [Reason 1 — tied to their specific situation]
- [Reason 2 — addresses a concern they raised]
- [Reason 3 — differentiates from alternatives]

What's explicitly NOT included:
- [Out of scope item 1]
- [Out of scope item 2]
(This prevents scope creep and manages expectations)
```

#### 4. Proof & Credibility

Pick 2-3 of these (not all):

```yaml
proof_elements:
  case_study:
    client: "[Similar company]"
    challenge: "[Similar problem]"
    solution: "[What you did]"
    result: "[Quantified outcome]"
    timeline: "[How long it took]"
    
  testimonial:
    quote: ""
    attribution: "[Name, Title, Company]"
    
  credentials:
    - "[Relevant certification]"
    - "[Years of experience in this specific area]"
    - "[Number of similar projects completed]"
    
  methodology:
    name: ""
    description: "Brief explanation of your proven process"
    
  guarantee:
    type: ""  # money-back, performance, satisfaction
    terms: ""
```

**Rule:** Every proof element must be relevant to THIS client's situation. Generic "we're great" claims are worse than no proof at all.

#### 5. Project Plan & Timeline

```yaml
timeline:
  phase_1:
    name: "Discovery & Planning"
    duration: ""
    activities:
      - task: ""
        owner: ""  # "Us" or "Client"
    deliverable: ""
    milestone: ""  # What signals this phase is complete?
    client_requirements: []  # What do you need from them?
    
  phase_2:
    name: "Build / Execute"
    duration: ""
    activities: []
    deliverable: ""
    milestone: ""
    client_requirements: []
    
  phase_3:
    name: "Review & Launch"
    duration: ""
    activities: []
    deliverable: ""
    milestone: ""
    client_requirements: []
    
  ongoing:  # If applicable
    name: "Support & Optimization"
    duration: ""
    activities: []
    review_cadence: ""
```

**Include client responsibilities.** Delays are almost always caused by the client. Document what you need from them and when.

#### 6. Investment (Pricing)

Present the three tiers from Section 3. Frame as investment, not cost.

```
ROI framing:
"The [Better] option is an investment of $X. Based on [discovery data], 
we expect this to [generate/save] $Y within [timeframe], representing 
a [N]x return."

Cost of inaction:
"Every month without a solution, [Client] is [losing $X / spending Y hours / 
risking Z]. Over the proposal validity period alone, that's $[amount]."
```

#### 7. Next Steps & Terms

```
To proceed:
1. Select your preferred option (Good / Better / Best)
2. Sign this proposal (e-signature below or reply "approved")
3. Submit deposit of [amount]
4. Kickoff call scheduled within [X] business days

This proposal is valid until [date — 14-30 days].
After that, pricing and availability may change.
```

### Terms to include:
- Payment schedule
- Revision/change request process (with cost implications)
- Cancellation terms
- IP ownership (who owns the deliverables?)
- Confidentiality
- Limitation of liability

## 5. Proposal Quality Checklist

Score each dimension 0-10. Minimum 70/100 before sending.

| # | Dimension | Check | Score |
|---|-----------|-------|-------|
| 1 | **Relevance** | Does every section reference THEIR specific situation? | /10 |
| 2 | **Clarity** | Could a non-expert understand what you're proposing? | /10 |
| 3 | **Proof** | Are claims backed by data, cases, or testimonials? | /10 |
| 4 | **Value framing** | Is ROI/cost-of-inaction clearly articulated? | /10 |
| 5 | **Specificity** | Concrete deliverables, dates, numbers (not vague promises)? | /10 |
| 6 | **Objection handling** | Does it preemptively address likely concerns? | /10 |
| 7 | **Visual quality** | Clean formatting, easy to scan, professional? | /10 |
| 8 | **Call to action** | Crystal clear next steps with timeline? | /10 |
| 9 | **Risk reduction** | Guarantees, testimonials, or milestones that reduce buyer fear? | /10 |
| 10 | **Competitive edge** | Does it show why YOU vs alternatives? | /10 |

## 6. Proposal Delivery & Follow-Up

### Delivery Rules
1. **Never email a proposal cold.** Present it live (call/meeting) or send with a Loom video walkthrough.
2. Send PDF + a one-paragraph email. Don't bury it in a wall of text.
3. Subject line: "[Client Name] × [Your Company] — Proposal for [Outcome]"

### Follow-Up Cadence

```yaml
follow_up:
  day_0: "Send proposal + personal video walkthrough (2-3 min)"
  day_2: "Quick check-in: 'Did you have a chance to review? Any questions?'"
  day_5: "Value-add: Share a relevant article, case study, or insight"
  day_8: "Direct ask: 'Are you leaning toward an option? Happy to jump on a quick call'"
  day_14: "Scarcity: 'Proposal valid until [date]. Want to lock in the timeline?'"
  day_21: "Last touch: 'Wanted to check in one final time. If timing isn't right, no worries — happy to revisit when it makes sense.'"
  day_30: "Close the loop: Move to 'closed-lost' if no response. Send graceful close email."
```

### Objection Response Templates

**"It's too expensive"**
→ Reframe to value: "I understand. Let me ask — if this [achieves outcome], what would that be worth to your business over 12 months? The investment is [X]% of that value."
→ Offer the Good tier: "We also have the [Good option] at $[X] that covers the core need."

**"We need to think about it"**
→ Diagnose: "Absolutely. To help you evaluate — is there a specific concern I can address, or information you need that would help the decision?"

**"We're looking at other options"**
→ Differentiate: "Smart to compare. What criteria are most important in your decision? I want to make sure our proposal addresses what matters most."

**"The timeline doesn't work"**
→ Adapt: "When would be ideal? Let me see if we can restructure phases to align with your timeline."

**"We need to get approval from [someone]"**
→ Enable: "Happy to join a brief call with [person] to answer any questions directly. Would that help speed things up?"

## 7. Proposal Templates by Type

### Consulting/Advisory Proposal
Focus on: situation analysis, methodology, expected outcomes, engagement structure
Tone: authoritative, advisory
Pricing: project fee or monthly retainer
Key proof: similar client results, methodology name

### Software/Technical Proposal
Focus on: technical approach, architecture overview, integration plan, support
Tone: clear, technical but accessible
Pricing: project phases + ongoing license/maintenance
Key proof: technical credentials, uptime stats, security compliance

### Creative/Agency Proposal
Focus on: creative vision, mood boards/references, deliverable list, revision process
Tone: confident, visually-driven
Pricing: project fee with defined revision rounds
Key proof: portfolio samples, brand work examples

### RFP Response
Focus on: point-by-point compliance, differentiators, team bios, references
Tone: formal, thorough
Pricing: as specified in RFP
Key proof: relevant contract experience, certifications, references
**Tip:** Answer every question in the RFP even if irrelevant. Non-responsive = disqualified.

## 8. Common Mistakes (Avoid These)

1. **Writing about yourself first.** Lead with THEIR problem, not your company bio.
2. **One option only.** Always offer 3 tiers. One option = take it or leave it.
3. **Vague deliverables.** "Marketing strategy" means nothing. "30-page go-to-market playbook covering channels, budget allocation, and 90-day campaign calendar" means everything.
4. **No deadline.** Open-ended proposals die. Always include expiration date.
5. **Sending without presenting.** Proposals sent blind close at 10-20%. Presented live: 40-60%.
6. **No follow-up system.** 80% of deals close after the 5th follow-up. Most people stop at 1.
7. **Burying the price.** Don't make them hunt for it. Investment section should be easy to find.
8. **Ignoring the real decision maker.** If you're writing for the wrong person, you've already lost.
9. **Over-designing, under-writing.** Beautiful PDF with weak content loses to ugly doc with killer strategy.
10. **Not quantifying value.** If you can't show ROI, the price is always "too much."

## Quick Start

**"Create a proposal for [client]"** → I'll walk you through discovery extraction, qualification scoring, pricing strategy, and generate the full proposal with follow-up plan.

**"Score this opportunity: [details]"** → BANT-Plus qualification score with go/no-go recommendation.

**"Help me price [project]"** → Three-tier pricing with value framing and payment terms.

**"Review my proposal: [paste/file]"** → Quality checklist score with specific improvement suggestions.

---

*Built by AfrexAI — AI-powered business tools that actually work.*
