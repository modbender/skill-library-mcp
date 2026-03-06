---
name: sales-rhythm-tracker
version: 1.0.0
author: yinguofeng007
description: >
  B2B sales pipeline manager powered by the Alibaba Iron Army (阿里铁军) methodology.
  Use this skill for daily sales briefings, lead management, pipeline health checks,
  weekly sprint planning, customer follow-up prioritization, and closing strategy.
  Triggered by phrases like: "morning sales brief", "add lead", "pipeline review",
  "who should I call today", "weekly sales plan", "sales update", "close rate",
  "follow up", "deal stuck", "customer type", "sales sprint".
tags: [sales, crm, pipeline, b2b, productivity, business, revenue]
category: business
---

# Sales Rhythm Tracker
### Powered by the Alibaba Iron Army Methodology (阿里铁军方法论)

> "Let 80% of your people achieve 80% of the top performer's results — through system, not talent."
> — Alibaba Iron Army Core Principle

---

## What This Skill Does

This skill transforms your OpenClaw agent into a personal B2B sales coach and pipeline manager. It applies the same methodology that built Alibaba's legendary direct sales force — the "Iron Army" that grew Alibaba.com from zero to market dominance across China's SMB sector.

Unlike generic CRM tools, this skill encodes *sales thinking*, not just data storage. Your agent will tell you **who to call, when, why, and how** — based on proven rhythms, not gut feel.

**Data lives locally.** No SaaS subscription. No API keys. Your pipeline in plain markdown files.

---

## The Methodology: Alibaba Iron Army Framework

Before using this skill, understand the philosophy your agent now operates on:

### Principle 1: The Boiling Water Theory (烧水理论)
Every customer relationship is like water heating toward boiling (closing). A first visit gets the water to 70°C. Consistent follow-up brings it to 100°C (close). **A gap that's too long lets the water cool back to cold** — and you restart from scratch. Your agent tracks the "temperature" of every lead and alerts you before deals go cold.

### Principle 2: Three-Step Sprint Cycle (三步一杀)
Every 4-week cycle follows this rhythm:
- **Week 1 — Seed (播种)**: Maximum outreach. Volume is the foundation. Target 40+ touches.
- **Week 2 — Flip (翻牌)**: Filter ruthlessly. Identify the top 30% worth pursuing. Walk away from the rest.
- **Week 3 — Harvest (采果)**: Close sprint. Push every qualified lead to YES or NO. No gray zones.
- **Week 4 — Reset (机动)**: Handle onboarding, collect payment, start seeding next cycle.

### Principle 3: The 8-Visit Daily Structure (每日八访)
A productive sales day consists of:
- 4 × New customer visits/calls (seed phase)
- 2 × Follow-up visits (nurture phase, 2nd or 3rd contact)
- 2 × Closing visits (harvest phase, move to YES/NO)

### Principle 4: Four Customer Personality Types (四型客户)
Every customer has a dominant style. Matching your approach to their type is the single highest-leverage sales skill:

| Type | Chinese | Traits | What They Need | Your Approach |
|------|---------|--------|---------------|---------------|
| **Tiger** | 老虎型 | Direct, decisive, impatient, results-driven | Bottom line, ROI, fast answers | Lead with outcomes. Be brief. Skip small talk. Use data. |
| **Peacock** | 孔雀型 | Enthusiastic, social, optimistic, status-conscious | Recognition, relationships, exciting vision | Build rapport first. Tell success stories. Be energetic. |
| **Koala** | 无尾熊型 | Patient, loyal, risk-averse, team-oriented | Safety, proof, support, consensus | Build trust slowly. Provide case studies. Never rush. |
| **Owl** | 猫头鹰型 | Analytical, precise, systematic, skeptical | Data, accuracy, process, completeness | Prepare detailed answers. Be precise. Address every concern. |

### Principle 5: The Traffic Light System (红黄绿)
Every lead gets a status color at each review:
- 🟢 **Green**: Momentum is healthy. Follow-up on schedule. Keep heating.
- 🟡 **Yellow**: Stalled. Something slowed down. Needs diagnosis and intervention.
- 🔴 **Red**: Relationship cooling. Urgent action required or acknowledge as lost.

### Principle 6: Four-Step Sales Conversation (四步销售法)
Every customer interaction follows this sequence:
1. **挖需求 (Uncover)**: Ask questions to understand their real pain. 70% listening, 30% talking.
2. **抛产品 (Present)**: Match your solution to their specific pain. Not features — outcomes.
3. **解问题 (Address)**: Handle objections. Every objection is a buying signal in disguise.
4. **提成交 (Close)**: Ask for the commitment. Silence after asking is your best tool.

### Principle 7: Phone Call Protocol (电话拜访规则)
- Optimal call length: **3–5 minutes** (maximum 6 minutes)
- Before every call: Write down your ONE objective for this call
- Best use cases: Follow-up confirmation, closing push, payment collection
- After every call: Log the result within 10 minutes while memory is fresh

### Principle 8: ASK Growth System
Every sales improvement requires development in three dimensions:
- **A — Attitude (心态)**: Belief in the product, resilience, ownership mindset
- **S — Skill (技能)**: Prospecting, questioning, objection handling, closing
- **K — Knowledge (知识)**: Industry, product, competition, customer context

---

## Pipeline Stages

Leads move through 8 stages. Your agent tracks stage and days-in-stage:

| Stage | Label | Description | Healthy Duration |
|-------|-------|-------------|-----------------|
| 1 | `prospect` | Identified, not yet contacted | — |
| 2 | `connected` | First contact made, initial interest | 1–3 days |
| 3 | `qualified` | Pain confirmed, budget exists | 3–7 days |
| 4 | `presented` | Solution presented | 3–7 days |
| 5 | `proposal` | Formal proposal submitted | 3–10 days |
| 6 | `negotiation` | Active negotiation on terms | 3–14 days |
| 7 | `closing` | Final push — YES or NO this week | 1–5 days |
| 8 | `won` | Closed. Onboarding. Collect payment. | — |
| 9 | `lost` | Lost. Record reason. Learn. | — |

**Alert rule**: Any lead stuck in the same stage for more than double the healthy duration = 🔴 Red status.

---

## Lead Scoring (0–100)

Your agent automatically scores each lead to prioritize your daily actions:

| Factor | Max Points | How It's Calculated |
|--------|-----------|---------------------|
| Stage progression | 25 | Higher stage = more points |
| Recency of contact | 20 | Last contact < 3 days = 20pts; < 7 days = 10pts; > 14 days = 0pts |
| Engagement level | 20 | Customer-initiated contact = high; passive = low |
| Deal size | 15 | Relative to your average deal size |
| Time pressure | 20 | Customer deadline approaching = high score |

**Score interpretation**:
- 80–100: 🔥 Hot — close this week
- 60–79: ✅ Warm — maintain rhythm, don't let cool
- 40–59: 🟡 Lukewarm — needs intervention or deprioritize
- Below 40: 🔴 Cold — decide: revive or move on

---

## Commands & Usage

### Daily Commands

**Morning Brief** (run every morning before 9am):
> "Morning sales brief" / "Who should I call today?" / "Sales priorities today"

Agent will: Scan pipeline → Score all leads → Generate top 3–5 priority actions → Suggest approach for each based on customer type.

**Log Activity** (after every call/meeting):
> "Log: [customer name] — [what happened] — [next step]"
> Example: "Log: Sarah Chen at TechBridge — she's interested but wants to loop in her CEO — next step: send exec summary by Thursday"

Agent will: Record activity → Update lead status → Recalculate score → Flag if rhythm is at risk.

**Add New Lead**:
> "New lead: [Name] at [Company] — [context]"
> Example: "New lead: David Park at Sunrise Manufacturing — met at trade show, interested in reducing procurement costs"

Agent will: Create lead profile → Classify personality type from context → Set stage to connected → Add to next morning brief.

**Check Deal Status**:
> "How is [customer name] doing?" / "Update on [company]"

Agent will: Pull customer profile → Show stage, score, last contact, temperature → Recommend next action.

### Weekly Commands

**Weekly Sprint Plan** (every Monday morning):
> "Weekly sprint plan" / "Monday sales planning"

Agent will: Apply Three-Step Sprint logic to current week in the cycle → Categorize all leads by this week's priority tier → Generate a concrete 5-day action plan → Identify leads that need a YES/NO decision this week.

**Pipeline Health Review** (every Friday):
> "Pipeline review" / "End of week sales check" / "Pipeline health"

Agent will: Calculate overall pipeline velocity → Flag stalled deals → Identify temperature-cooling risks → Suggest which leads to cut (翻牌) → Project next 2-week revenue likelihood.

**Stuck Deal Diagnosis**:
> "Deal stuck: [customer name]" / "[Customer] hasn't responded, what do I do?"

Agent will: Diagnose cause of stall using Iron Army framework → Suggest intervention based on customer type → Provide exact language/script for next outreach.

---

## File Structure

This skill uses local files in your workspace:

```
~/.openclaw/workspace/sales/
├── pipeline.md          ← Your CRM: all active leads
├── activity-log.md      ← Every interaction logged
├── weekly-sprint.md     ← Current week's plan
└── closed-deals.md      ← Won/lost deals (for learning)
```

To initialize: run `scripts/init-pipeline.sh` once.

---

## Morning Brief Format

Every morning brief follows this structure:

```
📊 SALES MORNING BRIEF — [Date]
Cycle: Week [1/2/3/4] of [Month] Sprint

🔥 TOP PRIORITY TODAY (must-do):
1. [Customer] — [Stage] — Score: [X] — [Why urgent] — [Recommended action]
2. [Customer] — [Stage] — Score: [X] — [Why urgent] — [Recommended action]

✅ MAINTAIN RHYTHM (important):
3. [Customer] — [Stage] — Last contact: [X days ago] — [Action]
4. [Customer] — [Stage] — Last contact: [X days ago] — [Action]

⚡ SEED TODAY (new outreach):
- [Target sector/type for today's cold outreach]

📈 PIPELINE SNAPSHOT:
- Active leads: [N]
- This week's close targets: [N]
- Deals cooling (>7 days no contact): [N]
- 🔴 Red alerts: [N]
```

---

## Weekly Sprint Plan Format

```
🗓 WEEKLY SPRINT — Week [N] of [Month] — [3-Step Phase]
Phase: [SEED / FLIP / HARVEST / RESET]

PHASE OBJECTIVE:
[What this week is about based on the 3-step cycle]

MONDAY — Launch:
TUESDAY — Deepen:
WEDNESDAY — Accelerate:
THURSDAY — Push:
FRIDAY — Review & Reset:

THIS WEEK'S CLOSE TARGETS (need YES or NO):
1. [Customer] — [Stage] — Closing script: [approach]
2. [Customer] — [Stage] — Closing script: [approach]

LEADS TO FLIP (qualify or drop):
- [Customer] — [Reason to decide]

SEED TARGETS (new outreach, 4+ per day):
- [Target profile for this week]

FRIDAY SUCCESS CRITERIA:
□ [N] deals moved forward at least one stage
□ [N] YES or NO decisions obtained
□ [N] new leads added to pipeline
```

---

## Stuck Deal Scripts (by Customer Type)

### Tiger (老虎型) — deal stalled:
> "I know you're busy, so I'll be direct: the question on the table is X. If we move forward by [date], you get [specific benefit]. If not, I completely understand. Which is it?"

### Peacock (孔雀型) — deal stalled:
> "Hey [name], I was just showing your situation to a colleague and they immediately said this reminded them of [success story]. Made me think — let's get the team together for a quick 20-min call this week. When works for you?"

### Koala (无尾熊型) — deal stalled:
> "I wanted to check in and share something that might help ease the decision. Three other companies in your industry have been through exactly this situation — here's what they found. No rush at all — just want to make sure you have everything you need to feel confident."

### Owl (猫头鹰型) — deal stalled:
> "I realized I hadn't sent over the complete technical spec and the full pricing breakdown with all variables. Sending that now. Let me know if any number looks different from what you expected — I'd rather address it directly than have any ambiguity."

---

## Integration Notes

- Works with any messaging channel (Telegram, WhatsApp, Slack, Discord)
- No external API required — all data stored locally
- Pairs well with: `gog` skill (Google Calendar integration for scheduling follow-ups)
- Compatible with: `memo` (brew) for quick voice-to-text lead logging
- Daily cron suggested: `0 8 * * 1-5` for automatic morning brief delivery

---

## Quick Start

```bash
# 1. Install skill
cp -r sales-rhythm-tracker ~/.openclaw/skills/

# 2. Initialize your pipeline workspace
~/.openclaw/skills/sales-rhythm-tracker/scripts/init-pipeline.sh

# 3. Add your first lead (via your messaging app):
# "New lead: [Name] at [Company] — [context of how you met]"

# 4. Get your first morning brief:
# "Morning sales brief"
```

---

*Built on the Alibaba Iron Army (阿里铁军) methodology — the sales system that trained 10,000+ B2B salespeople and generated billions in SMB revenue across China.*
