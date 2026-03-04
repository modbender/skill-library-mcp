# Interview Architect

Complete hiring interview system — from job scorecard design through structured question banks, live evaluation rubrics, panel coordination, and offer decisions. Eliminates gut-feel hiring with evidence-based frameworks that predict on-the-job performance.

## Quick Start

Tell me what you need:
- "Design interviews for [role]" → Full interview plan (scorecard + questions + rubrics)
- "Create a scorecard for [role]" → A-Player definition with measurable outcomes
- "Generate questions for [skill/competency]" → Targeted question bank
- "Build a take-home assignment for [role]" → Technical assessment with rubric
- "Evaluate this candidate" → Structured debrief with scoring
- "Audit our interview process" → Bias check + effectiveness review

---

## Phase 1: Job Scorecard (Define Before You Evaluate)

**Rule: Never look at a resume before defining what "great" looks like.**

### Scorecard Template

```yaml
scorecard:
  role: "[Title]"
  level: "[Junior/Mid/Senior/Staff/Principal/Director/VP]"
  team: "[Team name]"
  hiring_manager: "[Name]"
  created: "YYYY-MM-DD"

  mission:
    statement: "[One sentence: why does this role exist?]"
    success_metric: "[How we'll know this hire was successful in 12 months]"

  outcomes:
    # 3-5 specific, measurable results expected in first 12 months
    - outcome: "[e.g., Reduce deployment time from 45min to <10min]"
      measure: "[Metric: deployment duration, measured via CI/CD logs]"
      timeline: "Q1-Q2"
      priority: "critical"

    - outcome: "[e.g., Ship v2 API with 99.9% uptime]"
      measure: "[Uptime %, error rate, customer adoption]"
      timeline: "Q2-Q3"
      priority: "critical"

    - outcome: "[e.g., Mentor 2 junior engineers to mid-level competency]"
      measure: "[Promotion readiness assessment, PR quality metrics]"
      timeline: "Q3-Q4"
      priority: "important"

  competencies:
    technical:
      must_have:
        - name: "[e.g., System design]"
          level: "[Novice/Competent/Proficient/Expert]"
          evidence: "[What demonstrates this: e.g., designed systems handling 10K+ RPS]"
        - name: "[e.g., TypeScript/React]"
          level: "Proficient"
          evidence: "[Shipped production TS/React apps, not just tutorials]"
      nice_to_have:
        - name: "[e.g., Kubernetes]"
          level: "Competent"

    behavioral:
      must_have:
        - name: "Ownership"
          definition: "Takes responsibility for outcomes, not just tasks. Doesn't wait to be told."
          anti_pattern: "Says 'that's not my job' or 'I was told to do X'"
        - name: "Communication"
          definition: "Explains complex ideas simply. Writes clear docs. Raises issues early."
          anti_pattern: "Surprises stakeholders. Can't explain their own work."
        - name: "Growth mindset"
          definition: "Seeks feedback. Admits mistakes. Improves from failure."
          anti_pattern: "Defensive about criticism. Repeats same mistakes."
      nice_to_have:
        - name: "[e.g., Cross-functional leadership]"

    cultural:
      values_alignment:
        - "[Company value 1: what this looks like in practice]"
        - "[Company value 2: what this looks like in practice]"
      anti_signals:
        - "[Red flag behavior 1]"
        - "[Red flag behavior 2]"

  compensation:
    band: "[min - max]"
    equity: "[range if applicable]"
    flexibility: "[What's negotiable]"

  deal_breakers:
    # Hard no's — instant disqualification
    - "[e.g., Cannot start within 4 weeks]"
    - "[e.g., No experience with production systems at scale]"
    - "[e.g., Requires >30% above band]"
```

### Scorecard Quality Check

Before proceeding, verify:
- [ ] Mission statement is one sentence (not a paragraph)
- [ ] Each outcome has a specific number or metric (not "improve" or "help with")
- [ ] Competencies distinguish must-have from nice-to-have
- [ ] Anti-patterns defined for each behavioral competency
- [ ] Deal breakers are objective (not subjective feelings)
- [ ] Band is realistic for the market (check levels.fyi, Glassdoor)

---

## Phase 2: Interview Structure Design

### Interview Loop Template

```yaml
interview_loop:
  role: "[from scorecard]"
  total_duration: "[X hours across Y sessions]"
  
  stages:
    - stage: "Resume Screen"
      duration: "5-10 min"
      who: "Recruiter or hiring manager"
      evaluates: ["deal_breakers", "basic_qualification"]
      pass_rate_target: "30-40%"
      
    - stage: "Phone Screen"
      duration: "30 min"
      who: "Hiring manager"
      evaluates: ["communication", "motivation", "outcome_1_capability"]
      format: "Structured conversation"
      pass_rate_target: "50%"
      
    - stage: "Technical Assessment"
      duration: "60-90 min"
      who: "Senior engineer"
      evaluates: ["technical_competencies"]
      format: "Live coding OR take-home (see Phase 4)"
      pass_rate_target: "40-50%"
      
    - stage: "System Design"
      duration: "45-60 min"
      who: "Staff+ engineer"
      evaluates: ["system_design", "trade_off_thinking", "communication"]
      format: "Whiteboard/collaborative design"
      pass_rate_target: "50%"
      applies_to: "Senior+ only"
      
    - stage: "Behavioral Deep-Dive"
      duration: "45-60 min"
      who: "Hiring manager + cross-functional partner"
      evaluates: ["behavioral_competencies", "cultural_values"]
      format: "STAR-based structured interview"
      pass_rate_target: "60%"
      
    - stage: "Team Fit / Reverse Interview"
      duration: "30 min"
      who: "2-3 potential teammates"
      evaluates: ["collaboration_style", "candidate_questions"]
      format: "Informal but structured"
      pass_rate_target: "80%"
      
    - stage: "Hiring Manager Final"
      duration: "30 min"
      who: "Hiring manager"
      evaluates: ["remaining_concerns", "motivation", "offer_readiness"]
      format: "Conversation"

  timeline:
    screen_to_onsite: "< 5 business days"
    onsite_to_decision: "< 2 business days"
    decision_to_offer: "< 1 business day"
    total_process: "< 3 weeks"
```

### Level-Appropriate Loop Adjustments

| Level | Skip | Add | Emphasis |
|-------|------|-----|----------|
| Junior (0-2 yr) | System design | Pair programming, learning ability | Potential > experience |
| Mid (2-5 yr) | — | — | Balanced: execution + growth |
| Senior (5-8 yr) | — | Architecture discussion | Impact, ownership, mentoring |
| Staff (8+ yr) | Basic coding | Design doc review, strategy | Influence, technical vision |
| Principal | Basic coding | Vision presentation, exec interview | Org-wide impact |
| Manager | Live coding | Skip-level, cross-functional | People outcomes, strategy |
| Director+ | All IC technical | Board/exec presentation | Business impact, org building |

---

## Phase 3: Question Banks

### Behavioral Questions (STAR Format)

**For each question below:**
- Ask the main question
- Then probe with: "Walk me through specifically what YOU did" (not the team)
- Then probe with: "What was the measurable result?"
- Watch for: vague answers, "we" without "I", unable to recall specifics

#### Ownership & Initiative

```
Q: "Tell me about a time you identified a problem no one asked you to fix, and you fixed it anyway."
  Probe: "How did you discover it? What did you do first? What was the outcome?"
  Green signal: Specific problem, proactive action, measurable impact
  Red flag: Can't recall an example, or problem was trivial

Q: "Describe a project that failed or didn't meet expectations. What was your role?"
  Probe: "What would you do differently? What did you learn?"
  Green signal: Owns their part, specific lessons, changed behavior afterward
  Red flag: Blames others, no learning, defensive

Q: "Tell me about the last time you disagreed with your manager's technical decision."
  Probe: "How did you raise it? What happened? Would you do it differently?"
  Green signal: Respectful pushback with data, compromise or acceptance
  Red flag: Never disagrees, or went around manager, or still bitter
```

#### Communication & Collaboration

```
Q: "Describe the most complex technical concept you had to explain to a non-technical audience."
  Probe: "How did you know they understood? What would you change?"
  Green signal: Adapts language, checks understanding, uses analogies
  Red flag: Talks down, uses jargon anyway, frustrated by the need

Q: "Tell me about a cross-team project that had conflicting priorities."
  Probe: "How did you align the teams? What trade-offs were made?"
  Green signal: Proactive communication, documented agreements, escalated appropriately
  Red flag: Waited for someone else to resolve, or steamrolled

Q: "Give me an example of written communication that had significant impact."
  Probe: "What was the context? Who was the audience? What resulted?"
  Green signal: Design doc, RFC, post-mortem that changed decisions
  Red flag: Can't think of one, or only Slack messages
```

#### Technical Excellence

```
Q: "What's the best piece of code or system you've built? Walk me through it."
  Probe: "What trade-offs did you make? What would you change now?"
  Green signal: Deep understanding, clear trade-off reasoning, honest about flaws
  Red flag: Can't go deep, no awareness of trade-offs

Q: "Tell me about a production incident you were involved in resolving."
  Probe: "How did you diagnose it? What was root cause? What prevented recurrence?"
  Green signal: Systematic debugging, root cause fix (not band-aid), prevention measures
  Red flag: Only applied quick fix, blamed infrastructure, no follow-up

Q: "Describe a time you had to make a technical decision with incomplete information."
  Probe: "What did you know? What didn't you know? How did you decide?"
  Green signal: Explicit about unknowns, gathered what they could, made reversible decision
  Red flag: Paralyzed, or overconfident without data
```

#### Leadership & Mentoring (Senior+)

```
Q: "Tell me about someone you helped grow significantly in their career."
  Probe: "What did you specifically do? How did you know it was working?"
  Green signal: Specific actions (pair programming, stretch assignments, feedback), measurable growth
  Red flag: "I told them what to do" or can't name anyone

Q: "Describe a technical strategy or vision you set for your team."
  Probe: "How did you get buy-in? How did you measure progress?"
  Green signal: Clear rationale, stakeholder alignment, adapted based on feedback
  Red flag: Top-down mandate, or never set direction

Q: "Tell me about a time you had to say no to a stakeholder or product request."
  Probe: "How did you explain it? What was the outcome?"
  Green signal: Data-driven reasoning, offered alternatives, maintained relationship
  Red flag: Just said no, or always says yes
```

### Forensic Resume Questions (Pressure Tests)

For each resume highlight, design verification questions:

```
Pattern: "[Impressive claim on resume]"
→ "Walk me through [specific project]. What was the state when you joined?"
→ "What was YOUR specific contribution vs the team's?"
→ "What was the hardest technical problem YOU solved?"
→ "If I called your manager from that time, what would they say was your biggest weakness?"

Pattern: "Led team of X"
→ "How many people reported to you directly?"
→ "Name someone you had to give tough feedback to. What happened?"
→ "Who was the weakest performer? What did you do about it?"

Pattern: "Improved X by Y%"
→ "What was the baseline measurement? How did you measure it?"
→ "What was it before you started? After? How long did it take?"
→ "What else changed during that period that could explain the improvement?"

Pattern: "Short tenure (< 1 year)"
→ "Walk me through your decision to leave [company]."
→ "What would your manager there say about your departure?"
→ "What did you learn from that experience?"

Pattern: "Gap in employment"
→ Ask once, move on. Don't dwell. Valid reasons: health, family, travel, learning, job market.
→ Red flag only if: story keeps changing, or they're evasive about a very long gap
```

### Future Simulation Questions (Performance Prediction)

Design scenario questions based on the actual role's outcomes:

```
Template:
"In this role, one of your first challenges will be [outcome from scorecard].
The current situation is [honest context]. 
Walk me through how you'd approach this in your first [timeframe]."

Example (Senior Backend):
"Our API currently handles 2K RPS but we need to scale to 50K by Q3.
The codebase is a 3-year-old Node.js monolith with PostgreSQL.
Budget for infrastructure is $10K/mo. Team is 4 engineers including you.
How would you approach this?"

Probe sequence:
1. "What would you do in week 1?" (Information gathering)
2. "What data would you need?" (Analytical thinking)
3. "What are the biggest risks?" (Risk awareness)
4. "If [constraint changes], how does your approach change?" (Adaptability)
5. "How would you communicate progress to stakeholders?" (Communication)

Scoring:
5 — Structured approach, asks clarifying questions, identifies trade-offs, realistic timeline
4 — Good approach with minor gaps
3 — Reasonable but generic, doesn't probe assumptions
2 — Jumps to solution without understanding problem
1 — No coherent approach, or unrealistic
```

---

## Phase 4: Technical Assessments

### Live Coding Assessment Design

```yaml
coding_assessment:
  duration: "60 min"
  structure:
    warm_up: "5 min — environment setup, introduce the problem"
    problem_1: "20 min — core implementation"
    problem_2: "25 min — extension or new problem"
    debrief: "10 min — trade-offs discussion"

  problem_design_rules:
    - Solvable in the time limit (test it yourself first — halve your time)
    - Multiple valid approaches (no single "right answer")
    - Extension points for stronger candidates
    - Relevant to actual work (not algorithm puzzles unless role requires it)
    - Candidate chooses their language
    - Provide starter code / boilerplate to reduce setup time

  evaluation_rubric:
    problem_solving:
      5: "Breaks down problem, considers edge cases upfront, efficient approach"
      3: "Gets to solution but misses edge cases or takes indirect path"
      1: "Struggles to break down problem, no clear approach"
    
    code_quality:
      5: "Clean, readable, well-named, handles errors, testable"
      3: "Works but messy, some error handling, reasonable naming"
      1: "Barely works, no error handling, unclear naming"
    
    communication:
      5: "Thinks aloud, explains trade-offs, asks clarifying questions"
      3: "Some explanation, responds to prompts"
      1: "Silent, defensive about suggestions, doesn't explain reasoning"
    
    testing_awareness:
      5: "Writes tests unprompted, considers edge cases, talks about test strategy"
      3: "Writes tests when prompted, covers happy path"
      1: "No testing consideration"
    
    speed_and_fluency:
      5: "Fast, clearly experienced, language/tooling fluent"
      3: "Reasonable pace, occasional lookups"
      1: "Very slow, struggles with syntax/tooling"

  do_not:
    - Ask trick questions or gotchas
    - Time pressure beyond reasonable
    - Penalize for looking things up
    - Judge IDE/editor choice
    - Ask questions that require proprietary knowledge
```

### Take-Home Assessment Design

```yaml
take_home:
  time_limit: "3-4 hours (honor system, state clearly)"
  deadline: "5-7 days from send"
  
  problem_design:
    - Real-world scenario (not academic)
    - Clear requirements with defined scope
    - Extension section for candidates who want to show more
    - Starter repo with CI, linting, test framework pre-configured
    
  deliverables:
    required:
      - Working solution
      - Tests (at minimum: happy path + 2 edge cases)
      - README explaining approach, trade-offs, what you'd improve
    optional:
      - Architecture diagram
      - Performance analysis
      - Additional features from extension section
  
  evaluation_rubric:
    functionality: "30% — Does it work? Edge cases handled?"
    code_quality: "25% — Clean, readable, maintainable, well-structured"
    testing: "20% — Coverage, meaningful tests, edge cases"
    documentation: "15% — README quality, trade-off explanations"
    extras: "10% — Extension features, thoughtful additions"

  anti_gaming:
    - Check git history (single mega-commit = suspicious)
    - Ask about implementation details in follow-up interview
    - Vary the problem slightly across candidates
    - Time the follow-up discussion: over-engineered solutions + can't explain = red flag
```

### System Design Assessment (Senior+)

```yaml
system_design:
  duration: "45-60 min"
  structure:
    requirements: "10 min — clarify scope, constraints, scale"
    high_level: "15 min — components, data flow, API design"
    deep_dive: "15 min — pick 1-2 areas to go deep"
    trade_offs: "10 min — discuss alternatives, failure modes"
    extensions: "5 min — how would this evolve?"

  evaluation:
    requirements_gathering:
      5: "Asks about scale, users, latency requirements, budget before designing"
      3: "Some clarifying questions but misses key constraints"
      1: "Jumps straight to drawing boxes"
    
    high_level_design:
      5: "Clear components with well-defined boundaries, data flows make sense"
      3: "Reasonable architecture but some unclear responsibilities"
      1: "Vague boxes with arrows, can't explain data flow"
    
    depth:
      5: "Deep knowledge in chosen area, considers failure modes, cites real experience"
      3: "Good knowledge but stays surface level"
      1: "Can't go deep on any component"
    
    trade_off_awareness:
      5: "Explicitly names trade-offs, compares alternatives, knows when each fits"
      3: "Acknowledges trade-offs when prompted"
      1: "Presents one approach as the only option"
    
    scalability:
      5: "Considers growth path, bottleneck identification, realistic scaling strategy"
      3: "Basic scaling awareness"
      1: "No consideration of scale or unrealistic assumptions"
```

---

## Phase 5: Evaluation & Decision

### Per-Interviewer Scorecard

```yaml
interviewer_scorecard:
  candidate: "[name]"
  interviewer: "[name]"
  stage: "[which interview]"
  date: "YYYY-MM-DD"
  
  # Score BEFORE reading other interviewers' feedback
  overall: 1-5  # 1=Strong No, 2=Lean No, 3=Neutral, 4=Lean Yes, 5=Strong Yes
  
  competency_scores:
    - competency: "[from scorecard]"
      score: 1-5
      evidence: "[Specific quote or behavior observed]"
      
    - competency: "[from scorecard]"
      score: 1-5
      evidence: "[Specific quote or behavior observed]"
  
  green_signals:
    - "[Specific positive indicator with evidence]"
    
  red_flags:
    - "[Specific concern with evidence]"
    
  questions_for_next_interviewer:
    - "[What to probe further]"

  # IMPORTANT: Submit before debrief. Do not change after discussion.
```

### Debrief Protocol

```
1. BEFORE debrief:
   - All interviewers submit scorecards independently
   - Hiring manager collects but does NOT share scores

2. DEBRIEF structure (30-45 min):
   a. Each interviewer states their overall vote FIRST (no explanation yet)
      → This prevents anchoring bias from persuasive speakers
   
   b. Lowest scorer goes first (explain concerns)
      → Prevents positive bias from drowning out concerns
   
   c. Highest scorer responds
   
   d. Open discussion — focus on EVIDENCE not feelings
      → "They seemed smart" is not evidence
      → "They designed a cache invalidation strategy that handled..." IS evidence
   
   e. Address conflicting signals:
      → If strong yes + strong no on same competency, that's the discussion
      → Resolve with: "What specific behavior did you observe?"
   
   f. Final vote (all interviewers):
      → Strong Hire / Hire / No Hire / Strong No Hire
      → Any "Strong No Hire" triggers discussion but NOT automatic rejection
      → Hiring manager makes final call but must document reasoning

3. AFTER debrief:
   - Decision recorded with reasoning
   - Feedback compiled for candidate (regardless of outcome)
   - Action items assigned (offer prep or rejection with feedback)
```

### Scoring Decision Matrix

```
Strong Hire (all 4-5):
  → Make offer within 24 hours
  → Expedite process — strong candidates have multiple offers

Hire (mix of 3-5, no 1s):
  → Make offer within 48 hours
  → Address any 3-scores with targeted onboarding plan

Borderline (mix of 2-4):
  → Additional data needed — one more focused interview on weak areas
  → Set a deadline: if still borderline after additional data → No Hire
  → "When in doubt, don't hire" — the cost of a bad hire > cost of continuing search

No Hire (any 1, or multiple 2s):
  → Decline with specific, constructive feedback
  → Document clearly for future reference (candidate may reapply)

Strong No Hire (multiple 1s or deal breaker):
  → Immediate decline
  → Review: did we miss this in screening? Fix the funnel.
```

---

## Phase 6: Bias Mitigation

### Pre-Interview Bias Checks

```
Before each interview, remind yourself:
□ I will evaluate against the SCORECARD, not my "gut feeling"
□ I will give the same weight to disconfirming evidence as confirming
□ I will not let one great/terrible answer color the entire evaluation
□ I will not compare this candidate to the last one — compare to the scorecard
□ I will note specific behaviors, not general impressions
□ I will not evaluate "culture fit" as "would I have a beer with them"
```

### Common Biases in Hiring

| Bias | What It Looks Like | Mitigation |
|------|--------------------|------------|
| **Halo effect** | Great at coding → assume great at everything | Score each competency independently |
| **Horn effect** | Weak communication → assume weak technically | Same: score independently |
| **Similarity bias** | "Reminds me of me" → favorable rating | Evaluate against scorecard, not self |
| **Anchoring** | First impression sets the tone | Score after all questions, not during |
| **Confirmation bias** | Early positive → only notice positives | Actively look for counter-evidence |
| **Contrast effect** | Looks great after a weak candidate | Compare to scorecard, not other candidates |
| **Recency bias** | Remember last answer, forget first | Take notes during interview |
| **Attribution error** | Success = skill, failure = circumstances | Probe both: "What went wrong? What helped?" |
| **Leniency bias** | Avoid conflict, rate everyone 3-4 | Force yourself to use the full 1-5 scale |
| **Urgency bias** | "We need someone NOW" → lower bar | Never lower scorecard standards — extend timeline instead |

### Structured Interview Rules

1. **Same questions for same role** — every candidate gets the same core questions
2. **Score immediately after** — before discussing with anyone
3. **Evidence-based only** — every score needs a specific observation
4. **Diverse panel** — at least one interviewer from a different team/background
5. **Blind resume screen** — remove name, school, company names for initial screen (if possible)
6. **No leading questions** — "You're probably great at X, right?" → "Tell me about your experience with X"
7. **Time-boxed** — same duration for every candidate (don't cut short or extend based on vibes)

---

## Phase 7: Candidate Experience

### Communication Templates

**After each stage — within 24 hours:**

```
ADVANCING:
"Hi [name], thank you for your time today. We enjoyed our conversation about [specific topic]. 
We'd like to move forward with [next stage]. [Interviewer name] will be speaking with you 
about [topic]. Available times: [options]. 
Any questions before then? — [recruiter name]"

REJECTION (after phone screen):
"Hi [name], thank you for taking the time to speak with us about [role].
After careful consideration, we've decided not to move forward at this stage.
[One specific, constructive piece of feedback if appropriate].
We'll keep your information on file and may reach out for future opportunities that 
align more closely. Wishing you the best in your search. — [name]"

REJECTION (after onsite):
"Hi [name], thank you for investing [X hours] in our interview process.
We were impressed by [specific positive], but ultimately decided to move forward 
with a candidate whose [specific competency] more closely matches our current needs.
Feedback: [1-2 specific, actionable items].
We genuinely appreciated your time and would welcome a future conversation 
if circumstances change. — [hiring manager name]"

OFFER (verbal, then written within 24h):
"Hi [name], I'm excited to share that we'd like to offer you the [role] position.
We were particularly impressed by [specific evidence from interviews].
Here's what we're proposing: [comp summary]. I'll send the formal offer letter 
within 24 hours. Do you have any initial questions? — [hiring manager]"
```

### Candidate Experience Scorecard

After every hire (and quarterly for all candidates):

| Dimension | Target | How to Measure |
|-----------|--------|----------------|
| Time to schedule | < 48h between stages | Track in ATS |
| Interviewer preparedness | 100% read scorecard before | Post-interview survey |
| Communication timeliness | < 24h response | Track in ATS |
| Feedback quality | Specific + actionable | Candidate survey |
| Overall experience | 4+/5 | Candidate survey (all, not just hires) |
| Offer acceptance rate | > 80% | Track in ATS |

---

## Phase 8: Process Audit & Improvement

### Quarterly Hiring Review

```yaml
quarterly_review:
  period: "Q[N] YYYY"
  
  funnel_metrics:
    applications: N
    screens_passed: N  # → Screen pass rate
    onsites: N         # → Onsite conversion rate  
    offers: N          # → Offer rate
    accepts: N         # → Acceptance rate
    
  quality_metrics:
    ninety_day_retention: "X%"
    manager_satisfaction_90d: "X/5"
    time_to_productivity: "X weeks"
    regretted_attrition_1yr: "X%"
    
  process_metrics:
    time_to_fill: "X days (target: <30)"
    time_in_stage:
      screen: "X days"
      onsite: "X days"  
      decision: "X days"
      offer: "X days"
    interviewer_calibration: "score variance across interviewers"
    
  actions:
    - "[Improvement 1 based on metrics]"
    - "[Improvement 2]"
```

### Interview Question Effectiveness Tracking

For each question in your bank, track:

```yaml
question_effectiveness:
  question: "[question text]"
  times_asked: N
  
  signal_quality:
    strong_differentiator: N  # Times this question clearly separated strong/weak
    no_signal: N              # Times everyone answered similarly
    confusing: N              # Times candidates misunderstood
    
  # If no_signal > 50% → Replace the question
  # If confusing > 20% → Reword the question
  # If strong_differentiator > 70% → Keep and promote
```

### Interviewer Calibration

```
Monthly: Compare interviewer scores across candidates
- Interviewer A averages 4.2, Interviewer B averages 2.8 → calibration needed
- Run calibration session: review same candidate, discuss scoring differences
- Goal: interviewers should be within 0.5 points on average for same candidates

Training for new interviewers:
1. Shadow 3 interviews (observe, don't participate)
2. Reverse shadow 2 interviews (conduct, observed by experienced interviewer)
3. Solo with debrief for 3 interviews
4. Full autonomy after calibration check
```

---

## Edge Cases

### Internal Candidates
- Use SAME scorecard as external (fairness)
- Different question strategy: focus on future role, not past (you already know their past)
- If not selected: manager delivers feedback personally, development plan, timeline for re-candidacy
- Never promise the internal candidate gets special treatment

### Executive Hiring
- Add: reference checks (5+ structured, including back-channel)
- Add: board/exec team dinner (culture, not evaluation)
- Add: 90-day plan presentation as final stage
- Extended scorecard: strategic thinking, board management, talent magnetism
- Use executive search firm for sourcing, but own evaluation internally

### High-Volume Hiring (10+ same role)
- Standardize EVERYTHING: same questions, same rubric, same order
- Use structured scoring sheets, not free-form notes
- Batch calibration sessions weekly
- Consider: group assessment centers for initial stages
- Track: quality variance across hiring managers (should be low)

### Remote/Async Interviews
- Test tech setup before the interview (not during)
- Camera on (both sides) — non-verbal cues matter
- Record (with consent) for calibration purposes
- Take-home > live coding for timezone-challenged candidates
- Bias alert: don't penalize for background noise, accent, or non-native English fluency

### Boomerang Employees
- Treat as new candidate (things change)
- Skip: basic company knowledge questions
- Focus: why they left, what changed, what they learned outside
- Check: has the team/role changed since they left? Do current team members want them back?

### Counteroffers
- If candidate receives counteroffer:
  - Don't panic-increase. Your offer should already be fair.
  - "We made our best offer based on the value of the role. We'd love to have you, but understand if you decide to stay."
  - Statistics: 80% of people who accept counteroffers leave within 18 months anyway
  - If they stay: respect it, keep the door open

---

## Natural Language Commands

| Say | I Do |
|-----|------|
| "Design interviews for [role]" | Full loop: scorecard + structure + questions + rubrics |
| "Create a scorecard for [role]" | A-Player definition with outcomes and competencies |
| "Generate behavioral questions for [competency]" | STAR questions with probes and scoring |
| "Build a take-home for [role]" | Assessment with rubric and anti-gaming measures |
| "Design a system design interview for [level]" | Structure + evaluation rubric |
| "Evaluate candidate [name]" | Structured debrief template with scoring |
| "Create a phone screen for [role]" | 30-min structured screen with pass/fail criteria |
| "Write rejection feedback for [candidate]" | Specific, constructive rejection message |
| "Audit our interview process" | Full process review with metrics and recommendations |
| "Calibrate interviewers" | Calibration session plan with scoring alignment |
| "Design interview for [role] at [company stage]" | Adjusted for startup/growth/enterprise context |
| "Generate reference check questions for [role]" | Structured reference interview guide |
