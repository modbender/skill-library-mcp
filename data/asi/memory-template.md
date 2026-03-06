# Memory Template — ASI

Create `~/asi/memory.md` with this structure:

```markdown
# ASI Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## User Model
<!-- How this user thinks, what they value -->
reasoning_style: analytical | intuitive | pragmatic
depth_preference: compressed | balanced | exhaustive
anticipation_tolerance: do_it | ask_first | explain_first

## Active Domains
<!-- Domains relevant to current work, for cross-synthesis -->
- domain 1
- domain 2

## Calibration Notes
<!-- What works for this user, what doesn't -->

## Open Loops
<!-- Problems still being worked, patterns still developing -->

---
*Updated: YYYY-MM-DD*
```

---

Create `~/asi/synthesis-log.md`:

```markdown
# Synthesis Log

## Connections
<!-- Cross-domain insights that worked -->

### [Date] Source → Target
- Problem: ...
- Source domain: ...
- Pattern extracted: ...
- Application: ...
- Outcome: ...

---
*Updated: YYYY-MM-DD*
```

---

Create `~/asi/improvements.md`:

```markdown
# Self-Improvement Log

## Patterns Identified

### [Date] Pattern Name
- Situation: ...
- What I missed: ...
- What I should do next time: ...
- Applied: yes | pending

## Knowledge Gaps

### [Date] Gap Description
- How exposed: ...
- Priority: high | medium | low
- Addressed: yes | pending

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still calibrating | Observe and adapt |
| `complete` | Fully calibrated | Operate at full capability |
| `paused` | User prefers minimal | Apply patterns silently |

## Key Principles

- **Ask and confirm** — Save only what user explicitly approves
- **Log improvements** — Every gap is an opportunity
- **Track synthesis** — Cross-domain connections compound over time
- Most users stay `ongoing` — calibration is continuous
