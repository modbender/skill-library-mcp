# Shared Schemas

## session.json

The single accumulator for all session state. Seeded by `generate_criteria`, updated by `evaluate_page` and `update_criteria`, finalized by `create_wrap_up`.

```json
{
  "schema_version": 2,
  "goal_slug": "...",
  "goal_text": "...",
  "constraints": [],
  "status": "active",
  "started_at": "...",
  "updated_at": "...",
  "criteria": [
    { "text": "CPU and GPU benchmark comparisons under $1000", "covered": true, "best_relevance": 0.9, "sources": 2 },
    { "text": "Battery life test results (hours)", "covered": false, "best_relevance": 0.4, "sources": 1 }
  ],
  "pages": [
    { "url": "...", "title": "...", "relevance": "high", "confidence": 0.9, "reasoning": "...", "evaluated_at": "..." }
  ],
  "findings": [
    { "type": "spec", "text": "...", "source_url": "..." }
  ],
  "candidates": [
    { "name": "...", "attributes": {}, "pros": [], "cons": [] }
  ]
}
```

No separate `pages.json`, `findings.json`, or `candidates.json` files.

## criteria.json

Snapshot of the criteria array, kept in sync by every operation that modifies criteria. Same shape as `session.json.criteria` wrapped in metadata:

```json
{
  "schema_version": 2,
  "criteria": [
    { "text": "...", "covered": false, "best_relevance": 0.0, "sources": 0 }
  ],
  "created_at": "2026-02-19T10:00:00Z",
  "updated_at": "2026-02-19T10:00:00Z"
}
```

### Criteria coverage rules

- On `generate_criteria`: set `covered: false`, `best_relevance: 0.0`, `sources: 0`.
- On `evaluate_page`: update `best_relevance` to `max(existing, new relevance)`. Increment `sources` if page scored ≥ 0.3 for this criterion. Set `covered: true` when `best_relevance >= 0.7`, subject to the per-page coverage cap (max 3 newly covered per page).
- On `update_criteria`: removed criteria lose data; replaced/added criteria start fresh.

## active-session.md

Overwritten on every operation to reflect live state. On `create_wrap_up`, write once with `status: finished`, then overwrite with `No active goal.`.

Path: `/home/ubuntu/.openclaw/workspace/memory/goal-mode/active-session.md`

```markdown
# Active Goal

**Goal:** {goal_text}
**Constraints:** {constraints joined with ", "}
**Status:** {active | finished}
**Progress:** {covered criteria count}/{total criteria count} criteria covered
**Pages evaluated:** {count}
**Started:** {YYYY-MM-DD}
**Updated:** {YYYY-MM-DD HH:MM UTC}

## Criteria

- [x] Covered criterion 1 (best: 0.9, 3 sources)
- [ ] Uncovered criterion 2 (best: 0.4, 1 source)
- [x] Covered criterion 3 (best: 0.7, 2 sources)

(show the highest relevance score and source count for each criterion)

## Recent Findings

- [{type}] {finding text} (from {source_url domain})
- [{type}] {finding text} (from {source_url domain})
(show last 5 findings max)

## Candidates

- **{name}**: {one-line summary of attributes}
(omit section if no candidates)
```

## active-goal.json

Cross-client discovery file:

```json
{
  "goal_slug": "buy-a-laptop-under-1000",
  "goal_text": "buy a laptop under $1000",
  "constraints": ["budget under $1000"],
  "status": "active",
  "started_at": "2026-02-19T10:00:00Z",
  "updated_at": "2026-02-19T12:30:00Z"
}
```
