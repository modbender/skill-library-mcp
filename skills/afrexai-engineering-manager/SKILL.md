---
name: Engineering Manager OS
description: Complete engineering management system — team building, 1:1s, performance, hiring, architecture decisions, incident management, and scaling. From IC-to-manager transition through director-level operations.
metadata: {"clawdbot":{"emoji":"⚙️","os":["linux","darwin","win32"]}}
---

# Engineering Manager Operating System

Your complete playbook for engineering leadership. Not generic management advice — this is the specific system that high-performing engineering managers run daily.

---

## Phase 1: Team Architecture

### Team Topology Assessment

Before managing people, understand the system they work in.

```yaml
team_topology:
  name: "[Team Name]"
  type: stream-aligned | platform | enabling | complicated-subsystem
  mission: "[One sentence — what does this team exist to do?]"
  boundaries:
    owns: ["service-x", "domain-y", "pipeline-z"]
    consumes: ["auth-service", "data-platform"]
    provides: ["checkout-api", "payment-events"]
  cognitive_load: low | medium | high | overloaded
  interaction_modes:
    - team: "[Other Team]"
      mode: collaboration | x-as-a-service | facilitating
      friction: low | medium | high
      notes: "[What's working/not working]"
  current_headcount: N
  ideal_headcount: N
  skill_gaps: ["observability", "mobile", "ML"]
```

### Team Health Radar (Monthly)

Score 1-5 for each dimension. Track trends over time.

| Dimension | Score | Signal |
|-----------|-------|--------|
| **Delivery pace** | _ /5 | Are we shipping what we committed? |
| **Quality** | _ /5 | Bug rate, incident frequency, tech debt trajectory |
| **Collaboration** | _ /5 | Cross-functional work, PR review speed, knowledge sharing |
| **Morale** | _ /5 | Energy in meetings, voluntary contributions, retention signals |
| **Learning** | _ /5 | New skills adopted, conference talks, internal tech talks |
| **Autonomy** | _ /5 | Can the team make decisions without waiting for me? |
| **Psychological safety** | _ /5 | Do people raise concerns, admit mistakes, challenge ideas? |
| **On-call health** | _ /5 | Page frequency, off-hours burden, burnout signals |

**Action rules:**
- Any dimension ≤2 → Address THIS WEEK (it's a fire)
- Any dimension at 3 → Create improvement plan within 2 weeks
- Overall average <3.5 → Team is struggling, block new commitments until fixed
- Track quarter-over-quarter — sustained decline in any dimension = systemic issue

### Team Composition Model

The ideal team has these roles covered (not necessarily 1:1 with people):

| Role | Description | Gap Impact |
|------|-------------|------------|
| **Tech lead** | Architecture decisions, code quality bar | Decisions bottleneck through you |
| **Senior IC** (2-3) | Carry complex work, mentor juniors | Velocity drops, quality suffers |
| **Mid-level** (2-3) | Reliable delivery, growing scope | No bench for senior pipeline |
| **Junior** (0-2) | Learning, fresh perspective | No talent pipeline |
| **Domain expert** | Deep knowledge of the problem space | Constantly solving wrong problems |

**Rule of thumb:** Never have >60% of team at same level. Mix creates natural mentorship.

---

## Phase 2: 1:1 System

### 1:1 Cadence

| Report Level | Frequency | Duration | Focus |
|-------------|-----------|----------|-------|
| Direct reports | Weekly | 30 min | Career + blockers + feedback |
| Skip-levels | Monthly | 30 min | Team health + career + honesty check |
| Your manager | Weekly | 30 min | Priorities + asks + air cover |
| Cross-functional peers | Bi-weekly | 25 min | Dependencies + alignment |

### 1:1 Template (Direct Reports)

```yaml
one_on_one:
  date: "YYYY-MM-DD"
  person: "[Name]"
  role: "[Title]"
  tenure: "[X months on team]"
  
  # Their agenda first — ALWAYS
  their_topics: []
  
  # Check-in (2 min)
  energy_level: 1-10  # "How are you feeling about work this week?"
  energy_trend: up | stable | down
  
  # Delivery (5 min)
  current_work: "[What they're working on]"
  blockers: []
  help_needed: "[What can I unblock?]"
  
  # Growth (10 min — skip if urgent topics dominate, but never 3 weeks in a row)
  career_conversation: "[Topic discussed]"
  feedback_given: "[Specific behavior → impact → request]"
  feedback_received: "[What they told me]"
  stretch_opportunity: "[Current or upcoming]"
  
  # Action items
  my_actions: []  # What I committed to do
  their_actions: []  # What they committed to do
  
  # Signals (private — don't share these)
  flight_risk: low | medium | high
  performance_trajectory: improving | stable | declining
  notes: "[Anything notable]"
```

### 1:1 Question Bank

**Opening (rotate these — never use the same opener 3 weeks in a row):**
- "What's on your mind?"
- "What was the best/worst part of your week?"
- "If you could change one thing about how we work, what would it be?"
- "What's something you're proud of from this week that I might not know about?"
- "On a scale of 1-10, how's your energy? What would move it up one point?"

**Career development (monthly deep-dive):**
- "Where do you want to be in 2 years? What's the gap between here and there?"
- "What skills are you not using that you'd like to use more?"
- "Who in the org (or industry) has a role you'd want? What specifically about it?"
- "What's the hardest technical problem you've solved recently? What did you learn?"
- "If you left tomorrow, what would you regret not doing here?"

**Team health (probe with care):**
- "Who on the team do you learn the most from? The least?"
- "Is there anyone whose work you don't trust to review?"
- "What's something the team avoids talking about?"
- "If you were me, what would you change about how this team operates?"

**Feedback solicitation (for YOU):**
- "What's one thing I could do differently that would help you most?"
- "Am I giving you too much direction or too little?"
- "Is there context I have that I'm not sharing that would help you?"
- "When was the last time I frustrated you? What happened?"

### Flight Risk Detection

Monitor these signals — if 3+ present, have a retention conversation within a week:

| Signal | Weight | Detection |
|--------|--------|-----------|
| LinkedIn profile update | 🔴 High | Someone mentions it, or you notice |
| Declining 1:1 engagement | 🔴 High | Shorter answers, less eye contact, "everything's fine" |
| Stopped volunteering for projects | 🟡 Medium | Used to raise hand, now doesn't |
| Increased PTO without travel | 🟡 Medium | Interviewing signal |
| Disengaged in meetings | 🟡 Medium | Camera off, multitasking, no opinions |
| Complaining shifted from specific to general | 🟡 Medium | "This sprint is rough" → "This place..." |
| Stopped arguing for their ideas | 🔴 High | They've mentally checked out |
| Life event (new baby, move, partner change) | 🟡 Medium | Re-evaluating everything |

**Retention conversation framework:**
1. Name it: "I've noticed [specific behavior change]. I want to check in."
2. Listen: Let them talk. Don't interrupt. Don't get defensive.
3. Understand: "What would make this the best job you've ever had?"
4. Act: Make a concrete commitment within 48 hours — title, comp, scope, flexibility
5. Follow up: Check back in 1 week. Did what you promised make a difference?

---

## Phase 3: Performance Management

### Performance Calibration Framework

Rate on two axes (both matter):

**Delivery Impact (What)**
| Level | Description |
|-------|-------------|
| 1 - Below | Missing commitments, quality issues, needs close oversight |
| 2 - Meeting | Delivering assigned work reliably |
| 3 - Exceeding | Delivering beyond scope, finding better solutions |
| 4 - Outstanding | Multiplying team output, solving problems no one asked them to |

**Behaviors (How)**
| Level | Description |
|-------|-------------|
| 1 - Below | Creating friction, not collaborating, ignoring feedback |
| 2 - Meeting | Professional, collaborative, receptive to feedback |
| 3 - Exceeding | Mentoring others, proactively improving processes |
| 4 - Outstanding | Shaping culture, attracting talent, raising the entire bar |

**Calibration matrix:**

| | Behavior 1 | Behavior 2 | Behavior 3 | Behavior 4 |
|---|---|---|---|---|
| **Delivery 4** | Coach behaviors | Strong | Top performer | Superstar |
| **Delivery 3** | Coach behaviors | Solid | Strong | Top performer |
| **Delivery 2** | PIP candidate | Meets expectations | Developing | Growing |
| **Delivery 1** | Exit | PIP | Coach delivery | Coach delivery |

### Feedback Framework: SBI-I (Situation-Behavior-Impact-Intent)

**Template:**
"In [situation], when you [specific behavior], the impact was [concrete effect]. I'd like to see [specific change] because [intent/why it matters]."

**Examples:**

✅ Good: "In yesterday's design review, when you challenged the API schema with the versioning concern, it caught a breaking change we would have shipped. That's exactly the kind of technical leadership I want to see more of."

❌ Bad: "You're doing great work. Keep it up." (Too vague — they learn nothing)

✅ Good: "In the last two sprints, PRs have been sitting in review for 3+ days. The impact is features are merging late and we're missing sprint commitments. I'd like us to commit to <24h first review because velocity depends on review speed."

❌ Bad: "You need to review PRs faster." (No situation, no impact, no collaboration)

### Performance Improvement Plan (PIP) Template

```yaml
pip:
  employee: "[Name]"
  role: "[Title]"
  manager: "[Your name]"
  start_date: "YYYY-MM-DD"
  end_date: "YYYY-MM-DD"  # 30-60 days, never >90
  
  context: |
    [Specific pattern of underperformance with dates and examples.
     Must reference prior feedback conversations and dates they occurred.]
  
  expectations:
    - area: "[Specific skill/behavior]"
      current_state: "[What's happening now — with examples]"
      target_state: "[What success looks like — measurable]"
      measurement: "[How we'll measure — PR metrics, sprint completion, etc.]"
      support: "[What I'll provide — pairing, training, reduced scope]"
  
  check_ins:
    frequency: weekly
    day: "[Day]"
    format: "[30 min 1:1 with written summary]"
  
  outcomes:
    success: "[What happens if targets met — return to normal performance management]"
    failure: "[What happens if targets not met — typically termination]"
  
  # CRITICAL: Have HR review before sharing. Document every check-in.
  hr_reviewed: false
  hr_reviewer: "[Name]"
```

**PIP rules:**
- A PIP should never be a surprise — if it is, YOU failed at feedback
- PIPs are for capability gaps, not attitude problems (attitude = manage out faster)
- 70% of PIPs end in termination — be honest with yourself about whether this is a development tool or a documentation exercise
- Weekly check-ins are non-negotiable — document everything in writing
- If performance improves during PIP then declines after: second PIP is rarely worth it

### Promotion Case Template

```yaml
promotion_case:
  candidate: "[Name]"
  current_level: "[Level]"
  target_level: "[Level]"
  manager: "[Your name]"
  date: "YYYY-MM-DD"
  
  # Already operating at next level (past 6+ months)
  evidence:
    - dimension: "Technical complexity"
      examples:
        - "[Specific project/decision with measurable impact]"
        - "[Another example]"
    - dimension: "Scope & ownership"
      examples:
        - "[Owned X end-to-end, previously needed guidance]"
    - dimension: "Influence & leadership"
      examples:
        - "[Mentored Y, led Z initiative, shaped team direction]"
    - dimension: "Business impact"
      examples:
        - "[Revenue/efficiency/reliability improvement with numbers]"
  
  peer_feedback:
    - from: "[Name, role]"
      quote: "[Specific praise with examples]"
  
  # Why now, not 6 months from now?
  timing_justification: |
    [They've been consistently operating at next level for X months.
     Delaying creates retention risk and sends wrong signal to team.]
  
  # What's the gap? (Be honest — calibration committees will find it)
  growth_areas: |
    [Areas they're still developing. Frame as "growing into" not "lacking."]
```

---

## Phase 4: Hiring Machine

### Hiring Pipeline

```
Role opened → Job description → Sourcing (5-7 days)
→ Resume screen → Recruiter screen (30 min)
→ Technical phone screen (60 min) → Take-home OR live coding (2-4 hrs)
→ Onsite/virtual loop (3-4 hrs) → Debrief → Offer → Close

Target: <21 days from first screen to offer
```

### Job Description Template

```markdown
# [Role Title] — [Team Name]

## What you'll do
[3-5 bullet points of ACTUAL work, not generic responsibilities]
- Ship [specific feature/system] that [specific impact]
- Own [specific domain] end-to-end
- [Concrete example of a recent problem this person would solve]

## What you'll need
[Must-haves only — each one must be a genuine filter]
- X years building [specific technology/domain]
- Experience with [specific technical requirement]
- [Skill that actually differentiates candidates]

## Nice to have (genuinely nice, not secretly required)
- [Thing that would accelerate ramp-up]
- [Adjacent skill that adds value]

## What we offer
[Be specific — "competitive salary" means nothing]
- Salary range: $X-$Y (based on [location/level])
- [Specific benefits that matter to engineers]
- [Team/culture thing that's actually true and differentiating]

## How we hire
[Timeline and what to expect — respect their time]
1. [Step]: [Duration] — [What we're assessing]
2. [Step]: [Duration] — [What we're assessing]
Total time investment: ~X hours
```

### Interview Scorecard (Per Interviewer)

```yaml
scorecard:
  candidate: "[Name]"
  interviewer: "[Name]"
  interview_type: "technical | system design | behavioral | culture"
  date: "YYYY-MM-DD"
  
  # Score each dimension 1-4 (no 3s allowed — forces a decision)
  dimensions:
    - name: "Technical depth"
      score: _  # 1=no hire, 2=lean no, 4=lean yes, 5=strong yes (skip 3)
      evidence: "[Specific examples from the interview]"
    - name: "Problem solving approach"
      score: _
      evidence: "[How they broke down the problem, handled hints]"
    - name: "Communication clarity"
      score: _
      evidence: "[Could they explain their thinking? Did they ask good questions?]"
    - name: "Collaboration signals"
      score: _
      evidence: "[How did they respond to pushback? Did they build on ideas?]"
  
  # Overall
  hire_recommendation: strong_no | no | yes | strong_yes
  level_recommendation: "[What level would you place them?]"
  concerns: "[Anything that gave you pause]"
  highlights: "[What impressed you most]"
```

### Debrief Protocol

1. **No pre-discussion** — Submit scorecards BEFORE the debrief meeting
2. **Hire bar holder speaks last** — Prevent anchoring
3. **Discuss each dimension, not overall vibes** — "Tell me about their system design approach" not "What did you think?"
4. **Any strong_no is a veto** — Unless the interviewer can be convinced their signal was a misread
5. **Decide in the room** — Don't "sleep on it" unless genuinely torn (then it's probably a no)
6. **Leveling before offer** — Agree on level first, then comp follows from band

### Closing Candidates

**The 3 things that close engineers:**
1. **The problem** — "Here's the specific hard problem you'd work on"
2. **The people** — Connect them with future teammates before offer
3. **The growth** — "Here's where this role leads in 18 months"

**Offer call structure (15-20 min):**
1. Express genuine excitement (2 min)
2. Present offer details — base, equity, bonus, start date (3 min)
3. Explain equity/comp philosophy (3 min)
4. Ask: "How does this compare to what you were expecting?" (listen)
5. Address concerns immediately if possible
6. Set a decision deadline (3-5 business days, not open-ended)
7. Ask: "Is there anything that would make this a clear yes?"

---

## Phase 5: Technical Leadership

### Architecture Decision Record (ADR)

```yaml
adr:
  id: "ADR-NNN"
  title: "[Decision title]"
  date: "YYYY-MM-DD"
  status: proposed | accepted | deprecated | superseded
  superseded_by: "ADR-NNN"  # if applicable
  
  context: |
    [What situation are we in? What forces are at play?
     Include constraints: timeline, team skill, budget, scale requirements.]
  
  options:
    - name: "[Option A]"
      pros: ["pro 1", "pro 2"]
      cons: ["con 1", "con 2"]
      effort: "[T-shirt size]"
      risk: low | medium | high
    - name: "[Option B]"
      pros: ["pro 1"]
      cons: ["con 1", "con 2", "con 3"]
      effort: "[T-shirt size]"
      risk: low | medium | high
  
  decision: |
    [What we decided and WHY. The "why" is the most important part.
     Future readers need to understand the reasoning, not just the choice.]
  
  consequences: |
    [What follows from this decision? What becomes easier/harder?
     What do we need to monitor?]
  
  review_date: "YYYY-MM-DD"  # When to revisit this decision
```

### Tech Debt Prioritization

Score each debt item on two axes:

**Impact of fixing (1-5):**
- 5: Unblocks multiple teams or critical features
- 4: Significant velocity improvement for our team
- 3: Moderate improvement, prevents future problems
- 2: Nice to have, minor improvement
- 1: Cosmetic or theoretical benefit

**Cost of NOT fixing (1-5):**
- 5: Will cause incidents or data loss
- 4: Blocking hiring/onboarding (can't explain the code)
- 3: Slowing every feature by >20%
- 2: Occasional friction, workarounds exist
- 1: Annoying but harmless

**Priority = Impact × Cost-of-not-fixing**

| Score | Action |
|-------|--------|
| 20-25 | Fix THIS sprint — it's an emergency |
| 12-19 | Schedule within 2 sprints |
| 6-11 | Add to quarterly tech debt budget (allocate 15-20% of sprint capacity) |
| 1-5 | Backlog — revisit quarterly |

### Code Review Culture Guidelines

```yaml
code_review_standards:
  sla:
    first_review: "< 4 hours during work hours"
    follow_up: "< 2 hours"
    max_pr_size: 400  # lines changed — larger needs pre-review or splitting
  
  what_to_review:
    always:
      - "Correctness — does it do what it claims?"
      - "Edge cases — what happens with nil/empty/max/concurrent?"
      - "Security — auth checks, input validation, secrets exposure"
      - "Naming — will someone understand this in 6 months?"
    sometimes:
      - "Performance — only if in hot path or O(n²)+ risk"
      - "Style — only if it significantly hurts readability"
    never:
      - "Personal preference disguised as improvement"
      - "Premature optimization suggestions"
      - "Rewriting working code to your style"
  
  tone_rules:
    - "Ask questions instead of making demands: 'What happens if X is nil?' not 'Handle the nil case'"
    - "Prefix opinion with 'nit:' or 'optional:' — make severity clear"
    - "Praise good code — 'Nice abstraction here' costs nothing"
    - "If >5 comments, offer to pair instead"
    - "Approve with comments when nothing is blocking — trust your team"
```

---

## Phase 6: Sprint & Delivery

### Sprint Ceremony Cheat Sheet

| Ceremony | Duration | Who | Purpose | Your Role |
|----------|----------|-----|---------|-----------|
| **Sprint planning** | 1-2 hrs | Team + PO | Commit to sprint goal | Facilitate, challenge estimates, protect capacity |
| **Daily standup** | 15 min | Team | Surface blockers | Listen for problems, DON'T manage tasks |
| **Backlog refinement** | 1 hr | Team + PO | Prepare future work | Ensure technical feasibility, flag risks |
| **Sprint review** | 30 min | Team + stakeholders | Demo working software | Let the team present, handle stakeholder Qs |
| **Retrospective** | 1 hr | Team only | Improve process | Facilitate, ensure psychological safety, track actions |

### Sprint Health Metrics

Track these weekly — trend matters more than absolute numbers:

| Metric | Healthy Range | Red Flag |
|--------|---------------|----------|
| **Sprint completion rate** | 80-100% of committed points | <70% for 2+ sprints |
| **Carry-over stories** | 0-1 per sprint | Same story carried 3+ sprints |
| **PR cycle time** | <48 hours open to merge | >72 hours consistently |
| **Bug escape rate** | <10% of stories create bugs | Rising trend |
| **Deployment frequency** | Daily to weekly | Monthly or less |
| **Sprint goal achievement** | Yes/No binary | No for 3+ consecutive sprints |

### Estimation Heuristic

When the team struggles with estimation:

| Certainty Level | Approach |
|----------------|----------|
| "We've done this exact thing before" | Size by comparison to past work |
| "We understand the problem but not the solution" | Spike first (timeboxed), then estimate |
| "We don't fully understand the problem" | Discovery task (1-2 days), then re-scope |
| "We have no idea" | Break it down until you reach pieces you can estimate |

**Rule:** If an estimate is >8 points (or >5 days), it's not estimated — it's a guess. Break it down further.

---

## Phase 7: Incident Management

### Incident Response Framework

```yaml
incident:
  id: "INC-YYYY-NNN"
  severity: SEV1 | SEV2 | SEV3 | SEV4
  detected: "YYYY-MM-DD HH:MM UTC"
  resolved: "YYYY-MM-DD HH:MM UTC"
  duration: "Xh Ym"
  commander: "[Name]"
  
  # Severity guide
  # SEV1: Revenue impact, data loss, full outage — ALL HANDS, exec notification
  # SEV2: Degraded service, partial outage — On-call + team lead
  # SEV3: Minor degradation, workaround exists — On-call handles
  # SEV4: Cosmetic, no user impact — Normal ticket
  
  timeline:
    - time: "HH:MM"
      action: "[What happened / what was done]"
      who: "[Name]"
  
  root_cause: |
    [Technical root cause — be specific. 
     "Human error" is never the root cause. What system allowed the error?]
  
  contributing_factors:
    - "[Factor 1 — e.g., missing monitoring on X]"
    - "[Factor 2 — e.g., deployment during peak without feature flag]"
  
  action_items:
    - description: "[Specific fix]"
      owner: "[Name]"
      due_date: "YYYY-MM-DD"
      priority: P0 | P1 | P2
      status: open | in_progress | done
```

### Blameless Post-Mortem Template

**Facilitation rules:**
1. Focus on systems, not individuals
2. "What" and "how," never "who"
3. Everyone involved attends (including on-call who was paged)
4. Schedule within 48 hours of resolution (memories fade)
5. Write it up and share publicly within the engineering org

**Structure (60-90 min):**
1. **Timeline review** (20 min) — Walk through chronologically. Fill gaps.
2. **Root cause analysis** (15 min) — "5 Whys" until you hit a systemic issue
3. **What went well** (10 min) — Reinforce good incident response behaviors
4. **What went wrong** (15 min) — Process failures, detection gaps, communication issues
5. **Action items** (15 min) — Each must have an owner and due date. Max 5 items — focus beats volume.

### On-Call Health Guidelines

| Metric | Healthy | Unhealthy |
|--------|---------|-----------|
| Pages per week | <5 | >10 |
| Off-hours pages | <2/week | >5/week |
| Time to acknowledge | <5 min | >15 min |
| False positive rate | <20% | >50% |
| Rotation size | 4+ people | <3 people |
| Consecutive weeks on-call | Never >2 | Regular 3+ week stretches |

**If on-call is unhealthy:** This is a tech debt problem, not a people problem. Invest in reliability before adding headcount.

---

## Phase 8: Scaling & Org Design

### When to Split a Team

| Signal | Action |
|--------|--------|
| Team >8 people | Split before communication overhead kills velocity |
| Two distinct domains in one team | Split along domain boundaries |
| Standup takes >15 min | Too many threads — people are tuning out |
| PR review queue >48 hours consistently | Not enough context overlap — specialize |
| On-call covers too many services | Reduce blast radius per team |

### Splitting Protocol

1. **Define boundaries clearly** — What does each new team OWN? Write it down.
2. **Split the backlog** — Every ticket gets a home. Shared backlogs = shared ownership = no ownership.
3. **Split on-call** — Each team owns their services' reliability.
4. **Name the teams** — Sounds trivial, matters for identity.
5. **Designate tech leads** — Don't leave both teams looking to you for technical decisions.
6. **Give it 3 months** — Resist re-orging again too quickly. Turbulence is normal.

### Manager-to-IC Ratio

| Team Size | Structure |
|-----------|-----------|
| 3-5 ICs | Player-coach (you're still coding ~30-40%) |
| 5-8 ICs | Full-time manager (stop coding in critical path) |
| 8-12 ICs | Split the team OR add a tech lead as force multiplier |
| 12+ ICs | Must split — you cannot manage this effectively |

### The IC-to-Manager Transition

If you're newly managing (or coaching someone through it):

**Stop doing:**
- Writing code in the critical path (you're now the bottleneck)
- Solving every technical problem yourself
- Being the best engineer on the team (your job changed)

**Start doing:**
- Asking "who should own this?" instead of doing it yourself
- Measuring success by team output, not your output
- Having uncomfortable conversations early (feedback, performance, conflict)
- Blocking time for thinking, not just meetings

**Keep doing:**
- Staying technical enough to evaluate decisions (read code, review designs)
- Coding on side projects, tools, or prototypes (stay sharp)
- Having strong technical opinions (but hold them loosely)

**Timeline to competence:**
- Month 1-3: Imposter syndrome, everything feels slow. Normal.
- Month 3-6: Finding your rhythm, some wins, some failures. Normal.
- Month 6-12: Confident in the role, building systems. Target.
- Month 12+: Multiplying impact. If you're not here by month 18, honest conversation needed.

---

## Phase 9: Communication & Stakeholder Management

### Weekly Status Update Template

Send this to your manager and stakeholders every Friday:

```markdown
# [Team Name] — Week of [Date]

## 🎯 Sprint Goal: [Goal] — On Track / At Risk / Off Track

## ✅ Shipped This Week
- [Feature/fix] — [Impact in user/business terms]
- [Feature/fix] — [Impact]

## 🔨 In Progress
- [Work item] — [Status, ETA, any blockers]

## 🚨 Risks & Blockers
- [Risk] — [What you're doing about it, what you need]

## 📊 Key Metrics
- Deploy frequency: X
- Incident count: X (SEV breakdown)
- Sprint completion: X%

## 🔮 Next Week
- [Priority 1]
- [Priority 2]
```

### Managing Up Checklist

| Do | Don't |
|----|-------|
| Bring solutions with problems | Dump problems without proposals |
| Flag risks early with mitigation plans | Surprise with bad news at the last minute |
| Quantify impact (hours, $$, users) | Use vague language ("it's kinda slow") |
| Say "I need X from you by Y" | Hope they'll figure out you need help |
| Send written updates proactively | Wait to be asked for status |
| Disagree in private | Disagree in public meetings |
| Ask for feedback regularly | Assume no news is good news |

### Cross-Functional Relationship Map

```yaml
stakeholders:
  - name: "[Product Manager]"
    relationship: partner
    cadence: "Daily async + weekly 1:1"
    currency: "Scope clarity, user data, priority decisions"
    
  - name: "[Design Lead]"
    relationship: partner
    cadence: "Bi-weekly sync + ad-hoc"
    currency: "Early technical feasibility input"
    
  - name: "[Platform/Infra Team]"
    relationship: dependency
    cadence: "Monthly sync + Slack"
    currency: "Clear requirements, advance notice of needs"
    
  - name: "[Your Manager]"
    relationship: air_cover
    cadence: "Weekly 1:1"
    currency: "No surprises, clear asks, good judgment"
```

---

## Phase 10: Engineering Manager Rituals

### Daily (15 min total)

- [ ] Scan Slack/email for blockers — unblock before standup
- [ ] Attend standup — listen for patterns, not task updates
- [ ] Check PR queue — nudge any >24h reviews
- [ ] One piece of feedback (positive or constructive) to someone

### Weekly

- [ ] All 1:1s completed (never cancel — reschedule if needed)
- [ ] Sprint metrics reviewed
- [ ] Status update sent to stakeholders
- [ ] Calendar audit — am I in meetings I shouldn't be in?
- [ ] One skip-level or cross-functional conversation

### Monthly

- [ ] Team health radar updated
- [ ] Career development conversation with each report
- [ ] Tech debt review and prioritization
- [ ] On-call health review
- [ ] Update team topology doc

### Quarterly

- [ ] Performance calibration (formal or informal)
- [ ] Team goals review and reset
- [ ] Architecture review — any ADRs need revisiting?
- [ ] Headcount planning — what do we need in 6 months?
- [ ] Retrospective on YOUR performance — ask your team for feedback

---

## Phase 11: Difficult Situations Playbook

### Scenario: Two Senior Engineers Disagree on Architecture

1. Let them present both approaches in a design doc (each writes their own section)
2. Define decision criteria BEFORE evaluating: reversibility, maintenance cost, team familiarity, timeline
3. Facilitate a time-boxed discussion (60 min max)
4. If no consensus: the tech lead or DRI decides. Not you (unless you must).
5. Document the decision as an ADR — the "why" matters more than the "what"
6. The person who "lost" must commit fully. Monitor for passive resistance.

### Scenario: High Performer Wants to Be a Manager

1. Explore motivation: "Tell me what you think a manager does day-to-day"
2. Test with real work: lead a project, mentor a junior, run a retrospective
3. Be honest about tradeoffs: less coding, more meetings, slower feedback loops, ambiguous success metrics
4. Offer the Staff/Principal IC path as a genuine alternative, not a consolation prize
5. If they proceed: set explicit check-in at 3 months — "Is this what you wanted?"

### Scenario: You Inherit a Low-Performing Team

1. **Week 1-2:** Listen. 1:1 with every person. Don't change anything yet.
2. **Week 3-4:** Identify the 1-2 systemic issues (usually: unclear priorities, no accountability, or trust deficit)
3. **Month 2:** Make ONE process change. Get a quick win. Build credibility.
4. **Month 3:** Address performance issues you've now observed firsthand
5. **Never:** Blame the previous manager publicly. Never say "things are going to change around here."

### Scenario: Layoffs / Reorg Affecting Your Team

1. **Before announcement:** Prepare a plan for remaining team — who covers what?
2. **During:** Be honest about what you know and what you don't. "I don't know" > corporate-speak.
3. **After:** 1:1 with every remaining person within 48 hours. Expect anger, fear, guilt.
4. **Ongoing:** Workload audit — don't expect same output from fewer people. Push back on scope.
5. **Self-care:** This is one of the hardest parts of the job. Talk to your own manager or a coach.

### Scenario: Your Best Engineer Gives Notice

1. **Same day:** Have a real conversation. Not a counteroffer — understand why.
2. **If it's about money:** Match or beat if they're worth it. If your company won't, that tells you something.
3. **If it's about growth/role:** Can you create what they want? Be honest if you can't.
4. **If they're leaving for the right reasons:** Celebrate them. Write a recommendation. Don't make it weird.
5. **Immediately:** Start knowledge transfer plan. Identify what only they know.
6. **To the team:** Transparent but positive. "X is leaving for a great opportunity. Here's our transition plan."

---

## Scoring Rubric: Engineering Manager Effectiveness (0-100)

| Dimension | Weight | Indicators |
|-----------|--------|------------|
| **Team health** | 20% | Retention, engagement scores, psychological safety signals |
| **Delivery** | 20% | Sprint completion, quality metrics, stakeholder satisfaction |
| **People development** | 20% | Promotions, skill growth, 1:1 quality, mentorship |
| **Technical stewardship** | 15% | Tech debt trajectory, architecture quality, incident trends |
| **Hiring** | 10% | Pipeline health, offer acceptance rate, new hire ramp time |
| **Communication** | 10% | Stakeholder relationships, information flow, no surprises |
| **Self-improvement** | 5% | Seeking feedback, adapting, growing as a leader |

**Scoring:**
- 90-100: Exceptional — team thriving, people growing, shipping reliably
- 75-89: Strong — most things working, some areas to develop
- 60-74: Developing — foundational skills present, needs coaching
- 40-59: Struggling — significant gaps, at risk of losing team trust
- <40: Intervention needed — coaching, role change, or transition

---

## Natural Language Commands

- "Prepare 1:1 with [name]" → Generate agenda from recent context
- "Write performance review for [name]" → Calibrate and draft using framework
- "Create job description for [role]" → Generate using template
- "Run team health check" → Walk through radar dimensions
- "Draft ADR for [decision]" → Structure architecture decision
- "Incident post-mortem for [incident]" → Generate post-mortem template
- "Sprint health report" → Analyze metrics and flag issues
- "Promotion case for [name]" → Build evidence-based promotion doc
- "Evaluate tech debt [item]" → Score using prioritization matrix
- "Flight risk assessment" → Review signals for each team member
- "Stakeholder update" → Generate weekly status from context
- "Interview scorecard for [candidate]" → Create structured evaluation
