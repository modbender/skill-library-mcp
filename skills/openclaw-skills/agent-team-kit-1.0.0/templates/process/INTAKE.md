# Intake Process: How Work Flows

*The self-sustaining loop that keeps work moving without bottlenecks.*

---

## The Problem We're Solving

Before: One person manually added tasks. Ideas sat in parking lots. Nothing moved unless someone pushed it.

After: A self-sustaining system where work flows continuously and agents can self-serve.

---

## The Intake Loop

```
     ┌─────────────────────────────────────────────────────────┐
     │                                                         │
     ▼                                                         │
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│ DISCOVER│───▶│  TRIAGE │───▶│  READY  │───▶│ EXECUTE │──────┘
│         │    │         │    │         │    │         │
│ Scout 🔍│    │Rhythm 🥁│    │Self-Srv │    │ Agents  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     ▲                                              │
     │              Feedback Loop                   │
     └──────────────────────────────────────────────┘
```

---

## Phase 1: DISCOVER 🔍

**Owner:** Scout (or any agent who finds something)

**Sources of work:**
- User feedback (community channels, DMs, emails)
- Research findings (gaps, competitors, market shifts)
- Build failures (bugs, broken things, tech debt)
- Shipped work retrospectives (what should we improve?)
- External signals (social mentions, community requests)
- Internal signals (heartbeat checks, monitoring alerts)

**Output:** Raw ideas logged to `process/OPPORTUNITIES.md`

**Format for new entries:**
```markdown
### [Opportunity Name]
**Discovered:** YYYY-MM-DD
**Source:** [where it came from]
**Description:** [what's the opportunity/problem]
**Suggested action:** [rough idea of what to do]
```

**Who can add:** ANYONE. Discovery is open. If you see something, log it.

**Cadence:** 
- Scout does a dedicated discovery pass 2x/week
- Anyone adds opportunistically when they encounter things

---

## Phase 2: TRIAGE 🥁

**Owner:** Rhythm (Backlog Owner)

**When:** 
- Daily quick scan (5 min, async)
- Deep triage session at sprint boundaries

**The Triage Decision:**

For each item in OPPORTUNITIES.md, decide:

| Decision | Criteria | Destination |
|----------|----------|-------------|
| **READY** | Clear scope, high impact, can start now | → BACKLOG.md "Ready" section |
| **BLOCKED** | Needs info, depends on other work | → BACKLOG.md "Blocked" section |
| **PARK** | Good idea, not now | Leave in OPPORTUNITIES.md |
| **KILL** | Not aligned, low value | Delete from OPPORTUNITIES.md |

**Ready Criteria Checklist:**
- [ ] Clear outcome defined (what does "done" look like?)
- [ ] Size estimated (S/M/L)
- [ ] No blocking dependencies
- [ ] Aligned with current sprint/strategy
- [ ] Someone could pick this up without asking questions

---

## Phase 3: READY QUEUE 📋

**Location:** `process/BACKLOG.md` → "Ready" section

**Structure:**
```markdown
## 🟡 Ready (can be picked up)

### High Priority
| Task | Size | Notes |
|------|------|-------|
| [task] | S/M/L | [context] |

### Medium Priority
| Task | Size | Notes |
|------|------|-------|

### Low Priority
| Task | Size | Notes |
|------|------|-------|
```

**Rules:**
1. High priority = needs to happen this sprint
2. Medium priority = should happen soon
3. Low priority = when there's capacity
4. Agents pick from top-down (high before medium before low)
5. If two agents want the same task, first claim wins

---

## Phase 4: SELF-SERVICE EXECUTION 🤖

**How agents claim work:**

1. **Check the queue:** Read `process/BACKLOG.md`
2. **Pick a task:** Choose from Ready section (respect priority order)
3. **Claim it:** Update STATUS.md with your name + task
4. **Work it:** Do the thing
5. **Complete it:** Move to DONE, update STATUS.md

**Claim Format (in STATUS.md):**
```markdown
## Active Work

| Agent | Task | Started | Status |
|-------|------|---------|--------|
| [Agent] | [Task name] | [Date] | 🟡 In Progress |
```

**No bottleneck rule:** Agents don't need permission to pick up Ready tasks. If it's in Ready, it's fair game.

---

## Phase 5: FEEDBACK LOOP 🔄

**Owner:** Whoever completes the work

**After completing any task:**

1. **Log completion:** Update DONE section with what shipped
2. **Capture learnings:** What did we discover while building?
3. **Spawn opportunities:** Did this work reveal new tasks/problems?

**Feedback Template:**
```markdown
### [Task Name] — Completed YYYY-MM-DD

**What shipped:** [brief description]

**Learnings:**
- [what we learned]

**New opportunities discovered:**
- [any new ideas → add to OPPORTUNITIES.md]
```

**This closes the loop:** Completed work generates new discoveries, which feed back into the top of the funnel.

---

## Ownership Summary

| Phase | Owner | Backup |
|-------|-------|--------|
| Discover | Scout 🔍 | Any agent (opportunistic) |
| Triage | Rhythm 🥁 | Human (strategic decisions) |
| Ready Queue | Self-serve | Rhythm maintains queue health |
| Execute | Assigned agent | Spawn sub-agents as needed |
| Feedback | Completing agent | — |

---

## Anti-Patterns to Avoid

❌ **"[Human] will add it"** — No. Anyone adds to OPPORTUNITIES.md.

❌ **"Waiting for approval"** — No. If it's in Ready, pick it up.

❌ **"I'll remember this idea"** — No. Log it or lose it.

❌ **"This is too small to log"** — No. Small tasks clog brains. Log them.

❌ **"Someone else will notice"** — No. You noticed. You log it.

---

*The system runs itself. Your job is to feed it and trust it.*
