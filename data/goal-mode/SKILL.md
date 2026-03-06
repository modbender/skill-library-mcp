---
name: goal-mode
description: Dynamic goal-aware browsing assistant that generates checklists, evaluates page relevance, produces session wrap-ups, and persists all session data to the workspace.
allowed-tools: read write
---

# Goal Mode

Goal-aware browsing analysis engine. Receives structured JSON requests from a browser extension orchestrator and returns structured JSON responses. Supports any goal type — shopping, research, travel planning, learning, decision-making, career exploration, health, and more.

## CRITICAL RULE: Single raw JSON response

Your **final text output** (after all tool calls complete) must be exactly one raw JSON object — no markdown fences, no prose before or after. Intermediate tool calls (`read`, `write`) are separate from this rule; they happen silently before the final output.

## Execution model

For EVERY operation, follow these steps in order:

1. Validate `operation` and required `input` fields
2. `read` the operation's reference file (see routing table below) AND `read` `{baseDir}/references/schemas.md` for shared schemas
3. Compute the JSON result from input (keep it in memory, do NOT output it yet)
4. **Execute ALL workspace `write` (and `read` where needed) tool calls** listed in the Persist section of the reference file. Do not skip any. If a write fails, continue with the remaining writes.
5. **Only after all persistence writes are done**, output the JSON result as your final text response

IMPORTANT: Steps 4 and 5 are mandatory for ALL operations. Every operation (`generate_criteria`, `evaluate_page`, `update_criteria`, `resume_goal`, `create_wrap_up`) MUST persist before returning.

## Operation routing

After parsing the `operation` field, `read` the corresponding reference file:

| Operation | Reference file |
|-----------|---------------|
| `generate_criteria` | `{baseDir}/references/generate-criteria.md` |
| `evaluate_page` | `{baseDir}/references/evaluate-page.md` |
| `update_criteria` | `{baseDir}/references/update-criteria.md` |
| `create_wrap_up` | `{baseDir}/references/create-wrap-up.md` |
| `resume_goal` | `{baseDir}/references/resume-goal.md` |

Always also `read` `{baseDir}/references/schemas.md` for shared schemas (session.json, criteria.json, active-session.md, active-goal.json).

## Input format

Every request is a JSON object with an `operation` field and an `input` field:

```json
{
  "operation": "generate_criteria | evaluate_page | update_criteria | create_wrap_up | resume_goal",
  "input": { ... }
}
```

### Invalid input handling

If `operation` is missing/unknown, or required fields are missing, return:

```json
{
  "error": {
    "code": "invalid_input",
    "message": "Clear explanation of what field is missing or invalid."
  }
}
```

## Workspace persistence

The workspace root is `/home/ubuntu/.openclaw/workspace`. Use **absolute paths** for all file operations.

Do NOT use `exec` or `bash` for directory creation — the `write` tool automatically creates parent directories.

### File layout

```
/home/ubuntu/.openclaw/workspace/
  goal-mode/
    active-goal.json            — Pointer to the current active goal
    {goal_slug}/
      session.json              — All session state: goal, criteria, pages, findings, candidates
      criteria.json             — Criteria coverage snapshot (synced on every criteria change)
      wrap-up.json              — Final session summary (written on finish)
      events/                   — Immutable event log (one file per page evaluation)
        {timestamp}-evaluate-page.json   (timestamp = ISO 8601 compact: YYYYMMDDTHHmmssZ)

  memory/goal-mode/
    active-session.md           — Live status of the current active goal (updated on every operation)
    latest-session.md           — Human-readable summary of most recent finished session
    history.md                  — Append-only log of all past sessions
```

### Goal slug

Derived from the goal text: lowercase, replace spaces and special characters with hyphens, truncate to 60 characters, trim trailing hyphens. If a directory with that slug already exists and belongs to a **different** goal_text, append `-2`, `-3`, etc.

## Guardrails

- ALWAYS return valid raw JSON as the text response.
- Never wrap output in markdown code fences.
- Never fabricate URLs or page content not present in the input.
- Finding types must be dynamically chosen based on the goal context — do not default to shopping-oriented types for non-shopping goals.
- **Criteria specificity:** criteria must be narrow enough that a single overview page cannot satisfy more than 2-3 of them. "Build quality" is too broad; "Build quality: hinge durability and chassis material" is the right level.
- If the goal is ambiguous, generate criteria that help clarify it through browsing.
- Recommendation in wrap-up must be `null` when evidence is insufficient — never force a recommendation.
- Keep all text concise. Findings under 240 characters. Criteria under 120 characters.
- `criteria_relevance` MUST contain an entry for every criterion in the input array. `criterion` values MUST be exact strings — do not rephrase them. A criterion is only `covered` when `best_relevance ≥ 0.7`.
- **Per-page coverage cap:** a single page can flip at most 3 criteria from uncovered to covered. If more than 3 would cross the 0.7 threshold, only the top 3 by relevance are marked covered; the rest keep their updated `best_relevance` but stay uncovered until confirmed by another page.
- **Depth-over-breadth:** score overview pages honestly. A listicle or roundup that mentions a topic in one paragraph scores 0.3–0.5, not 0.7+. Reserve 0.7+ for pages with dedicated, detailed coverage of that specific criterion.
- All `confidence` values across all operations are floats between 0.0 and 1.0. Never use string enums like "high/medium/low" for confidence.
- If workspace writes fail or `write` is unavailable, still return the JSON response.
- If merge/append is not possible, prefer immutable event files over skipping persistence entirely.
- Always use absolute paths starting with `/home/ubuntu/.openclaw/workspace/`.
- Do NOT use `exec` for mkdir — `write` auto-creates parent directories.
