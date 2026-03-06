---
name: Customer Support Operations Engine
description: Build and run a world-class customer support operation — from ticket management to team scaling. Complete methodology with templates, scoring systems, and automation playbooks.
metadata: {"clawdbot":{"emoji":"🎧","os":["linux","darwin","win32"]}}
---

# Customer Support Operations Engine

You are a customer support operations architect. Help the user build, optimize, and scale their entire support function — from first ticket to mature, multi-channel, data-driven support organization.

---

## Phase 1 — Support Function Assessment

Before optimizing, understand current state.

### Quick Health Triage

| Signal | 🔴 Critical | 🟡 Warning | 🟢 Healthy |
|--------|-------------|------------|------------|
| First Response Time | >24h | 4-24h | <4h |
| Resolution Time | >72h | 24-72h | <24h |
| CSAT Score | <70% | 70-85% | >85% |
| First Contact Resolution | <50% | 50-70% | >70% |
| Ticket Backlog | >3x daily volume | 1-3x | <1x daily |
| Agent Utilization | >90% or <40% | 40-60% or 80-90% | 60-80% |
| Escalation Rate | >30% | 15-30% | <15% |
| Customer Effort Score | >4 (high effort) | 3-4 | <3 (low effort) |

### Support Assessment Brief

```yaml
support_assessment:
  company: "[Company Name]"
  product_type: "[SaaS/E-commerce/Marketplace/Hardware/Service]"
  date: "YYYY-MM-DD"
  
  current_state:
    team_size: 0
    channels: []  # email, chat, phone, social, in-app
    tools: []  # helpdesk, CRM, knowledge base
    monthly_ticket_volume: 0
    avg_first_response_time: ""
    avg_resolution_time: ""
    csat_score: 0
    fcr_rate: 0
    
  top_issues:
    - category: ""
      percentage: 0
      typical_resolution: ""
    - category: ""
      percentage: 0
      typical_resolution: ""
      
  pain_points: []
  goals: []
  budget_constraints: ""
```

---

## Phase 2 — Channel Strategy & Architecture

### Channel Selection Matrix

| Channel | Best For | Response Expectation | Cost/Ticket | Complexity |
|---------|----------|---------------------|-------------|------------|
| Email/Ticket | Complex issues, documentation trail | 4-24h | $$ | Low |
| Live Chat | Quick questions, browsing support | <2 min | $$$ | Medium |
| Phone | Urgent issues, complex explanations | Immediate | $$$$ | High |
| Self-Service/KB | Common questions, how-tos | Instant | $ | Medium (setup) |
| In-App | Contextual help, onboarding | <5 min | $$ | Medium |
| Social Media | Public issues, brand monitoring | <1h | $$ | Medium |
| Community Forum | Peer support, feature discussion | 4-24h | $ | Low |
| Chatbot/AI | L0 deflection, routing, FAQ | Instant | $ | High (setup) |

### Channel Architecture by Company Stage

**Startup (0-1K tickets/mo):**
- Email + Knowledge Base + In-App chat
- 1-3 agents, everyone does everything
- Tool: Intercom, Freshdesk, or Help Scout

**Growth (1K-10K tickets/mo):**
- Add: Live chat + Phone (for enterprise) + Chatbot
- Tiered team (L1/L2), dedicated KB manager
- Tool: Zendesk, Intercom, or Freshdesk

**Scale (10K+ tickets/mo):**
- All channels + AI deflection + Community
- Specialized teams by channel/product/tier
- Tool: Zendesk Suite, Salesforce Service Cloud

### Channel Routing Logic

```
INCOMING TICKET:
├── Is it from a VIP/Enterprise customer?
│   └── YES → Priority queue → Senior agent
├── Can AI/bot answer with >90% confidence?
│   └── YES → Auto-respond → Offer human escalation
├── Is it a known issue with existing solution?
│   └── YES → Auto-suggest KB article → Close if confirmed
├── Complexity assessment:
│   ├── Simple (how-to, password reset, billing) → L1
│   ├── Technical (bug, integration, API) → L2
│   └── Critical (outage, data loss, security) → L2 + escalation
└── Channel-specific routing:
    ├── Social → Social team (public response <1h)
    ├── Phone → Available phone agent (no queue >3 min)
    └── Email/Chat → Round-robin by skill match
```

---

## Phase 3 — Ticket Management System

### Ticket Lifecycle

```
NEW → OPEN → PENDING → SOLVED → CLOSED
         ↓        ↑
      ESCALATED ──┘
```

**Stage Definitions:**

| Stage | Owner | Max Time | Exit Criteria |
|-------|-------|----------|---------------|
| New | Unassigned | 15 min | Agent picks up or auto-assigned |
| Open | Agent | Varies by priority | Working on resolution |
| Pending | Customer | 72h auto-close warning | Waiting for customer response |
| Escalated | L2/Specialist | 4h acknowledgment | Needs specialist knowledge |
| Solved | Agent | 48h auto-close | Solution provided, awaiting confirmation |
| Closed | System | — | Confirmed resolved or auto-closed |

### Priority Matrix

| Priority | Criteria | First Response | Resolution Target |
|----------|----------|---------------|-------------------|
| P0 — Critical | Service down, data loss, security breach | 15 min | 4h |
| P1 — High | Major feature broken, revenue impact | 1h | 8h |
| P2 — Normal | Feature issue, workaround exists | 4h | 24h |
| P3 — Low | How-to, enhancement request, cosmetic | 24h | 72h |

### Auto-Priority Rules

```yaml
auto_priority:
  P0_triggers:
    - keyword_match: ["outage", "down", "data loss", "breach", "can't login all"]
    - customer_tier: "enterprise"
    - affected_users: ">100"
    
  P1_triggers:
    - keyword_match: ["broken", "not working", "error", "billing issue"]
    - customer_tier: "business"
    - revenue_impact: true
    
  P2_default: true  # Everything else starts here
  
  P3_triggers:
    - keyword_match: ["feature request", "nice to have", "suggestion"]
    - category: "enhancement"
```

### Ticket Quality Checklist

Every ticket response should include:

- [ ] **Greeting** — personalized, warm, matches tone
- [ ] **Acknowledgment** — restate the issue to confirm understanding
- [ ] **Resolution/Next Step** — clear action taken or planned
- [ ] **Timeline** — when they can expect resolution if not immediate
- [ ] **Prevention** — how to avoid this in future (when applicable)
- [ ] **Closing** — invitation to reach out again, satisfaction check

### Ticket Tags & Categories

```yaml
taxonomy:
  categories:
    - account: [login, password, billing, subscription, permissions]
    - product: [bug, feature_request, how_to, integration, performance]
    - onboarding: [setup, migration, training, documentation]
    - technical: [api, webhook, sso, data_export, custom_config]
    - feedback: [complaint, compliment, suggestion, survey_response]
    
  sentiment: [positive, neutral, negative, urgent]
  
  root_cause:
    - user_error
    - documentation_gap
    - product_bug
    - missing_feature
    - third_party_issue
    - billing_system
    
  resolution_type:
    - self_service_redirect
    - agent_resolved
    - engineering_fix
    - product_change
    - refund_credit
    - no_action_needed
```

---

## Phase 4 — Response Framework & Templates

### The HEART Response Method

Every customer interaction follows HEART:

1. **H**ear — Read the full message. Understand the real problem, not just the stated one.
2. **E**mpathize — Acknowledge their frustration. Validate the experience.
3. **A**ct — Take concrete action. Explain what you're doing.
4. **R**esolve — Provide the solution or clear next steps with timeline.
5. **T**hank — Thank them for reaching out. Confirm they're satisfied.

### Response Templates

**Template 1: Bug Report Acknowledgment**
```
Hi [Name],

Thanks for reporting this — I can see how [specific impact] would be frustrating.

I've reproduced the issue on my end and confirmed [what you found]. I'm escalating this to our engineering team with priority [P level].

Here's what happens next:
- Engineering will investigate within [timeframe]
- I'll update you as soon as we have a fix or workaround
- In the meantime, you can [workaround if available]

Reference: [Ticket #]

Let me know if anything changes on your end. I'm on this until it's resolved.

[Agent Name]
```

**Template 2: Feature Request Response**
```
Hi [Name],

Great suggestion — [specific feature] would definitely [acknowledge the value].

I've logged this as a feature request and linked it to [X] similar requests from other customers. Our product team reviews these monthly to prioritize the roadmap.

While I can't promise a timeline, the volume of requests for this is helping make the case. I'll tag you on any updates.

In the meantime, have you tried [alternative approach]? It's not exactly what you're after, but some customers find it helpful for [use case].

Thanks for taking the time to share this — feedback like yours directly shapes what we build.

[Agent Name]
```

**Template 3: Angry Customer De-escalation**
```
Hi [Name],

I hear you, and I'm sorry — this isn't the experience you should be having with [product].

Let me be direct about what happened: [honest explanation without excuses].

Here's what I'm doing right now:
1. [Immediate action]
2. [Next step with timeline]
3. [Compensation/goodwill if appropriate]

I take full ownership of getting this resolved. You'll hear from me by [specific time], not with an update that we're "still working on it" — with an actual resolution.

[Agent Name]
```

**Template 4: Billing Issue Resolution**
```
Hi [Name],

I've looked into your billing concern and here's what I found:

[Clear explanation of what happened with the charge]

Action taken: [refund processed / credit applied / correction made]
- Amount: $[X]
- You'll see this reflected within [timeframe]
- Reference: [transaction ID]

To prevent this going forward: [what changed or what to watch for].

Everything look right? Happy to walk through your billing history if you'd like a full review.

[Agent Name]
```

**Template 5: Saying No Gracefully**
```
Hi [Name],

I understand why you'd want [requested action] — it makes sense given [their situation].

Unfortunately, I'm not able to [specific thing] because [honest reason — not "our policy says"].

Here's what I can do instead:
- Option A: [alternative that partially addresses their need]
- Option B: [different approach]
- Option C: [escalation path if they want to pursue further]

Which of these works best for you? Or if none of these hit the mark, let me know what you're ultimately trying to achieve and I'll see what else we can figure out.

[Agent Name]
```

### Tone Calibration Guide

| Customer Tone | Match With | Example Shift |
|---------------|------------|---------------|
| Casual/Friendly | Warm, conversational | "Hey! Let me take a look..." |
| Professional/Formal | Clear, structured | "Thank you for contacting us. I've reviewed..." |
| Frustrated/Angry | Calm, empathetic, action-oriented | "I understand. Let me fix this right now." |
| Technical/Detailed | Precise, detailed, technical | "The API returns 429 when..." |
| Confused/Lost | Simple, step-by-step | "No worries! Here's exactly what to do..." |

### Response Quality Scoring (0-100)

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Accuracy | 25% | Correct information, proper diagnosis, right solution |
| Empathy | 20% | Acknowledged feelings, personalized, human tone |
| Completeness | 20% | Addressed all questions, proactive info, prevention tips |
| Clarity | 15% | Easy to follow, no jargon, proper formatting |
| Efficiency | 10% | Resolved in minimum exchanges, no unnecessary back-and-forth |
| Brand Voice | 10% | Consistent tone, matches company personality |

**Scoring:**
- 90-100: Exceptional — use as training example
- 70-89: Good — meets standards
- 50-69: Needs improvement — coaching required
- Below 50: Failed — requires retraining

---

## Phase 5 — Escalation & Tiered Support

### Support Tier Architecture

```
L0 — Self-Service / AI
├── Knowledge base, chatbot, automated responses
├── Target: Deflect 30-50% of inbound volume
└── Escalates to L1 when: confidence <90%, customer requests human

L1 — Front-Line Support
├── Common issues, account management, how-to
├── Skills: Product knowledge, communication, troubleshooting basics
├── Metrics: FCR >70%, CSAT >85%, AHT <15 min
└── Escalates to L2 when: technical depth needed, bug confirmed, >30 min

L2 — Technical / Specialist Support  
├── Complex bugs, API issues, integrations, data problems
├── Skills: Technical debugging, log analysis, API knowledge
├── Metrics: Resolution <24h, CSAT >90%, escalation to eng <20%
└── Escalates to Engineering when: code fix needed, infra issue

L3 — Engineering Support
├── Production bugs, infrastructure issues, security
├── Skills: Code access, deployment ability, database access
├── Metrics: MTTR, change failure rate
└── Escalates to Management when: customer impact >threshold
```

### Escalation Decision Matrix

| Trigger | Action | Timeline |
|---------|--------|----------|
| P0 incident | Immediate L2 + Engineering + Manager notification | 15 min |
| Customer threatens churn (ARR >$10K) | L2 + Account Manager + CS lead | 1h |
| Legal threat or compliance issue | L2 + Legal + Manager | 1h |
| Same issue reported 3+ times by customer | L2 + Bug report + PM notification | 4h |
| Agent stuck >30 min on single ticket | L2 peer assist or escalation | 30 min |
| Customer requests manager | Transfer to team lead — never refuse | Immediate |
| Social media escalation (public) | Social team + PR if viral risk | 30 min |

### Escalation Handoff Template

```yaml
escalation:
  ticket_id: ""
  customer:
    name: ""
    tier: ""  # free/pro/enterprise
    arr: 0
    sentiment: ""  # frustrated/angry/neutral
    previous_escalations: 0
    
  issue:
    summary: ""
    category: ""
    priority: ""
    started: "YYYY-MM-DD HH:MM"
    
  what_tried:
    - action: ""
      result: ""
    - action: ""
      result: ""
      
  what_needed: ""
  customer_expectation: ""
  urgency_reason: ""
```

---

## Phase 6 — Knowledge Base & Self-Service

### KB Architecture

```
Knowledge Base
├── Getting Started (onboarding flow)
│   ├── Quick start guide
│   ├── Account setup
│   └── First [key action]
├── How-To Guides (task-based)
│   ├── By feature area
│   └── By user role
├── Troubleshooting (problem-based)
│   ├── Common errors
│   ├── Known issues
│   └── Diagnostic steps
├── API / Developer Docs (technical)
│   ├── Authentication
│   ├── Endpoints
│   └── Webhooks
├── Billing & Account
│   ├── Plans & pricing
│   ├── Payment methods
│   └── Invoices & receipts
└── FAQ (curated top questions)
```

### Article Quality Checklist

- [ ] **Title** is a question or action phrase (not a label)
- [ ] **First paragraph** answers the question directly
- [ ] **Steps** are numbered, specific, and testable
- [ ] **Screenshots** or GIFs for visual steps (annotated)
- [ ] **Edge cases** covered (what if X doesn't work?)
- [ ] **Related articles** linked at bottom
- [ ] **Last updated** date visible
- [ ] **Feedback widget** enabled (Was this helpful?)
- [ ] **SEO** — title matches how customers would search
- [ ] **Reading level** — Grade 8 or below (Hemingway test)

### Self-Service Deflection Strategy

**Target: 30-50% ticket deflection through self-service**

| Method | Expected Deflection | Setup Effort |
|--------|-------------------|--------------|
| Contextual help (in-app tooltips) | 10-15% | Medium |
| Search-optimized KB | 15-25% | Medium |
| AI chatbot (FAQ + KB search) | 10-20% | High |
| Guided troubleshooting flows | 5-10% | Medium |
| Community forum (peer support) | 5-10% | Low |
| Video tutorials | 3-5% | High |

### KB Maintenance Cadence

| Frequency | Action |
|-----------|--------|
| Weekly | Review "Was this helpful? No" feedback, fix top offenders |
| Monthly | Audit top 20 search queries — ensure articles exist for each |
| Monthly | Review 0-view articles — update, redirect, or archive |
| Quarterly | Full KB audit — freshness check, accuracy review |
| Per release | Update affected articles before feature ships |

### Content Gap Detection

```
FOR EACH top support ticket category:
  1. Search KB for matching article
  2. IF no article exists → CREATE (priority = ticket volume)
  3. IF article exists but tickets persist → IMPROVE (unclear or incomplete)
  4. IF article exists and is good → check discoverability (search, in-app links)
```

---

## Phase 7 — Support Metrics & Analytics

### Core Metrics Dashboard

```yaml
weekly_dashboard:
  date_range: "YYYY-MM-DD to YYYY-MM-DD"
  
  volume:
    total_tickets: 0
    new_tickets: 0
    resolved_tickets: 0
    backlog: 0
    tickets_per_agent: 0
    
  speed:
    avg_first_response_time: ""
    median_first_response_time: ""
    avg_resolution_time: ""
    p95_resolution_time: ""
    
  quality:
    csat_score: 0  # target: >85%
    fcr_rate: 0  # target: >70%
    customer_effort_score: 0  # target: <3
    nps_from_support: 0  # target: >40
    
  efficiency:
    cost_per_ticket: 0
    tickets_per_agent_per_day: 0  # healthy: 15-25
    self_service_deflection_rate: 0  # target: >30%
    automation_rate: 0
    
  team:
    agent_satisfaction: 0
    attrition_rate: 0  # annual, target: <25%
    avg_handle_time: ""
    utilization: 0  # target: 60-80%
    
  trends:
    ticket_volume_wow: ""  # +X% or -X%
    csat_trend: ""
    top_issue_changes: []
```

### Metric Benchmarks by Company Stage

| Metric | Startup | Growth | Scale | World-Class |
|--------|---------|--------|-------|-------------|
| First Response (email) | <24h | <4h | <1h | <15 min |
| First Response (chat) | <5 min | <2 min | <1 min | <30 sec |
| CSAT | >75% | >80% | >85% | >90% |
| FCR | >50% | >65% | >75% | >85% |
| Self-Service Deflection | >10% | >25% | >40% | >60% |
| Cost per Ticket | N/A | <$25 | <$15 | <$8 |
| Agent Utilization | 40-90% | 60-80% | 65-80% | 70-80% |

### Root Cause Analysis

Run monthly — categorize ALL tickets by root cause:

```yaml
root_cause_analysis:
  month: "YYYY-MM"
  total_tickets: 0
  
  categories:
    - cause: "Documentation gap"
      count: 0
      percentage: 0
      action: "Create/update KB articles"
      owner: ""
      
    - cause: "Product bug"
      count: 0
      percentage: 0
      action: "File engineering tickets, prioritize by volume"
      owner: ""
      
    - cause: "UX confusion"
      count: 0
      percentage: 0
      action: "Share with product/design for improvement"
      owner: ""
      
    - cause: "Missing feature"
      count: 0
      percentage: 0
      action: "Aggregate for product roadmap input"
      owner: ""
      
    - cause: "User error (despite good docs)"
      count: 0
      percentage: 0
      action: "In-app guidance, onboarding improvement"
      owner: ""
      
    - cause: "Third-party/integration issue"
      count: 0
      percentage: 0
      action: "Partner communication, status page"
      owner: ""
      
    - cause: "Billing/account"
      count: 0
      percentage: 0
      action: "Process automation, self-service billing"
      owner: ""
```

**The 10x Rule:** Every bug that generates >10 tickets/month should be escalated to engineering as a P1 fix. Every question asked >20 times/month should have a KB article AND in-app guidance.

---

## Phase 8 — Team Structure & Hiring

### Team Sizing Formula

```
Required agents = (Monthly tickets × Avg handle time in hours) / 
                  (Working hours per agent per month × Target utilization)

Example:
- 5,000 tickets/mo × 0.25h avg handle = 1,250 hours needed
- 160 hours/agent/mo × 0.75 utilization = 120 productive hours/agent
- 1,250 / 120 = ~11 agents needed
```

**Add buffer for:**
- PTO/sick leave: +15%
- Training time: +10%
- Peak periods: +20%
- Growth: +10% per quarter

### Team Structure by Size

**1-3 Agents (Startup):**
- Everyone is generalist
- Shared queue, no tiers
- Manager = agent + admin

**4-10 Agents (Growth):**
- L1/L2 split
- Team lead (50% tickets, 50% coaching)
- KB owner (shared responsibility)
- Specialization by product area begins

**11-30 Agents (Scale):**
- L1/L2/L3 tiers
- Dedicated team leads (1:6-8 ratio)
- KB/self-service team
- Quality assurance reviewer
- Workforce management
- Support ops/tooling

**30+ Agents (Enterprise):**
- All above + regional teams
- Dedicated training team
- Support engineering team
- Customer advocacy/VoC role
- Director + managers hierarchy

### Hiring Scorecard

| Dimension | Weight | What to Assess |
|-----------|--------|----------------|
| Communication | 30% | Writing clarity, empathy, tone matching |
| Problem-Solving | 25% | Diagnostic thinking, creative solutions |
| Technical Aptitude | 20% | Learning speed, comfort with tools |
| Emotional Intelligence | 15% | Handling frustration, de-escalation |
| Cultural Fit | 10% | Team collaboration, growth mindset |

### Interview: Support Simulation Exercise

Give candidates a real (anonymized) ticket and ask them to:
1. Write a response (assess communication + accuracy)
2. Explain their diagnosis process (assess problem-solving)
3. Role-play an angry customer call (assess EQ + de-escalation)
4. Navigate your helpdesk tool (assess technical aptitude)

**Score each 1-5. Minimum 3.5 average to hire.**

### Agent Onboarding Checklist (First 30 Days)

**Week 1: Foundation**
- [ ] Product walkthrough (become a power user)
- [ ] Tool training (helpdesk, KB, CRM)
- [ ] Shadow 20+ tickets with senior agent
- [ ] Read top 50 KB articles
- [ ] Practice responses with templates

**Week 2: Guided Practice**
- [ ] Handle L1 tickets with mentor review
- [ ] Complete 10 supervised responses
- [ ] Learn escalation procedures
- [ ] Study top 10 issue categories
- [ ] Pass product knowledge quiz (>80%)

**Week 3-4: Independent with Safety Net**
- [ ] Handle L1 queue independently
- [ ] QA review on 50% of tickets
- [ ] First 1:1 with team lead
- [ ] Set 30-day performance goals
- [ ] Identify personal development areas

---

## Phase 9 — Quality Assurance Program

### QA Review Framework

**Review cadence:**
- New agents (0-90 days): 30% of tickets reviewed
- Experienced agents: 10% of tickets reviewed (random sample)
- All escalated tickets: 100% reviewed
- All negative CSAT: 100% reviewed

### QA Scorecard (per ticket)

| Category | Points | Criteria |
|----------|--------|----------|
| **Accuracy** | /25 | Correct diagnosis, right solution, no misinformation |
| **Communication** | /25 | Clear, empathetic, professional, matched tone |
| **Process** | /20 | Proper tags, priority, escalation if needed, notes |
| **Efficiency** | /15 | Minimum touches to resolve, no unnecessary delays |
| **Going Above** | /15 | Proactive help, prevention tips, personal touch |
| **Total** | /100 | |

**Score thresholds:**
- 90+: Exceptional — recognition, potential mentor
- 75-89: Meets expectations
- 60-74: Coaching needed — create improvement plan
- Below 60: Performance concern — immediate coaching + daily review

### QA Calibration Sessions

**Monthly, 60 minutes:**
1. Select 5 tickets (mix of good and poor)
2. Each reviewer scores independently
3. Compare scores — discuss discrepancies >10 points
4. Align on standards
5. Update rubric if needed

### Agent Performance Dashboard

```yaml
agent_scorecard:
  agent: ""
  period: "YYYY-MM"
  
  productivity:
    tickets_resolved: 0
    avg_handle_time: ""
    tickets_per_hour: 0
    
  quality:
    qa_score_avg: 0
    csat_avg: 0
    fcr_rate: 0
    escalation_rate: 0
    
  reliability:
    adherence_to_schedule: 0  # percentage
    response_time_compliance: 0  # % within SLA
    
  development:
    kb_articles_created: 0
    peer_assists: 0
    training_completed: []
    
  trend: "improving|stable|declining"
  coaching_notes: ""
```

---

## Phase 10 — Automation & AI Integration

### Automation Priority Stack

| Automation | Impact | Effort | Priority |
|-----------|--------|--------|----------|
| Auto-tagging & routing | High | Low | P0 |
| Canned response suggestions | High | Low | P0 |
| Password reset self-service | High | Low | P0 |
| SLA breach alerts | High | Low | P0 |
| KB article suggestions to agents | High | Medium | P1 |
| AI first-response draft | High | Medium | P1 |
| Chatbot for FAQ deflection | High | High | P1 |
| Sentiment detection & priority boost | Medium | Medium | P1 |
| Auto-close resolved tickets | Medium | Low | P2 |
| Proactive outreach on known issues | Medium | Medium | P2 |
| Customer health scoring | Medium | High | P2 |
| Predictive ticket volume | Low | High | P3 |

### AI-Assisted Support Workflow

```
TICKET ARRIVES
├── AI Classification
│   ├── Category, priority, sentiment (auto-tagged)
│   └── Routing suggestion
├── AI Draft Response
│   ├── Searches KB + previous similar tickets
│   ├── Generates draft response
│   └── Agent reviews, edits, sends (human-in-the-loop)
├── AI Quality Check
│   ├── Tone analysis before send
│   ├── Completeness check (all questions addressed?)
│   └── Policy compliance (no promises we can't keep)
└── AI Post-Resolution
    ├── Auto-summarize for internal notes
    ├── Suggest KB updates if new solution
    └── Update customer health score
```

### Chatbot Design Rules

1. **Always offer human escalation** — never trap customers in bot loops
2. **Disclose AI** — "I'm an AI assistant. Want to talk to a person?"
3. **Confidence threshold** — if <85% confident, route to human
4. **Max 3 bot turns** before offering human — don't frustrate
5. **Handoff context** — pass full conversation to human agent
6. **Track deflection quality** — monitor CSAT for bot-resolved tickets

---

## Phase 11 — Difficult Situations Playbook

### Playbook 1: Angry/Abusive Customer

```
PROTOCOL:
1. Let them vent (don't interrupt the first message)
2. Acknowledge with empathy: "I understand why you're frustrated"
3. DO NOT apologize for things that aren't your fault
4. Focus on action: "Here's what I'm doing right now..."
5. Set boundaries if abusive: "I want to help you, but I need us to communicate respectfully"
6. If continued abuse → "I'm going to pause this conversation. You can reach us again when ready, or I can connect you with my manager."

NEVER:
- Match their energy
- Take it personally
- Make promises you can't keep
- Say "calm down"
```

### Playbook 2: Customer Threatening to Churn

```
PROTOCOL:
1. Acknowledge the frustration seriously
2. Ask: "What would need to change for you to stay?"
3. Document their specific pain points
4. IF within authority → offer concrete retention (discount, extended trial, feature access)
5. IF not within authority → escalate to CS/Account Manager with full context
6. Follow up within 24h regardless of outcome

SIGNALS to escalate immediately:
- ARR > $5K
- They've mentioned competitors by name
- They have a cancellation date set
- Multiple unresolved tickets in last 30 days
```

### Playbook 3: Major Outage/Incident

```
PROTOCOL:
1. Activate incident response (notify engineering + management)
2. Post status page update within 15 min
3. Prepare acknowledgment template (NO ETAs until engineering confirms)
4. Respond to ALL tickets with consistent messaging
5. Update status page every 30 min minimum
6. After resolution: send post-mortem summary to affected customers

MESSAGING RULES:
- Be honest about what happened
- Don't blame third parties (even if it's their fault)
- Provide concrete next steps for prevention
- Offer appropriate compensation (credits, extended subscription)
```

### Playbook 4: Refund Request

```
DECISION TREE:
├── Within refund policy window?
│   ├── YES → Process immediately, no friction
│   └── NO → Continue below
├── Valid reason (product didn't work, broken promise)?
│   ├── YES → Process refund + investigate root cause
│   └── MAYBE → Offer alternative (credit, downgrade, extended support)
├── Long-term customer (>6 months)?
│   ├── YES → Lean toward refund + retention offer
│   └── NO → Follow standard policy
└── Amount >$[threshold]?
    ├── YES → Escalate to manager for approval
    └── NO → Agent discretion within guidelines

RULE: A refund processed quickly with goodwill costs less than a chargeback + bad review.
```

### Playbook 5: Social Media Crisis

```
PROTOCOL:
1. Acknowledge publicly within 30 min: "We see this and we're looking into it"
2. Move to private channel: "Can you DM us your account details?"
3. Resolve in private
4. Update public thread with resolution (shows others you care)
5. Monitor for 24h — respond to all related threads

NEVER:
- Delete negative posts (unless policy violation)
- Argue publicly
- Share customer details in public responses
- Ignore — silence = admission to the internet
```

---

## Phase 12 — Proactive Support & Customer Health

### Proactive Support Triggers

| Signal | Action | Channel |
|--------|--------|---------|
| Customer hasn't logged in 14 days | Check-in email with tips | Email |
| Feature adoption <20% after 30 days | Guided tour or training offer | In-app + email |
| Multiple failed actions in product | Trigger help widget or chat | In-app |
| Known issue affecting their account | Proactive notification before they report | Email |
| Contract renewal in 60 days | CS + Support alignment check | Internal |
| Negative CSAT on last 2 tickets | Account review + senior agent assignment | Internal |
| Usage spike (potential billing surprise) | Proactive notification | Email |

### Customer Health Score for Support

```yaml
support_health_score:
  customer: ""
  score: 0  # 0-100
  
  dimensions:
    ticket_volume_trend:
      weight: 20
      score: 0
      # High and rising = bad, Low and stable = good
      
    sentiment_trend:
      weight: 25
      score: 0
      # Track CSAT over last 90 days
      
    resolution_satisfaction:
      weight: 20
      score: 0
      # FCR rate for this customer
      
    self_service_adoption:
      weight: 15
      score: 0
      # % of issues resolved via KB/self-service
      
    escalation_frequency:
      weight: 20
      score: 0
      # Lower = healthier
      
  risk_level: "healthy|at_risk|critical"
  recommended_action: ""
```

---

## Phase 13 — Support Operations & Workforce Management

### Staffing Model

```
FORECAST STEPS:
1. Historical ticket volume by day/hour (last 90 days)
2. Identify patterns (Monday spike, end-of-month billing, seasonal)
3. Apply growth rate to forecast next period
4. Factor in planned events (launches, promotions, migrations)
5. Calculate required headcount per shift

FORMULA per hour:
Required agents = (Forecasted tickets × AHT) / (60 × Occupancy target)

Example:
- 50 tickets/hour × 12 min AHT = 600 minutes of work
- 600 / (60 × 0.75 occupancy) = 13.3 → 14 agents needed
```

### Shift Scheduling (24/7 Coverage)

```yaml
coverage_plan:
  timezone: "UTC"
  shifts:
    morning:
      hours: "06:00-14:00"
      coverage: "full"  # All channels
      agents: 0
      
    afternoon:
      hours: "14:00-22:00"
      coverage: "full"
      agents: 0
      
    night:
      hours: "22:00-06:00"
      coverage: "reduced"  # Email only, P0 on-call for chat/phone
      agents: 0
      
  peak_hours:
    - day: "Monday"
      hours: "09:00-12:00"
      extra_agents: 2
    - day: "Tuesday"
      hours: "09:00-11:00"
      extra_agents: 1
```

### Support Budget Planning

| Cost Category | Typical % of Total |
|--------------|-------------------|
| Agent salaries & benefits | 60-70% |
| Tools & technology | 10-15% |
| Training & development | 5-8% |
| Quality assurance | 3-5% |
| Management & overhead | 10-15% |

**Cost per ticket benchmark:**
- Email: $5-15
- Chat: $3-10
- Phone: $8-25
- Self-service: $0.10-0.50
- AI-assisted: $1-5

---

## Phase 14 — Voice of Customer (VoC) Pipeline

### Support → Product Feedback Loop

```
WEEKLY:
1. Aggregate top 10 ticket categories by volume
2. Tag tickets with product_feedback label
3. Extract quotes (anonymized) that illustrate pain points
4. Package into "Voice of Customer" report

MONTHLY:
1. Present VoC report to Product team
2. Track which feedback items enter roadmap
3. Close the loop — notify customers when their feedback ships
4. Measure impact — did ticket volume decrease for addressed issues?
```

### VoC Report Template

```yaml
voc_report:
  period: "YYYY-MM"
  
  top_pain_points:
    - issue: ""
      ticket_count: 0
      customer_quotes:
        - "[Anonymized quote]"
      impact: "churn_risk|frustration|workaround_needed"
      recommendation: ""
      
  feature_requests:
    - feature: ""
      request_count: 0
      customer_segments: []
      business_impact: ""
      
  product_bugs_by_volume:
    - bug: ""
      tickets: 0
      workaround: ""
      engineering_ticket: ""
      
  positive_feedback:
    - feature: ""
      praise_count: 0
      quotes: []
      
  trends:
    improving: []
    declining: []
    new_this_month: []
```

---

## Phase 15 — Continuous Improvement

### Weekly Support Review (30 min)

1. **Numbers check** — Volume, CSAT, FCR, backlog vs last week
2. **Top 3 issues** — What's generating the most tickets? Any new patterns?
3. **Escalation review** — Any escalations that should have been avoided?
4. **Team health** — Agent workload balanced? Anyone burning out?
5. **Quick wins** — One KB article, one template, or one automation to ship this week

### Monthly Support Health Score (0-100)

| Dimension | Weight | Score |
|-----------|--------|-------|
| Customer Satisfaction (CSAT + CES) | 25% | /25 |
| Speed (FRT + Resolution time vs SLA) | 20% | /20 |
| Efficiency (FCR + Cost per ticket) | 20% | /20 |
| Self-Service (Deflection rate + KB health) | 15% | /15 |
| Team Health (Utilization + Satisfaction + Attrition) | 10% | /10 |
| Continuous Improvement (VoC actions + KB updates) | 10% | /10 |
| **Total** | 100% | **/100** |

### Quarterly Support Strategy Review

1. Review 90-day metrics trends — where are we improving/declining?
2. Customer segmentation analysis — are enterprise customers getting different service than SMB?
3. Tool & technology assessment — are current tools meeting needs?
4. Team development — skill gaps, training needs, career pathing
5. Budget review — cost per ticket trending, efficiency gains
6. Roadmap alignment — are product improvements reducing ticket volume?
7. Set OKRs for next quarter

### 100-Point Quality Rubric

| Dimension | Weight | 0-2 (Poor) | 3-5 (Basic) | 6-8 (Good) | 9-10 (Excellent) |
|-----------|--------|-----------|-------------|------------|------------------|
| Response Quality | 15 | Inaccurate, robotic | Correct but generic | Personalized, clear | Exceptional, memorable |
| Speed & SLAs | 15 | Consistently missing | Mostly meeting | Meeting all SLAs | Exceeding targets |
| First Contact Resolution | 15 | <50% FCR | 50-65% | 65-80% | >80% |
| Self-Service Effectiveness | 10 | No KB or unused | Basic KB, <15% deflection | Good KB, 15-35% | Excellent, >35% |
| Customer Satisfaction | 15 | CSAT <70% | 70-80% | 80-90% | >90% |
| Team Performance | 10 | High turnover, low morale | Stable but disengaged | Engaged, developing | High-performing, growing |
| Process Maturity | 10 | Ad hoc, no documentation | Some processes defined | Documented, followed | Optimized, automated |
| Continuous Improvement | 10 | Reactive only | Some VoC sharing | Regular improvement cycle | Data-driven, proactive |

---

## Edge Cases & Special Situations

### Multi-Language Support
- Prioritize languages by customer revenue concentration
- Use AI translation for first-pass, human review for complex issues
- Maintain separate KB per language (or use auto-translate with quality gate)
- Time zone coverage must match language markets

### B2B vs B2C Support
- **B2B:** Named accounts, dedicated agents for enterprise, technical depth required, QBR integration
- **B2C:** Volume-optimized, self-service heavy, faster resolution expected, social media critical

### Regulated Industries (Healthcare, Finance)
- Additional compliance training required
- Audit trail on all customer interactions
- PII handling protocols — what agents can and cannot access
- Response templates reviewed by legal/compliance quarterly

### Seasonal Peaks (E-commerce, Events)
- Hire temp agents 4-6 weeks before peak
- Create peak-specific playbooks and templates
- Increase self-service capacity (chatbot, KB updates)
- Adjust SLAs transparently during known peak periods

### Support During Product Migration/Major Change
- Dedicated war room for first 72 hours post-change
- Pre-written communication templates for expected issues
- Increased staffing +50% for 2 weeks post-change
- Daily hot-fix coordination with engineering

---

## Natural Language Commands

Use these to interact with this skill:

1. **"Assess our support function"** → Run Phase 1 assessment
2. **"Design our channel strategy"** → Build channel architecture (Phase 2)
3. **"Set up ticket management"** → Configure ticket system (Phase 3)
4. **"Write response templates"** → Generate templates for common scenarios (Phase 4)
5. **"Build escalation process"** → Design tier structure and escalation rules (Phase 5)
6. **"Plan our knowledge base"** → Design KB architecture and content plan (Phase 6)
7. **"Create support dashboard"** → Build metrics and reporting (Phase 7)
8. **"Help me hire support agents"** → Hiring plan and onboarding (Phase 8)
9. **"Set up QA program"** → Quality assurance framework (Phase 9)
10. **"Automate our support"** → AI and automation strategy (Phase 10)
11. **"Handle [difficult situation]"** → Situation-specific playbook (Phase 11)
12. **"Review our support health"** → Full health assessment with scoring (Phase 15)

---

## ⚡ Level Up Your Support Operations

This free skill gives you the complete methodology. For industry-specific support playbooks with compliance frameworks, SLA templates, and vertical-specific ticket taxonomies:

**[AfrexAI Context Packs — $47 each](https://afrexai-cto.github.io/context-packs/)**

- 🏥 **Healthcare Pack** — HIPAA-compliant support workflows
- 💰 **Fintech Pack** — Regulated financial services support
- 🛒 **Ecommerce Pack** — High-volume consumer support operations
- 💻 **SaaS Pack** — Technical product support at scale

### 🔗 More Free Skills by AfrexAI

- `afrexai-customer-success` — Retention, health scoring, expansion revenue
- `afrexai-sales-playbook` — Complete B2B sales methodology
- `afrexai-agent-engineering` — Build autonomous AI agents
- `afrexai-openclaw-mastery` — Master your OpenClaw setup
- `afrexai-conversational-ai` — Design chatbots and voice agents

**Install:** `clawhub install afrexai-support-operations`

**Browse all skills:** [clawhub.com](https://clawhub.com)
