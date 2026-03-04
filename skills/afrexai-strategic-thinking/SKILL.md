---
name: afrexai-strategic-thinking
description: >
  Complete strategic thinking & mental models toolkit. 50+ decision frameworks
  organized by situation type — business strategy, investing, hiring, pricing,
  risk, negotiations, product, and personal life. Use when facing any important
  decision, analyzing a situation, or building a decision culture. Includes
  scoring rubrics, templates, anti-patterns, and real-world application guides.
---

# Strategic Thinking & Mental Models Engine

The comprehensive decision-making methodology for founders, operators, investors, and leaders. 50+ mental models organized by when to use them, with templates and scoring systems.

---

## Quick Start — /decide

When the user says "help me decide" or "analyze this decision":

1. Ask: **What's the decision?** (one sentence)
2. Ask: **What type?** (business / investment / hiring / product / personal / technical)
3. Ask: **Reversibility?** (easy to undo / hard to undo / permanent)
4. Ask: **Time pressure?** (minutes / days / weeks / no deadline)
5. Select the right framework(s) from the catalog below
6. Walk through step-by-step
7. Score using the Decision Quality Rubric (Phase 10)
8. Output a Decision Record (Phase 11)

---

## /8 — Quick Decision Health Check

Score the current decision process (1-5 each):

| Dimension | Score | Signal |
|-----------|-------|--------|
| Problem clarity | _ /5 | Can you state the decision in one sentence? |
| Options explored | _ /5 | Have you considered 3+ alternatives including "do nothing"? |
| Evidence quality | _ /5 | Data-backed or gut feeling? |
| Bias awareness | _ /5 | Have you actively looked for disconfirming evidence? |
| Reversibility mapped | _ /5 | Do you know the cost of being wrong? |
| Stakeholders consulted | _ /5 | Has anyone challenged this? |
| Second-order effects | _ /5 | What happens AFTER this decision plays out? |
| Time-appropriateness | _ /5 | Are you spending the right amount of time on this? |

**≥32:** Strong process — proceed with confidence
**24-31:** Decent — address weak dimensions before committing
**16-23:** Gaps — slow down and fill them
**≤15:** Stop — you're about to wing a consequential decision

---

## Phase 1: Decision Classification

Not all decisions deserve the same process. Classify first.

### Type 1 vs Type 2 (Bezos Framework)

| | Type 1 (One-Way Door) | Type 2 (Two-Way Door) |
|---|---|---|
| **Reversibility** | Irreversible or very costly to reverse | Easily reversible |
| **Process** | Full analysis, multiple perspectives, sleep on it | Decide fast, iterate, don't overthink |
| **Who decides** | Senior person or group | Individual closest to the information |
| **Time budget** | Hours to weeks | Minutes to hours |
| **Examples** | Acquisition, firing someone, pricing model, market entry | Feature priority, tool selection, meeting format, hiring channel |

**The #1 mistake:** Treating Type 2 decisions like Type 1. This creates organizational paralysis. Speed on Type 2 decisions is a competitive advantage.

### Consequence Mapping

Before choosing a framework, map consequences:

```yaml
decision: "[What you're deciding]"
type: 1 | 2
reversibility_cost: "$X / Y hours / Z reputation damage"
upside_if_right: "[Best realistic outcome]"
downside_if_wrong: "[Worst realistic outcome]"
time_to_know: "[When will you know if this was right?]"
asymmetry: "positive | negative | symmetric"
# positive = upside >> downside (bet freely)
# negative = downside >> upside (be cautious)
# symmetric = roughly equal (use expected value)
```

---

## Phase 2: First Principles Thinking

Before reaching for frameworks, strip the problem to fundamentals.

### The 5 Whys (Root Cause)

Don't solve symptoms. Ask "Why?" five times:

1. **Why** are we losing customers? → They churn after month 3.
2. **Why** month 3? → That's when the free premium features expire.
3. **Why** do they leave when features expire? → They haven't built habits around core features.
4. **Why** haven't they built habits? → Onboarding doesn't guide them to sticky features.
5. **Why** doesn't onboarding cover this? → It focuses on setup, not value realization.

**Root cause:** Onboarding design, not pricing or product gaps.

### Inversion (Jacobi Method)

Instead of "How do I succeed?", ask "How would I guarantee failure?"

Template:
```
Goal: [What you want to achieve]

How to guarantee failure:
1. [Anti-pattern 1]
2. [Anti-pattern 2]
3. [Anti-pattern 3]
4. [Anti-pattern 4]
5. [Anti-pattern 5]

Therefore, avoid:
1. [Inverted actionable rule]
2. [Inverted actionable rule]
3. [Inverted actionable rule]
```

### Regret Minimization (Bezos)

For life-altering Type 1 decisions:

> "Project yourself to age 80. Which choice minimizes regret?"

Use when:
- Career changes (leave job to start company?)
- Major financial commitments
- Relationship decisions
- The analytical frameworks feel inadequate because values are at stake

---

## Phase 3: The Core Mental Models Catalog

### 3.1 — Strategy & Business

#### Porter's Five Forces (Industry Attractiveness)

Score each 1-5 (1 = favorable, 5 = threatening):

| Force | Score | Evidence |
|-------|-------|----------|
| Threat of new entrants | _ /5 | Barriers to entry? Capital requirements? Network effects? |
| Supplier power | _ /5 | Few suppliers? Switching costs? Unique inputs? |
| Buyer power | _ /5 | Few buyers? Price sensitive? Easy to switch? |
| Threat of substitutes | _ /5 | Alternative solutions? Different categories solving same job? |
| Competitive rivalry | _ /5 | Many competitors? Slow growth? High fixed costs? |
| **Industry Score** | _ /25 | ≤10 = attractive, 11-17 = moderate, ≥18 = difficult |

#### Moat Assessment (Competitive Advantage)

Score each dimension 0-10:

| Moat Type | Score | Evidence | Durability (years) |
|-----------|-------|----------|---------------------|
| Network effects | _ /10 | Each user makes product more valuable for others? |  |
| Switching costs | _ /10 | Pain of leaving? Data lock-in? Learning curve? |  |
| Brand | _ /10 | Premium pricing power? Trust? Recognition? |  |
| Scale economies | _ /10 | Cost advantages that grow with size? |  |
| Proprietary tech/data | _ /10 | Patents? Unique datasets? Trade secrets? |  |
| Regulatory | _ /10 | Licenses? Compliance barriers? Government relationships? |  |
| Distribution | _ /10 | Exclusive channels? Embedded in workflows? |  |
| Counter-positioning | _ /10 | Incumbent can't copy without hurting their core business? |  |
| **Total Moat** | _ /80 | ≥50 = fortress, 30-49 = solid, 15-29 = narrow, <15 = no moat |

#### OODA Loop (Speed Advantage)

For competitive situations where speed matters:

1. **Observe:** What's happening? Raw data, signals, changes.
2. **Orient:** What does it mean? Context, mental models, cultural factors.
3. **Decide:** What will we do? Select action from options.
4. **Act:** Execute. Then observe again.

**Key insight:** The winner isn't who has the best strategy — it's who cycles through OODA faster. If you can observe and orient faster than competitors, you'll always be inside their decision loop.

#### Wardley Mapping (Strategic Positioning)

Map components by:
- **Y-axis:** Visibility to user (top = visible, bottom = invisible)
- **X-axis:** Evolution stage: Genesis → Custom → Product → Commodity

Rules:
- Build what's in Genesis/Custom (your differentiation)
- Buy what's in Product/Commodity (don't reinvent wheels)
- Watch for components about to shift stages (opportunity/threat)

### 3.2 — Investment & Financial

#### Expected Value Calculation

For any bet or investment:

```
EV = (Probability of Win × Win Amount) - (Probability of Loss × Loss Amount)

Example:
- 30% chance of winning $100,000
- 70% chance of losing $20,000
- EV = (0.30 × $100,000) - (0.70 × $20,000) = $30,000 - $14,000 = +$16,000

Decision: Positive EV → take the bet (if you can afford the loss)
```

**Kelly Criterion** (optimal bet sizing):
```
Kelly % = (bp - q) / b
Where:
  b = odds received (win/loss ratio)
  p = probability of winning
  q = probability of losing (1 - p)

Example: 60% win rate, 2:1 payout
Kelly = (2 × 0.6 - 0.4) / 2 = 0.4 = 40%
Half-Kelly (safer): 20% of bankroll
```

**Rule:** Never bet full Kelly. Half-Kelly or quarter-Kelly in practice.

#### Margin of Safety (Graham/Buffett)

```yaml
intrinsic_value: "$X (your best estimate)"
current_price: "$Y"
margin_of_safety: "(X - Y) / X × 100%"
# ≥30% for stable businesses
# ≥50% for uncertain/cyclical
# ≥70% for speculative/turnarounds
```

**Application beyond investing:**
- Hiring: Can this person do 30% more than the role requires?
- Timelines: Add 50% buffer to estimates
- Revenue projections: Plan for 70% of optimistic scenario
- Server capacity: Provision 2x expected peak

#### Asymmetric Risk/Reward

The best decisions have **capped downside and uncapped upside:**

| Bet Type | Downside | Upside | Action |
|----------|----------|--------|--------|
| Asymmetric positive | Small, known loss | Large, open-ended gain | **Take aggressively** |
| Symmetric | Equal loss and gain | Equal loss and gain | Take only if +EV |
| Asymmetric negative | Large, open-ended loss | Small, known gain | **Avoid or hedge** |

**Examples of asymmetric positive bets:**
- Angel investing ($5K loss max, 100x upside possible)
- Content creation (time investment, infinite distribution upside)
- Learning a skill (months invested, decades of returns)
- Cold outreach (rejection cost = 0, deal value = $$$)

### 3.3 — Product & Prioritization

#### ICE Scoring (Quick Prioritization)

| Initiative | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Score |
|-----------|---------------|-------------------|-------------|-----------|
| Feature A | 8 | 7 | 5 | 280 |
| Feature B | 6 | 9 | 8 | 432 |
| Feature C | 9 | 4 | 3 | 108 |

**Score = Impact × Confidence × Ease**

**Calibration:**
- Impact: Revenue, retention, or growth effect
- Confidence: How sure are you about Impact? (data-backed = 8+, gut = 3-5)
- Ease: 10 = hours, 7 = days, 4 = weeks, 1 = months

#### Jobs To Be Done (JTBD)

Template:
```
When [situation/trigger],
I want to [motivation/job],
So I can [expected outcome].

Functional job: [What they're literally trying to do]
Emotional job: [How they want to feel]
Social job: [How they want to be perceived]
```

**Insight:** People don't buy products. They hire them to make progress. Understand the job, and the product/feature decisions become obvious.

#### Eisenhower Matrix (Time/Priority)

| | Urgent | Not Urgent |
|---|---|---|
| **Important** | DO (crises, deadlines) | SCHEDULE (strategy, relationships, health) |
| **Not Important** | DELEGATE (interruptions, some emails) | ELIMINATE (busywork, most meetings) |

**Key insight:** Most people spend 80% of time in Urgent (both quadrants). Winners spend 80% in Important/Not Urgent (Q2) — that's where compounding happens.

### 3.4 — Risk & Uncertainty

#### Pre-Mortem (Klein)

Before committing to a plan:

> "Imagine it's 6 months from now. This decision was a disaster. What went wrong?"

Template:
```yaml
decision: "[What we're about to do]"
pre_mortem_failures:
  - failure: "[What went wrong]"
    probability: "high | medium | low"
    severity: "catastrophic | major | minor"
    prevention: "[What we'll do to prevent this]"
    detection: "[How we'll know early if this is happening]"
```

Run with 3+ people independently, then combine. The exercise works because it gives permission to voice concerns that "positive thinking" culture suppresses.

#### Scenario Planning (Shell Method)

Don't predict the future. Prepare for multiple futures.

```yaml
scenarios:
  optimistic:
    name: "[Descriptive name]"
    assumptions: ["[Key assumption 1]", "[Key assumption 2]"]
    probability: "X%"
    our_response: "[Strategy if this happens]"
    leading_indicators: ["[Signal 1]", "[Signal 2]"]

  base_case:
    name: "[Descriptive name]"
    assumptions: ["[Key assumption 1]", "[Key assumption 2]"]
    probability: "X%"
    our_response: "[Strategy if this happens]"
    leading_indicators: ["[Signal 1]", "[Signal 2]"]

  pessimistic:
    name: "[Descriptive name]"
    assumptions: ["[Key assumption 1]", "[Key assumption 2]"]
    probability: "X%"
    our_response: "[Strategy if this happens]"
    leading_indicators: ["[Signal 1]", "[Signal 2]"]

  black_swan:
    name: "[Descriptive name]"
    assumptions: ["[Unlikely but catastrophic event]"]
    probability: "<5%"
    our_response: "[Survival plan]"
    hedges: ["[Protection 1]", "[Protection 2]"]
```

**Rule:** If your plan only works in one scenario, it's not a plan — it's a prayer.

#### Antifragility Assessment (Taleb)

Score your system/business/portfolio:

| Dimension | Fragile (-2 to 0) | Robust (0) | Antifragile (0 to +2) |
|-----------|-------------------|------------|----------------------|
| Revenue concentration | 1 client = 80% revenue | Diversified, equal | Gets stronger with market chaos |
| Operational dependencies | Single point of failure | Redundant | Failures trigger improvements |
| Financial structure | Leveraged, thin margins | Cash reserves, no debt | Optionality, cash to deploy in downturns |
| Knowledge/IP | Key-person dependent | Documented, distributed | Learning system that compounds |
| Market position | Commodity, price-taker | Differentiated | Benefits from competitor mistakes |

**Total: ≥4 = antifragile, 0 = robust, ≤-4 = fragile (fix immediately)**

### 3.5 — People & Organizational

#### Circle of Competence (Munger)

Before any decision in a domain:

```
Domain: [Area of decision]

Inside my circle:
- [What I genuinely understand from experience]
- [Where I have real data and pattern recognition]
- [Decisions I've made successfully before in this space]

Edge of my circle:
- [What I know I don't know]
- [Where I'd need expert input]

Outside my circle:
- [What I'm completely unfamiliar with]
- [Where I'd be guessing]

Decision: Am I inside my circle for THIS specific decision?
If no → find someone who is, or do the homework first.
```

#### Hanlon's Razor + Steel Man

Before reacting to someone's behavior or proposal:

1. **Hanlon's Razor:** "Never attribute to malice what is adequately explained by incompetence" (or ignorance, busy-ness, different priorities)
2. **Steel Man:** Before arguing against a position, articulate the STRONGEST version of it. If you can't steel-man it, you don't understand it enough to disagree.

#### Second-Order Thinking

Every decision has consequences (1st order). Those consequences have consequences (2nd order).

Template:
```
Decision: [What we're doing]

1st order effects (immediate):
- [Direct result 1]
- [Direct result 2]

2nd order effects (weeks/months later):
- [Consequence of result 1] → [Further consequence]
- [Consequence of result 2] → [Further consequence]

3rd order effects (months/years later):
- [Systemic change 1]
- [Systemic change 2]

Counter-intuitive insight: [What becomes clear only at 2nd/3rd order]
```

**Classic examples:**
- Lowering prices (1st: more customers → 2nd: competitors match → 3rd: margin compression industry-wide)
- Remote work (1st: flexibility → 2nd: global talent pool → 3rd: global competition for your job)
- Firing quickly (1st: team relief → 2nd: hiring bar rises → 3rd: culture of accountability)

### 3.6 — Negotiation & Persuasion

#### BATNA Analysis (Fisher/Ury)

Before any negotiation:

```yaml
my_batna: "[Best Alternative To Negotiated Agreement — what I do if we don't agree]"
my_batna_value: "$X or equivalent"
their_batna: "[Their best alternative]"
their_batna_value: "$Y or equivalent"
zopa: "[Zone Of Possible Agreement: range between our walk-away points]"
my_reservation_price: "[Minimum I'd accept]"
my_aspiration: "[What I actually want]"
their_likely_reservation: "[Best guess at their minimum]"

power_assessment: "I have more power | balanced | they have more power"
# Whoever has the better BATNA has the power
```

#### Cialdini's 6 Principles (Influence Audit)

For any persuasion situation, check which levers apply:

| Principle | Application | Your Move |
|-----------|------------|-----------|
| Reciprocity | Give first, then ask | [What value can you provide upfront?] |
| Commitment/Consistency | Get small yeses first | [What's the micro-commitment?] |
| Social proof | Others are doing it | [Who else has done this successfully?] |
| Authority | Expert endorsement | [What credentials or evidence establish authority?] |
| Liking | Build rapport first | [What genuine connection exists?] |
| Scarcity | Limited availability | [What's genuinely scarce — time, spots, pricing?] |

### 3.7 — Technical & Engineering

#### Build vs Buy Decision Matrix

| Criterion | Weight | Build | Buy |
|-----------|--------|-------|-----|
| Core differentiator? | 5 | If yes: +5 | If no: +5 |
| Time to market | 4 | Score 1-5 | Score 1-5 |
| Long-term cost (3yr) | 4 | Score 1-5 | Score 1-5 |
| Customization needed | 3 | Score 1-5 | Score 1-5 |
| Team capability | 3 | Score 1-5 | Score 1-5 |
| Maintenance burden | 3 | Score 1-5 | Score 1-5 |
| Vendor risk | 2 | N/A (0) | Score 1-5 |
| Integration complexity | 2 | Score 1-5 | Score 1-5 |

**Shortcut:** If it's your core differentiator → build. If it's commodity → buy. Everything else → this matrix.

#### Reversibility-First Architecture

Design decisions by reversibility:

| Reversibility | Examples | Approach |
|--------------|---------|----------|
| **Easy** (hours) | Feature flags, config, UI copy | Just do it. Iterate. |
| **Medium** (days-weeks) | API design, database indexes, tool choices | Light analysis, time-box to 1 day |
| **Hard** (months) | Database engine, programming language, cloud provider | Full evaluation, prototype, team input |
| **Permanent** | Public API contracts, data deletion, legal agreements | Maximum rigor, external review, sleep on it |

---

## Phase 4: Cognitive Bias Defense System

Biases are the #1 threat to decision quality. Active defense required.

| Bias | What It Does | Defense |
|------|-------------|---------|
| **Confirmation bias** | Seek info that confirms what you already believe | Assign someone to argue the opposite. Search for "why [your thesis] is wrong" |
| **Anchoring** | First number you hear dominates your estimate | Generate your own estimate BEFORE looking at anyone else's |
| **Sunk cost fallacy** | Continue because you've already invested | Ask: "If I were starting fresh today, would I begin this?" |
| **Survivorship bias** | Study winners, ignore the dead | Ask: "How many tried this and failed? What did they have in common?" |
| **Dunning-Kruger** | Overconfidence in areas of low competence | Check: Am I inside my circle of competence? |
| **Recency bias** | Overweight recent events | Look at 5-10 year base rates, not last quarter |
| **Status quo bias** | Prefer current state even when suboptimal | Evaluate "do nothing" as an active choice with its own costs |
| **Groupthink** | Agree with the room to avoid conflict | Write opinions independently BEFORE discussing. Use anonymous voting. |
| **Availability heuristic** | Judge probability by how easily examples come to mind | Check actual data. Plane crashes feel common because they're memorable. |
| **Loss aversion** | Feel losses 2x more than equivalent gains | Reframe: "What do I gain by NOT doing this?" |
| **Narrative fallacy** | Construct stories to explain random events | Ask: "Is this a pattern or am I connecting random dots?" |
| **Planning fallacy** | Underestimate time/cost for tasks | Use reference class forecasting: how long did SIMILAR projects take others? |

### Daily Bias Checklist (Before Major Decisions)

- [ ] Have I actively sought disconfirming evidence?
- [ ] Am I anchored to someone else's number/frame?
- [ ] Am I continuing because of sunk costs?
- [ ] Would I make this same choice starting from zero?
- [ ] Have I considered the base rate, not just my situation?
- [ ] Has someone challenged this decision?

---

## Phase 5: Decision-Making Under Uncertainty

### Confidence Calibration

Before acting on any estimate:

| Your Confidence | What It Should Mean | Calibration Test |
|----------------|-------------------|-----------------|
| 50% | Coin flip — could go either way | Would you bet your own money at even odds? |
| 70% | More likely than not, but real chance of being wrong | Would you bet 2:1? |
| 90% | Very confident, would be surprised if wrong | Would you bet 9:1? |
| 95% | Extremely confident | Would you bet 19:1? |
| 99% | Near certain | Have you been wrong at "99% confidence" before? (You have.) |

**Rule:** Most people are overconfident. If you think you're 90% sure, you're probably 70% sure. Adjust down.

### Information Value Assessment

Before spending time/money gathering more data:

```
Decision to make: [X]
Current best guess: [Y]
Current confidence: [Z%]

If I gather [this information]:
- Cost: [$X / Y hours]
- Would it change my decision? [yes / maybe / probably not]
- By how much would confidence increase? [+5% / +15% / +30%]

Value of information = (confidence gain × decision stakes) - gathering cost
```

**Rule:** Don't research a $1,000 decision for 40 hours. Match effort to stakes.

### When to Decide (Timing Framework)

| Situation | Optimal Decision Time | Why |
|-----------|----------------------|-----|
| Information depreciates quickly | Immediately (minutes) | Waiting destroys the option |
| Easy to reverse | Quickly (hours) | Cost of being wrong < cost of delay |
| Moderate stakes, some data | 70% information rule | At 70% confidence, decide. Waiting for 95% means you're too late. |
| High stakes, irreversible | Take available time (days-weeks) | Use it all. Sleep on it. Get perspectives. |
| Emotional decision | Wait minimum 24 hours | Emotions are data, not directives. Let them settle. |

---

## Phase 6: Group Decision-Making

### Structured Disagreement Protocol

For team/partner decisions where people disagree:

1. **Independent write-up:** Each person writes their recommendation and reasoning (5 min, no discussion)
2. **Share simultaneously:** Everyone reveals at once (prevents anchoring)
3. **Steel man opposition:** Each person must articulate the best version of the opposing view
4. **Identify cruxes:** What's the ONE factual question where if resolved, you'd change your mind?
5. **Resolve or decide:** If crux is resolvable → get the data. If not → whoever has the best BATNA decides, or the person closest to the information decides.

### RACI for Decisions

| Role | Definition | Rule |
|------|-----------|------|
| **R** — Responsible | Does the analysis, prepares recommendation | Max 2 people |
| **A** — Accountable | Makes the final call | **Exactly 1 person** |
| **C** — Consulted | Provides input before decision | Keep small (3-5) |
| **I** — Informed | Told after decision is made | Everyone affected |

**Common failure:** No clear A. If two people think they're the decider, no decision gets made.

---

## Phase 7: Compounding & Systems Thinking

### Compounding Mental Model

Most people think linearly. Compounding is the most powerful force:

```
Linear: 1 + 1 + 1 + 1 = 4 (after 4 periods)
Compounding: 1 × 1.1 × 1.1 × 1.1 × 1.1 = 1.46 (after 4 periods)

But after 50 periods:
Linear: 50
Compounding: 117.39

Rule of 72: Years to double = 72 / growth rate%
- 10% growth → doubles in 7.2 years
- 20% growth → doubles in 3.6 years
- 1% daily improvement → 37x in one year
```

**Application:** Every decision should be evaluated for its compounding potential. A decision that creates a 1% improvement to a daily process is worth more than a one-time 50% improvement to an annual process.

### Leverage Points (Meadows)

Where to intervene in a system, ranked by effectiveness:

1. **Paradigms** (most powerful) — Change the mindset/goals of the system
2. **Goals** — What the system is optimizing for
3. **Rules** — Incentives, constraints, punishments
4. **Information flows** — Who knows what, when
5. **Feedback loops** — Speed and accuracy of response
6. **Structure** — How components connect
7. **Parameters** (least powerful) — Numbers, budgets, quotas

**Insight:** Most people intervene at #7 (adjust the budget). The highest-leverage interventions are at #1-3 (change what we're optimizing for).

---

## Phase 8: Personal Decision-Making

### The Energy Audit

Not all decisions need the same energy:

```yaml
high_energy_decisions: # Use frameworks, sleep on it
  - Career changes
  - Major financial commitments (>10% of net worth)
  - Hiring/firing
  - Market entry/exit
  - Relationship commitments

medium_energy_decisions: # 30-min analysis, then decide
  - Quarterly priorities
  - Tool/vendor selection
  - Pricing adjustments
  - Content strategy

low_energy_decisions: # Decide in <5 min or automate
  - What to eat, wear, read
  - Meeting attendance
  - Social media responses
  - Routine purchases

rule: "Match decision energy to decision stakes. Most people overthink low-energy decisions and underthink high-energy ones."
```

### Default Rules (Eliminate Decision Fatigue)

Create personal defaults so you don't waste energy:

```yaml
defaults:
  new_meeting_request: "Default NO unless clearly advances top 3 priorities"
  price_negotiation: "Never discount more than 15% — offer value instead"
  new_project: "Default NO unless it replaces something on current list"
  email_response: "Batch 2x/day. Respond in ≤3 sentences or schedule a call"
  investment: "Default index fund. Active only with genuine edge + margin of safety"
  delegation: "If someone can do it 80% as well, delegate"
  saying_yes: "If it's not a HELL YES, it's a no"
```

---

## Phase 9: Decision Frameworks by Situation

Quick reference — which framework for which situation:

| Situation | Primary Framework | Supporting Model |
|-----------|------------------|-----------------|
| Should we enter this market? | Porter's Five Forces + Moat Assessment | Scenario Planning |
| Should I take this job/opportunity? | Regret Minimization + Circle of Competence | Asymmetric Risk |
| Which feature to build next? | ICE Scoring + JTBD | 2nd Order Thinking |
| Should we invest/bet on X? | Expected Value + Margin of Safety | Pre-Mortem |
| How to price our product? | *See afrexai-pricing-strategy* | Competitive Positioning |
| Hiring decision? | *See afrexai-interview-architect* | Circle of Competence |
| How to negotiate this deal? | BATNA + Cialdini | *See afrexai-negotiation-mastery* |
| Build or buy this component? | Build vs Buy Matrix | Reversibility Assessment |
| Team disagrees on direction | Structured Disagreement Protocol | Pre-Mortem |
| I'm overwhelmed with options | Eisenhower Matrix + Default Rules | Energy Audit |
| Business feels fragile | Antifragility Assessment | Scenario Planning |
| Competitor making moves | OODA Loop + *See afrexai-competitive-intel* | Wardley Mapping |
| Something failed, now what? | 5 Whys + Inversion | Sunk Cost check |
| Big life decision | Regret Minimization + Second-Order | Sleep on it (24h rule) |

---

## Phase 10: Decision Quality Rubric

Score any decision AFTER making it (or retrospectively):

| Dimension | Weight | Score (0-10) | Weighted |
|-----------|--------|-------------|----------|
| Problem definition clarity | 15% | _ | _ |
| Options explored (≥3, incl. "do nothing") | 15% | _ | _ |
| Evidence quality (data vs. gut) | 15% | _ | _ |
| Bias mitigation (actively countered?) | 15% | _ | _ |
| Stakeholder input (right people consulted?) | 10% | _ | _ |
| Second-order effects considered | 10% | _ | _ |
| Reversibility & downside mapped | 10% | _ | _ |
| Time-appropriate process | 10% | _ | _ |
| **Total** | 100% | | _ /100 |

**≥80:** Excellent process — outcome is in fortune's hands, not yours
**60-79:** Good — minor gaps but fundamentally sound
**40-59:** Mediocre — important dimensions skipped
**≤39:** Poor — outcome is a coin flip regardless of luck

**Critical insight:** Judge decisions by PROCESS quality, not outcomes. A good process can produce bad outcomes (variance). A bad process that produces good outcomes is dangerous — it teaches bad habits.

---

## Phase 11: Decision Record Template

Document every significant decision:

```yaml
decision_record:
  id: "DR-[YYYY-MM-DD]-[number]"
  date: "YYYY-MM-DD"
  decision: "[One sentence — what we decided]"
  type: "1 | 2"
  context: "[Why this decision was needed now]"
  options_considered:
    - option: "[Option A]"
      pros: ["...", "..."]
      cons: ["...", "..."]
    - option: "[Option B]"
      pros: ["...", "..."]
      cons: ["...", "..."]
    - option: "Do nothing"
      pros: ["...", "..."]
      cons: ["...", "..."]
  decision_rationale: "[Why we chose this option]"
  frameworks_used: ["[Framework 1]", "[Framework 2]"]
  key_assumptions: ["[Assumption 1]", "[Assumption 2]"]
  risks_accepted: ["[Risk 1]", "[Risk 2]"]
  success_criteria: "[How we'll know this was right]"
  review_date: "YYYY-MM-DD (when to evaluate)"
  quality_score: "X/100 (Phase 10 rubric)"
  decided_by: "[Name]"
  consulted: ["[Name 1]", "[Name 2]"]
  
  # Fill in at review_date:
  outcome: "[What actually happened]"
  lessons: "[What we learned]"
  would_decide_differently: "yes | no"
  why: "[If yes, what would we change about the PROCESS?]"
```

---

## Phase 12: Advanced Patterns

### Barbell Strategy (Taleb)

Combine extreme safety with extreme risk. Avoid the middle.

```
Portfolio: 85-90% ultra-safe (treasuries, cash, index) + 10-15% high-risk/high-reward (startups, crypto, moonshots)
Time: 80% predictable deep work + 20% wild exploration/experimentation
Products: Cash cow product (boring, reliable) + speculative bets (innovative, might fail)
Career: Stable income source + asymmetric side projects
```

**Why no middle:** The "medium risk" zone gives you medium returns with hidden tail risk. Better to KNOW you're safe on one side and gambling on the other.

### Lindy Effect

The longer something has survived, the longer it will likely survive.

**Applications:**
- Books: A 100-year-old book is more likely relevant in 10 years than a 1-year-old book
- Technologies: SQL (50 years) will outlast this year's hot framework
- Business models: Subscription model (centuries old as concept) > novel monetization
- Advice: Wisdom from 2,000 years ago (Stoics, Sun Tzu) > last week's Twitter thread

### Via Negativa (Subtract, Don't Add)

Often the best decision is what to REMOVE, not what to add:

- Remove a feature (focus)
- Remove a meeting (time)
- Remove a client (sanity, team morale)
- Remove a goal (clarity)
- Remove a bad habit (energy)
- Remove complexity (reliability)

**Template:** "What's the ONE thing I could eliminate that would improve everything else?"

### Opportunity Cost Consciousness

Every yes is a no to something else:

```
If I do X:
- Direct benefit: [value gained]
- Time cost: [hours/days/weeks]
- Best alternative use of that time: [what I'm saying no to]
- Opportunity cost: [value of best alternative forgone]

Net value = Direct benefit - Opportunity cost
```

**If net value is negative, you're destroying value by saying yes — even though it "feels productive."**

---

## 10 Decision-Making Commandments

1. **Classify before analyzing.** Type 1 or Type 2? Match process to stakes.
2. **"Do nothing" is always an option.** Evaluate it explicitly.
3. **Seek disconfirming evidence.** The moment you like an idea, hunt for why it's wrong.
4. **Separate process from outcome.** Good process, bad outcome = fine. Bad process, good outcome = lucky.
5. **Time-box decisions.** Set a deadline. Perfectionism is a form of procrastination.
6. **Write it down.** Unwritten decisions can't be reviewed, learned from, or challenged.
7. **One decider.** Every decision needs exactly one person who makes the final call.
8. **Sleep on Type 1 decisions.** Your brain processes during sleep. Use it.
9. **Review decisions.** Quarterly, look at your decision records. What patterns emerge?
10. **Compound decision quality.** Each good decision process makes the next one better. This is the real edge.

---

## 10 Common Decision Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Deciding too slowly on Type 2 decisions | Set a timer. If reversible, decide now. |
| 2 | Never writing down assumptions | Every decision has assumptions. Write them. Test them. |
| 3 | Asking for consensus instead of input | Consensus = lowest common denominator. Get input, then one person decides. |
| 4 | Optimizing for one variable | Life is multi-variable. Use weighted scoring. |
| 5 | Ignoring opportunity cost | "This is good" isn't enough. "This is better than alternatives" is the bar. |
| 6 | Deciding when emotional | 24-hour rule for anything you'd regret. |
| 7 | Copying without context | "Amazon does X" means nothing if you're not Amazon. Understand WHY they do X. |
| 8 | Analysis paralysis on small decisions | Automate (defaults) or delegate anything under $500/2 hours. |
| 9 | Never reviewing past decisions | Same mistakes on repeat. Quarterly decision reviews = compounding improvement. |
| 10 | Conflating confidence with competence | Loud ≠ right. Data ≠ understanding. Check circle of competence. |

---

## Natural Language Commands

- **"Help me decide [X]"** → Full decision walkthrough (Quick Start)
- **"Score this decision"** → Decision Quality Rubric (Phase 10)
- **"Pre-mortem [plan]"** → Pre-mortem exercise (Phase 4)
- **"Is this inside my circle?"** → Circle of Competence check
- **"Bias check"** → Daily Bias Checklist
- **"Expected value of [bet]"** → EV calculation
- **"Map the second-order effects"** → Second-order thinking template
- **"BATNA analysis for [negotiation]"** → Full BATNA template
- **"Rate this market"** → Porter's Five Forces scoring
- **"How strong is the moat?"** → Moat Assessment
- **"Which framework should I use?"** → Phase 9 situation lookup
- **"Write a decision record"** → DR template (Phase 11)
