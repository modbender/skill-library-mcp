# Conceptual Framework

This document teaches the philosophical foundations of the Nate Jones Second Brain system. Understanding WHY the system works this way is essential for operating it correctly.

## System Overview

The Nate Jones Second Brain is a personal knowledge database built on two primitives:
- **Supabase**: PostgreSQL + pgvector (memory layer)
- **OpenRouter**: AI gateway (compute layer)

It has 5 tables:
- `thoughts` (inbox log)
- `people` (relationship tracking)
- `projects` (work tracking)
- `ideas` (creative capture)
- `admin` (tasks and logistics)

The system follows a capture-classify-route-surface pattern. The user captures thoughts. The agent classifies and routes them. The system surfaces what matters when it matters.

---

## Building Blocks

### 1. The Drop Box

**One frictionless capture point.**

The user throws thoughts at their agent through whatever channel they use — Slack, Signal, SMS, voice, CLI. The agent receives content; everything goes to the `thoughts` table first. No decisions required from the user at capture time.

**Why this matters:** The number one reason second brains fail is they require taxonomy work at capture time. The Drop Box eliminates that. One inbox. One action. One habit.

### 2. The Sorter

**AI classification with structured routing.**

When a thought arrives, the LLM classifies it:
- What type is it? (person_note, task, idea, observation, reference)
- Who's mentioned?
- What topics?
- Any action items?
- How confident is the classification? (0-1 score)

Based on the type and confidence, the agent routes the thought to the appropriate structured table (people, projects, ideas, admin) or leaves it in thoughts if it's a general observation/reference.

**Why this matters:** Humans hate organizing. AI is excellent at routing into a small set of stable buckets. Let the system sort so the user doesn't have to.

### 3. The Form

**Each table has a defined schema — a data contract.**

The people table always has name, context, follow_ups, tags. The projects table always has name, status, next_action, notes. Consistency enables automation.

**Why this matters:** Without a consistent form, you get messy notes that can't be reliably queried, summarized, or surfaced. The form is what makes everything downstream possible — daily digests, status queries, relationship lookups. It's a contract between the system and the user's future self.

### 4. The Filing Cabinet

**The structured tables are the source of truth.**

The structured tables (people, projects, ideas, admin) are the source of truth for each category. When there's a question about what's real — what projects are active, what you promised to follow up on, what ideas you've captured — these tables have the answer.

The thoughts table is the inbox log, NOT the source of truth for structured data. Once a thought is routed to a structured table, that table owns the data. The thoughts table keeps the audit trail.

### 5. The Bouncer

**Confidence threshold.**

When the LLM classifies a thought with confidence below 0.6, DON'T route it to a structured table. Leave it in the thoughts table with `routed_to: null` and tell the user you weren't sure where to file it.

**Why this matters:** The fastest way to kill a system is to fill it with garbage. If every half-formed thought and misclassified entry ends up in the structured tables, the user stops trusting the data. The Bouncer keeps things clean enough to maintain trust. Trust is what keeps people coming back.

### 6. The Receipt

**The thoughts table IS the receipt.**

Every capture is logged there with: the original text, the classification metadata, the confidence score, where it was routed, and the ID of the destination record.

**Why this matters:** People don't abandon systems because they're imperfect. They abandon them because errors feel mysterious. The Receipt gives visibility: what came in, what the system did with it, how confident it was. Trust comes from visibility.

### 7. The Tap on the Shoulder (Application Layer)

**Proactive surfacing — the system pushing useful information at the right time.**

Daily digest of active projects + pending tasks. Weekly review of what was captured. Follow-up reminders from the people table.

The data structure supports this (query active projects, pending admin tasks, recent people follow-ups), but the delivery mechanism is application layer — the agent, a cron job, a dashboard, whatever the user builds.

**Why this matters:** Humans don't retrieve consistently. We don't wake up and search our databases. But we respond to what shows up in front of us. Build the data so a Tap on the Shoulder is easy to implement.

### 8. The Fix Button

**Agent-mediated corrections.**

When the user says "that should be a project, not a task" or "you filed Sarah wrong," the agent:
1. Finds the original record
2. Deletes it from the wrong table
3. Creates it in the right table
4. Updates the thoughts row's routed_to and routed_id

Corrections must be trivial or people won't make them. The agent IS the Fix Button.

---

## Key Principles

### Reduce the human's job to one reliable behavior

The user captures thoughts. That's it. Everything else — classification, routing, filing, embedding, confirming — is the agent + the system. If your workflow requires the human to do more than capture, you're building a self-improvement program, not a system.

### Separate memory from compute from interface

- **Memory** = Supabase (where truth lives)
- **Compute** = OpenRouter (where intelligence runs)
- **Interface** = The agent, Slack, Signal, CLI, a web dashboard (where the human interacts)

Each layer has one job. Swap any layer without touching the others. Change your interface from Signal to Slack without rebuilding your database. Swap Claude for GPT without touching your storage. This is what makes the system future-proof.

### Default to safe behavior when uncertain

When the Bouncer triggers (confidence < 0.6), don't route. Log it, flag it, ask the user. A wrong classification pollutes the database with bad data. Bad data erodes trust. Eroded trust kills the system. The safest default is: when uncertain, don't act.

### Prefer routing over organizing

Don't make users maintain structures. Let the Sorter route into a small set of stable buckets. Four structured tables (people, projects, ideas, admin) is enough for most knowledge work. Each additional category creates more decision surface. Keep it small.

### Use "next action" as the unit of execution

"Work on the website" is not an action — it's an intention. "Email Sarah to confirm the copy deadline" is an action. When classifying project-related thoughts, extract concrete next actions. If your project entries don't have concrete next steps, any digest you build will feel motivational rather than operational.

### Design for restart, not perfection

Users will fall off. They'll stop capturing for a week. That's normal. The system must be patient — don't require "catching up." Just restart. Do a brain dump, let the system sort it, and resume. The automation keeps running whether the user engages or not.

### Keep categories and fields painfully small

Four structured tables. Five to six fields each. Start simple. Stay simple until there's genuine pain that a new field would solve. "This would be cool" is not pain. "I keep losing track of X" is pain. Minimal fields mean faster entry, easier maintenance, and fewer things to go wrong. You can always add sophistication. You can't undo abandonment.

---

Built by Limited Edition Jonathan • natebjones.com
