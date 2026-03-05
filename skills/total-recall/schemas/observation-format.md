# Observation Format — Extended Schema (Phase 2)

*Total Recall / Dream Cycle — Memory Type System*
*Schema version: 2.0 | Author: Dream Cycle WP1 | 2026-02-23*

---

## Overview

This document defines the extended observation format introduced in Dream Cycle Phase 2 (WP1: Memory Type System). It is the reference for:

- The **Dream Cycle agent** — which reads and classifies observations using type metadata
- The **Observer** — which will optionally tag new observations at write time (Phase 3 enhancement)
- The **decay function** (`dream-cycle.sh decay`, WP2) — which reads type and date to apply per-type TTL decay

Phase 1 observations (untagged) remain fully valid. The backward-compatibility rule ensures they are treated as `type: fact`, `ttl_days: 90` by default.

---

## The Seven Observation Types

| Type | TTL (days) | Description |
|------|-----------|-------------|
| `fact` | 90 | Factual information, configs, settings, versions, tool outputs |
| `preference` | 180 | User preferences, decisions, chosen approaches, stated likes/dislikes |
| `goal` | 365 | Active goals, targets, milestones, things being worked toward |
| `habit` | 365 | Recurring behaviours, routines, patterns, consistent workflows |
| `event` | 14 | One-off occurrences, daily summaries, status updates, single-session logs |
| `rule` | ∞ (never) | Operational rules, hard constraints, policies, safety rules |
| `context` | 30 | Temporary context, session notes, in-progress work, transient state |

**TTL = ∞** means the observation is never automatically archived based on age alone. It can only be archived manually or when explicitly superseded.

---

## Metadata Comment Format

The extended observation metadata is embedded as an HTML comment immediately after the observation header line (or as the first line of the observation body). This format is:

- **Invisible in rendered markdown** — does not affect human-readable display
- **Does not break Phase 1 processing** — Phase 1 ignores these comments entirely
- **Machine-parseable** by the WP2 decay function and future tooling

### Format

```
<!-- dc:type=<type> dc:importance=<0.0-10.0> dc:ttl=<days> dc:confidence=<0.0-1.0> dc:source=<source-type> dc:date=<YYYY-MM-DD> -->
```

**Minimum required fields for decay function:** `dc:type`, `dc:importance`, `dc:date`.
All other fields are optional but recommended.

### Fields

| Field | Description | Example |
|-------|-------------|---------|
| `dc:type` | One of the 7 type values | `dc:type=preference` |
| `dc:importance` | Float importance score 0.0–10.0 (see rubric below) | `dc:importance=7.5` |
| `dc:ttl` | TTL in days; use `never` for rules | `dc:ttl=180` or `dc:ttl=never` |
| `dc:confidence` | Confidence score 0.0–1.0 (WP0.5) | `dc:confidence=0.85` |
| `dc:source` | Source type: `explicit`, `implicit`, `inference`, `weak`, `uncertain` | `dc:source=explicit` |
| `dc:date` | ISO date the observation was first recorded | `dc:date=2026-02-22` |

### Importance Score (WP2)

Importance is a float in `[0.0, 10.0]` that indicates how critical this observation is to retain:

| Score range | Category | Typical content |
|-------------|----------|----------------|
| 9.0–10.0 | Critical | Operational rules, active blockers, family safety |
| 7.0–8.9 | High | High-impact decisions, active project state, financial |
| 5.0–6.9 | Medium | Medium-impact events, useful context |
| 3.0–4.9 | Low | Routine operational noise, older non-critical events |
| 0.0–2.9 | Minimal | Duplicate, expired, superseded, or trivial |

**Default for untagged observations:** `5.0` (neutral — treated as medium importance).

### Importance Decay (WP2)

The `dream-cycle.sh decay` command applies daily decay to importance scores based on observation type. Decay is applied to the `dc:importance` field in the metadata comment.

**Decay rates per type:**

| Type | Decay rate (per day) | Rationale |
|------|---------------------|-----------|
| `event` | −0.5 | One-off events lose relevance quickly |
| `fact` | −0.1 | Facts age out slowly |
| `preference` | −0.02 | Preferences are stable; minimal drift |
| `context` | −0.1 | Temporary context expires at fact rate |
| `rule` | 0 (no decay) | Rules are permanent until superseded |
| `habit` | 0 (no decay) | Habits are persistent |
| `goal` | 0 (no decay) | Goals are preserved until completed |

**Formula:** `new_importance = max(0.0, importance − decay_rate × days_elapsed)`

**Unknown types** fall back to the `fact` decay rate (−0.1/day).

**Observations without `dc:importance` metadata** are skipped by the decay function and default to `5.0` for classification purposes.

### Examples

**A preference observation (with full WP2 metadata):**
```markdown
## Model Selection — Codex 5.3 as Primary Coder
<!-- dc:type=<type> dc:importance=<0.0-10.0> dc:ttl=<days> dc:confidence=<0.0-1.0> dc:source=<source-type> dc:date=<YYYY-MM-DD> -->
```

**A goal observation:**
```markdown
## Goal: Phase 2 Dream Cycle Live by Friday
<!-- dc:type=<type> dc:importance=<0.0-10.0> dc:ttl=<days> dc:confidence=<0.0-1.0> dc:source=<source-type> dc:date=<YYYY-MM-DD> -->
```

**An event observation (will decay at -0.5/day):**
```markdown
## Fitbit Summary — 2026-02-22
<!-- dc:type=<type> dc:importance=<0.0-10.0> dc:ttl=<days> dc:confidence=<0.0-1.0> dc:source=<source-type> dc:date=<YYYY-MM-DD> -->
22,376 steps, 3,450 cal burned, 162 active min...
```

---

## Phase Rollout

| Phase | Who writes tags | Status |
|-------|----------------|--------|
| Phase 1 | Nobody — all observations are untagged | Live |
| Phase 2 | Dream Cycle classifies types **mentally** during analysis; does not write tags to `observations.md` | Building |
| Phase 3 | Observer tags new observations at write time using the `<!-- dc:... -->` format | Planned |

**Phase 2 behaviour:** The Dream Cycle agent reads observations, assigns a type and TTL internally for archiving decisions, and reports the distribution in the dream log. It does **not** write `<!-- dc:... -->` tags back into `observations.md` — that is Phase 3 (Observer integration).

---

## Backward Compatibility

Observations without any `<!-- dc:... -->` metadata comment are treated as:

```
type: fact
ttl_days: 90
importance: 5.0  (neutral default — medium importance)
```

This means:
- All existing Phase 1 observations are valid without modification
- The dream cycle will never error on an untagged observation
<!-- dc:type=<type> dc:importance=<0.0-10.0> dc:ttl=<days> dc:confidence=<0.0-1.0> dc:source=<source-type> dc:date=<YYYY-MM-DD> -->

---

## Classification Rules

When assigning a type to an observation, apply these rules in order:

1. **Explicit tag wins** — if the observation has a `<!-- dc:type=X -->` comment, use X.
2. **Content signals** — if no explicit tag, classify by content:
   - Contains "rule", "never", "always", "must", "hard constraint", "policy" → `rule`
   - Contains "goal", "target", "milestone", "working toward", "plan to" → `goal`
   - Describes a recurring pattern ("every day", "always uses", "consistently") → `habit`
   - Is a one-off dated entry (daily summary, single event log) → `event`
   - Describes a decision or preference ("prefers", "chosen", "decided") → `preference`
   - Is temporary or in-progress context → `context`
   - Everything else → `fact`
3. **Ambiguity rule** — when two types are equally plausible, prefer the one with the **longer TTL** (err on the side of retention).
4. **No `undefined`** — every observation must resolve to exactly one of the 7 types. No exceptions.

---

## Archive Format Extension (WP2+)

When the WP2 decay function is active, archive entries gain an `importance` field in their JSON payload:

```json
{
  "id": "OBS-20260222-003",
  "original_date": "2026-02-22",
  "impact": "low",
  "type": "event",
  "ttl_days": 14,
  "importance": 1.2,
  "archived_reason": "event TTL expired (14 days)",
  "full_text": "..."
}
```

This field is added by WP2 and is not required for WP1 compliance.

---

## Future Retrieval Feedback (Phase 3 Preview)

When `memory_search` returns an observation and it is used in a response, the importance score may be boosted by +0.5 (relevance feedback). This is a Phase 3 capability — not implemented in Phase 2. The `dc:date` field enables the decay function to know when to start counting from.

---

*This schema is the source of truth for observation metadata format. Any future Observer, decay function, or retrieval system should reference this document.*
