---
name: Triage
description: Auto-learns to prioritize tasks by urgency, impact, and user patterns. Grows smarter with each decision.
---

## Auto-Adaptive Priority Memory

This skill auto-evolves. Observe prioritization signals, detect patterns, confirm before internalizing.

**Core Loop:**
1. **Assess** — When tasks arrive, evaluate urgency + importance
2. **Classify** — Assign priority level (P0-P3)
3. **Route** — P0 immediately, P1-P3 into queue
4. **Learn** — Notice when user overrides priority → propose pattern
5. **Confirm** — After 2+ corrections, ask: "Should X always be P[n]?"

Check `signals.md` for urgency indicators. Check `patterns.md` for learned priority rules.

---

## Priority Levels

| Level | Response | Examples |
|-------|----------|----------|
| P0 | Interrupt immediately | Server down, security breach, deadline today |
| P1 | Next available slot | Blocking work, waiting users, same-day tasks |
| P2 | Scheduled queue | Important but not urgent, planning, reviews |
| P3 | Backlog | Ideas, "someday", low-impact optimizations |

**Default:** When uncertain, ask. Start conservative, learn boundaries.

---

## Urgency Signals

Automatic P0 triggers:
- Words: "urgent", "ASAP", "down", "broken", "emergency"
- Context: External deadlines, blocked team members
- Pattern: User previously escalated similar tasks

Automatic P3 triggers:
- Words: "when you have time", "no rush", "idea for later"
- Context: No deadline mentioned, exploratory

---

## Entry Format

One line: `pattern: priority (level) [context]`

Examples:
- `deploy-issues: P0 (confirmed) [always urgent]`
- `refactoring: P2 (pattern) [user deprioritized 3x]`
- `docs-updates: P3 (confirmed) [explicit "low priority"]`

---

### Work Categories
<!-- Task types and default priorities -->

### Time Patterns
<!-- Time-based rules: mornings, Fridays, etc. -->

### Source Routing
<!-- Priority by source: Slack vs email vs direct -->

### Overrides
<!-- User corrections that became patterns -->

---

## Queue Management

When multiple tasks compete:
1. **Group by priority** — P0 first, always
2. **Within same priority** — Order by arrival or explicit sequence
3. **Report queue** — "3 P1 tasks queued, handling X first"
4. **Re-triage on change** — New P0 interrupts P1 work

---

## Learning Triggers

Phrases that signal priority pattern:
- "This should be higher priority"
- "Drop everything and..."
- "This can wait"
- "Handle [X] before [Y]"
- "Not urgent" / "No rush"

**After hearing these:** Update entry, wait for 2nd occurrence, then confirm permanent rule.

---

*Empty sections = still learning. Start conservative, observe corrections, propose only after patterns emerge.*
