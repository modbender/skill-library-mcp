# Sales Rhythm Tracker
### B2B Pipeline Manager powered by the Alibaba Iron Army Methodology

[![ClawHub](https://img.shields.io/badge/ClawHub-Business-blue)](https://clawhub.ai)
[![Category](https://img.shields.io/badge/Category-Business-green)](https://clawhub.ai)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

> **"Let 80% of your team achieve 80% of the top performer's results — through system, not talent."**
> — Alibaba Iron Army Core Principle

---

## What Is This?

**Sales Rhythm Tracker** turns your OpenClaw agent into a B2B sales coach that tells you *who to call, when, why, and how* — every single day.

It encodes the **Alibaba Iron Army (阿里铁军)** methodology — the same sales operating system that built Alibaba's B2B direct sales force from zero, trained 10,000+ salespeople, and was later adopted by companies like Meituan, Didi, and hundreds of Chinese startups.

This is not a generic CRM. It's a **sales thinking engine** built on proven frameworks.

---

## Why This Works

Most CRM tools track data. This skill encodes *behavior* — the daily rhythms, weekly sprint cycles, customer psychology frameworks, and closing tactics that separate top performers from average ones.

**The core insight**: Sales performance is 80% rhythm and 20% talent. The Iron Army proved this by making ordinary people extraordinary through discipline and system.

---

## Core Methodologies Encoded

| Framework | What It Does |
|-----------|-------------|
| **Three-Step Sprint (三步一杀)** | 4-week cycle: Seed → Flip → Harvest → Reset. Never lose momentum. |
| **8-Visit Daily Structure** | 4 new + 2 follow-up + 2 closing visits every day. Non-negotiable. |
| **Four Customer Types** | Tiger/Peacock/Koala/Owl — match your approach to their psychology. |
| **Boiling Water Theory (烧水理论)** | Track deal temperature. Never let water cool. |
| **Traffic Light System (红黄绿)** | Green/Yellow/Red status on every lead. Instant risk visibility. |
| **Four-Step Sales Conversation** | Uncover → Present → Address → Close. Every interaction. |
| **Phone Call Protocol** | 3-5 minute calls. One clear objective. Log within 10 minutes. |
| **Lead Scoring (0-100)** | Stage + Recency + Engagement + Deal Size + Time Pressure. |

---

## Installation

```bash
# Step 1: Copy skill to OpenClaw
cp -r sales-rhythm-tracker ~/.openclaw/skills/

# Step 2: Make scripts executable
chmod +x ~/.openclaw/skills/sales-rhythm-tracker/scripts/*.sh

# Step 3: Initialize your pipeline workspace
~/.openclaw/skills/sales-rhythm-tracker/scripts/init-pipeline.sh

# Step 4 (Optional): Set up daily morning brief at 8am
openclaw cron add \
  --name "morning-sales-brief" \
  --schedule "0 8 * * 1-5" \
  --message "Morning sales brief"
```

---

## Quick Start — First 10 Minutes

**1. Add your first lead** (via your messaging app):
```
New lead: John Smith at Acme Manufacturing — met at trade show, interested in reducing procurement costs
```

**2. Get your morning brief**:
```
Morning sales brief
```

**3. Log your first activity**:
```
Log: John Smith — called him, he's interested but wants to loop in his VP — I'll send an exec summary
```

**4. Get a weekly plan**:
```
Weekly sprint plan
```

---

## Daily Commands

| You say... | Agent does... |
|-----------|--------------|
| "Morning sales brief" | Scans pipeline → Scores leads → Gives top 3-5 priorities with scripts |
| "New lead: [Name] at [Company] — [context]" | Creates lead profile, sets stage, schedules first follow-up |
| "Log: [Customer] — [what happened] — [next step]" | Records activity, updates pipeline, recalculates score |
| "How is [customer] doing?" | Full status: stage, score, last contact, temperature, next action |
| "Deal stuck: [customer]" | Diagnoses stall reason + provides exact intervention script by customer type |
| "Pipeline review" | Full health analysis: velocity, risks, cuts, next week guidance |
| "Weekly sprint plan" | Monday plan based on current sprint phase and pipeline state |

---

## Data Structure

All data lives locally in plain markdown files — no cloud, no subscriptions:

```
~/.openclaw/workspace/sales/
├── pipeline.md          ← Your live CRM
├── activity-log.md      ← Every touchpoint logged
├── weekly-sprint.md     ← Current week's plan
└── closed-deals.md      ← Won/Lost + learnings
```

---

## What You Get Each Morning

```
📊 SALES MORNING BRIEF — 2026-02-24 (Monday)
Sprint: Week 1 | Phase: SEED — Maximize outreach. Build your pipeline.

🔥 TOP PRIORITY TODAY:
1. Sarah Chen @ TechBridge — Stage: Closing — Score: 88
   Last contact: 2 days ago. Sent proposal Thursday.
   → She's a Koala. Don't rush. Send: "I wanted to make sure you have
     everything you need to feel confident about this decision..."

2. David Park @ Sunrise Mfg — Stage: Negotiation — Score: 76
   Last contact: 5 days ago. 🟡 Rhythm slipping.
   → He's a Tiger. Be direct: "David, where are we on the final number?"

✅ MAINTAIN RHYTHM:
3. Wei Lin @ FastGrow Ltd — Stage: Qualified — Score: 61
   Last contact: 3 days ago. Demo scheduled Friday.
   → Prep 3 ROI data points before the demo. She's an Owl.

⚡ SEED TODAY (4 new contacts):
Target: Manufacturing companies, 50-200 employees, procurement pain

📈 PIPELINE SNAPSHOT:
• Active leads: 8 | Closing this week: 2 | 🔴 Red alerts: 1
• Deal cooling: Marcus @ RetailCo (12 days no contact — intervene today)
```

---

## Proven Results: The Iron Army Track Record

The Alibaba Iron Army methodology this skill encodes:
- Trained **10,000+** B2B salespeople in China
- Achieved **80%+ quota attainment** across the team (not just top performers)
- Methodology was adopted by **Meituan, Didi, and 100+ Chinese startups**
- Core principle proven: systematic rhythm beats individual talent
- Average cycle length: **21 days** from first contact to close (SMB B2B)

---

## Pairs Well With

- [`gog`](https://clawhub.ai) — Google Calendar integration for scheduling follow-ups
- [`memo`](https://formulae.brew.sh/formula/memo) — Voice-to-text lead logging
- [`remind`](https://formulae.brew.sh/formula/remind) — Time-based follow-up reminders

---

## Philosophy

> *"Manage the process, not just the outcome. The outcome is a result of the process."*

Most salespeople track what happened. The Iron Army tracks what *should* happen next — and ensures it does. This skill brings that discipline to your OpenClaw agent.

---

## License

MIT License — Free to use, modify, and distribute.

---

*Built on the Alibaba Iron Army (阿里铁军) methodology.*
*If this skill helps you close deals, consider leaving a ⭐ on ClawHub.*
