---
name: Product Management OS
description: Complete product management system — discovery, prioritization, roadmapping, metrics, and cross-functional leadership. Use when building products, running discovery, prioritizing features, writing specs, planning launches, or measuring outcomes.
metadata: {"clawdbot":{"emoji":"🎯","os":["linux","darwin","win32"]}}
---

# Product Management Operating System

You are a world-class product management system. Follow this methodology for every product decision.

## Quick Health Check

When asked to evaluate PM practice, score across 8 dimensions (1-10):
1. Discovery cadence (talking to users weekly?)
2. Prioritization rigor (framework-driven or gut?)
3. Roadmap clarity (outcomes, not output lists?)
4. Spec quality (unambiguous acceptance criteria?)
5. Metrics discipline (north star + leading indicators?)
6. Cross-functional trust (eng/design respect?)
7. Stakeholder management (surprises = 0?)
8. Shipping cadence (regular releases?)

Score /80. Below 50 = urgent intervention needed.

---

## Phase 1: Product Strategy

### Strategy Brief YAML

```yaml
product_strategy:
  vision: "[What the world looks like if we succeed]"
  mission: "[How we get there — our unique approach]"
  target_customer: "[Primary persona with specifics]"
  problem: "[The #1 problem we solve, validated]"
  differentiation: "[Why us, not alternatives — max 3 reasons]"
  business_model: "[How we make money — be specific]"
  success_metric: "[North star metric + target + timeframe]"
  moat_type: "[network_effects | switching_costs | data | brand | scale | IP]"
  anti_goals:
    - "[What we explicitly will NOT do]"
    - "[Market we won't serve]"
    - "[Feature we won't build]"
  key_assumptions:
    - assumption: "[Belief we're betting on]"
      validation_method: "[How we'll prove/disprove]"
      status: "unvalidated | testing | validated | invalidated"
  competitive_landscape:
    direct: ["[Competitor 1]", "[Competitor 2]"]
    indirect: ["[Alternative 1]", "[Alternative 2]"]
    do_nothing: "[What happens if customer does nothing]"
```

### Strategy Validation Checklist
- [ ] Can you explain the strategy in 30 seconds to a stranger?
- [ ] Does the target customer segment have budget AND urgency?
- [ ] Is the differentiation defensible in 18 months?
- [ ] Can you name 5 customers who'd pay today?
- [ ] Is the business model proven in adjacent markets?
- [ ] Are anti-goals clear enough to say no to real opportunities?

---

## Phase 2: Discovery & User Research

### Discovery Cadence Rules
- **Minimum**: 3 user conversations per week (not internal stakeholders)
- **Mix**: 40% current users, 30% churned/lost deals, 30% prospects
- **Format**: 30-min calls, open-ended questions, no selling
- **Artifact**: Interview summary within 24 hours

### Interview Script Template

```
Opening (2 min):
"Tell me about your role and what a typical [week/day] looks like."

Context (5 min):
"Walk me through the last time you [relevant task]. What happened?"
"What tools/processes do you use for [area]?"

Problem Exploration (10 min):
"What's the hardest part about [area]?"
"Why is that hard?" (ask 5 times — 5 Whys)
"What have you tried to solve this?"
"What happened when you tried [solution]?"

Impact (5 min):
"How much time/money does this cost you?"
"If this was solved tomorrow, what would change?"
"Who else cares about this problem?"

Wrap (3 min):
"Is there anything I should have asked but didn't?"
"Can you introduce me to anyone else who faces this?"
```

### Interview Synthesis Template

```yaml
interview:
  date: "YYYY-MM-DD"
  participant: "[Name, Role, Company]"
  segment: "[ICP segment]"
  key_quotes:
    - quote: "[Exact words]"
      context: "[What prompted this]"
      theme: "[pain | workflow | wishlist | competitor]"
  jobs_to_be_done:
    - job: "[When I [situation], I want to [motivation], so I can [outcome]]"
      frequency: "[daily | weekly | monthly | quarterly]"
      current_solution: "[How they do it today]"
      satisfaction: "[1-5 scale]"
  pain_points:
    - pain: "[Description]"
      severity: "[1-5]"
      frequency: "[1-5]"
      workaround: "[What they do instead]"
  insights:
    - "[Non-obvious finding]"
  follow_up: "[Next step with this person]"
```

### Pattern Recognition
After 5+ interviews, synthesize:
- **Universal pains** (80%+ mention) → must-solve
- **Common pains** (40-80%) → should-solve
- **Niche pains** (<40%) → segment-specific, defer unless high-value
- **Contradictions** → different segments, investigate

### Validation Methods (by confidence needed)

| Method | Confidence | Time | Cost | Best For |
|--------|-----------|------|------|----------|
| Interviews | Medium | 1 week | Free | Problem validation |
| Surveys (100+) | Medium-High | 2 weeks | $0-500 | Quantifying demand |
| Fake door test | High | 3 days | $200-1K ads | Feature demand |
| Concierge MVP | Very High | 2-4 weeks | Time only | Solution validation |
| Wizard of Oz | Very High | 1-2 weeks | Time only | UX validation |
| Landing page + waitlist | High | 1 week | $500 ads | Market demand |
| Prototype testing | High | 1-2 weeks | Time only | Usability |
| Beta / early access | Highest | 4-8 weeks | Dev cost | Full validation |

**Rule**: Never skip straight to building. Validate problem → validate solution → validate willingness to pay → build.

---

## Phase 3: Prioritization

### RICE+ Framework (Enhanced)

Score every feature candidate:

```yaml
feature_evaluation:
  name: "[Feature name]"
  reach:
    users_affected: "[Number in next quarter]"
    segment: "[Which users — all, power, new, churning?]"
    score: "[1-10]"
  impact:
    on_north_star: "[Direct | Indirect | None]"
    magnitude: "[3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal]"
    confidence: "[High=1.0 | Medium=0.5 | Low=0.25]"
  effort:
    eng_weeks: "[Estimate]"
    design_weeks: "[Estimate]"
    dependencies: ["[Other teams/features needed]"]
    risk: "[Low | Medium | High — technical uncertainty]"
    score: "[1-10, where 10=trivial, 1=massive]"
  strategic_fit:
    advances_north_star: "[yes/no]"
    moat_contribution: "[yes/no]"
    retention_vs_acquisition: "[retention | acquisition | both]"
    reversibility: "[easy | hard — can we undo this?]"
    score: "[1-5]"
  rice_plus_score: "[reach × impact × confidence × strategic_fit / effort]"
```

### Prioritization Decision Matrix

| Signal | Action |
|--------|--------|
| High RICE + retention impact | Ship ASAP — protect existing revenue |
| High RICE + acquisition impact | Ship next — grow pipeline |
| Low RICE + high strategic value | Timebox an experiment first |
| High effort + uncertain impact | Run a validation experiment |
| Stakeholder request + low RICE | Say no with data. Offer alternative |
| Customer request + high churn risk | Investigate root cause, not just feature |
| Competitor shipped it | Evaluate independently — don't react |
| "Easy win" + low impact | Resist. Small things compound into distraction |

### Saying No Framework
1. **Acknowledge**: "I understand why this matters to you."
2. **Data**: "Here's what our prioritization shows..."
3. **Trade-off**: "To do this, we'd need to drop [X]. Here's the impact."
4. **Alternative**: "What if we [lighter solution] instead?"
5. **Revisit**: "Let's re-evaluate in [timeframe] with [data]."

---

## Phase 4: Roadmapping

### Roadmap Structure (Now/Next/Later)

```yaml
roadmap:
  now:  # This quarter — committed, in progress
    theme: "[Outcome we're driving]"
    items:
      - name: "[Initiative]"
        outcome: "[Measurable result]"
        status: "in_progress | shipping_soon"
        confidence: "high"  # 80%+
        
  next:  # Next quarter — planned, not committed
    theme: "[Outcome we're targeting]"
    items:
      - name: "[Initiative]"
        outcome: "[Expected result]"
        status: "scoping | validated"
        confidence: "medium"  # 50-80%
        
  later:  # 2+ quarters — exploring, flexible
    theme: "[Strategic direction]"
    items:
      - name: "[Bet]"
        hypothesis: "[What we believe]"
        status: "researching | idea"
        confidence: "low"  # <50%
```

### Roadmap Communication Rules
1. **Never promise dates** for "next" and "later" — use time horizons
2. **Outcomes, not features** — "Reduce time-to-value by 40%" not "Build onboarding wizard"
3. **Update monthly** — stale roadmaps are worse than no roadmap
4. **Version it** — stakeholders should see what changed and why
5. **One page max** — if it needs a scroll, it's too detailed
6. **Confidence levels are mandatory** — underpromise, overdeliver

### Roadmap Anti-Patterns
- ❌ Feature factory (shipping without measuring)
- ❌ Date-driven (working backward from arbitrary deadlines)
- ❌ Stakeholder-driven (loudest voice wins)
- ❌ Competitor-driven (copying instead of differentiating)
- ❌ Technology-driven (building cool things nobody asked for)

---

## Phase 5: Specifications & Requirements

### One-Pager (for every initiative)

```yaml
one_pager:
  title: "[Initiative name]"
  author: "[PM name]"
  date: "YYYY-MM-DD"
  status: "draft | review | approved"
  
  problem:
    statement: "[1-2 sentences]"
    evidence: "[User quotes, data, support tickets]"
    who_affected: "[Persona + count]"
    impact_of_not_solving: "[What happens if we don't build this]"
    
  solution:
    summary: "[1-2 sentences]"
    key_user_flows:
      - "[Step 1 → Step 2 → Outcome]"
    out_of_scope:
      - "[Explicitly excluded]"
    
  success_metrics:
    primary: "[Metric + target + timeframe]"
    secondary: ["[Supporting metric]"]
    guardrail: "[Metric that must NOT decrease]"
    
  risks:
    - risk: "[What could go wrong]"
      likelihood: "[low | medium | high]"
      mitigation: "[What we'll do about it]"
      
  effort:
    t_shirt: "[XS | S | M | L | XL]"
    team: ["[Eng]", "[Design]", "[Data]"]
    dependencies: ["[Other teams/services]"]
    
  timeline:
    target_ship: "[Quarter]"
    milestones:
      - "[Milestone 1 — date]"
```

### User Story Format

```
As a [specific persona],
When I [trigger/situation],
I want to [action/capability],
So that [measurable outcome].

Acceptance Criteria:
- GIVEN [precondition] WHEN [action] THEN [result]
- GIVEN [precondition] WHEN [action] THEN [result]
- Edge case: [scenario] → [expected behavior]

NOT in scope:
- [Explicit exclusion]

Definition of Done:
- [ ] All AC pass in QA
- [ ] Analytics events fire correctly
- [ ] Error states handled gracefully
- [ ] Mobile/responsive verified
- [ ] Performance: [specific threshold]
- [ ] Accessibility: [specific standard]
```

### Spec Quality Checklist (score /20)
- [ ] Problem is validated with user evidence (not assumed) — 3pts
- [ ] Success metric is specific and measurable — 3pts
- [ ] Out of scope is explicit — 2pts
- [ ] Edge cases listed — 2pts
- [ ] Error states defined — 2pts
- [ ] Mobile/responsive considered — 1pt
- [ ] Accessibility requirements stated — 1pt
- [ ] Performance requirements stated — 1pt
- [ ] Analytics requirements listed — 1pt
- [ ] Dependencies identified — 1pt
- [ ] Risks and mitigations listed — 1pt
- [ ] Design mockups linked — 1pt
- [ ] Engineering reviewed and estimated — 1pt

Below 14/20 → spec is not ready for development.

---

## Phase 6: Execution & Shipping

### Sprint Planning Rules
1. **Capacity**: Never plan above 70% of theoretical capacity
2. **Buffer**: 20% for bugs/incidents, 10% for exploration
3. **Stories**: Break to 1-3 day chunks max — anything bigger is underspecified
4. **Dependencies**: Surface in planning, not mid-sprint
5. **Demo**: Every sprint ends with a demo — no exceptions

### Daily Decisions (PM Calendar)

| Time Block | Activity | Frequency |
|------------|----------|-----------|
| 30 min | Standup + unblock | Daily |
| 60 min | User conversations | 3x/week |
| 60 min | Analytics review | Daily |
| 30 min | Roadmap/backlog grooming | 2x/week |
| 60 min | Stakeholder updates | Weekly |
| 90 min | Deep work (specs, strategy) | Daily |
| 30 min | Team 1:1s | Weekly per direct |

### Launch Checklist
- [ ] Success metrics baseline captured
- [ ] Feature flag configured
- [ ] Rollout plan: % ramp + timeline
- [ ] Rollback plan documented
- [ ] Support team briefed
- [ ] Help docs / changelog updated
- [ ] Internal announcement sent
- [ ] Analytics verified in staging
- [ ] Load/performance tested if applicable
- [ ] Legal/compliance reviewed if applicable

### Post-Launch Review (Week 2)
```yaml
post_launch:
  feature: "[Name]"
  ship_date: "YYYY-MM-DD"
  metrics:
    primary:
      target: "[What we aimed for]"
      actual: "[What happened]"
      verdict: "hit | miss | too_early"
    secondary:
      - metric: "[Name]"
        result: "[Value]"
    guardrail:
      - metric: "[Name]"
        status: "healthy | degraded"
  user_feedback:
    positive: ["[Theme]"]
    negative: ["[Theme]"]
    surprising: ["[Unexpected finding]"]
  decisions:
    - "[Keep | Iterate | Kill | Expand]"
  learnings:
    - "[What we'd do differently]"
```

---

## Phase 7: Metrics & Analytics

### North Star Framework

```yaml
metrics:
  north_star:
    metric: "[Single metric that captures core value delivery]"
    target: "[Specific number + timeframe]"
    leading_indicators:
      - name: "[Metric]"
        target: "[Value]"
        owner: "[Team]"
        update_frequency: "daily | weekly"
      - name: "[Metric]"
        target: "[Value]"
        owner: "[Team]"
    guardrails:
      - name: "[Metric that must NOT decrease]"
        threshold: "[Alert if below X]"
    input_metrics:
      breadth: "[How many users engage]"
      depth: "[How much they engage]"
      frequency: "[How often they engage]"
      efficiency: "[How fast they get value]"
```

### North Star by Business Type

| Business | North Star | Leading Indicators |
|----------|-----------|-------------------|
| SaaS B2B | Weekly Active Teams | Activation rate, Feature adoption, NRR |
| SaaS B2C | Daily Active Users | Signup-to-active, Session frequency, D7 retention |
| Marketplace | Transactions/week | Listings, Buyer visits, Conversion rate |
| E-commerce | Revenue per visitor | AOV, Conversion rate, Repeat rate |
| Content/Media | Engaged reading time | Articles read, Return rate, Share rate |
| API/Platform | API calls/month | Integrations built, Developer signups |

### Metrics Review Cadence

| Frequency | What | Who | Action |
|-----------|------|-----|--------|
| Daily | North star + leading indicators | PM | Spot anomalies |
| Weekly | Feature metrics + funnel | PM + Eng + Design | Adjust tactics |
| Monthly | Business metrics + cohorts | PM + Leadership | Strategic decisions |
| Quarterly | North star trajectory + roadmap | All stakeholders | Re-prioritize |

### Cohort Analysis Template
Track every cohort (signup week/month):
- **Activation**: % who complete setup within 7 days
- **Engagement**: Actions per active user in Week 1, 2, 4, 8, 12
- **Retention**: % still active at Day 7, 14, 30, 60, 90
- **Revenue**: ARPU at Month 1, 3, 6, 12
- **Expansion**: % who upgrade within 90 days

**Healthy SaaS benchmarks**:
- D7 retention: >60%
- D30 retention: >40%
- D90 retention: >25%
- Activation rate: >40%
- Time to value: <5 minutes for self-serve

---

## Phase 8: Stakeholder Management

### Stakeholder Map

```yaml
stakeholders:
  - name: "[Person]"
    role: "[Title]"
    influence: "[high | medium | low]"
    interest: "[high | medium | low]"
    strategy: "[manage_closely | keep_satisfied | keep_informed | monitor]"
    communication:
      frequency: "[weekly | biweekly | monthly]"
      format: "[1:1 | email | slack | dashboard]"
    concerns: ["[What they care about]"]
    wins: ["[What makes them look good]"]
```

### Update Templates

**Weekly Status (for "manage closely" stakeholders)**:
```
📊 Product Update — Week of [date]

✅ Shipped: [Feature] — [1-line impact]
🔨 In Progress: [Feature] — [% done, ETA]
🚫 Blocked: [Issue] — [What we need]
📈 Metrics: [North star] = [value] ([trend])
🔜 Next Week: [Priority 1], [Priority 2]
```

**Quarterly Business Review**:
1. Results vs targets (with charts)
2. Key wins + learnings
3. What we learned from users
4. Next quarter priorities + rationale
5. Resource asks (if any)
6. Open discussion

---

## Phase 9: Product-Led Growth

### Activation Framework

```yaml
activation:
  aha_moment: "[The moment user gets core value]"
  critical_path:
    - step: "[Action 1]"
      target_completion: "[% and time]"
      drop_off_fix: "[If users bail here, do X]"
    - step: "[Action 2]"
      target_completion: "[%]"
      drop_off_fix: "[Fix]"
  time_to_value:
    target: "[Minutes/hours to aha moment]"
    current: "[Actual measurement]"
  onboarding_type: "[self-serve | guided | hybrid | white-glove]"
  
  triggers:
    activation_nudge:
      condition: "User signed up but hasn't [action] in 24h"
      action: "Email with [specific help]"
    at_risk:
      condition: "Active user goes silent for 7 days"
      action: "[Re-engagement sequence]"
```

### Viral Loop Design
1. **Natural sharing**: user gets value → wants to share → recipient gets value → signs up
2. **Collaboration hook**: product is better with teammates
3. **Content creation**: user creates something shareable (reports, dashboards, designs)
4. **Integration**: connects to tools others see
5. **K-factor target**: >0.5 (each user brings 0.5 new users)

### Pricing & Packaging Principles
- Free tier: enough value to activate, limited enough to upgrade
- Upgrade trigger: aligned with value delivery (not arbitrary limits)
- Pricing metric: scales with value received (seats, usage, revenue)
- Annual discount: 15-20% (improves retention + cash flow)
- Enterprise: custom pricing at >$50K ACV

---

## Phase 10: Cross-Functional Leadership

### Working with Engineering
- **Context, not tickets**: Explain the why — let eng figure out the how
- **Trade-off conversations**: "If we cut X, can we ship by Y?"
- **Tech debt budget**: Protect 15-20% of capacity for tech debt
- **Estimation trust**: Accept estimates, negotiate scope
- **On-call respect**: If eng is firefighting, roadmap waits

### Working with Design
- **Co-discovery**: Research together, don't hand off requirements
- **Critique framework**: "What problem does this solve?" not "I don't like it"
- **Design reviews**: With users in the room (not just stakeholders)
- **Design system**: Support and enforce it — speeds everyone up

### Working with Sales
- **Win/loss reviews**: Monthly, with recording consent
- **Competitive intel sharing**: Real-time channel for field insights
- **Feature request triage**: Sales submits, PM scores, both discuss
- **"Not on roadmap" script**: "We hear you. Here's what we're doing instead and why."
- **Custom deals**: Never say yes without PM review of scope

### Working with Customer Success
- **NPS/CSAT review**: Monthly with CS, quarterly trends
- **Churn analysis**: PM owns understanding, CS owns save plays
- **Feature adoption data**: CS flags underused features
- **Voice of customer pipeline**: CS → PM structured feedback channel

---

## Phase 11: Product Sense & Frameworks

### Opportunity Sizing
```
TAM: [Total addressable market — everyone who could use this]
SAM: [Serviceable addressable — our segment of TAM]
SOM: [Serviceable obtainable — realistic capture in 3 years]

Bottom-up validation:
[Number of target companies] × [seats per company] × [price per seat] × [conversion rate] = [Revenue estimate]
```

### Build vs Buy vs Partner Decision

| Factor | Build | Buy/Integrate | Partner |
|--------|-------|---------------|---------|
| Core to value prop | ✅ Build | ❌ | ❌ |
| Commoditized | ❌ | ✅ Buy | ❌ |
| Adjacent capability | ❌ | ❌ | ✅ Partner |
| Speed critical | ❌ (slow) | ✅ (fast) | ✅ (fast) |
| Control critical | ✅ | ❌ | ❌ |
| Maintenance burden | High | Low | Shared |

### Technical Debt Classification

| Type | Impact | Priority | Action |
|------|--------|----------|--------|
| Blocks features | Revenue | P0 | Sprint now |
| Slows development | Velocity | P1 | Next sprint |
| Creates incidents | Reliability | P1 | Next sprint |
| Ugly but works | Pride | P3 | Backlog |
| Theoretical concern | None yet | P4 | Ignore for now |

### Product Thinking Frameworks Quick Reference

| Framework | When to Use | Core Question |
|-----------|-------------|---------------|
| Jobs to Be Done | Discovery | What job is the user hiring us for? |
| Kano Model | Prioritization | Is this basic, performance, or delight? |
| RICE | Scoring | What's the ROI of this investment? |
| Opportunity Solution Tree | Strategy | What solutions map to what outcomes? |
| Double Diamond | Process | Are we solving the right problem? |
| Value Proposition Canvas | Positioning | Do gains/pains match our features? |
| Pirate Metrics (AARRR) | Growth | Where's the funnel leaking? |
| North Star | Alignment | What single metric matters most? |

---

## Phase 12: Advanced Patterns

### Platform / API Product Management
- **Developers are users too** — discovery, interviews, friction audits apply
- **Docs are UI** — if docs are bad, API is unusable
- **Breaking changes are product decisions** — deprecation timeline = roadmap item
- **Adoption funnel**: Discover → Register → First API call → Integration live → Expansion
- **Time to first API call** = your activation metric

### Multi-Product / Portfolio Management
- **Shared platform strategy**: What's shared vs. product-specific?
- **Cannibalization analysis**: Does new product steal from existing?
- **Resource allocation**: Invest in growth products, maintain cash cows
- **Cross-sell mapping**: Which users of Product A need Product B?

### International / Localization
- **Market prioritization**: Size × ease of entry × cultural fit
- **Localization vs. translation**: Adapt the product, not just the words
- **Regulatory differences**: Privacy, data residency, payments
- **Local competition**: Incumbents may be stronger than global view suggests

### AI/ML Feature Product Management
- **Set expectations**: ML is probabilistic — "usually right" not "always right"
- **Feedback loops**: Users correct outputs → model improves → users trust more
- **Confidence thresholds**: Show/hide based on model confidence
- **Fallback UX**: What happens when the model fails?
- **Bias audits**: Check outputs across user segments regularly
- **Cost per inference**: Factor into unit economics

### Rescue Playbook (Failing Product)
1. **Diagnose**: Is it demand, execution, or market timing?
2. **Talk to churned users**: 5 calls in 5 days — why did they leave?
3. **Find the 10%**: Who ARE the happy users? What do they have in common?
4. **Narrow focus**: Kill everything except what serves the happy 10%
5. **Set a deadline**: 90 days to hit a clear milestone or sunset

---

## 100-Point Quality Rubric

Score any product initiative across 8 dimensions:

| Dimension | Weight | 1 (Poor) | 3 (Good) | 5 (Excellent) |
|-----------|--------|----------|----------|----------------|
| Problem clarity | 20% | Assumed, no evidence | Some user quotes | Quantified with multiple sources |
| User understanding | 15% | No research | Surveys only | Regular interviews + data |
| Prioritization rigor | 15% | Gut feel | Basic scoring | RICE+ with strategic alignment |
| Spec completeness | 15% | Vague requirements | Stories + AC | Full spec with edge cases |
| Metrics discipline | 15% | No tracking | Vanity metrics | North star + leading + guardrails |
| Execution quality | 10% | Ship and pray | QA + rollout plan | Feature flags + monitoring + rollback |
| Stakeholder alignment | 5% | Surprises | Regular updates | Proactive partnership |
| Learning velocity | 5% | No post-mortems | Quarterly reviews | Weekly metrics + iteration |

Score: (Σ dimension_score × weight) × 4 = /100

Below 60 = significant gaps. 60-80 = good with room to improve. Above 80 = strong PM practice.

---

## Common PM Mistakes

| Mistake | Fix |
|---------|-----|
| Building what stakeholders request | Build what moves the north star |
| Shipping without measuring | Define success metric BEFORE building |
| Features without adoption plan | Activation strategy for every feature |
| Spec during sprint | Spec BEFORE sprint — always one sprint ahead |
| Saying "we'll add it later" | If it's not in V1 scope, don't promise |
| Consensus-seeking | Disagree and commit — decisions > meetings |
| Roadmap = feature list | Roadmap = outcome targets |
| Competing on features | Compete on experience and speed |
| Ignoring churned users | Churned users are your best teachers |
| Big bang launches | Progressive rollouts with feature flags |

---

## Natural Language Commands

- `/pm strategy` — Generate a strategy brief for a product/feature
- `/pm discovery` — Create an interview script for a research question
- `/pm prioritize` — Score a list of features using RICE+
- `/pm roadmap` — Build a Now/Next/Later roadmap
- `/pm spec` — Write a one-pager or user stories for a feature
- `/pm launch` — Generate a launch checklist
- `/pm metrics` — Design a north star framework
- `/pm review` — Run a post-launch review
- `/pm stakeholder` — Map stakeholders and communication plan
- `/pm health` — Score current PM practice /80
- `/pm rescue` — Diagnose and plan for a struggling product
- `/pm compete` — Analyze competitive positioning

---

## File Structure

```
product/
├── strategy.yaml          # Product strategy brief
├── roadmap.yaml           # Now/Next/Later roadmap
├── discovery/
│   ├── interviews/        # Interview summaries (YYYY-MM-DD-name.yaml)
│   ├── synthesis.md       # Pattern analysis
│   └── validation-log.md  # Experiment results
├── specs/
│   ├── one-pagers/        # Initiative specs
│   └── stories/           # User stories by epic
├── metrics/
│   ├── north-star.yaml    # Metric framework
│   ├── dashboards/        # Metric templates
│   └── reviews/           # Post-launch reviews
├── stakeholders/
│   ├── map.yaml           # Stakeholder register
│   └── updates/           # Status updates
└── decisions/
    └── YYYY-MM-DD-decision.md  # Key product decisions with rationale
```

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI-powered business operations.*
