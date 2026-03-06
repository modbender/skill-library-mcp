# Operation: create_wrap_up

## Input

```json
{
  "operation": "create_wrap_up",
  "input": {
    "goal_text": "string",
    "goal_slug": "string",
    "constraints": ["array"],
    "pages": [
      { "url": "...", "title": "...", "relevance": "high", "confidence": 0.9, "reasoning": "..." }
    ],
    "findings": [
      { "type": "...", "text": "...", "source_url": "..." }
    ],
    "candidates": [{ "name": "...", "attributes": {}, "pros": [], "cons": [] }],
    "criteria": [
      { "text": "...", "covered": true, "best_relevance": 0.9, "sources": 3 },
      { "text": "...", "covered": false, "best_relevance": 0.4, "sources": 1 }
    ]
  }
}
```

## Behavior

Using ONLY the data in the input:

- Compute `progress` from the criteria array: `covered count / total count`
- Summarize what was learned in structured sections (see output shape)
- Make a recommendation if enough evidence exists (null if insufficient data)
- List trade-offs between identified options/findings
- Identify unresolved conflicts in the evidence
- Derive remaining uncertainties from uncovered criteria
- Suggest concrete final actions the user should take

## Output JSON shape

```json
{
  "progress": 0.75,
  "pages_evaluated": 5,
  "key_learnings": [
    "One-sentence learning referencing a specific finding or page"
  ],
  "gaps": ["Criterion X was not covered — no dedicated source found"],
  "verdict": "One-paragraph overall conclusion about the goal.",
  "recommendation": {
    "candidate": "recommended option/item name",
    "reasoning": "Why this is recommended.",
    "confidence": 0.85
  },
  "candidates_compared": [{ "...same structure as input candidates..." }],
  "trade_offs": ["trade-off 1", "trade-off 2"],
  "unresolved_conflicts": ["conflict 1"],
  "suggested_final_actions": ["action 1", "action 2"]
}
```

- `progress` is computed from input criteria: `covered count / total count`. Do NOT expect it in the input.
- `key_learnings` — each entry is a concrete takeaway referencing specific findings/pages.
- `gaps` — uncovered criteria and why they remain uncovered.
- `verdict` — short overall conclusion paragraph.
- `recommendation` is `null` when evidence is insufficient. `recommendation.confidence` is a float 0.0–1.0.

## Persist

Always write ALL five files:

1. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/wrap-up.json` — the full wrap-up JSON you generated
2. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/active-goal.json` — update status to `"finished"`, set `finished_at` timestamp
3. `write` to `/home/ubuntu/.openclaw/workspace/memory/goal-mode/latest-session.md` — human-readable markdown summary: goal, constraints, pages evaluated count, key findings, recommendation, remaining uncertainties
4. `read` then `write` to `/home/ubuntu/.openclaw/workspace/memory/goal-mode/history.md` — append one line: `YYYY-MM-DD | {goal_text} | {constraints summary} | {status} | {N} pages evaluated | {recommendation or "no recommendation"}`. If file doesn't exist, create it.
5. `write` to `/home/ubuntu/.openclaw/workspace/memory/goal-mode/active-session.md` — write `No active goal.` to indicate the session is done
