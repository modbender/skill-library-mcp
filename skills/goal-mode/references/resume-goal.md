# Operation: resume_goal

## Input

```json
{
  "operation": "resume_goal",
  "input": {
    "goal_slug": "string — slug of the goal to resume (optional, defaults to active goal)"
  }
}
```

## Behavior

1. If `goal_slug` is provided, read `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/session.json`. If not provided, read `active-goal.json` to get the current slug, then read its session.
2. If the session has `status: "finished"`, return an error: `{ "error": { "code": "goal_finished", "message": "This goal is already finished. Start a new goal with generate_criteria." } }`
3. Return the full session state so the caller can continue from where it left off.

## Output JSON shape

```json
{
  "goal_slug": "...",
  "goal_text": "...",
  "constraints": [],
  "status": "active",
  "criteria": [
    { "text": "...", "covered": true, "best_relevance": 0.9, "sources": 2 },
    { "text": "...", "covered": false, "best_relevance": 0.4, "sources": 1 }
  ],
  "pages_evaluated": 5,
  "pages": [
    { "url": "...", "title": "...", "relevance": "high", "confidence": 0.9, "reasoning": "...", "evaluated_at": "..." }
  ],
  "findings_count": 12,
  "candidates": [
    { "name": "...", "attributes": {}, "pros": [], "cons": [] }
  ],
  "progress": 0.6
}
```

`progress` is calculated as: number of covered criteria / total criteria.

## Persist

1. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/active-goal.json` — update to point to this goal slug with `status: "active"` and fresh `updated_at`
2. `write` to `/home/ubuntu/.openclaw/workspace/memory/goal-mode/active-session.md` — regenerate from the session state (see references/schemas.md)
