---
name: afrexai-okr-engine
description: >
  Complete OKR & Strategy Execution system — from company vision to weekly execution.
  Covers goal hierarchy, OKR writing methodology, scoring rubrics, alignment cascading,
  KPI dashboards, review cadences, team accountability, and quarterly planning rituals.
  Use when setting goals, running planning cycles, tracking OKRs, building KPI dashboards,
  running retrospectives, or aligning team work to strategy.
  Trigger on: "OKR", "objectives", "key results", "goal setting", "quarterly planning",
  "KPIs", "strategy execution", "annual planning", "team goals", "alignment", "review cadence",
  "what should we focus on", "prioritize", "goal tracking", "north star metric".
---

# OKR & Strategy Execution Engine

> Set bold objectives. Measure what matters. Execute with discipline. Review ruthlessly.

---

## Quick Health Check (/8)

Before building anything, score your current goal system:

| Signal | ✅ Healthy | ❌ Broken |
|--------|-----------|-----------|
| Written goals exist | Documented, shared | In someone's head |
| Goals have metrics | Every goal is measurable | "Improve customer experience" |
| Cascade is clear | Team goals → company goals | Disconnected silos |
| Review cadence exists | Weekly check-ins happen | Goals set then forgotten |
| Scoring is honest | Red/yellow/green with data | Everything is "on track" |
| Goals are ambitious | 70% hit rate = healthy | 100% hit rate = sandbagging |
| Resource allocation matches | Top goals get most time | Urgent eats important |
| Retros happen | Quarterly learning cycles | Same mistakes repeat |

**Score: /8** → ≤3 = rebuild from scratch, 4-5 = fix gaps, 6+ = optimize

---

## Phase 1: Strategic Foundation

### Vision Statement (Revisit Annually)

Your vision is a direction, not a destination. 1-2 sentences max.

**Formula:** `We exist to [verb] [who] by [how], creating a world where [outcome].`

**Quality test:**
- [ ] Inspiring (makes people want to show up)
- [ ] Directional (eliminates options that don't fit)
- [ ] Timeless (wouldn't change if product/market shifts)
- [ ] Memorable (can recite without reading)

### Mission Statement

Mission = how you pursue the vision right now. Changes every 2-5 years.

**Formula:** `We [what we do] for [who] by [unique approach], delivering [measurable impact].`

### North Star Metric

One metric that captures the core value you deliver. Everything else is a supporting metric.

**Selection criteria:**
1. Reflects customer value delivered (not vanity)
2. Leading indicator of revenue (not lagging)
3. Measurable weekly (not annually)
4. Every team can influence it (not one department)

**By business type:**

| Business Type | North Star Metric | Why |
|---------------|------------------|-----|
| SaaS | Weekly Active Users or NRR | Usage = value = retention |
| Marketplace | Transactions per week | Liquidity = value for both sides |
| E-commerce | Revenue per visitor | Combines traffic quality + conversion + AOV |
| Services | Monthly recurring revenue | Predictable value delivery |
| Media/Content | Engaged time per user | Attention = ad/subscription value |
| B2B Enterprise | Expansion revenue % | Proves ongoing value post-sale |

### Strategic Pillars (3-5 Max)

Pillars are the 3-5 themes that your goals cluster around. They persist for 1-3 years.

```yaml
strategic_pillars:
  - name: "Product-Led Growth"
    description: "Make the product the primary acquisition and expansion engine"
    north_star_contribution: "Drives WAU through self-serve onboarding"
    
  - name: "Enterprise Readiness"
    description: "Build features and processes that enterprise buyers require"
    north_star_contribution: "Drives NRR through larger deal sizes"
    
  - name: "Operational Excellence"
    description: "Reduce cost-to-serve and increase team velocity"
    north_star_contribution: "Enables more output per headcount"
```

**Rule: If a goal doesn't map to a pillar, it doesn't get resourced.**

---

## Phase 2: Annual Planning

### Annual Goal Template

Set 3-5 annual goals. Each must connect to a strategic pillar.

```yaml
annual_goal:
  id: "AG-2026-01"
  statement: "Reach $1M ARR through product-led acquisition"
  pillar: "Product-Led Growth"
  why_now: "Market window closing, competitors raising Series A"
  success_metric: "ARR ≥ $1M by Dec 31"
  current_baseline: "$120K ARR"
  milestones:
    q1: "$250K ARR"
    q2: "$450K ARR"
    q3: "$700K ARR"
    q4: "$1M ARR"
  dependencies:
    - "Hire 2 engineers by Feb"
    - "Launch self-serve by March"
  risk_factors:
    - "Churn > 5% monthly kills growth math"
    - "Engineering capacity if hiring delayed"
  owner: "CEO + CRO"
```

### Annual Planning Ritual (1-2 Days)

**Pre-work (1 week before):**
- Each leader submits: top 3 wins, top 3 misses, top 3 opportunities for next year
- Finance provides: revenue forecast, budget constraints, headcount plan
- Product provides: competitive landscape, customer feedback themes

**Day 1: Review & Align**
1. Score last year's goals honestly (30 min)
2. External landscape review — market, competitors, macro (45 min)
3. Internal capability review — what are we great at? where do we suck? (30 min)
4. Confirm/update vision, mission, pillars (30 min)
5. Brainstorm annual goal candidates — aim for 10-15 (60 min)

**Day 2: Prioritize & Commit**
1. Score candidates on Impact × Feasibility matrix (45 min)
2. Select top 3-5 — kill the rest explicitly (30 min)
3. Define success metrics and quarterly milestones (60 min)
4. Assign owners — one person per goal (15 min)
5. Identify top 3 risks and mitigations (30 min)
6. Write up and share within 48 hours

---

## Phase 3: OKR Writing Methodology

### The OKR Formula

```
OBJECTIVE: [Qualitative, inspiring, time-bound statement]
  KR1: [Metric] from [baseline] to [target] by [date]
  KR2: [Metric] from [baseline] to [target] by [date]
  KR3: [Metric] from [baseline] to [target] by [date]
```

### Objective Quality Rules

| Rule | Good | Bad |
|------|------|-----|
| Qualitative | "Become the fastest way to onboard" | "Increase onboarding by 30%" |
| Inspiring | "Delight enterprise buyers" | "Complete enterprise features" |
| Time-bound | "This quarter" (implicit) | No deadline |
| Achievable-ish | 70% confidence of hitting | 100% or 10% confidence |
| Verb-forward | "Launch", "Build", "Dominate" | "Continue", "Maintain" |
| No metrics in objective | Described in key results | "Achieve 50% growth" |

### Key Result Quality Checklist

Every KR must pass ALL of these:

- [ ] **Measurable** — a number, not a judgment ("increase NPS from 32 to 50" not "improve satisfaction")
- [ ] **Has a baseline** — you know where you are today
- [ ] **Has a target** — specific number, not directional ("to 50" not "higher")
- [ ] **Outcome-based** — measures the result, not the activity ("reduce churn to 3%" not "launch retention emails")
- [ ] **Within your control** — your team can actually influence this
- [ ] **Verifiable** — someone else can confirm if it was hit
- [ ] **Not a task** — tasks go in your project plan, not your OKRs

### KR Scoring (0.0 — 1.0)

| Score | Meaning | Signal |
|-------|---------|--------|
| 0.0 - 0.3 | Failed to make progress | Wrong goal or wrong approach |
| 0.4 - 0.6 | Made progress but fell short | Decent goal, execution gap |
| 0.7 | Hit target (this is the goal!) | Sweet spot — ambitious but achievable |
| 0.8 - 1.0 | Exceeded target | Either amazing execution or goal was too easy |

**Healthy OKR program: average score across all KRs = 0.6-0.7**
- Average > 0.8 = goals are too safe (sandbagging)
- Average < 0.4 = goals are too aggressive or execution is broken

### OKR Anti-Patterns

| Anti-Pattern | Example | Fix |
|-------------|---------|-----|
| **Task masquerading as KR** | "Launch new onboarding flow" | "Reduce time-to-first-value from 7 days to 2 days" |
| **Vanity metric** | "Reach 10K Twitter followers" | "Generate 50 qualified leads from social" |
| **Binary KR** | "Ship enterprise SSO" | "Enterprise accounts using SSO: 0 → 15" |
| **Sandbagging** | Target you'll hit by week 3 | Stretch to what you'd hit with exceptional execution |
| **Too many OKRs** | 8 objectives, 24 KRs | Max 3-5 objectives, 2-4 KRs each |
| **No owner** | "The team" owns it | One person accountable per OKR |
| **Moving goalposts** | Change target mid-quarter | Lock targets; add context in scoring |
| **Activity KR** | "Send 500 outreach emails" | "Book 30 discovery calls from outbound" |

### OKR YAML Template

```yaml
okr:
  quarter: "Q1 2026"
  team: "Growth"
  parent_annual_goal: "AG-2026-01"
  
  objective: "Make self-serve onboarding so good that word-of-mouth becomes our #1 channel"
  
  key_results:
    - id: "KR1"
      metric: "Time to first value (TTFV)"
      baseline: "7 days"
      target: "< 2 days"
      measurement: "Median from signup to first meaningful action"
      owner: "Sarah"
      confidence: 0.6  # at start of quarter
      
    - id: "KR2"
      metric: "Self-serve conversion rate"
      baseline: "8%"
      target: "18%"
      measurement: "Free trial → paid within 14 days"
      owner: "Mike"
      confidence: 0.5
      
    - id: "KR3"
      metric: "Organic referral signups"
      baseline: "12/month"
      target: "50/month"
      measurement: "Signups attributed to referral/word-of-mouth"
      owner: "Sarah"
      confidence: 0.4

  initiatives:  # HOW you'll hit the KRs (not OKRs themselves)
    - "Rebuild onboarding wizard with progressive disclosure"
    - "Add in-app referral program with credits"
    - "Weekly onboarding funnel analysis"
```

---

## Phase 4: Alignment & Cascading

### Cascade Architecture

```
COMPANY OKRs (CEO + leadership)
  ↓ aligns to
TEAM/DEPARTMENT OKRs (team leads)
  ↓ aligns to
INDIVIDUAL OKRs or COMMITMENTS (ICs)
```

### Alignment Rules

1. **Every team OKR must support at least one company OKR** — if it doesn't, why are you doing it?
2. **Not everything cascades down literally** — team interprets company goals through their lens
3. **Bottom-up input is mandatory** — teams propose OKRs, leadership adjusts, not top-down dictation
4. **Cross-team dependencies are explicit** — if your KR depends on another team, write it down
5. **Max 60% of capacity on OKRs** — leave 40% for operational work, fires, and innovation

### Alignment Map Template

```yaml
alignment_map:
  company_objective: "Become the fastest way to onboard"
  
  team_contributions:
    - team: "Product"
      objective: "Rebuild onboarding to be self-serve"
      key_results: ["TTFV < 2 days", "Self-serve conversion 18%"]
      
    - team: "Marketing"
      objective: "Make onboarding quality a core brand message"
      key_results: ["Case studies published: 5", "Onboarding-focused content: 40% of output"]
      
    - team: "Success"
      objective: "Eliminate onboarding as a churn driver"
      key_results: ["30-day churn from onboarding issues: < 2%", "Onboarding CSAT: > 4.5"]
      
  cross_dependencies:
    - from: "Marketing"
      to: "Product"
      need: "New onboarding screenshots and demo environment by week 3"
    - from: "Success"
      to: "Product"
      need: "In-app feedback widget for onboarding flows"
```

### Individual Commitments (For ICs)

Not everyone needs formal OKRs. For individual contributors:

```yaml
individual_commitment:
  name: "Alex"
  quarter: "Q1 2026"
  role: "Senior Engineer"
  
  commitments:
    - description: "Ship onboarding wizard v2"
      supports_kr: "TTFV < 2 days"
      milestones:
        - "Design complete by Jan 15"
        - "MVP in staging by Feb 1"
        - "GA with telemetry by Feb 15"
      
    - description: "Reduce p95 API latency to < 200ms"
      supports_kr: "Self-serve conversion 18%"
      milestone: "Completed by March 15"
      
  growth_goal: "Lead first architecture design review"
```

---

## Phase 5: KPI Dashboard

### KPI Selection Framework

KPIs are always-on metrics. OKRs are quarterly focus areas. They complement each other.

**KPI categories:**

| Category | Purpose | Examples |
|----------|---------|---------|
| **Health** | Is the business alive? | MRR, burn rate, runway |
| **Growth** | Are we getting bigger? | MoM growth, new customers, expansion |
| **Efficiency** | Are we getting better? | CAC, LTV/CAC, magic number |
| **Quality** | Are customers happy? | NPS, CSAT, churn rate |
| **Velocity** | Are we moving fast? | Cycle time, deployment frequency |

### KPI Dashboard YAML

```yaml
kpi_dashboard:
  cadence: "weekly"
  
  health_metrics:
    - name: "MRR"
      current: "$85K"
      target: "$100K"
      trend: "up"  # up/down/flat
      status: "yellow"  # green/yellow/red
      
    - name: "Gross Burn"
      current: "$45K/mo"
      target: "< $50K/mo"
      trend: "flat"
      status: "green"
      
    - name: "Runway"
      current: "18 months"
      target: "> 12 months"
      trend: "flat"
      status: "green"
  
  growth_metrics:
    - name: "New Customers (Monthly)"
      current: 12
      target: 20
      trend: "up"
      status: "yellow"
      
    - name: "Net Revenue Retention"
      current: "108%"
      target: "> 110%"
      trend: "up"
      status: "yellow"
  
  quality_metrics:
    - name: "Monthly Churn Rate"
      current: "4.2%"
      target: "< 3%"
      trend: "down"  # down is good for churn
      status: "red"
      
    - name: "NPS"
      current: 42
      target: "> 50"
      trend: "up"
      status: "yellow"
```

### Metric Hygiene Rules

1. **Every metric has an owner** — one person updates it weekly
2. **Every metric has a source of truth** — where does the number come from?
3. **Every metric has thresholds** — green/yellow/red defined in advance
4. **Review weekly, act on red** — yellow is a watch, red is an action item
5. **Limit to 10-15 KPIs** — more = nobody reads the dashboard
6. **Separate leading from lagging** — leading indicators predict; lagging confirms
7. **Never game a metric** — if behavior changes to hit the number without delivering value, the metric is wrong

---

## Phase 6: Review Cadences

### Weekly Check-In (30 min)

**Purpose:** Are we on track this week? Any blockers?

**Format:**
```
1. KPI dashboard review (5 min)
   - Any metric turn red since last week?
   - Action owner for each red metric

2. OKR confidence update (10 min)
   - Each KR owner: confidence score (0.0-1.0) + one sentence why
   - Flag anything that dropped > 0.2 since last week

3. Top 3 priorities this week (10 min)
   - Each team member: what are you working on?
   - Does it connect to an OKR? If not, why?

4. Blockers & asks (5 min)
   - What's stuck? Who can unblock it?
```

**Rules:**
- No status presentations — update a shared doc BEFORE the meeting
- Meeting is for discussion, not information transfer
- If everything is green and no blockers, cancel the meeting (seriously)

### Monthly Review (60 min)

**Purpose:** Are we on track this quarter? Should we adjust?

```
1. KPI trend review (15 min)
   - Month-over-month trends for all KPIs
   - 3 metrics that improved most, 3 that degraded most

2. OKR mid-quarter assessment (20 min)
   - Score each KR honestly
   - Identify at-risk KRs — what's the rescue plan?
   - Any KR that's clearly going to miss 0.3 → discuss kill or pivot

3. Resource check (10 min)
   - Are the right people working on the right things?
   - Any reallocation needed?

4. Learnings & adjustments (15 min)
   - What surprised us this month?
   - What would we do differently?
   - Document decisions in meeting notes
```

### Quarterly Planning & Retrospective (Half Day)

**Morning: Retrospective (2 hours)**
```
1. Score all KRs (30 min)
   - Final 0.0-1.0 score for each KR
   - Brief narrative: what happened and why

2. Objective-level scoring (15 min)
   - Average KR scores per objective
   - Did we achieve the spirit of the objective?

3. What worked? (20 min)
   - Practices, decisions, approaches that drove results
   - Capture for repetition

4. What didn't? (20 min)
   - What failed, was abandoned, or underperformed?
   - Root cause: wrong goal? wrong approach? wrong timing? under-resourced?

5. Lessons learned (15 min)
   - 3 things we'll do differently next quarter
   - 3 things we'll keep doing
   - 1 thing we'll stop doing
```

**Afternoon: Next Quarter Planning (2 hours)**
```
1. Annual goal progress check (15 min)
   - Are quarterly milestones on track?
   - Any annual goal that needs re-scoping?

2. Context update (15 min)
   - Market changes, competitive moves, customer feedback
   - Any new constraints or opportunities?

3. Draft OKRs (45 min)
   - Each team proposes 2-3 objectives with KRs
   - Stress-test: does this connect to annual goals?

4. Alignment review (30 min)
   - Map team OKRs to company OKRs
   - Identify cross-team dependencies
   - Resolve conflicts

5. Commit & communicate (15 min)
   - Lock objectives and key results
   - Set initial confidence scores
   - Assign owners
   - Share company-wide within 48 hours
```

---

## Phase 7: Accountability & Scoring

### OKR Scoring Template

```yaml
okr_score:
  quarter: "Q1 2026"
  team: "Growth"
  
  objective: "Make self-serve onboarding so good that word-of-mouth becomes our #1 channel"
  objective_score: 0.6  # weighted average of KRs + qualitative judgment
  
  key_results:
    - id: "KR1"
      metric: "TTFV"
      baseline: "7 days"
      target: "< 2 days"
      actual: "3.2 days"
      score: 0.5
      narrative: "Rebuilt wizard but edge cases with enterprise SSO added 2 days for 30% of users"
      
    - id: "KR2"
      metric: "Self-serve conversion"
      baseline: "8%"
      target: "18%"
      actual: "14%"
      score: 0.6
      narrative: "Improved significantly but pricing page redesign delayed to Q2"
      
    - id: "KR3"
      metric: "Organic referral signups"
      baseline: "12/month"
      target: "50/month"
      actual: "38/month"
      score: 0.7
      narrative: "Referral program launched week 4, ramped well. On trajectory for 50+ in Q2"
  
  lessons:
    - "SSO complexity was underestimated — involve security team in planning"
    - "Referral program should have launched week 1, not week 4"
    - "Pricing page has massive impact on conversion — prioritize in Q2"
  
  carry_forward:
    - "Enterprise SSO onboarding optimization"
    - "Pricing page redesign"
```

### Grading Culture

**Healthy scoring culture:**
- 0.7 is a WIN — it means you set ambitious targets and mostly hit them
- Consistent 1.0 across the board = goals are too easy, push harder
- Consistent 0.3 = goals are disconnected from reality, recalibrate
- Misses are learning opportunities, not punishment
- Sandbagging (setting easy goals to look good) is worse than failing on ambitious ones

**Red flags in scoring:**
- Every team scores 0.8+ every quarter → sandbagging epidemic
- Scores are always exactly 0.7 → people are gaming the target
- Teams argue about scoring definitions after the quarter → define measurement upfront
- No one cares about the scores → OKRs aren't connected to actual work

### Accountability Without Bureaucracy

**For small teams (< 15 people):**
- Company OKRs only (no team-level)
- Weekly standup covers OKR progress
- Quarterly retrospective + planning = one afternoon
- Individual commitments instead of individual OKRs

**For medium teams (15-50 people):**
- Company + team OKRs
- Weekly team check-ins + monthly leadership review
- Quarterly planning = half day per team + half day cross-team

**For larger organizations (50+ people):**
- Company + department + team OKRs
- Dedicated OKR champion/program manager
- Software tool for tracking (Lattice, Weekdone, Perdoo, etc.)
- Quarterly cycle with 2-week drafting period

---

## Phase 8: Common Scenarios

### Scenario 1: First Time Setting OKRs

**Start simple:**
1. Set 2 company objectives with 3 KRs each (that's it)
2. Review weekly for one quarter
3. Score honestly at end of quarter
4. Add team-level OKRs in Q2 if Q1 worked

**Common first-timer mistakes:**
- Setting 8 objectives → pick 2-3
- Making KRs into task lists → focus on outcomes
- Not reviewing weekly → put it on the calendar NOW
- Changing goals mid-quarter → lock them, learn from the miss

### Scenario 2: OKRs for a Solo Founder / Solopreneur

```yaml
solo_okr:
  quarter: "Q1 2026"
  
  objective_1: "Build a revenue engine that doesn't depend on my time"
  key_results:
    - "Monthly recurring revenue from $2K to $8K"
    - "Percentage of revenue from productized offers: 0% to 60%"
    - "Hours worked per $1K revenue: 40 to 15"
  
  objective_2: "Establish market authority in [niche]"
  key_results:
    - "Email list from 200 to 1,000 subscribers"
    - "Inbound leads per month from 3 to 15"
    - "Published content pieces: 0 to 12"
  
  weekly_ritual: "Friday 30 min — update KR numbers, plan next week's top 3"
  monthly_ritual: "Last Friday — full review, adjust tactics (not goals)"
```

### Scenario 3: Pivoting Mid-Quarter

Sometimes the world changes and your OKRs become irrelevant.

**Decision framework:**
1. Is this a temporary disruption or a fundamental shift? → Temporary = stay the course
2. Would continuing the OKR waste more than 20% of remaining quarter capacity? → Yes = pivot
3. Can you modify KRs without changing the objective? → Try this first

**If you pivot:**
- Score original OKRs as-is with narrative explaining the pivot
- Set new OKRs for remaining time with appropriately scaled targets
- Don't pretend the pivot didn't happen — document the learning

### Scenario 4: OKRs Across Remote/Async Teams

- **Written over verbal** — all OKR updates in shared doc, not meetings
- **Async weekly updates** — each person posts by Friday EOD
- **Sync monthly** — video call for the monthly review only
- **Time zone equity** — rotate meeting times if team spans > 6 hours
- **Overcommunicate confidence** — in person you can read body language; async you can't

### Scenario 5: Connecting OKRs to Performance Reviews

**Caution:** Tying OKR scores directly to compensation creates sandbagging.

**Better approach:**
- Evaluate EFFORT and LEARNING, not just score
- Someone who scores 0.5 on an ambitious OKR and learns from it > someone who scores 1.0 on a safe one
- Use OKRs as INPUT to performance conversations, not the grade itself
- Assess: Did they set good goals? Did they execute with discipline? Did they learn from misses?

---

## Phase 9: Goal Quality Scoring Rubric (0-100)

| Dimension | Weight | 0-25 (Poor) | 50 (Okay) | 75-100 (Excellent) |
|-----------|--------|-------------|-----------|---------------------|
| **Ambition** | 15% | Obviously achievable | Moderate stretch | 60-70% confidence, would be proud to hit |
| **Measurability** | 20% | Vague, subjective | Has a metric but fuzzy measurement | Specific number, clear source, baseline documented |
| **Alignment** | 15% | Doesn't connect to strategy | Loosely related | Directly supports a pillar + annual goal |
| **Outcome Focus** | 20% | List of tasks/activities | Mix of outputs and outcomes | Pure outcome — measures the result, not the work |
| **Ownership** | 10% | "The team" or unassigned | Team-level but no individual | One person accountable, they wrote the OKR |
| **Time-Bound** | 10% | No deadline | "This quarter" | Specific milestones within the quarter |
| **Independence** | 10% | Entirely dependent on other teams | Some dependency, documented | Primarily within your control |

**Scoring guide:**
- 80-100: Ship it — this is a well-crafted OKR
- 60-79: Good foundation, tighten weak dimensions
- 40-59: Needs significant rework before committing
- Below 40: Start over — this isn't an OKR yet

---

## Phase 10: Tools & Templates

### Quarterly OKR One-Pager

```markdown
# Q[X] 20XX OKRs — [Team Name]

## Context
- Annual goal this supports: [reference]
- Key assumption: [what must be true for these to matter]
- Biggest risk: [what could derail us]

## Objective 1: [Inspiring statement]
| KR | Baseline | Target | Owner | Confidence |
|----|----------|--------|-------|------------|
| [metric] | [current] | [target] | [name] | [0.0-1.0] |
| [metric] | [current] | [target] | [name] | [0.0-1.0] |
| [metric] | [current] | [target] | [name] | [0.0-1.0] |

**Key initiatives:** [2-3 bullet points of HOW]

## Objective 2: [Inspiring statement]
[same format]

## Dependencies
- Need from [team]: [what] by [when]

## What we're NOT doing this quarter
- [Explicit list of things we're deprioritizing]
```

### Weekly Update Template

```markdown
# Weekly OKR Update — [Date]

## KPI Status
| Metric | Last Week | This Week | Status |
|--------|-----------|-----------|--------|
| [metric] | [value] | [value] | 🟢/🟡/🔴 |

## OKR Confidence
| KR | Last | Now | Δ | Note |
|----|------|-----|---|------|
| [KR1] | 0.6 | 0.5 | ↓ | [why it dropped] |

## Top 3 This Week
1. [priority] → supports [KR]
2. [priority] → supports [KR]
3. [priority] → operational

## Blockers
- [blocker] → need [action] from [person]
```

### Retrospective Template

```yaml
retrospective:
  quarter: "Q1 2026"
  date: "2026-04-01"
  
  scores:
    - objective: "[text]"
      score: 0.65
      key_results:
        - kr: "[text]"
          score: 0.7
        - kr: "[text]"
          score: 0.5
        - kr: "[text]"
          score: 0.75
  
  overall_average: 0.65
  
  wins:
    - "[what worked and why]"
    - "[what worked and why]"
  
  misses:
    - "[what failed and root cause]"
    - "[what failed and root cause]"
  
  keep_doing:
    - "[practice to continue]"
  
  start_doing:
    - "[new practice]"
  
  stop_doing:
    - "[practice to eliminate]"
  
  carry_forward_to_next_quarter:
    - "[unfinished work worth continuing]"
```

---

## Phase 11: Advanced Patterns

### OKRs + Agile Integration

**Sprint planning connection:**
- Each sprint should advance at least one KR
- Sprint goals reference which KR they support
- Sprint retro includes: "did this sprint move our OKRs?"
- If 3+ sprints pass without OKR progress, something is misaligned

### Stretch Goals vs Committed Goals

**Google-style two-tier approach:**
- **Committed OKRs** (expect 1.0): must-hit goals with consequences for missing
- **Aspirational OKRs** (expect 0.7): ambitious stretch goals where 0.7 is success

**When to use which:**
- Revenue targets customers depend on → Committed
- Innovation or market expansion → Aspirational
- Operational SLAs → Committed
- Culture/employer brand → Aspirational

### Leading vs Lagging Indicator Design

Every KR should ideally have a leading indicator you track weekly:

| Lagging KR (quarterly) | Leading Indicator (weekly) |
|------------------------|---------------------------|
| Revenue from $X to $Y | Pipeline generated this week |
| Churn from 5% to 3% | Health score distribution changes |
| NPS from 32 to 50 | Support ticket resolution time |
| Conversion from 8% to 18% | Onboarding completion rate |
| New hires: 5 | Candidates in pipeline by stage |

### Multi-Team OKR Dependencies

```yaml
dependency_contract:
  provider_team: "Platform"
  consumer_team: "Growth"
  deliverable: "Self-serve SSO integration"
  needed_by: "2026-02-15"
  provider_kr: "Ship 3 enterprise features"
  consumer_kr: "Enterprise onboarding TTFV < 3 days"
  escalation_date: "2026-02-01"  # if not on track by this date, escalate
  status: "on_track"
```

### OKRs for Non-Typical Roles

**Support/Ops teams:**
- Objective: "Deliver world-class support that turns users into advocates"
- KRs: First response time, CSAT, escalation rate, knowledge base deflection %

**HR/People teams:**
- Objective: "Build a hiring engine that attracts top talent faster"
- KRs: Time-to-fill, offer acceptance rate, 90-day retention, hiring manager satisfaction

**Finance teams:**
- Objective: "Give leadership real-time financial visibility"
- KRs: Monthly close time (days), forecast accuracy (%), board deck delivery (days before meeting)

---

## Phase 12: 10 OKR Commandments

1. **Less is more** — 3 objectives × 3 KRs = plenty. More = dilution.
2. **Outcomes over outputs** — Measure what changed, not what you did.
3. **Honest scoring or don't bother** — A dishonest 0.7 is worse than an honest 0.3.
4. **Weekly rhythm or it dies** — OKRs without regular check-ins are decoration.
5. **One owner per OKR** — Shared ownership = no ownership.
6. **Lock goals, iterate tactics** — Don't change the OKR mid-quarter; change how you pursue it.
7. **Ambitious is calibrated** — 70% hit rate is the target. Not 100%, not 30%.
8. **Alignment ≠ top-down dictation** — Teams propose, leadership aligns.
9. **Say what you're NOT doing** — Every yes requires explicit nos.
10. **OKRs ≠ performance reviews** — Use them as input, not the grade.

---

## 10 Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Too many OKRs | Max 3-5 objectives company-wide |
| 2 | KRs are tasks | Rewrite as measurable outcomes |
| 3 | No baseline | You can't improve what you haven't measured |
| 4 | Set and forget | Weekly reviews are non-negotiable |
| 5 | 100% hit rate | You're sandbagging — aim higher |
| 6 | Changing goals mid-quarter | Lock them; learn from the miss |
| 7 | OKRs in a spreadsheet nobody opens | Put them where daily work happens |
| 8 | No retrospective | Without learning, cycles are just calendars |
| 9 | Top-down only | Bottom-up input creates buy-in and better goals |
| 10 | Conflating KPIs and OKRs | KPIs = always-on health; OKRs = quarterly focus |

---

## Natural Language Commands

- "Set OKRs for Q[X]" → Phase 3 template + scoring
- "Score our OKRs" → Phase 7 scoring template
- "Run quarterly planning" → Phase 6 full retrospective + planning ritual
- "Create KPI dashboard" → Phase 5 dashboard YAML
- "Check OKR alignment" → Phase 4 alignment map
- "Write annual goals" → Phase 2 annual goal template
- "Weekly OKR update" → Phase 6 weekly template
- "Grade this OKR" → Phase 9 rubric (0-100)
- "Plan our retro" → Phase 6 retrospective template
- "Help me write a key result" → Phase 3 quality checklist
- "What's our north star?" → Phase 1 north star selection
- "OKRs for solo founder" → Phase 8 Scenario 2
