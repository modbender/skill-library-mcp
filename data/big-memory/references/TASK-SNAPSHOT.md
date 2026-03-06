# Task Snapshot Template

Use this template when creating a BIG-MEMORY-SNAPSHOT. Copy the structure exactly.
Fill every field. Write "none" for empty fields -- do not omit them.

## Template

```markdown
---

## Task Snapshot -- {HH:MM}

<!-- BIG-MEMORY-SNAPSHOT v1 -->
<!-- timestamp: {YYYY-MM-DDTHH:MM:SS} -->
<!-- snapshot-id: {YYYY-MM-DD}-{NN, starting at 01} -->

### [SNAPSHOT] Active Goal
{One sentence describing the user's current objective, including why}

### [SNAPSHOT] Current State
- Phase: {planning|implementing|debugging|testing|reviewing|deploying}
- Branch: {git branch name, or "n/a"}
- Blocked: {yes|no} -- {if yes, describe the blocker}
- Progress: {percentage or milestone description}

### [SNAPSHOT] Files In Play
- `{/absolute/path/to/file}` -- {what is happening in this file}
- `{/absolute/path/to/other}` -- {purpose of this file in current task}

### [SNAPSHOT] Decisions Made
1. {Decision}: {rationale for why this was chosen}
2. {Decision}: {rationale}

### [SNAPSHOT] Code Context
```{language}
// Only include code that cannot be reconstructed from reading files
// Function signatures, error messages, exact patterns, config values
// Keep under 50 lines total
```

### [SNAPSHOT] Key Names & Values
- {identifier type}: `{exact value}`
- {identifier type}: `{exact value}`

### [SNAPSHOT] Blockers & Open Questions
- {Blocker or question, with context}

### [SNAPSHOT] Next Steps
1. {Specific, actionable step with enough context to resume without re-reading the conversation}
2. {Next step}
3. {Next step}

<!-- /BIG-MEMORY-SNAPSHOT -->
```

## Field Guidelines

### Active Goal
- Single sentence, present tense
- Include the "why" not just the "what"
- Good: "Implement user authentication with JWT so the app can support multi-tenant access"
- Bad: "Working on auth" (too vague to resume from)

### Current State
- **Phase** must be one of: planning, implementing, debugging, testing, reviewing, deploying
- **Branch** helps orient which git context to restore
- **Blocked** should include what is needed to unblock
- **Progress** can be rough -- "~60%" or "3 of 5 endpoints done"

### Files In Play
- Use absolute paths so the agent can `Read` them immediately after recovery
- Include every file being actively modified, not just the "main" one
- One-line purpose per file, focused on what is changing

### Decisions Made
- Include the rationale, not just the decision
- These are the hardest things to reconstruct after compaction
- Good: "Using Drizzle ORM over Prisma because the project needs raw SQL escape hatches"
- Bad: "Using Drizzle" (no rationale, easy to second-guess after compaction)

### Code Context
- Only include code the agent could NOT reconstruct from reading committed files
- Function signatures being designed (not yet written to disk)
- Error messages being debugged (exact stack traces, error codes)
- Regex patterns or complex expressions being refined
- If code IS in a committed file, just reference the path and line range instead

### Key Names & Values
- API endpoints, database table/column names, environment variable names
- Error codes and messages currently being debugged
- Magic numbers, thresholds, feature flag names
- User-provided requirements that are easy to misremember
- Config keys and their values

### Blockers & Open Questions
- Include enough context that the blocker makes sense in isolation
- For questions, include the options being considered
- Good: "Question: UUID v4 vs v7 for user IDs -- v4 is simpler but v7 is time-sortable which helps with pagination"
- Bad: "Need to decide on UUID version"

### Next Steps
- Ordered by priority (most important first)
- Specific enough to resume without re-reading any conversation
- Include edge cases, test scenarios, or acceptance criteria where relevant
- Good: "Write tests for POST /api/users covering: duplicate email (409), missing required fields (400), successful creation (201), and rate limiting (429)"
- Bad: "Write tests" (too vague to resume from)
