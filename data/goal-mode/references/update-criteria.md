# Operation: update_criteria

## Input

```json
{
  "operation": "update_criteria",
  "input": {
    "goal_slug": "string",
    "add": ["new criterion string", "another new criterion"],
    "remove": ["exact text of criterion to remove"],
    "replace": [
      { "old": "exact text of existing criterion", "new": "replacement criterion text" }
    ]
  }
}
```

All three fields (`add`, `remove`, `replace`) are optional — include only what's needed. At least one must be present.

## Behavior

1. `read` the current `session.json` for the given `goal_slug`.
2. If the session has `status: "finished"`, return an error.
3. Apply changes to the criteria array in order: `remove` first, then `replace`, then `add`.
   - Removed criteria lose their coverage data permanently.
   - Replaced criteria keep `covered: false`, `best_relevance: 0.0`, `sources: 0` (fresh start for the new text).
   - Added criteria start with `covered: false`, `best_relevance: 0.0`, `sources: 0`.
4. Validate the result still has 4-10 criteria. If not, return an error.
5. Return the updated criteria array and progress.

## Output JSON shape

```json
{
  "criteria": [
    { "text": "...", "covered": true, "best_relevance": 0.9, "sources": 2 },
    { "text": "...", "covered": false, "best_relevance": 0.0, "sources": 0 }
  ],
  "progress": 0.5,
  "changes": {
    "added": 1,
    "removed": 1,
    "replaced": 0
  }
}
```

## Persist

1. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/session.json` — updated session with new criteria array and fresh `updated_at`
2. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/criteria.json` — updated criteria snapshot
3. `write` to `/home/ubuntu/.openclaw/workspace/memory/goal-mode/active-session.md` — regenerate from updated session state (see references/schemas.md)
