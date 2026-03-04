# Urgency Signals

## Language Signals

### P0 Triggers (Immediate)
- "urgent", "ASAP", "emergency", "critical"
- "down", "broken", "not working", "crashed"
- "deadline today", "due now", "meeting in X minutes"
- "blocking", "can't continue without"
- ALL CAPS messages (often indicates urgency)
- Multiple messages in rapid succession about same issue

### P1 Triggers (High)
- "today", "by EOD", "this afternoon"
- "waiting on this", "need this for"
- "important", "high priority"
- External stakeholders mentioned
- Client-facing issues

### P2 Triggers (Medium)
- "this week", "when possible"
- "would be nice", "should probably"
- Internal improvements
- No explicit deadline

### P3 Triggers (Low)
- "no rush", "when you have time"
- "idea", "thought", "maybe"
- "someday", "future", "backlog"
- "nice to have", "optional"

---

## Context Signals

### Escalate Priority When:
- External deadline mentioned
- Multiple people affected
- Revenue/customer impact
- Security or safety implications
- User explicitly says it's urgent
- Follow-up to previously urgent item

### De-escalate Priority When:
- User says "no rush" or equivalent
- Exploratory/brainstorming context
- No external dependencies
- User is multitasking on other priorities
- Weekend/off-hours (unless P0)

---

## Source-Based Defaults

| Source | Default | Rationale |
|--------|---------|-----------|
| Direct message | P1 | User took time to message directly |
| Scheduled check-in | P2 | Planned, not urgent |
| Automated alert | P0-P1 | Systems rarely cry wolf |
| Email forward | P2 | If urgent, wouldn't use email |
| "FYI" prefix | P3 | Informational by definition |

---

## Time-Based Modifiers

- **Monday morning** — Batch P2/P3 review, don't interrupt with backlog
- **Friday afternoon** — Deprioritize non-urgent (weekend buffer)
- **User's focus time** — Hold P2/P3, only interrupt for P0/P1
- **Before known meetings** — Compress timelines appropriately

---

## Anti-Patterns

**Don't auto-elevate:**
- Repeated mentions of same task (frustration ≠ urgency)
- Length of message (verbosity ≠ importance)
- Exclamation marks alone (style ≠ priority)

**Don't auto-lower:**
- Polite phrasing ("would you mind...") — check actual deadline
- Casual tone — user might just be friendly
