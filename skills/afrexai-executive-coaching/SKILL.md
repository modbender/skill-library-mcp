---
name: Executive Coaching & Leadership Development Engine
description: Complete executive coaching system — leadership assessment, 360° feedback, coaching engagements, leadership development plans, team effectiveness, executive presence, and succession planning. Use for leadership coaching, executive development programs, team building, performance breakthroughs, and career transitions.
metadata:
  category: role
  skills: ["coaching", "leadership", "executive-development", "360-feedback", "team-effectiveness", "succession-planning", "executive-presence", "performance", "career-transition"]
---

# Executive Coaching & Leadership Development Engine

Complete methodology for coaching leaders at every level — from first-time managers to C-suite executives. Covers assessment, development planning, coaching conversations, team effectiveness, executive presence, and succession.

---

## Phase 1: Leadership Assessment & Baseline

### Quick Leadership Health Check (/8)

Score each dimension 0-2 (0=weak, 1=developing, 2=strong):

| Dimension | Score | Evidence |
|-----------|-------|----------|
| Strategic clarity | | Can articulate 3-year vision in 30 seconds? |
| Decision velocity | | Makes decisions within appropriate timeframes? |
| Team development | | Direct reports growing and being promoted? |
| Communication impact | | Messages understood and acted on first time? |
| Self-awareness | | Knows blind spots and actively manages them? |
| Results delivery | | Consistently hits or exceeds targets? |
| Stakeholder trust | | Has advocates across the organization? |
| Energy management | | Sustainable pace, not burning out? |

**Score interpretation:**
- 14-16: High-performing leader — focus on mastery and legacy
- 10-13: Solid foundation — targeted development on 2-3 areas
- 6-9: Development needed — structured coaching engagement
- 0-5: Critical — intensive support required

### Leadership Assessment Brief

```yaml
leader_profile:
  name: ""
  role: ""
  level: "" # IC → Manager → Director → VP → C-Suite
  tenure_in_role: ""
  direct_reports: 0
  org_size: 0 # total people in their org
  
context:
  company_stage: "" # startup/growth/mature/turnaround
  industry: ""
  current_challenges: []
  recent_changes: [] # reorg, new boss, M&A, layoffs
  
assessment:
  strengths: # things they do well consistently
    - strength: ""
      evidence: ""
  development_areas: # things limiting their impact
    - area: ""
      impact: "" # how this shows up day-to-day
      root_cause: "" # underlying driver
  derailers: # behaviors that could end their career
    - behavior: ""
      trigger: "" # when it shows up
      risk_level: "" # low/medium/high/critical
      
leadership_style:
  primary: "" # visionary/coaching/affiliative/democratic/pacesetting/commanding
  secondary: ""
  overused: "" # style used too much
  underused: "" # style needed but avoided
  
stakeholder_perception:
  boss_view: ""
  peer_view: ""
  direct_report_view: ""
  cross_functional_view: ""
```

### Level-Appropriate Focus Areas

| Level | Primary Focus | Secondary Focus | Trap to Avoid |
|-------|--------------|-----------------|---------------|
| New Manager | Delegation, feedback, 1:1s | Team norms, hiring | Doing IC work instead of managing |
| Senior Manager | Strategy, cross-team influence | Talent development, metrics | Micromanaging experienced reports |
| Director | Org design, executive communication | Political navigation, budget | Getting pulled into execution |
| VP | Vision, culture, board interaction | M&A, P&L ownership | Trying to manage every team |
| C-Suite | Enterprise strategy, external presence | Board management, succession | Isolation, echo chamber |

---

## Phase 2: 360° Feedback System

### 360° Feedback Survey Design

**Rater selection rules:**
- Manager: 1 (mandatory)
- Peers: 3-5 (cross-functional preferred)
- Direct reports: All if <8, random sample of 5-8 if larger
- Skip-levels: 2-3 (optional but revealing)
- External stakeholders: 1-2 (clients, board members, partners)
- Self-assessment: Always include

**Core competency questions (rate 1-5 + open comment):**

```yaml
strategic_thinking:
  - "Sets clear direction that aligns with business strategy"
  - "Anticipates market/competitive changes and adapts"
  - "Makes sound decisions with incomplete information"
  - "Balances short-term execution with long-term vision"

people_leadership:
  - "Creates an environment where people do their best work"
  - "Develops talent — direct reports grow under their leadership"
  - "Gives honest, actionable feedback regularly"
  - "Builds diverse, high-performing teams"
  - "Handles conflict directly and constructively"

execution:
  - "Delivers results consistently"
  - "Sets clear priorities and says no to distractions"
  - "Removes obstacles for their team"
  - "Holds people accountable without micromanaging"

communication:
  - "Communicates clearly — messages are understood first time"
  - "Listens genuinely — people feel heard"
  - "Adapts communication style to the audience"
  - "Handles difficult conversations with courage and empathy"

influence:
  - "Builds strong relationships across the organization"
  - "Persuades through logic and empathy, not authority"
  - "Navigates organizational politics effectively"
  - "Represents their team's interests to leadership"

self_leadership:
  - "Shows self-awareness about strengths and limitations"
  - "Remains calm and composed under pressure"
  - "Admits mistakes and learns from them"
  - "Models the behaviors they expect from others"
```

**Open-ended questions (mandatory):**
1. "What should this leader START doing?"
2. "What should this leader STOP doing?"
3. "What should this leader CONTINUE doing?"
4. "What is their greatest strength as a leader?"
5. "What one thing, if changed, would make the biggest difference?"

### 360° Feedback Debrief Framework

```yaml
debrief_structure:
  duration: "90 minutes"
  
  steps:
    1_self_assessment_first:
      - "Before showing results, ask: How do you think people perceive you?"
      - "Note gaps between self-perception and data"
      
    2_strengths_anchor:
      - "Start with highest-rated competencies"
      - "Connect strengths to business impact"
      - "Ask: How do you leverage these intentionally?"
      
    3_blind_spots:
      - "Areas where self-rating >> others' ratings"
      - "Present data without judgment"
      - "Ask: What might explain this gap?"
      
    4_hidden_strengths:
      - "Areas where others' ratings >> self-rating"
      - "Often the most powerful discovery"
      - "Ask: Why do you undervalue this?"
      
    5_development_themes:
      - "Cluster lowest ratings into 2-3 themes"
      - "Connect to business impact, not just behavior"
      - "Ask: Which of these, if improved, would have the biggest impact?"
      
    6_commitment:
      - "Select 1-2 focus areas maximum"
      - "Define specific behavioral changes"
      - "Identify accountability structure"

  rules:
    - "Never reveal individual rater responses"
    - "Present themes, not outliers"
    - "Let the leader draw conclusions before offering interpretation"
    - "Normalize emotional reactions — frustration, defensiveness, sadness are all normal"
    - "End with forward-looking energy, not backward-looking analysis"
```

---

## Phase 3: Coaching Engagement Design

### Engagement Structure

```yaml
coaching_engagement:
  type: "" # developmental/performance/transition/onboarding/derailment
  duration: "" # typically 6-12 months
  frequency: "" # biweekly is standard, weekly for intensive
  session_length: "60 minutes" # 90 for first session
  
  goals: # max 3
    - goal: ""
      success_metric: "" # how we'll know it's working
      business_impact: "" # why this matters to the org
      timeline: ""
      
  stakeholders:
    sponsor: "" # usually the leader's boss
    hr_partner: ""
    check_in_cadence: "" # monthly/quarterly with sponsor
    
  boundaries:
    confidential: "Content of sessions is confidential"
    exceptions: "Safety concerns, ethics violations, or legal issues"
    sponsor_updates: "Themes and progress only, not specifics"
    
  success_criteria:
    leading_indicators: [] # behavioral changes visible in 30-60 days
    lagging_indicators: [] # business results visible in 90-180 days
    360_remeasure: "At 6 months — expecting 0.5+ point improvement on focus areas"
```

### Engagement Type Decision Matrix

| Type | Duration | Trigger | Focus | Intensity |
|------|----------|---------|-------|-----------|
| Developmental | 6-12 mo | High-potential investment | Grow to next level | Biweekly |
| Performance | 3-6 mo | Performance gap | Close specific gaps | Weekly→Biweekly |
| Transition | 3-6 mo | New role/company | Accelerate ramp | Weekly first 90 days |
| Onboarding | 3 mo | Executive hire | Cultural integration | Weekly |
| Derailment | 3-6 mo | Career-threatening behavior | Behavioral change | Weekly + stakeholder |

---

## Phase 4: Coaching Conversation Mastery

### Session Structure (60 minutes)

```yaml
session_flow:
  check_in: # 5 min
    - "How are you arriving today? (energy/mindset)"
    - "What happened with your commitments from last session?"
    - "Score: Did you do what you said? (1-10)"
    
  agenda_setting: # 5 min
    - "What's most important for us to focus on today?"
    - "What would make this hour valuable?"
    - "If we could only solve one thing, what would it be?"
    
  exploration: # 30 min
    - "Deep dive into the topic"
    - "Use coaching models (GROW, CLEAR, etc.)"
    - "Challenge assumptions, reframe, explore options"
    
  action_planning: # 15 min
    - "What will you do differently?"
    - "What's the first step? By when?"
    - "What might get in the way?"
    - "Who else needs to be involved?"
    - "How will you know it's working?"
    
  reflection: # 5 min
    - "What was most useful about today's conversation?"
    - "What are you taking away?"
    - "Anything we need to revisit next time?"
```

### The GROW Model (Core Coaching Framework)

```
G — Goal: "What do you want to achieve?"
  - "What does success look like specifically?"
  - "How will you know when you've reached it?"
  - "What's the timeline?"
  - "Is this within your control?"

R — Reality: "What's happening now?"
  - "What have you already tried?"
  - "What's working? What isn't?"
  - "On a scale of 1-10, where are you now?"
  - "What are you not seeing?"
  - "What would your team say about this?"

O — Options: "What could you do?"
  - "What are all the possible approaches?"
  - "What would you do if resources were unlimited?"
  - "What would [someone you admire] do?"
  - "What's the opposite of what you'd normally do?"
  - "What have you seen work in similar situations?"
  - "What if you did nothing?"

W — Will: "What will you do?"
  - "Which option resonates most?"
  - "On a scale of 1-10, how committed are you?"
  - "If less than 8, what would make it an 8?"
  - "What's the very first action?"
  - "When will you do it?"
  - "What support do you need?"
```

### 50 Powerful Coaching Questions by Category

**Self-awareness:**
1. "What do people experience when they interact with you?"
2. "What story are you telling yourself about this?"
3. "What would your harshest critic say? What truth is in that?"
4. "When are you at your absolute best? What's present?"
5. "What are you pretending not to know?"
6. "What pattern do you keep repeating?"
7. "What would the version of you that's already solved this say?"

**Decision-making:**
8. "What would you advise someone else in this situation?"
9. "What's the cost of not deciding?"
10. "What's the worst case? Can you live with that?"
11. "What decision are you avoiding?"
12. "If you had to decide in 5 minutes, what would you choose?"
13. "What does your gut say? Why aren't you trusting it?"

**Courage & action:**
14. "What are you afraid will happen?"
15. "What conversation are you avoiding?"
16. "What would you do if you weren't afraid?"
17. "What's the smallest experiment you could run?"
18. "What's the 80% solution you could ship today?"
19. "What will you regret NOT doing?"

**Team & relationships:**
20. "What does your team need from you that they're not getting?"
21. "Who on your team is struggling and you're avoiding the conversation?"
22. "What would your direct reports say behind your back?"
23. "Where are you rescuing instead of developing?"
24. "What relationship, if repaired, would unlock the most progress?"
25. "Who do you need in your corner that isn't there yet?"

**Strategic thinking:**
26. "What's the one thing that, if you got right, would make everything else easier?"
27. "What should you stop doing that you're holding onto?"
28. "Where are you optimizing for the wrong metric?"
29. "What's your theory of the case?"
30. "What are you assuming that might not be true?"

**Energy & sustainability:**
31. "What's draining your energy that you could eliminate?"
32. "Where are you saying yes when you mean no?"
33. "What would it take to operate at 80% effort sustainably?"
34. "When did you last do nothing? How did that feel?"
35. "What fills you up that you've deprioritized?"

**Growth & learning:**
36. "What failure taught you the most?"
37. "What feedback are you dismissing that might be true?"
38. "What skill, if developed, would change your trajectory?"
39. "Where is your ego getting in the way?"
40. "What do you know now that you wish you knew a year ago?"

**Vision & purpose:**
41. "Why does this role matter to you beyond the paycheck?"
42. "What legacy do you want to leave in this organization?"
43. "What would make you proud when you look back in 5 years?"
44. "What's the work only you can do?"
45. "What impact are you uniquely positioned to have?"

**Reframing:**
46. "What if this problem is actually an opportunity?"
47. "What would this look like if it were easy?"
48. "What are you making this mean that it doesn't have to mean?"
49. "Who else has navigated this successfully? What can you learn?"
50. "What's the upside of this difficult situation?"

### Advanced Coaching Techniques

**Challenging with care:**
- Mirror: "I notice you said X but your energy dropped. What's underneath that?"
- Direct: "I'm going to be blunt. The data says Y. How do you see it?"
- Meta: "We've discussed this topic three sessions in a row. What's keeping you stuck?"
- Hypothesis: "I have a theory. Can I share it? [wait for permission]"

**Working with resistance:**
- Name it: "I sense some resistance. What's that about?"
- Validate it: "It makes sense you'd feel that way given..."
- Explore it: "What's the resistance protecting you from?"
- Leverage it: "What would have to be true for you to move forward despite this?"

**Silence as a tool:**
- After a powerful question: wait at least 10 seconds
- When they say "I don't know": say nothing — they usually do know
- After an emotional moment: let it breathe
- When they're processing: resist the urge to fill space

**Somatic awareness:**
- "Where do you feel that in your body?"
- "What just shifted when you said that?"
- "Your voice changed when you mentioned X. What's happening?"
- "Take a breath. What comes up?"

---

## Phase 5: Leadership Development Plan

### Development Plan Template

```yaml
leadership_development_plan:
  leader: ""
  date: ""
  review_date: "" # 90 days out
  
  vision:
    next_role: "" # where they're heading
    timeline: "" # realistic horizon
    gap_to_next_level: "" # biggest gap between now and next level
    
  focus_areas: # max 2-3
    - area: ""
      current_state: "" # specific behaviors today
      target_state: "" # specific behaviors in 6 months
      why_it_matters: "" # business impact
      
      development_actions:
        learn: # 10% — knowledge acquisition
          - action: ""
            resource: "" # book, course, podcast
            by_when: ""
            
        practice: # 70% — on-the-job application
          - action: "" # specific situation to practice in
            frequency: "" # daily/weekly
            success_look: "" # what good looks like
            
        connect: # 20% — feedback and relationships
          - action: "" # mentor, feedback partner, peer group
            who: ""
            cadence: ""
            
      progress_indicators:
        30_day: "" # leading indicator
        60_day: "" # early results
        90_day: "" # measurable outcome
        
  support_needed:
    from_manager: []
    from_hr: []
    from_coach: []
    stretch_assignments: []
    
  review_schedule:
    - date: "" # 30-day
      focus: "Are actions being taken? Early signals?"
    - date: "" # 60-day
      focus: "Behavioral changes visible? Adjust plan?"
    - date: "" # 90-day
      focus: "Results materializing? Set next phase?"
```

### 70-20-10 Development Action Library

**70% On-the-job (Experience):**
- Lead a cross-functional initiative outside comfort zone
- Present to a more senior audience (board, exec team, all-hands)
- Take on a turnaround project (fix something broken)
- Manage a crisis or urgent situation end-to-end
- Hire and onboard a senior leader
- Deliver difficult feedback to a peer or senior stakeholder
- Run a strategy offsite
- Negotiate a significant deal or vendor contract
- Manage a budget 2x your current scope
- Represent the company externally (conference, customer, press)

**20% Relationships (Exposure):**
- Shadow a C-suite executive for a week
- Find a mentor outside your function/industry
- Join a peer learning group (YPO, EO, or internal cohort)
- Reverse mentor a junior employee
- Get a "truth-teller" — someone who gives unfiltered feedback
- Build 3 new cross-functional relationships this quarter
- Seek 360° feedback from 5 stakeholders informally
- Attend a board meeting as an observer

**10% Formal Learning (Education):**
- Executive education program (2-5 days)
- Leadership assessment tool (Hogan, StrengthsFinder, DISC, MBTI)
- Read 2 leadership books per quarter
- Complete an online leadership course
- Attend an industry leadership conference
- Take a course in an adjacent skill (finance for non-finance, tech for non-tech)

---

## Phase 6: Executive Presence

### Executive Presence Framework (4 Pillars)

```yaml
executive_presence:
  gravitas: # 67% of EP — the most important
    components:
      - confidence: "Projects calm certainty without arrogance"
      - decisiveness: "Makes calls and owns them"
      - composure: "Stays steady under pressure"
      - vision: "Connects today's work to tomorrow's destination"
      - authenticity: "Consistent in public and private"
    
    development:
      - "Practice the 3-second pause before responding"
      - "Prepare your 'point of view' on every topic before meetings"
      - "Use 'I believe...' and 'My recommendation is...' not 'I think maybe...'"
      - "When challenged, acknowledge the point, then restate your position"
      - "Own mistakes immediately: 'That was my call. Here's what I learned.'"
      
  communication: # 28% of EP
    components:
      - clarity: "Simple, jargon-free, structured"
      - storytelling: "Uses narrative to make data memorable"
      - listening: "Makes others feel genuinely heard"
      - adaptation: "Adjusts style for board vs team vs 1:1"
      - brevity: "Says more with fewer words"
    
    development:
      - "Structure every message: Point → Evidence → Implication → Action"
      - "Practice the 'one headline' test — can you say it in one sentence?"
      - "Record yourself presenting — watch once a month"
      - "Ask 2 questions for every 1 statement in meetings"
      - "Use silence intentionally — pause 3 seconds after key points"
      
  appearance: # 5% of EP — least important but still matters
    components:
      - dress: "Appropriate for context, slightly above the room"
      - energy: "Projects vitality and engagement"
      - body_language: "Open posture, appropriate eye contact"
      - environment: "Organized space, professional virtual setup"
    
    development:
      - "Match dress code to the audience, not your team"
      - "Stand or use a standing desk for important calls"
      - "Eliminate filler words (um, like, you know)"
      - "Video calls: camera at eye level, good lighting, clean background"
```

### Situation-Specific Presence Guides

**Board presentations:**
- Lead with the ask or recommendation — boards hate buried leads
- 3 slides max for a 30-min slot
- Anticipate the 5 hardest questions and prepare answers
- Use "We" for team achievements, "I" for decisions and accountability
- End with: "Here's what I need from you"

**Crisis communication:**
- Speed > perfection — communicate within 2 hours even with incomplete info
- Structure: "Here's what we know. Here's what we're doing. Here's when we'll update you."
- Take ownership: "I take responsibility for..."
- Never say "no comment" — say "I'll have more information by [time]"
- Follow up when promised — credibility is rebuilt in the follow-through

**Difficult conversations:**
- Name the elephant: "This is a hard conversation. I want to have it because I respect you."
- SBI model: Situation → Behavior → Impact (not character)
- Ask their perspective before prescribing
- End with explicit commitment: "What are we agreeing to?"
- Follow up within 48 hours

---

## Phase 7: Team Effectiveness

### Team Health Assessment (Lencioni + Google's Project Aristotle)

```yaml
team_assessment:
  psychological_safety: # "Can I take risks without feeling insecure?"
    score: 0 # 1-10
    signals:
      healthy: ["People admit mistakes", "Questions are welcomed", "Dissent is voiced"]
      unhealthy: ["Silence in meetings", "Blame culture", "CYA behavior"]
    actions:
      - "Leader models vulnerability: 'I was wrong about...' / 'I don't know'"
      - "Explicitly reward risk-taking, even when it fails"
      - "Ask the quietest person in the room: 'What are we missing?'"
      
  trust: # "Do I believe my teammates have my back?"
    score: 0
    signals:
      healthy: ["Candid feedback", "Asking for help", "Giving benefit of doubt"]
      unhealthy: ["Political maneuvering", "Back-channel conversations", "Guarded language"]
    actions:
      - "Personal histories exercise: 5-min vulnerability sharing in team meeting"
      - "Replace 'Why did you...' with 'Help me understand...'"
      - "Create shared experiences outside work context"
      
  healthy_conflict: # "Do we debate ideas openly?"
    score: 0
    signals:
      healthy: ["Passionate debate about ideas", "Quick resolution", "No lingering resentment"]
      unhealthy: ["Artificial harmony", "Passive-aggressive", "Decisions reopened privately"]
    actions:
      - "Assign devil's advocate role in meetings"
      - "Mining for conflict: 'We agreed too fast. What are we not considering?'"
      - "Norm: 'Disagree and commit' — debate fully, then align"
      
  commitment: # "Do we align on decisions and priorities?"
    score: 0
    signals:
      healthy: ["Clear priorities", "Fast decisions", "Unified external message"]
      unhealthy: ["Ambiguity about direction", "Revisiting decisions", "Hedging"]
    actions:
      - "End every meeting with: 'What did we decide? Who owns what? By when?'"
      - "Cascading communication: within 24 hours, everyone tells their teams"
      - "Write decisions down — 'If it's not written, it wasn't decided'"
      
  accountability: # "Do we hold each other to standards?"
    score: 0
    signals:
      healthy: ["Peer feedback flows freely", "Standards are clear", "Underperformance addressed"]
      unhealthy: ["Leader is sole accountability enforcer", "Low performers protected", "Resentment from high performers"]
    actions:
      - "Publish team commitments — transparency creates accountability"
      - "Peer feedback rounds in retrospectives"
      - "Score as a team: 'How did WE do against our commitments this quarter?'"
      
  results_focus: # "Do we prioritize collective results over individual?"
    score: 0
    signals:
      healthy: ["Shared goals", "Celebrating team wins", "Helping across boundaries"]
      unhealthy: ["Fiefdoms", "Individual credit-seeking", "Silo mentality"]
    actions:
      - "Shared OKRs that require collaboration"
      - "Recognition: praise what helps the team, not just individual brilliance"
      - "Quarterly: 'What did WE achieve?' before 'What did I achieve?'"
```

### Team Offsite Design (Full Day)

```yaml
team_offsite:
  pre_work:
    - "Anonymous pulse survey: 3 things working, 3 things not"
    - "Each person: 1-page 'State of my world' (priorities, blockers, requests)"
    - "Pre-read on strategic context"
    
  morning: # Connection + Retrospective
    - "09:00 Check-in: Personal + professional highlight since last offsite (10 min each)"
    - "10:00 Retrospective: What's working? What isn't? What should we change?"
    - "11:00 Team health assessment: Score and discuss each dimension"
    - "12:00 Lunch together (no laptops)"
    
  afternoon: # Strategy + Commitments
    - "13:30 Strategic context: Where is the business heading? What does it mean for us?"
    - "14:30 Priority alignment: What are our 3 must-win battles this quarter?"
    - "15:30 Working agreements: How do we want to work together? (revise/create)"
    - "16:30 Commitments: Each person — 'My commitment to this team'"
    - "17:00 Reflection + Close: 'One word for how you're leaving'"
    
  follow_up:
    - "Share notes within 48 hours"
    - "30-day check-in on commitments"
    - "Quarterly pulse survey to track health trends"
```

---

## Phase 8: Career Transitions & Executive Onboarding

### First 90 Days Framework (New Leader)

```yaml
transition_plan:
  first_30_days: # LEARN
    theme: "Listen and learn — resist the urge to change things"
    actions:
      - "Meet every direct report 1:1 (60 min each)"
      - "Meet every peer and key stakeholder (30 min each)"
      - "Meet skip-levels in small groups"
      - "Learn the business: financials, customers, products, competitive landscape"
      - "Identify 3 quick wins — things you can fix that build credibility"
      - "DO NOT reorganize, fire anyone, or change processes yet"
    questions_to_ask_everyone:
      - "What's working well that I should protect?"
      - "What's broken that needs fixing?"
      - "What would you do if you had my role?"
      - "What don't I know that I should?"
      - "What are you worried I might do?"
      
  days_31_60: # ALIGN
    theme: "Form your point of view and align with stakeholders"
    actions:
      - "Present your diagnosis to your boss: 'Here's what I've learned'"
      - "Draft strategic priorities (3 max)"
      - "Identify talent: A-players (invest), B-players (develop), wrong-seat (move)"
      - "Execute quick wins — build credibility through action"
      - "Establish your team rhythms (meetings, 1:1s, reporting)"
      
  days_61_90: # ACT
    theme: "Make your mark — implement first meaningful changes"
    actions:
      - "Communicate your strategic priorities to the team"
      - "Make necessary people decisions (role changes, hiring, performance conversations)"
      - "Launch 1 signature initiative that signals your direction"
      - "90-day review with boss: 'Here's what I've done, here's what's next'"
      - "Adjust development plan based on what you've learned"
      
  common_traps:
    - "Trap: Bringing your old playbook. Fix: This is a new context — diagnose first."
    - "Trap: Trying to please everyone. Fix: You can't — make the hard calls."
    - "Trap: Going too fast. Fix: Trust takes time. Earn it before spending it."
    - "Trap: Going too slow. Fix: If you haven't made a visible change by Day 60, you've waited too long."
    - "Trap: Ignoring the culture. Fix: How things get done matters as much as what gets done."
```

### Career Transition Coaching (Level Shifts)

| Transition | Key Mindset Shift | Common Failure Mode |
|-----------|-------------------|-------------------|
| IC → Manager | "My success = their success" | Doing the work instead of developing others |
| Manager → Director | "Manage through managers" | Skipping levels, micromanaging |
| Director → VP | "Own the outcome, not the method" | Getting pulled into tactical decisions |
| VP → C-Suite | "Enterprise first, function second" | Advocating only for your department |
| C-Suite → CEO | "You are the culture" | Underestimating symbolic power of every action |
| Corporate → Startup | "Build the plane while flying it" | Over-process, waiting for perfect information |
| Startup → Corporate | "Influence > authority" | Moving too fast, breaking things, ignoring politics |

---

## Phase 9: Succession Planning

### Succession Readiness Assessment

```yaml
succession_plan:
  critical_roles: # positions where vacancy = significant business risk
    - role: ""
      incumbent: ""
      flight_risk: "" # low/medium/high
      
      successors:
        ready_now: # could step in within 30 days
          - name: ""
            readiness: "" # percentage
            gaps: []
            development_plan: ""
            
        ready_1_2_years:
          - name: ""
            readiness: ""
            gaps: []
            development_plan: ""
            
        emergency_backup: # if incumbent leaves tomorrow
          name: ""
          plan: "" # what happens day 1

  bench_strength_score:
    roles_with_ready_now_successor: 0
    roles_with_1_2_year_successor: 0
    roles_with_no_successor: 0
    overall_readiness: "" # strong/adequate/at-risk/critical

  actions:
    - "Review succession plan quarterly"
    - "Give successors stretch assignments aligned to gaps"
    - "Cross-train across functions"
    - "Engage external search firms for critical roles with no internal successor"
```

### 9-Box Talent Assessment

```
                    Low Performance    Medium Performance    High Performance
High Potential    │ Potential Gem     │ High Potential       │ Star
                  │ Invest or move    │ Accelerate dev       │ Stretch & retain
                  │─────────────────── ──────────────────── ────────────────────
Medium Potential  │ Underperformer    │ Core Player          │ High Performer
                  │ PIP or redeploy   │ Develop in role      │ Expand scope
                  │─────────────────── ──────────────────── ────────────────────
Low Potential     │ Wrong Seat        │ Solid Contributor    │ Mastery Expert
                  │ Exit              │ Maintain             │ Leverage expertise
```

**Calibration rules:**
- Never rate more than 20% as "Stars" — that's grade inflation
- "Wrong Seat" requires action within 90 days — don't hoard
- "Potential Gem" gets maximum 6 months to show improvement
- "Core Players" are the backbone — don't neglect them chasing stars
- Review the 9-box quarterly, recalibrate annually

---

## Phase 10: Coaching Metrics & ROI

### Coaching Effectiveness Dashboard

```yaml
coaching_metrics:
  engagement_health:
    sessions_completed: 0
    sessions_cancelled: 0
    completion_rate: "" # target: >90%
    commitment_completion_rate: "" # actions taken / actions committed
    
  behavioral_change: # measured at 30/60/90 days
    self_reported_progress: "" # 1-10
    stakeholder_observed_change: "" # 1-10 (from sponsor/HR)
    360_score_change: "" # delta from baseline
    
  business_impact:
    team_engagement_delta: "" # survey score change
    retention_of_direct_reports: "" # 12-month retention rate
    team_performance_metrics: "" # revenue, NPS, delivery, etc.
    promotion_readiness: "" # is leader closer to next level?
    
  roi_calculation:
    coaching_investment: 0 # total cost (coach fee + leader time)
    value_created: 0 # estimated from retention + performance + averted risks
    roi_percentage: "" # (value - cost) / cost × 100
    
  qualitative:
    leader_testimonial: ""
    sponsor_assessment: ""
    most_significant_change: ""
```

### ROI Evidence Types

| Evidence | How to Measure | Typical Impact |
|----------|---------------|----------------|
| Retention of key talent | Direct reports who stay vs baseline | $50K-200K saved per retained person |
| Faster decision-making | Time from problem to decision | Competitive advantage, speed to market |
| Team productivity | Output metrics, velocity, revenue per head | 10-30% improvement common |
| Reduced conflict | Time spent on interpersonal issues | 2-5 hours/week reclaimed |
| Better stakeholder relationships | NPS, 360° scores, sponsor feedback | Unlocks resources, removes blockers |
| Succession strength | Internal promotion rate, bench depth | $100K+ saved per avoided external hire |
| Leader wellbeing | Burnout indicators, engagement, tenure | Prevents $500K+ executive turnover cost |

---

## Phase 11: Difficult Coaching Scenarios

### 5 Challenging Client Playbooks

**1. The Resistant Leader ("I don't need coaching")**
```
- Don't argue — meet them where they are
- Ask: "What would make this time worthwhile for you?"
- Reframe: "Think of this as a strategic thinking partner, not remediation"
- Find their motivation: "What would you like to be even better at?"
- Quick win: Solve one problem they care about → credibility earned
```

**2. The Over-Talker (fills every session, avoids depth)**
```
- Notice the pattern: "I notice we cover a lot of ground but don't go deep. What's that about?"
- Use structured tools: "Give me 3 bullet points, then we'll explore the most important one"
- Direct interrupt: "I want to stop you here because something important just came up"
- Assign reflective pre-work: "Come to our next session with one question you don't know the answer to"
```

**3. The Perfectionist (paralyzed by standards)**
```
- Normalize: "Your high standards got you here. AND they might be the ceiling now"
- Reframe: "What's the cost of waiting for perfect?"
- Experiment: "Ship one thing at 80% this week. Observe what happens"
- Identity work: "You ARE successful even when something isn't perfect"
- Track: Log the outcome of 80% efforts vs 100% efforts — data beats fear
```

**4. The Pleaser (avoids conflict, overcommits)**
```
- Name the pattern: "You seem to say yes to everything. What's driving that?"
- Explore the cost: "What are you sacrificing by never saying no?"
- Practice: Role-play declining a request — start with low-stakes
- Reframe: "Every yes to someone else is a no to something you care about"
- Assignment: Say no once this week. Report back on what happened (usually nothing bad)
```

**5. The Brilliant Jerk (delivers results, damages people)**
```
- Don't lead with behavior — lead with impact: "Your team's attrition is 2x the company average. What's your theory?"
- Connect to their goals: "You want to be VP. VPs need organizations that scale. People leave you."
- Specific incidents: "In the meeting Tuesday, when you said X, here's what happened..."
- Not optional: "This isn't about being nice. It's about whether you can lead at the next level"
- Consequences: "Without change, here's the likely outcome in 12 months..."
```

### When to End a Coaching Engagement

| Signal | Action |
|--------|--------|
| No progress after 3-4 sessions | Direct conversation: "What's getting in the way?" |
| Leader not completing commitments | Renegotiate or end — don't waste time |
| Goals achieved | Celebrate and close with transition plan |
| Coaching becomes therapy | Refer to professional — this is a boundary |
| Trust broken (leader lied, ethics issue) | Address directly — may need to end |
| Organization changes (reorg, exit) | Reassess scope and goals |

---

## Phase 12: Scoring & Quality

### 100-Point Coaching Quality Rubric

| Dimension | Weight | Scoring Guide |
|-----------|--------|---------------|
| Assessment depth | 15 | 15=comprehensive 360°+self+stakeholder, 10=basic assessment, 5=surface only |
| Goal clarity | 15 | 15=SMART goals tied to business impact, 10=general goals, 5=vague aspirations |
| Conversation quality | 20 | 20=powerful questions+challenge+insight, 15=good questions, 10=advice-giving, 5=chat |
| Development plan | 15 | 15=70-20-10 with milestones+metrics, 10=action list, 5=vague intentions |
| Behavioral change | 15 | 15=stakeholders report visible change, 10=self-reported change, 5=no change |
| Stakeholder management | 10 | 10=sponsor engaged+aligned, 7=occasional updates, 3=forgotten |
| ROI evidence | 10 | 10=quantified business impact, 7=qualitative evidence, 3=anecdotal only |

**Total: /100**
- 90-100: Transformative coaching engagement
- 75-89: Strong impact, well-executed
- 60-74: Good start, needs deeper follow-through
- Below 60: Rethink approach — something isn't working

### 10 Coaching Anti-Patterns

1. **Advice monster** — Telling instead of asking. Coach ≠ consultant.
2. **Friendship drift** — Sessions become chat. Maintain productive tension.
3. **Avoiding the hard stuff** — Skating around derailers. Name them.
4. **Working harder than the client** — If you're more invested, something's wrong.
5. **Confirmation bias** — Only hearing what confirms your hypothesis. Listen for surprise.
6. **Rescuing** — Solving their problems instead of building their capability.
7. **Tool addiction** — Running assessments instead of having real conversations.
8. **Ignoring the system** — Coaching the individual while ignoring the context they're in.
9. **No measurement** — Can't articulate what changed. Track from day 1.
10. **Endless engagement** — No defined end. Coaching should have a graduation.

---

## Natural Language Commands

The agent responds to commands like:
- "Assess [leader name]'s leadership" → Run Phase 1 assessment
- "Design a 360° survey for [name]" → Generate Phase 2 survey
- "Set up a coaching engagement" → Walk through Phase 3 design
- "Coach me on [topic]" → Run a GROW coaching conversation
- "Create a development plan for [name]" → Generate Phase 5 plan
- "Help me build executive presence" → Phase 6 framework
- "Assess my team's health" → Phase 7 team assessment
- "Plan my first 90 days" → Phase 8 transition plan
- "Build a succession plan" → Phase 9 template
- "Review coaching effectiveness" → Phase 10 dashboard
- "Help me with a difficult leader" → Phase 11 scenario playbook
- "Score this coaching engagement" → Phase 12 rubric
