---
slug: heartbeat
name: Heartbeat
version: 1.0.0
description: Auto-learns when to wake. Balances responsiveness with efficiency, grows autonomy over time.
---

## Auto-Adaptive Wake Management

This skill auto-evolves. Start conservative, learn patterns, confirm before assuming.

**Core Loop:**
1. **Wake** — Execute checklist, note what was useful
2. **Observe** — Track hit rate (useful wakes / total wakes)
3. **Pattern** — After 3+ wakes in category, detect optimal intervals
4. **Confirm** — Ask: "Should I check X every Y instead of Z?"
5. **Store** — Only after explicit yes, add to rules below
6. **Adapt** — Context changes? Re-evaluate intervals

Check `intervals.md` for timing strategies. Check `triggers.md` for event-based waking.

---

## Wake Levels

| Level | Interval | When |
|-------|----------|------|
| `active` | 5-15 min | Ongoing conversation, urgent monitor |
| `watching` | 30-60 min | Waiting for specific event |
| `idle` | 2-4 hours | Nothing pending, background checks |
| `dormant` | 4-8 hours | Night, inactive periods |

**Default to `idle`. Promote/demote based on context and learned patterns.**

---

## Hard Rules (Never Change)

- User says "don't wake me about X" → respect immediately, store
- User asleep (night hours) → `dormant` unless emergency
- Sub-agent running → `watching` until complete
- Nothing changed since last wake → extend interval

---

## Entry Format

One line: `trigger: interval (level) [hit rate]`

Examples:
- `email/urgent: 30min (watching) [80% useful]`
- `calendar/upcoming: 2h (idle) [confirmed]`
- `deploy/monitor: 10min (active) [until complete]`
- `social/mentions: 4h (idle) [low value, user said skip]`

---

### Monitors
<!-- What to check. Format: "source: interval (level)" -->

### Triggers
<!-- What justifies waking. Format: "event: action" -->

### Quiet
<!-- What user said to ignore/reduce -->

### Patterns
<!-- Observed optimal intervals by context -->

---

## On Each Wake

1. Run checklist (Monitors section)
2. Note: Was this wake useful? Why/why not?
3. Check Triggers: anything warrant action?
4. Decide next interval based on context
5. Update patterns if 3+ data points

---

## Learning Signals

Phrases that adjust autonomy:
- "Don't bug me about X" → add to Quiet, reduce frequency
- "Check X more often" → increase interval for X
- "That was useless" → mark wake as low-value, extend interval
- "Good catch" → mark wake as high-value, maintain/shorten
- "Wake me if Y" → add to Triggers

**After pattern emerges:** Confirm before internalizing. "I notice X rarely needs checking—reduce to every 4h?"

---

*Empty sections = still learning. Observe utility of each wake, propose adjustments.*
