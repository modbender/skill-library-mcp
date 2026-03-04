# Memory Compaction Workflow
**Purpose:** Keep long-term memory manageable and prevent context bloat

## Memory Structure

### Daily Logs (Raw)
- **Location:** `memory/YYYY-MM-DD.md`
- **Purpose:** Raw chronological log of events, decisions, learnings
- **Retention:** 30 days
- **Format:** Timestamped entries, unedited stream of consciousness

### Long-Term Memory (Curated)
- **Location:** `MEMORY.md`
- **Purpose:** Distilled wisdom, important patterns, key decisions
- **Retention:** Permanent (but updated/refined over time)
- **Format:** Organized sections, curated insights

### Archives (Compressed)
- **Location:** `memory/archive/YYYY-MM-summary.md`
- **Purpose:** Compressed summaries of old daily logs
- **Retention:** Indefinite (small footprint)
- **Format:** Weekly or monthly summaries

---

## Compaction Schedule

### Weekly Compaction (Every Sunday during heartbeat)
**Process:**
1. Review daily logs from 7-14 days ago
2. Extract:
   - Key decisions made
   - New patterns learned
   - Important context for future
   - Tool/skill discoveries
3. Update MEMORY.md with distilled insights
4. Create weekly summary if significant events occurred

**Time estimate:** 5-10 minutes

### Monthly Archival (First of each month)
**Process:**
1. Review all daily logs >30 days old
2. Create monthly summary in `memory/archive/`
3. Delete raw daily logs >30 days (after archival confirmation)
4. Update MEMORY.md index if structure changed

**Time estimate:** 15-20 minutes

---

## What to Extract to MEMORY.md

### ✅ Keep Long-Term:
- **Patterns:** Recurring issues, successful workflows, failure modes
- **Decisions:** Major architectural choices, tool selections, rejected alternatives
- **Context:** Background info needed to understand why things are the way they are
- **Preferences:** Eugene's stated preferences about communication, tools, workflows
- **Relationships:** Connections between different parts of the system
- **Lessons:** "Don't do X because Y" type insights

### ❌ Don't Keep:
- Ephemeral task updates ("Started X", "Finished Y")
- Routine operations (daily heartbeat acks, simple queries)
- Temporary states that are no longer relevant
- Debug logs from resolved issues
- Duplicated information already in MEMORY.md

---

## Compaction Checklist

### Weekly (Sundays)
- [ ] Read daily logs from last 7-14 days
- [ ] Identify 2-3 key insights worth keeping
- [ ] Update relevant sections in MEMORY.md
- [ ] Note if any old info in MEMORY.md is now obsolete
- [ ] Log compaction completion in today's daily log

### Monthly (1st of month)
- [ ] Create archive summary for previous month
- [ ] Move summary to `memory/archive/`
- [ ] Delete daily logs >30 days old (after archival)
- [ ] Review MEMORY.md structure — is it still organized?
- [ ] Update this checklist if workflow needs adjustment

---

## Memory Sections in MEMORY.md

**Current structure:**
1. Identity (who I am, who Eugene is)
2. Setup (technical configuration, tools, access)
3. Model Routing (cost optimization, model selection)
4. Working Style Lessons (proactive behavior, communication)
5. Security Rules
6. TODO (active tasks, pending items)

**Review these sections during compaction:**
- Is info still accurate?
- Are there duplicates?
- Is anything missing?
- Does structure make sense?

---

## Automation

### Cron Job (Optional - Phase 3)
Create a weekly cron job that sends a reminder:
```
Every Sunday 10:00 AM: "Weekly memory compaction time. Review last week's daily logs and update MEMORY.md."
```

**Implementation:** Use OpenClaw cron with isolated session + announce delivery

---

## Metrics to Track

- **Daily log size:** Avg lines per day (track bloat)
- **MEMORY.md size:** Total lines (should grow slowly)
- **Archive count:** Number of monthly summaries
- **Compaction frequency:** Actual vs. planned
- **Time spent:** Minutes per compaction session

**Goal:** Keep MEMORY.md under 500 lines, daily logs under 200 lines avg, compaction time under 10 min.

---

## Status

- **Last weekly compaction:** Never (workflow just created)
- **Last monthly archival:** N/A
- **Next weekly:** 2026-02-16 (Sunday)
- **Next monthly:** 2026-03-01
- **Current MEMORY.md size:** ~100 lines
- **Oldest daily log:** 2026-02-12 (2 days old)
