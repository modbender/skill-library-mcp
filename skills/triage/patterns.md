# Priority Patterns

## Pattern Recognition

When user corrects a priority assignment, record the pattern:

```
[DATE] Task type: original → corrected (user comment)
```

After 2+ similar corrections, propose confirmation:
> "I've noticed you prioritize [task type] as P[n]. Should I default to this?"

---

## Pattern Categories

### By Task Type
```
# Observed patterns (add as learned)
# Format: task_type: Pn (confidence) [last updated]
```

### By Source
```
# Patterns based on where task came from
# Format: source: default_priority (confidence)
```

### By Time
```
# Time-based priority adjustments
# Format: condition: adjustment (confidence)
```

### By Keyword
```
# Specific words/phrases that indicate priority
# Format: "phrase": Pn (confidence)
```

---

## Confidence Levels

| Level | Meaning | Action |
|-------|---------|--------|
| `observed` | Seen once | Note, don't apply automatically |
| `pattern` | Seen 2+ times | Propose confirmation |
| `confirmed` | User said yes | Apply automatically |
| `locked` | Reinforced multiple times | High confidence, rarely override |

---

## Pattern Evolution

Patterns can change:
1. **Strengthen** — More corrections in same direction
2. **Weaken** — Contradictory corrections
3. **Split** — Same task type needs different priority by context

When patterns conflict, ask rather than guess.

---

## Queue History

Track priority distributions to detect drift:
```
# Weekly summary (auto-generated)
# P0: n% | P1: n% | P2: n% | P3: n%
# Compare to previous weeks for anomalies
```

If P0 ratio spikes → something systemic may be wrong.
If everything is P3 → triage may be too conservative.

---

## Override Tracking

When user explicitly overrides:
1. Record the override with context
2. Look for pattern in overrides
3. After pattern emerges, update default

```
# Recent overrides (last 10)
# [DATE] task: old_priority → new_priority "reason"
```
