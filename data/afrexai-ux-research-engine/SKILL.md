---
name: afrexai-ux-research-engine
description: Complete UX Research & Design system — user discovery, persona building, journey mapping, usability testing, research synthesis, and design validation. Zero dependencies.
---

# UX Research Engine ⚡

Complete UX research methodology — from discovery to validated design decisions. No scripts, no APIs, no dependencies. Pure agent skill.

---

## Phase 1: Research Planning

### Research Brief YAML

```yaml
project: "[Product/Feature Name]"
research_question: "[What do we need to learn?]"
business_context:
  objective: "[Business goal this research supports]"
  decision: "[What decision will this research inform?]"
  stakeholders: ["PM", "Design Lead", "Engineering"]
  deadline: "YYYY-MM-DD"
scope:
  product_area: "[Feature/flow being studied]"
  user_segment: "[Who are we studying?]"
  geographic: "[Regions/markets]"
methodology: "[See selection matrix below]"
sample_size: "[See calculator below]"
timeline:
  planning: "Week 1"
  recruiting: "Week 1-2"
  fieldwork: "Week 2-3"
  analysis: "Week 3-4"
  reporting: "Week 4"
budget:
  participant_incentives: "$X"
  tools: "$X"
  total: "$X"
success_criteria:
  - "[Specific insight we need]"
  - "[Confidence level required]"
  - "[Actionable output format]"
```

### Method Selection Matrix

| Method | Best For | Sample Size | Time | Cost | Confidence |
|--------|----------|-------------|------|------|------------|
| User Interviews | Deep "why" understanding, exploring unknowns | 5-15 | 2-4 weeks | $$ | High (qualitative) |
| Usability Testing | Finding interaction problems, validating flows | 5-8 per round | 1-2 weeks | $$ | High (behavioral) |
| Surveys | Quantifying attitudes, measuring satisfaction | 100-400+ | 1-2 weeks | $ | High (statistical) |
| Card Sorting | Information architecture, navigation labels | 15-30 (open), 30+ (closed) | 1 week | $ | Medium |
| Diary Studies | Long-term behavior, context of use | 10-15 | 2-6 weeks | $$$ | High (longitudinal) |
| A/B Testing | Comparing specific design variants | 1000+ per variant | 1-4 weeks | $ | Very High |
| Contextual Inquiry | Understanding real environment, workflows | 4-8 | 2-3 weeks | $$$ | Very High |
| Tree Testing | Validating IA without visual design | 50+ | 1 week | $ | High |
| First-Click Testing | Navigation effectiveness | 30-50 | 1 week | $ | Medium |
| Concept Testing | Early-stage idea validation | 8-15 | 1-2 weeks | $$ | Medium |
| Heuristic Evaluation | Expert review of existing UI | 3-5 evaluators | 2-3 days | $ | Medium |
| Competitive UX Audit | Understanding market standards | N/A | 1 week | $ | Low-Medium |

### Decision Tree: Which Method?

```
Do you know WHAT the problem is?
├── NO → Generative Research
│   ├── Need context? → Contextual Inquiry
│   ├── Need attitudes? → User Interviews
│   ├── Need behaviors over time? → Diary Study
│   └── Need broad patterns? → Survey (exploratory)
│
└── YES → Evaluative Research
    ├── Have a prototype/product?
    │   ├── YES → Usability Testing
    │   │   ├── Early concept → Concept Test (paper/low-fi)
    │   │   ├── Key flow → Task-based Usability Test
    │   │   └── Comparing options → A/B Test
    │   └── NO → 
    │       ├── Testing IA → Card Sort / Tree Test
    │       └── Testing content → First-Click Test
    └── Need expert opinion fast? → Heuristic Evaluation
```

### Sample Size Calculator

**Qualitative (interviews, usability):**
- 5 users find ~85% of usability issues (Nielsen)
- 8-12 for thematic saturation in interviews
- 15+ for diverse populations or complex domains
- Rule: keep going until you hear the same things 3x

**Quantitative (surveys):**
| Population | 90% Confidence ±5% | 95% Confidence ±5% | 99% Confidence ±5% |
|------------|---------------------|---------------------|---------------------|
| 100 | 74 | 80 | 87 |
| 500 | 176 | 217 | 285 |
| 1,000 | 214 | 278 | 399 |
| 10,000 | 264 | 370 | 622 |
| 100,000+ | 271 | 384 | 660 |

**A/B Tests:**
- MDE (Minimum Detectable Effect) drives sample size
- 5% MDE, 80% power, 95% confidence → ~1,600 per variant
- 2% MDE → ~10,000 per variant
- Always run for full business cycles (min 1 week)

---

## Phase 2: Participant Recruiting

### Screener Template

```yaml
screener:
  title: "[Study Name] Participant Screener"
  target_profile:
    demographics:
      age_range: "[e.g., 25-45]"
      location: "[e.g., US-based]"
      language: "[e.g., English-fluent]"
    behavioral:
      product_usage: "[e.g., Uses [product] 3+ times/week]"
      experience_level: "[e.g., 1+ year with similar tools]"
      recent_activity: "[e.g., Made a purchase in last 30 days]"
    psychographic:
      decision_maker: "[e.g., Primary household purchaser]"
      tech_comfort: "[e.g., Comfortable with mobile apps]"
  
  screening_questions:
    - question: "How often do you use [product category]?"
      type: "single-select"
      options: ["Daily", "Weekly", "Monthly", "Rarely", "Never"]
      qualify: ["Daily", "Weekly"]
      disqualify: ["Never"]
    
    - question: "Which of these tools do you currently use?"
      type: "multi-select"
      options: ["Tool A", "Tool B", "Tool C", "None"]
      qualify_min: 1
      
    - question: "What is your primary role?"
      type: "single-select"
      options: ["Developer", "Designer", "PM", "Marketing", "Other"]
      qualify: ["Developer", "Designer", "PM"]
    
    - question: "Have you participated in a UX study in the last 6 months?"
      type: "single-select"
      options: ["Yes", "No"]
      disqualify: ["Yes"]  # Avoid professional participants
  
  anti-patterns:
    - "Works at a competitor or in UX research"
    - "Family/friends of team members"
    - "Participated in study for this product before"
  
  incentive: "$75 for 60-min session"
  
  recruiting_channels:
    - channel: "Existing user database"
      quality: "★★★★★"
      cost: "Free"
    - channel: "UserTesting.com / UserInterviews.com"
      quality: "★★★★"
      cost: "$50-150/participant"
    - channel: "Social media recruitment"
      quality: "★★★"
      cost: "Free-$$"
    - channel: "Craigslist / local posting"
      quality: "★★"
      cost: "$"
```

### Recruiting Quality Checklist
- [ ] Screener doesn't lead (no "right" answers obvious)
- [ ] Mix of demographics within target segment
- [ ] No more than 20% from single recruiting source
- [ ] At least 1 "edge case" participant (power user, new user, accessibility needs)
- [ ] Over-recruit by 20% for no-shows
- [ ] Consent form prepared and sent in advance
- [ ] Incentive delivery method confirmed

---

## Phase 3: User Interviews

### Interview Guide Template

```markdown
# Interview Guide: [Study Name]
Duration: 60 minutes
Moderator: [Name]

## Setup (5 min)
- Thank participant, confirm recording consent
- "There are no right or wrong answers — we're learning from YOUR experience"
- "Feel free to be critical — honest feedback helps us improve"
- "I didn't design this, so you won't hurt my feelings"

## Warm-Up (5 min)
- "Tell me about your role and what a typical day looks like"
- "How does [product area] fit into your work?"

## Core Questions (35 min)

### Context & Current Behavior
1. "Walk me through the last time you [did the task we're studying]"
   - Probe: "What happened next?"
   - Probe: "How did that make you feel?"
   - Probe: "What would you have preferred to happen?"

2. "What tools/methods do you currently use for [task]?"
   - Probe: "What do you like about that approach?"
   - Probe: "What frustrates you?"
   - Probe: "How long have you been doing it this way?"

3. "Can you show me how you typically [task]?" (if remote: screen share)

### Pain Points & Needs
4. "What's the hardest part about [task]?"
   - Probe: "How often does that happen?"
   - Probe: "What do you do when that happens?"
   - Probe: "How much time/money does that cost you?"

5. "If you could wave a magic wand and change one thing about [experience], what would it be?"

6. "Tell me about a time when [process] went really wrong"
   - Probe: "What was the impact?"
   - Probe: "How was it resolved?"

### Mental Models
7. "How would you explain [concept] to a colleague?"
8. "What do you expect to happen when you [action]?"
9. "Where would you look for [information/feature]?"

### Priorities & Trade-offs
10. "If you had to choose between [speed vs accuracy / ease vs power], which matters more? Why?"

## Concept Reaction (10 min) — if applicable
- Show prototype/concept
- "What's your first impression?"
- "What would you use this for?"
- "What's missing?"
- "Would this replace what you currently use? Why/why not?"

## Wrap-Up (5 min)
- "Is there anything else about [topic] we should know?"
- "Who else should we talk to about this?"
- Thank participant, confirm incentive delivery
```

### Interview Quality Rules
1. **80/20 rule**: Participant talks 80%, you talk 20%
2. **Never ask "Would you use this?"** — people can't predict future behavior
3. **Ask about past behavior**, not hypothetical futures
4. **Follow the energy** — when they get animated, dig deeper
5. **Silence is a tool** — pause 5 seconds after they answer; they'll elaborate
6. **"Tell me more about that"** — your most powerful phrase
7. **Watch for say/do gaps** — note when claimed behavior contradicts observed behavior
8. **Record everything** — audio minimum, video ideal, notes always

### Note-Taking Template (Per Interview)

```yaml
participant:
  id: "P01"
  date: "YYYY-MM-DD"
  demographics: "[age, role, experience level]"
  session_duration: "58 min"

key_quotes:
  - quote: "[Exact words]"
    timestamp: "12:34"
    context: "[What prompted this]"
    theme: "[Emerging theme tag]"

observations:
  behaviors:
    - "[What they DID, not what they said]"
  emotions:
    - "[Frustration when..., delight when..., confusion at...]"
  workarounds:
    - "[Creative solutions they've built]"

pain_points:
  - pain: "[Specific problem]"
    severity: "[1-5]"
    frequency: "[daily/weekly/monthly/rarely]"
    current_solution: "[How they cope]"
    
needs:
  - need: "[Unmet need identified]"
    type: "[functional/emotional/social]"
    evidence: "[Quote or behavior that reveals this]"

surprises:
  - "[Anything unexpected — these are gold]"

moderator_notes:
  - "[Post-session reflection, what to adjust for next interview]"
```

---

## Phase 4: Persona Building

### Data-Driven Persona Template

```yaml
persona:
  name: "[Realistic name — not cutesy]"
  photo: "[Representative stock photo description]"
  archetype: "[1-3 word label, e.g., 'The Overwhelmed Manager']"
  
  demographics:
    age: "[Range or specific]"
    role: "[Job title / life stage]"
    experience: "[Years with product/domain]"
    tech_proficiency: "[Novice / Intermediate / Advanced / Expert]"
    environment: "[Office / remote / mobile / field]"
  
  # MOST IMPORTANT SECTION
  goals:
    primary: "[The #1 thing they're trying to accomplish]"
    secondary:
      - "[Supporting goal]"
      - "[Supporting goal]"
    underlying: "[The emotional/social need behind the functional goal]"
  
  frustrations:
    - frustration: "[Specific pain point]"
      frequency: "[How often — from research data]"
      severity: "[1-5]"
      current_workaround: "[What they do today]"
      evidence: "[P03, P07, P11 mentioned this]"
  
  behaviors:
    usage_pattern: "[When, where, how often they engage]"
    decision_process: "[How they evaluate options]"
    information_sources: "[Where they learn / get help]"
    social_influence: "[Who influences their decisions]"
    key_workflows:
      - "[Task 1 — frequency — duration]"
      - "[Task 2 — frequency — duration]"
  
  mental_models:
    - "[How they think about [concept] — often surprising]"
    - "[Vocabulary they use — not our jargon]"
  
  motivations:
    gains: "[What success looks like to them]"
    fears: "[What failure looks like]"
    triggers: "[What prompts them to act]"
    barriers: "[What stops them from acting]"
  
  quotes:
    - "\"[Real quote from research that captures this persona]\""
    - "\"[Another revealing quote]\""
  
  design_implications:
    must_have:
      - "[Feature/quality this persona absolutely needs]"
    should_have:
      - "[Important but not dealbreaker]"
    must_avoid:
      - "[Things that will drive this persona away]"
    communication_style: "[How to talk to this persona]"
  
  data_sources:
    interviews: "[# of participants who map to this persona]"
    survey_segment: "[% of survey respondents]"
    analytics_cohort: "[Behavioral data that identifies this group]"
```

### Persona Validation Checklist
- [ ] Based on real research data, not assumptions
- [ ] Represents a meaningful segment (not 1 outlier)
- [ ] Goals are specific enough to design for
- [ ] Frustrations include frequency + severity (not just a list)
- [ ] Contains at least 2 real quotes
- [ ] Design implications are actionable
- [ ] Reviewed with 3+ stakeholders
- [ ] Cross-checked against analytics data
- [ ] Does NOT describe everyone (a good persona excludes people)

### Anti-Personas (Who We're NOT Designing For)

```yaml
anti_persona:
  name: "[Label]"
  description: "[Who this is]"
  why_excluded: "[Business reason — too small a segment, wrong market, etc.]"
  risk_if_included: "[What happens to the product if we try to serve them too]"
```

---

## Phase 5: Journey Mapping

### Journey Map Template

```yaml
journey_map:
  title: "[Persona] — [Goal/Scenario]"
  persona: "[Which persona]"
  scenario: "[Specific situation triggering this journey]"
  
  stages:
    - stage: "1. Awareness / Trigger"
      duration: "[Time in this stage]"
      goals: "[What they want to accomplish]"
      actions:
        - "[Step they take]"
        - "[Step they take]"
      touchpoints:
        - "[Where they interact — website, app, email, phone, in-person]"
      thoughts:
        - "\"[What they're thinking — from research]\""
      emotions:
        rating: 3  # 1=frustrated, 3=neutral, 5=delighted
        feeling: "[Curious but uncertain]"
      pain_points:
        - "[Problem encountered]"
      opportunities:
        - "[How we could improve this moment]"
    
    - stage: "2. Consideration / Research"
      # ... same structure
    
    - stage: "3. Decision / Sign-Up"
      # ... same structure
    
    - stage: "4. Onboarding / First Use"
      # ... same structure
    
    - stage: "5. Regular Use / Value Realization"
      # ... same structure
    
    - stage: "6. Expansion / Advocacy (or Churn)"
      # ... same structure
  
  moments_of_truth:
    - moment: "[Critical make-or-break interaction]"
      stage: "[Which stage]"
      current_experience: "[What happens now — score 1-5]"
      desired_experience: "[What should happen — score 1-5]"
      gap: "[Difference = priority]"
      
  service_blueprint_layer:  # Optional — behind-the-scenes
    - stage: "[Stage name]"
      frontstage: "[What user sees]"
      backstage: "[What team does]"
      support_systems: "[Tools/processes involved]"
      failure_points: "[Where things break down]"
```

### Emotion Curve Scoring
Plot emotions across the journey:
```
5 ★ Delighted  ──────────╮          ╭──
4 ☺ Happy               │          │
3 😐 Neutral    ──╮      │    ╭─────╯
2 😟 Frustrated    │      │    │
1 😤 Angry         ╰──────╯────╯
                  Stage1  Stage2  Stage3  Stage4  Stage5
```

### Journey Map Quality Rules
1. Based on research, not assumptions (note data source for each insight)
2. One persona per map (don't average)
3. Include BOTH functional and emotional dimensions
4. Identify "moments of truth" — the 2-3 interactions that make or break the experience
5. Prioritize opportunities by gap size (desired minus current)
6. Include backstage/blueprint layer for service design

---

## Phase 6: Usability Testing

### Test Plan Template

```yaml
usability_test:
  study_name: "[Name]"
  objective: "[What design question are we answering?]"
  
  format:
    type: "[Moderated / Unmoderated]"
    location: "[Remote / In-person / Lab]"
    device: "[Desktop / Mobile / Tablet / Cross-device]"
    duration: "60 min"
    recording: "[Screen + audio + face camera]"
  
  prototype:
    fidelity: "[Paper / Wireframe / Hi-fi / Live product]"
    tool: "[Figma / InVision / Live URL]"
    scope: "[Which flows are testable]"
    known_limitations: "[What won't work in the prototype]"
  
  participants:
    target: 5-8
    criteria: "[From screener — link to Phase 2]"
    incentive: "$75"
  
  tasks:
    - task_id: "T1"
      scenario: "You need to [context]. Using this app, [goal]."
      success_criteria: 
        - "[Specific completion definition]"
      time_limit: "5 min"
      priority: "critical"  # critical / important / nice-to-know
      metrics:
        - completion_rate
        - time_on_task
        - error_count
        - satisfaction_rating
    
    - task_id: "T2"
      scenario: "[Next task...]"
      # ... same structure
  
  post_task_questions:
    - "On a scale of 1-7, how easy was that? (SEQ)"
    - "What did you expect to happen when you [action]?"
    - "Was anything confusing?"
  
  post_test_questions:
    - "SUS (System Usability Scale) — 10 questions"
    - "What was the easiest part?"
    - "What was the most frustrating part?"
    - "Would you use this? Why/why not?"
    - "What's missing?"
```

### Task Writing Rules
1. **Set the scene** — give context, not instructions ("You want to book a flight to NYC next Friday" NOT "Click the search button")
2. **Don't use interface words** — say "find" not "navigate to," say "purchase" not "add to cart and checkout"
3. **Make it realistic** — use scenarios from actual research data
4. **One goal per task** — don't combine ("book a flight AND a hotel")
5. **Order: easy → hard** — build confidence before complex tasks

### Severity Rating Scale

| Severity | Label | Definition | Action |
|----------|-------|------------|--------|
| 0 | Not a problem | Disagreement among evaluators, no real issue | None |
| 1 | Cosmetic | Noticed but doesn't affect task completion | Fix if time allows |
| 2 | Minor | Causes hesitation or minor inefficiency | Schedule fix |
| 3 | Major | Causes significant difficulty, workarounds needed | Fix before launch |
| 4 | Catastrophic | Prevents task completion entirely | Fix immediately |

### Usability Finding Template

```yaml
finding:
  id: "UF-001"
  title: "[Short descriptive title]"
  severity: 3  # 0-4
  frequency: "4/5 participants"
  task: "T2"
  
  observation: "[What happened — factual, behavioral]"
  evidence:
    - participant: "P01"
      behavior: "[What they did]"
      quote: "\"[What they said]\""
      timestamp: "14:22"
    - participant: "P03"
      behavior: "[What they did]"
  
  root_cause: "[Why this happened — mental model mismatch, visibility, feedback, etc.]"
  
  recommendation:
    change: "[Specific design change]"
    rationale: "[Why this will fix it]"
    effort: "[S/M/L]"
    impact: "[High/Medium/Low]"
    
  heuristic_violated: "[Which Nielsen heuristic, if applicable]"
```

### Nielsen's 10 Heuristics (Quick Reference)

| # | Heuristic | What to Check |
|---|-----------|---------------|
| 1 | Visibility of system status | Loading indicators, progress bars, confirmation messages |
| 2 | Match real world | Labels match user language, not internal jargon |
| 3 | User control & freedom | Undo, back, cancel, exit are easy to find |
| 4 | Consistency & standards | Same action = same result everywhere |
| 5 | Error prevention | Confirmations, constraints, smart defaults |
| 6 | Recognition > recall | Options visible, not memorized |
| 7 | Flexibility & efficiency | Shortcuts for experts, simple for novices |
| 8 | Aesthetic & minimalist | No unnecessary information competing for attention |
| 9 | Error recovery | Clear error messages with solutions, not codes |
| 10 | Help & documentation | Searchable, task-focused, concise |

### Heuristic Evaluation Scorecard

Rate each heuristic 1-5 per screen/flow:

```yaml
heuristic_audit:
  screen: "[Screen/Flow name]"
  evaluator: "[Name]"
  date: "YYYY-MM-DD"
  
  scores:
    visibility_of_status: 4
    real_world_match: 3
    user_control: 2
    consistency: 4
    error_prevention: 3
    recognition_over_recall: 4
    flexibility_efficiency: 2
    aesthetic_minimal: 3
    error_recovery: 1
    help_documentation: 2
  
  total: 28  # out of 50
  grade: "C"  # A=45+, B=38+, C=28+, D=20+, F=<20
  
  critical_issues:
    - heuristic: "Error recovery"
      location: "[Where]"
      issue: "[What's wrong]"
      fix: "[Recommendation]"
```

---

## Phase 7: Research Synthesis

### Affinity Mapping Process

1. **Extract**: Pull every observation, quote, behavior onto individual notes
2. **Cluster**: Group similar notes (bottom-up, not top-down)
3. **Label**: Name each cluster with a theme (use participant language)
4. **Hierarchy**: Group clusters into meta-themes
5. **Prioritize**: Rank by frequency × impact

### Theme Template

```yaml
theme:
  name: "[Theme label — use participant language]"
  description: "[2-3 sentence summary]"
  
  evidence:
    participant_count: "8/12 participants"
    segments_affected: ["Persona A", "Persona B"]
    
    quotes:
      - participant: "P03"
        quote: "\"[Exact quote]\""
      - participant: "P07"
        quote: "\"[Exact quote]\""
    
    behaviors_observed:
      - "[What they did]"
      - "[Pattern across participants]"
    
    data_points:
      - "[Any quantitative support — survey %, analytics, etc.]"
  
  impact:
    on_users: "[How this affects their experience]"
    on_business: "[Revenue, retention, acquisition, support cost impact]"
    severity: "High"  # High / Medium / Low
  
  insight: "[The 'so what' — what does this mean for design?]"
  
  recommendations:
    - recommendation: "[Specific, actionable change]"
      effort: "M"
      impact: "High"
      confidence: "High"  # based on evidence strength
```

### Insight Formula

Every insight must follow: **Observation + Evidence + So What + Now What**

> "Users consistently [OBSERVATION] — seen in [X/Y participants, with supporting quotes]. This matters because [SO WHAT — impact on goals/business]. We should [NOW WHAT — specific recommendation]."

**Bad insight:** "Users found the navigation confusing"
**Good insight:** "7 of 12 participants couldn't find the settings page within 30 seconds. 4 looked in the profile menu, 2 used search, 1 gave up. This maps to 15% of support tickets ('How do I change my password'). Moving settings to the top-level nav and adding a search shortcut would reduce discovery time and cut related support volume."

### Research Scoring Rubric (0-100)

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Methodology Rigor | 20% | Right method for question, adequate sample, proper recruiting |
| Data Quality | 15% | Rich observations, real quotes, behavioral evidence |
| Analysis Depth | 20% | Beyond surface themes, root causes identified, patterns across segments |
| Insight Actionability | 25% | Specific recommendations, effort/impact rated, prioritized |
| Presentation Clarity | 10% | Stakeholders can understand and act without explanation |
| Business Connection | 10% | Findings connected to business metrics and goals |

**Scoring:**
- 90-100: Publication-quality research
- 75-89: Strong actionable research
- 60-74: Adequate — some gaps in methodology or analysis
- 40-59: Weak — findings are surface-level or poorly supported
- Below 40: Redo — methodology flaws undermine findings

---

## Phase 8: Research Report

### Executive Summary Template

```markdown
# [Study Name] — Research Report

## TL;DR (3 bullet max)
- [Most important finding + recommendation]
- [Second most important finding + recommendation]  
- [Third most important finding + recommendation]

## Study Overview
- **Method:** [e.g., 12 semi-structured interviews + 5 usability tests]
- **Participants:** [e.g., 12 mid-market SaaS PMs, 2-8 years experience]
- **Duration:** [e.g., 3 weeks, Jan 5-26 2026]
- **Confidence:** [High / Medium / Low — based on sample + methodology]

## Key Findings

### Finding 1: [Title] ⚠️ [Severity: Critical/High/Medium/Low]
**What we found:** [2-3 sentences with evidence]
**Why it matters:** [Business impact]
**Recommendation:** [Specific action]
**Effort:** [S/M/L] | **Impact:** [High/Med/Low]

### Finding 2: [Title]
...

## Personas Updated
[Link to updated persona YAML files]

## Journey Map
[Link to journey map]

## Design Recommendations (Prioritized)

| # | Recommendation | Finding | Effort | Impact | Priority |
|---|---------------|---------|--------|--------|----------|
| 1 | [Action] | F1 | S | High | P0 — Do now |
| 2 | [Action] | F3 | M | High | P1 — Next sprint |
| 3 | [Action] | F2 | L | Medium | P2 — Backlog |

## What We Still Don't Know
- [Open questions for future research]
- [Hypotheses to validate]

## Appendix
- Screener criteria
- Interview guide
- Raw data location
- Participant demographics
```

---

## Phase 9: Design Validation

### Design Critique Framework (CAMPS)

| Dimension | Questions to Ask |
|-----------|-----------------|
| **Clarity** | Can users understand what this is and what to do within 5 seconds? |
| **Alignment** | Does this solve the problem identified in research? For the right persona? |
| **Mental Model** | Does it match how users think about this task? (from interview data) |
| **Priority** | Does the visual hierarchy match user task priority? |
| **Simplicity** | Can anything be removed without losing function? |

### Prototype Review Checklist

```yaml
design_review:
  screen: "[Screen name]"
  reviewer: "[Name]"
  date: "YYYY-MM-DD"
  
  research_alignment:
    - check: "Addresses top pain point from research"
      status: "✅ / ❌ / ⚠️"
      notes: "[Which finding this addresses]"
    - check: "Uses language from user interviews (not internal jargon)"
      status: "✅ / ❌ / ⚠️"
    - check: "Matches mental model revealed in research"
      status: "✅ / ❌ / ⚠️"
    - check: "Works for primary persona AND doesn't break for secondary"
      status: "✅ / ❌ / ⚠️"
  
  usability:
    - check: "Primary action is visually dominant"
      status: "✅ / ❌ / ⚠️"
    - check: "Error states designed and messaged"
      status: "✅ / ❌ / ⚠️"
    - check: "Empty states designed (first use, no data, no results)"
      status: "✅ / ❌ / ⚠️"
    - check: "Loading states designed"
      status: "✅ / ❌ / ⚠️"
    - check: "Edge cases handled (long text, missing data, permissions)"
      status: "✅ / ❌ / ⚠️"
  
  accessibility:
    - check: "Color contrast meets WCAG AA (4.5:1 text, 3:1 UI)"
      status: "✅ / ❌ / ⚠️"
    - check: "Touch targets ≥44px"
      status: "✅ / ❌ / ⚠️"
    - check: "Information not conveyed by color alone"
      status: "✅ / ❌ / ⚠️"
    - check: "Logical reading/tab order"
      status: "✅ / ❌ / ⚠️"
    - check: "Alt text for meaningful images"
      status: "✅ / ❌ / ⚠️"
  
  overall_score: "[1-5]"
  ship_decision: "Ready / Needs changes / Needs testing / Needs research"
```

---

## Phase 10: Research Operations

### Research Repository Structure

```
research/
├── YYYY/
│   ├── Q1/
│   │   ├── [study-name]/
│   │   │   ├── plan.yaml          # Research brief
│   │   │   ├── screener.yaml      # Recruiting criteria
│   │   │   ├── guide.md           # Interview/test guide
│   │   │   ├── notes/             # Per-participant notes
│   │   │   │   ├── P01.yaml
│   │   │   │   └── P02.yaml
│   │   │   ├── synthesis/         # Themes, affinity maps
│   │   │   ├── personas/          # Updated personas
│   │   │   ├── journey-maps/      # Updated maps
│   │   │   ├── report.md          # Final report
│   │   │   └── recordings/        # Session recordings (link)
│   │   └── [next-study]/
│   └── Q2/
├── personas/                      # Master persona library
│   ├── persona-a.yaml
│   └── persona-b.yaml
├── journey-maps/                  # Master journey maps
├── insights-database.yaml         # Cross-study insight tracker
└── research-calendar.yaml         # Planned studies
```

### Cross-Study Insight Tracker

```yaml
insights_database:
  - insight_id: "INS-001"
    theme: "[Category]"
    insight: "[The insight]"
    first_found: "2026-01-15"
    studies: ["Study A", "Study C", "Study F"]
    evidence_strength: "Strong"  # 3+ studies
    status: "Addressed"  # Open / In Progress / Addressed / Won't Fix
    design_response: "[What was done]"
    impact_measured: "[Before/after metric if available]"
```

### Research Impact Tracking

| Metric | How to Measure | Target |
|--------|---------------|--------|
| Findings → shipped features | % of recommendations implemented within 2 quarters | >60% |
| Pre/post usability scores | SUS score before vs after changes | +10 points |
| Support ticket reduction | Related ticket volume after design change | -25% |
| Task completion rate | Usability test success rate over time | >85% |
| Time on task | Average task time trend | Decreasing |
| Stakeholder confidence | Post-study survey: "How useful was this?" | >4/5 |

---

## Quick Commands

| Command | What It Does |
|---------|-------------|
| "Plan a research study for [topic]" | Generate research brief YAML |
| "Build a screener for [audience]" | Generate screening questionnaire |
| "Create interview guide for [topic]" | Generate interview questions and structure |
| "Build persona from [data/notes]" | Synthesize data into persona YAML |
| "Map the journey for [persona + goal]" | Generate journey map |
| "Plan usability test for [prototype]" | Generate test plan with tasks |
| "Run heuristic evaluation of [screen/flow]" | Score against Nielsen's 10 |
| "Synthesize findings from [study]" | Generate themes and insights |
| "Write research report for [study]" | Generate executive summary and recommendations |
| "Score this research [report/study]" | Evaluate against quality rubric |
| "Review this design against research" | CAMPS critique + alignment check |
| "Set up research repository" | Create folder structure and templates |

---

## Edge Cases

### Small Budget / No Recruiting Budget
- Guerrilla testing: coffee shop intercepts (5 min tests, buy them a coffee)
- Internal users: use colleagues from different departments (not product/design team)
- Social media: post in relevant communities for volunteers
- Existing users: email opt-in for research panel

### Remote-Only Research
- Video call with screen share (Zoom, Google Meet)
- Async: Loom recordings of tasks + written responses
- Unmoderated: UserTesting.com, Maze, Lookback
- Diary studies: use messaging apps (WhatsApp, Telegram) for daily check-ins

### Stakeholder Pushback ("We don't have time for research")
- "5 users, 1 week, 3 critical findings" — the minimum viable study
- Pair research with existing touchpoints (support calls, sales demos)
- Frame as risk reduction: "Would you rather discover this before or after launch?"
- Show past research ROI (support ticket reduction, conversion improvement)

### Conflicting Findings
- Check sample composition — different segments may have different needs
- Prioritize by business impact: which segment is more valuable?
- Run a survey to quantify: "60% prefer A, 40% prefer B"
- Consider designing for both (progressive disclosure, personalization)

### International / Cross-Cultural Research
- Don't just translate — localize scenarios and contexts
- Account for cultural response bias (e.g., reluctance to criticize in some cultures)
- Use local moderators when possible
- Adjust incentives to local norms
- Watch for design patterns that don't transfer (icons, colors, reading direction)

### Accessibility Research
- Recruit participants with disabilities (screen reader users, motor impairments, cognitive differences)
- Test with actual assistive technology, not simulation
- Include in regular studies (at least 1 participant with accessibility needs per study)
- WCAG compliance testing is NOT a substitute for research with disabled users

---

*Built by AfrexAI — Autonomous Intelligence for Business*
