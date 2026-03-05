# Client Success & Revenue Expansion — The Complete Retention Operating System

Turn clients into long-term revenue engines. This isn't advice — it's a complete operating system with scoring models, templates, playbooks, and automation patterns that work for any B2B or B2C subscription business.

## Use When

- Designing or auditing your retention strategy end-to-end
- A client shows churn signals and you need an intervention playbook
- Building onboarding flows that stick (first 90 days)
- Planning expansion revenue from existing accounts
- Running quarterly business reviews (QBRs)
- Analyzing cohort retention data and identifying drop-off causes
- Creating reactivation campaigns for churned users
- Building a customer health scoring system
- Preventing involuntary churn (payment failures)

## Don't Use When

- Acquiring brand-new clients (use lead generation / outreach skills)
- One-time product sales with zero recurring component
- The client is genuinely a terrible fit — let them go gracefully

---

## Phase 1: Customer Health Score (Your Early Warning System)

Before anything else, build a health score. Without one, you're flying blind — reacting to churn instead of preventing it.

### Health Score Model (0-100)

Score every account weekly. Automate where possible.

```yaml
health_score:
  dimensions:
    usage:
      weight: 30
      signals:
        - login_frequency_vs_baseline: # % of their normal
            90-100%: 10
            70-89%: 7
            50-69%: 4
            below_50%: 1
        - core_feature_adoption: # % of key features used
            4+_features: 10
            3_features: 7
            2_features: 4
            1_or_fewer: 1
        - depth_of_usage: # power user vs surface
            advanced_features: 10
            intermediate: 6
            basic_only: 3
    
    engagement:
      weight: 25
      signals:
        - response_time_to_comms: # avg days to reply
            same_day: 10
            1-2_days: 7
            3-5_days: 4
            5+_days_or_no_reply: 1
        - attends_check_ins: # QBR/call attendance
            always: 10
            usually: 7
            sometimes: 4
            never: 1
        - proactive_requests: # they ask for more
            monthly: 10
            quarterly: 6
            rarely: 3
            never: 1
    
    financial:
      weight: 20
      signals:
        - payment_history: # last 6 months
            always_on_time: 10
            1_late: 7
            2+_late: 3
            failed_payment_unresolved: 0
        - contract_value_trend:
            expanding: 10
            stable: 6
            contracting: 2
        - billing_page_visits: # in last 30 days
            none: 10
            1-2: 6  # curious
            3+: 2   # shopping to leave
    
    relationship:
      weight: 15
      signals:
        - champion_status: # your internal advocate
            strong_champion: 10
            moderate: 6
            weak_or_unknown: 3
            champion_left_company: 0
        - stakeholder_breadth: # contacts you have
            3+_contacts: 10
            2_contacts: 6
            single_threaded: 2
        - sentiment_last_interaction:
            positive: 10
            neutral: 6
            negative: 2
    
    outcome:
      weight: 10
      signals:
        - achieving_stated_goals: # their original objectives
            exceeding: 10
            on_track: 7
            behind: 3
            unclear_goals: 2
        - roi_demonstrated:
            clear_positive_roi: 10
            probable_roi: 6
            unclear: 3
            negative: 0

  risk_tiers:
    healthy: 75-100    # green — nurture & expand
    monitor: 50-74     # yellow — proactive outreach
    at_risk: 25-49     # orange — intervention required
    critical: 0-24     # red — save or graceful exit
```

### Automated Health Alerts

| Score Change | Action |
|---|---|
| Drops 15+ points in one week | Immediate outreach — something changed |
| Enters "at-risk" tier | Trigger save playbook (Phase 5) |
| Enters "critical" | Escalate to founder/CEO within 24 hours |
| Rises to "healthy" from lower tier | Send congratulations + expansion conversation |
| Champion leaves company | Emergency: identify new champion within 48 hours |

---

## Phase 2: Onboarding (Days 0-90) — The Retention Foundation

**20%+ of voluntary churn traces back to poor onboarding** (Recurly). The first 90 days determine the next 900.

### Day-by-Day Onboarding Framework

```yaml
onboarding_playbook:
  day_0:
    - welcome_message: |
        Personal, not templated. Reference their specific goals from the sales process.
        Include: what happens next, timeline, who they'll work with, how to reach you.
    - access_setup: Grant all necessary access, tools, integrations
    - kickoff_call: 30 min — align on goals, success metrics, communication cadence
    - document: Record their stated goals and success criteria in CRM
  
  day_1-3:
    - quick_win: Deliver ONE visible result ASAP
    - examples:
        - SaaS: first workflow automated
        - Agency: first deliverable draft
        - Consulting: first insight or recommendation
    - why: Quick wins create commitment bias — they've now seen value
  
  day_7:
    - check_in_1: |
        "How's everything going? Any questions or blockers?"
        Goal: surface confusion early. Don't wait for them to complain.
    - share_progress: Show what's been done, even if small
  
  day_14:
    - first_result: Share measurable outcome with numbers
    - format: "[Metric] went from [X] to [Y] — here's what that means for you"
    - ask: "Is this aligned with what you expected?"
  
  day_30:
    - milestone_review:
        - Show ROI calculation
        - Confirm success metrics are being hit
        - Discuss next 60 days
        - Introduce expansion possibilities (plant seeds, don't sell)
    - document: Update CRM with 30-day health assessment
  
  day_60:
    - deeper_review:
        - Feature adoption check — are they using everything available?
        - Identify unused capabilities and train on them
        - Stakeholder expansion — meet other team members who should be involved
  
  day_90:
    - graduation:
        - Full QBR format (see Phase 4)
        - Transition from "onboarding" to "ongoing" cadence
        - Set annual goals
        - If health score is green: discuss year 1 roadmap
        - If yellow/orange: intervention before it becomes a habit
```

### Onboarding Scoring Rubric (0-100)

Grade your onboarding process:

| Dimension | Weight | Score 10 | Score 5 | Score 1 |
|---|---|---|---|---|
| Time to first value | 25 | < 3 days | 1-2 weeks | > 2 weeks |
| Client effort required | 20 | Minimal (you do it) | Moderate | Heavy lift |
| Personalization | 15 | Fully customized to goals | Semi-templated | Generic |
| Communication clarity | 15 | Proactive, clear timeline | Reactive | Confusing |
| Quick win delivered | 15 | Measurable result in week 1 | Vague progress | No win |
| Documentation | 10 | Full knowledge base / guide | Basic docs | Nothing |

**Target: 80+.** Below 60 = your onboarding is a churn factory.

---

## Phase 3: Ongoing Value Delivery (Monthly Proof)

Clients don't churn because your service stopped working. They churn because they **forgot it was working.**

### Monthly Value Report Template

```markdown
# [Month] Performance Report — [Client Name]

## Key Metrics
| Metric | This Month | Last Month | Change |
|--------|-----------|------------|--------|
| [Primary KPI] | [value] | [value] | [+/-]% |
| [Secondary KPI] | [value] | [value] | [+/-]% |
| [Tertiary KPI] | [value] | [value] | [+/-]% |

## What We Did
- [Specific action 1 with result]
- [Specific action 2 with result]
- [Optimization or improvement made]

## ROI Summary
- Your investment: $[monthly cost]
- Value delivered: $[quantified value]
- ROI: [X]x return

## What's Next
- [Planned improvement 1]
- [Planned improvement 2]

## Quick Question
[One specific question to keep dialogue open]
```

### Value Report Rules

1. **Send EVERY month without exception** — automate the data pull
2. **Real numbers only** — never vague "things are going well"
3. **Show the trend** — month-over-month shows trajectory
4. **Always end with a question** — keeps communication bidirectional
5. **Highlight one proactive improvement** — shows you're working even when they don't ask
6. **Keep it under 1 page** — executives skim, don't read novels

---

## Phase 4: Quarterly Business Reviews (QBRs)

QBRs are your highest-leverage retention activity. A good QBR simultaneously prevents churn, surfaces expansion, and deepens the relationship.

### QBR Agenda Template (45-60 min)

```yaml
qbr_agenda:
  1_celebrate_wins: # 10 min
    - "Here's what we've accomplished together this quarter"
    - Show 3-5 headline metrics with trends
    - Tie results to their original goals
    - Ask: "Does this match your perception?"
  
  2_deep_dive: # 15 min
    - One area of focus (their choice or your recommendation)
    - Bring analysis they haven't seen
    - Benchmark against industry if possible
    - "Here's what we've learned and what it means"
  
  3_feedback_loop: # 10 min
    - "What's working well?" (reinforce, don't skip this)
    - "What could we do better?" (write it down visibly)
    - "Has anything changed in your business we should know about?"
    - Listen for churn signals (see list below)
  
  4_roadmap: # 10 min
    - What's planned for next quarter
    - Any new capabilities or features relevant to them
    - Tie roadmap items to their stated needs
  
  5_expansion: # 5 min
    - "Based on your growth, here's where we could help more"
    - Present ONE expansion idea (not three — focused)
    - Frame as: "Other clients in your situation have found X valuable"
    - No pressure — plant the seed
  
  6_next_steps: # 5 min
    - Summarize action items (yours and theirs)
    - Confirm next QBR date
    - Send written summary within 24 hours
```

### QBR Scoring (Rate the Account 1-5)

| Dimension | 5 (Excellent) | 3 (Okay) | 1 (Danger) |
|---|---|---|---|
| Goal achievement | Exceeding all goals | Hitting some | Missing most |
| Engagement | Proactive, enthusiastic | Responsive | Disengaged |
| Relationship depth | Multi-threaded, exec sponsor | Single contact | Contact leaving |
| Expansion signals | Asking about more services | Open to discussion | Cutting scope |
| Payment health | Always on time, expanding | Stable | Late, questioning costs |

**Score 20-25:** Expansion candidate — push for upsell
**Score 15-19:** Healthy — maintain cadence
**Score 10-14:** At risk — increase touchpoints
**Score 5-9:** Critical — activate save playbook immediately

---

## Phase 5: Churn Prevention & Save Playbook

### 14 Churn Signals (Ranked by Severity)

| # | Signal | Severity | Response Time |
|---|---|---|---|
| 1 | Data export request | 🔴 Critical | Same day |
| 2 | Asks about cancellation terms | 🔴 Critical | Same day |
| 3 | Champion leaves company | 🔴 Critical | 48 hours |
| 4 | Payment failure (2nd attempt) | 🔴 Critical | Same day |
| 5 | Usage drops 50%+ from baseline | 🟠 High | 3 days |
| 6 | Stops responding to messages | 🟠 High | 1 week |
| 7 | Misses 2+ scheduled check-ins | 🟠 High | 1 week |
| 8 | Competitor mentioned in conversation | 🟡 Medium | Next touchpoint |
| 9 | Budget review announced internally | 🟡 Medium | 1 week |
| 10 | Key stakeholder change | 🟡 Medium | 2 weeks |
| 11 | Asks to reduce scope/tier | 🟡 Medium | Next touchpoint |
| 12 | Support tickets spike then go silent | 🟡 Medium | 1 week |
| 13 | Billing page visits increase | 🟡 Medium | Next touchpoint |
| 14 | Engagement score declining 3 weeks straight | 🟡 Medium | 2 weeks |

### Save Playbook (5 Stages)

```yaml
save_playbook:
  stage_1_detect:
    trigger: Health score enters "at-risk" OR churn signal detected
    action: |
      Internal alert to account owner + manager.
      Pull full account history: usage, payments, last interactions, open issues.
      Prepare value summary (total ROI delivered to date).
  
  stage_2_reach_out:
    timing: Within response time for the signal severity
    approach: |
      Personal, NOT templated. From a human, not "the team."
      "Hi [Name], I noticed [specific observation]. Wanted to check in — 
      is everything going well with [specific thing]?"
      DO NOT: mention churn, be defensive, or offer discounts preemptively.
    channel: Match their preferred channel (email, call, Slack, etc.)
  
  stage_3_listen:
    goal: Understand the real reason, not the surface excuse
    common_real_reasons:
      - "Not seeing value" → ROI not demonstrated clearly enough
      - "Too expensive" → Value perception gap (or genuine budget cut)
      - "Switched to competitor" → Feature/price gap you didn't know about
      - "Champion left" → Relationship wasn't broad enough
      - "Don't use it enough" → Adoption/training gap
      - "Priorities changed" → Their business shifted
    technique: |
      Ask "What would need to change for this to work for you?" 
      NOT "What's wrong?" (defensive) or "What can we do?" (desperate)
  
  stage_4_intervene:
    options_by_reason:
      not_seeing_value:
        - Emergency value review — show ROI with hard numbers
        - Offer dedicated optimization session
        - Set new, measurable goals with 30-day checkpoint
      too_expensive:
        - Tier adjustment (downgrade > cancel)
        - Pause option (1-2 months, hold their data/setup)
        - Annual discount if they commit
        - LAST RESORT: temporary price reduction with expiry
      low_usage:
        - Personalized training session
        - Assign an onboarding buddy
        - Simplify their setup (reduce complexity)
      champion_left:
        - Request intro to successor within 48 hours
        - Prepare "new stakeholder briefing" with full history + ROI
        - Offer fresh kickoff call with new contact
      competitor:
        - Understand specific features/price they're comparing
        - Build competitive comparison (honest, not FUD)
        - If you genuinely can't compete: let them go gracefully
  
  stage_5_outcome:
    saved:
      - Document what worked → update playbook
      - Set 30/60/90 day health checkpoints
      - Address root cause permanently (don't just bandage)
    churned:
      - Exit interview: "What could we have done differently?"
      - Leave door open: "We're here if things change"
      - Add to reactivation pipeline (see Phase 7)
      - Analyze: was this predictable? Update health score model
```

### Pause vs. Cancel Framework

**Always offer pause before accepting cancellation.**

| Scenario | Offer | Terms |
|---|---|---|
| Budget cut (temporary) | Pause 1-3 months | Hold data, hold price, resume anytime |
| Low usage (seasonal) | Downgrade to maintenance tier | Reduced scope, reduced price |
| Team transition | Pause 1 month | Free re-onboarding when new team is ready |
| "Just not a priority" | Pause with monthly check-in | Quick email: "Ready to resume?" |

**Why pauses work:** 40-60% of paused accounts reactivate. 0% of cancelled accounts come back voluntarily.

---

## Phase 6: Expansion Revenue (Grow Without Acquiring)

### The Expansion Playbook

**Top B2B SaaS companies generate 30-50% of new ARR from existing clients.** Expansion is cheaper, faster, and more reliable than acquisition.

### 5 Expansion Triggers

| Trigger | Signal | Approach |
|---|---|---|
| Usage ceiling | Hitting plan limits | "You're growing fast — here's how Scale tier removes the cap" |
| New use case | They mention adjacent problem | "We actually solve that too — want a quick demo?" |
| Team growth | New hires, departments | "Your team grew — want to add seats / expand access?" |
| Success milestone | Hit a big goal | "Congrats on [milestone]! Clients at your stage usually benefit from [X]" |
| Annual renewal | Contract renewal approaching | "Before we renew, let's look at what's changed and what you might need" |

### Pricing Psychology for Expansion

```yaml
expansion_pricing:
  anchor_to_value:
    - "This feature generates $X/month for similar clients"
    - "At your current volume, the upgrade pays for itself in [N] weeks"
  
  bundle_discount:
    - Package 2-3 add-ons at 15-20% less than individual prices
    - "Most clients at your stage add [X] and [Y] together"
  
  annual_commit:
    - 15-20% discount for annual payment
    - Position as: "Lock in this rate before our next price increase"
    - Only offer when health score is green (don't reward at-risk with discounts)
  
  land_and_expand:
    - Start small, prove value, grow scope
    - "Let's pilot this with one team for 30 days, then expand"
    - Lower risk = higher conversion
  
  never_do:
    - Discount to save a churning client (trains them to threaten churn)
    - Bundle everything together (leaves no expansion room)
    - Surprise price increases without added value
```

### Net Revenue Retention (NRR) Calculation

```
NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR × 100

Example:
  Starting MRR: $50,000
  Expansion (upsells): +$8,000
  Contraction (downgrades): -$2,000
  Churn: -$3,000
  
  NRR = ($50,000 + $8,000 - $2,000 - $3,000) / $50,000 × 100 = 106%

Target NRR by segment:
  SMB: 90-100% (some churn is normal)
  Mid-Market: 100-110%
  Enterprise: 110-130%
  Best in class: 130%+ (Snowflake, Twilio at scale)
```

---

## Phase 7: Reactivation (Win-Back Campaigns)

### Reactivation Timing Sequence

```yaml
reactivation_sequence:
  day_7:
    subject: "We saved your setup"
    tone: Soft, no pressure
    message: |
      Hey [Name], your [data/setup/config] is still here. 
      If anything changes, you can pick up right where you left off.
    cta: "Reactivate in one click"
  
  day_30:
    subject: "Here's what you're missing"
    tone: Value-focused
    message: |
      Since you left, we've added [new feature/improvement].
      Clients like you are seeing [specific result].
    cta: "See what's new"
    incentive: None yet
  
  day_60:
    subject: "[Name], quick question"
    tone: Personal, curious
    message: |
      I've been wondering — did you find a solution for [their original problem]?
      If not, I'd love to show you how [specific improvement] addresses 
      exactly what wasn't working before.
    cta: "15-min call"
    incentive: Optional — free month or reduced rate for 3 months
  
  day_90:
    subject: "Last one from me"
    tone: Respectful closure
    message: |
      I won't keep emailing — I know your inbox is busy.
      If you ever want to revisit [problem we solve], we'll be here.
      Your data is saved for another 90 days.
    cta: "Reactivate anytime"
    incentive: Best offer (30% off for 3 months, or free month)
  
  day_180:
    subject: "Your data is expiring"
    tone: Factual, urgency
    message: |
      Your [data/setup] will be deleted in 30 days per our retention policy.
      Want to keep it? Reactivate or export before [date].
    cta: "Save my data" / "Export"
```

### Reactivation Performance Benchmarks

| Metric | Good | Great | Best in Class |
|---|---|---|---|
| Overall win-back rate | 5-10% | 10-15% | 15-25% |
| Day 7-30 reactivation | 3-5% | 5-8% | 8-12% |
| Incentive conversion lift | 2x baseline | 3x | 4x |
| Reactivated client retention (6mo) | 50% | 65% | 80% |

---

## Phase 8: Involuntary Churn Prevention (Payment Recovery)

**30-40% of all churn is involuntary** — failed payments, expired cards, billing errors. This is free revenue you're leaving on the table.

### Payment Recovery Sequence

```yaml
payment_recovery:
  attempt_1_failed:
    action: Retry payment in 24 hours (automatic)
    notification: None (many are temporary holds)
  
  attempt_2_failed:
    action: Retry in 48 hours
    notification: |
      Friendly email: "Heads up — your payment didn't go through. 
      This usually happens when a card expires or has a temporary hold.
      Update your payment method here: [link]"
    tone: Helpful, not threatening
  
  attempt_3_failed:
    action: Retry in 72 hours
    notification: |
      More urgent: "Your account is at risk of interruption. 
      We don't want you to lose access to [specific value they use].
      Takes 30 seconds to update: [link]"
    add: In-app banner if applicable
  
  day_10:
    action: Final retry
    notification: |
      "Last attempt before we pause your account. 
      Your [data/setup/progress] is safe — just update payment to continue."
    escalation: Personal email from account manager for high-value accounts
  
  day_14:
    action: Pause account (don't delete)
    notification: |
      "Your account is paused. Everything is saved.
      Reactivate anytime: [link]"
    retention: Hold data for 90 days minimum
```

### Card Update Optimization

- **Pre-expiry reminder:** Email 30 days before card expires: "Your card ending in [XXXX] expires next month. Update now to avoid interruption."
- **Multiple payment methods:** Allow backup cards
- **Smart retry timing:** Retry on the 1st and 15th (payday alignment)
- **Account updater service:** Use Stripe/processor card updater to auto-refresh expired cards

---

## Phase 9: Segmented Retention Strategies

Different clients need different approaches.

### By Revenue Tier

```yaml
retention_by_tier:
  enterprise: # >$5,000/mo
    cadence: Weekly touchpoint, monthly deep dive, quarterly QBR
    team: Dedicated CSM + executive sponsor
    expansion: Custom solutions, multi-year deals
    save_budget: Up to 25% discount for 6 months
    
  mid_market: # $500-5,000/mo
    cadence: Bi-weekly check-in, quarterly QBR
    team: Shared CSM (1:20 ratio)
    expansion: Tier upgrades, add-on features
    save_budget: Up to 15% discount for 3 months
    
  smb: # <$500/mo
    cadence: Monthly automated report, quarterly email check-in
    team: Tech touch (automated) + pooled support
    expansion: Annual commit discount, referral program
    save_budget: Pause option only (no discounts at this tier)
    
  free_trial:
    cadence: Day 1, 3, 7, 10, 13 (end of trial)
    team: Automated sequences + sales for high-intent
    conversion: Demo offer at day 7, discount at day 12
```

### By Lifecycle Stage

| Stage | Focus | Key Metric | Action |
|---|---|---|---|
| 0-30 days | Activation | Time to first value | Accelerate onboarding |
| 30-90 days | Habit formation | Weekly active usage | Feature discovery |
| 90-180 days | Deepening | Feature breadth | Training, QBR |
| 180-365 days | Expansion | NRR | Upsell conversations |
| 365+ days | Loyalty | Advocacy score | Referral program, case study |

---

## Phase 10: Metrics Dashboard

### Weekly Retention Dashboard

```yaml
weekly_dashboard:
  headline_metrics:
    - gross_churn_rate: "% of MRR lost to cancellations"
    - net_churn_rate: "Gross churn minus expansion revenue"
    - nrr: "Net Revenue Retention — THE number that matters"
    - logo_churn: "% of customers lost (not weighted by revenue)"
  
  health_distribution:
    - healthy_accounts: "[count] ([%]) — $[MRR]"
    - monitor_accounts: "[count] ([%]) — $[MRR]"
    - at_risk_accounts: "[count] ([%]) — $[MRR]"
    - critical_accounts: "[count] ([%]) — $[MRR]"
  
  pipeline:
    - expansion_pipeline: "$[amount] in active upsell conversations"
    - renewals_next_30_days: "[count] accounts, $[MRR] at stake"
    - saves_this_week: "[count] interventions, [count] saved, $[MRR] recovered"
  
  cohort_snapshot:
    - latest_cohort_d30: "[%] — trending [up/down] vs prior cohort"
    - best_cohort: "[month] at [%] — analyze why"
    - worst_cohort: "[month] at [%] — analyze why"
```

### Monthly Executive Summary Template

```markdown
# Retention Report — [Month Year]

## Headline
- NRR: [X]% ([up/down] from [last month]%)
- Gross churn: [X]% ($[amount])
- Expansion: $[amount] ([count] accounts upgraded)
- Net change: [+/-]$[amount] MRR from existing clients

## Wins
- [Specific save story with numbers]
- [Expansion win with numbers]

## Risks
- [X] accounts in critical health ([total MRR at risk])
- Top risk: [Account name] — [reason] — [plan]

## Actions for Next Month
1. [Specific action with owner and deadline]
2. [Specific action with owner and deadline]
```

---

## Retention Benchmarks by Industry

| Industry | Good Monthly Churn | Great | Best in Class |
|---|---|---|---|
| B2B SaaS (SMB) | < 5% | < 3% | < 2% |
| B2B SaaS (Enterprise) | < 2% | < 1% | < 0.5% |
| B2C Subscription | < 7% | < 5% | < 3% |
| Agency / Consulting | < 8% | < 5% | < 3% |
| E-commerce (subscription box) | < 10% | < 7% | < 5% |
| Fitness / Wellness | < 12% | < 8% | < 5% |

---

## 10 Revenue-Killing Retention Mistakes

1. **No health score** — you learn about churn AFTER it happens
2. **Single-threaded relationships** — one contact leaves, you lose the account
3. **Generic onboarding** — same flow for a $100/mo and $10,000/mo client
4. **No monthly value report** — clients forget you exist
5. **Reactive QBRs** — only calling when renewal is due (too late)
6. **Discounting to save** — trains clients to threaten churn for deals
7. **Ignoring involuntary churn** — 30-40% of churn is payment failures you can prevent
8. **No reactivation sequence** — churned clients vanish forever
9. **Treating all churn the same** — voluntary vs involuntary, high-value vs low-value need different playbooks
10. **Measuring logo churn not revenue churn** — losing 10 small accounts is different from losing 1 whale

---

## Natural Language Commands

| Command | What It Does |
|---|---|
| "Score [client name]" | Calculate health score for specific account |
| "Onboarding checklist for [client]" | Generate personalized 90-day onboarding plan |
| "QBR prep for [client]" | Build QBR agenda with their metrics and talking points |
| "Churn risk report" | List all accounts by health tier with recommended actions |
| "Monthly report for [client]" | Generate value report with metrics template |
| "Save playbook for [client]" | Diagnose churn reason and recommend intervention |
| "Expansion opportunities" | List healthy accounts with upsell potential |
| "Reactivation list" | Show churned accounts eligible for win-back |
| "NRR this month" | Calculate net revenue retention |
| "Payment failures" | List accounts with failed payments and recovery status |
