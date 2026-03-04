## Phase 3: Review and Apply Improvements

Review the session for actionable findings:

- Skill gap
- Friction
- Missing knowledge
- Automation opportunity

Apply low-risk improvements immediately:

1. Update relevant `CLAUDE.md` or scoped rule files.
2. Save stable insights to memory with confidence labels.
3. Draft skill or hook specs for repetitive patterns.
4. Commit improvement changes separately from feature commits when possible.

If the session is routine with no actionable findings, state: `Nothing to improve`.

## Phase 4: Publish Queue

Scan the session for publishable material:

- Debugging story with clear lesson
- Reusable technical pattern
- Milestone or release-worthy update
- Educational walkthrough

If suitable content exists:

1. Create draft(s) under `Drafts/<slug>/<Platform>.md`.
2. Propose the best first post and schedule spacing for the rest.
3. Do not auto-post unless explicitly requested.

If nothing is suitable, state: `Nothing worth publishing from this session`.

## Output contract

Return two artifacts.

### Artifact A: human-readable report

Sections:

1. `Ship State`
2. `Memory Writes`
3. `Findings (applied)`
4. `No action needed`
5. `Publish queue`
6. `Blocked items` (only if any)

Every memory write must include:

- destination
- item text
- confidence (`low`, `medium`, `high`)
- evidence source

### Artifact B: machine-readable JSON

```json
{
  "mode": "execute|dry-run",
  "shipState": {},
  "memoryWrites": [],
  "findingsApplied": [],
  "noActionNeeded": [],
  "publishQueue": [],
  "blockedItems": [],
  "kpis": {
    "noiseRate": 0,
    "reuseRate": 0,
    "correctionRate": 0
  }
}
```

Use `assets/templates/wrap-report-template.md` as the default report skeleton.

### KPI tracking

- `noiseRate = rejected_candidates / total_candidates`
- `reuseRate = reused_memories / total_memories_read`
- `correctionRate = corrected_memories / total_writes`

## Guardrails

- Do not claim deployment if no deploy command was run.
- Do not claim push if push was gated.
- Do not create extra summary files unless the user asks.
- Keep edits scoped to requested outcomes.

## Framework alignment

- InfiAgent: infinite-horizon state and cross-session continuity.
- Letta + LangGraph: explicit memory blocks and typed state separation.
- A-MEM: selective memory formation and consolidation.
- Rowboat: event-threaded orchestration and observability.
- AgentSys and A-MemGuard: memory integrity and poisoning defenses.

## Resources

- `references/memory-frameworks.md`
- `assets/templates/wrap-report-template.md`
