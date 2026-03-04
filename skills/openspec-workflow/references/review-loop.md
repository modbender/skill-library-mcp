# Review Loop Protocol

## When to Review

Review any artifact with real design decisions, trade-offs, or ambiguity. Skip only genuinely trivial artifacts.

**Review:** proposals with multiple approaches, designs with architectural decisions, specs introducing new capabilities, complex task breakdowns.

**Skip:** one-line doc fixes, obvious config changes, mechanical renames, tasks for trivial changes. Always log: `Skipped review — trivial: <reason>`.

## How to Review

Two options depending on change complexity:

### Option A: Claude Code Review (preferred for code changes)

Launch Claude Code as the reviewer. It gets full codebase context automatically.

```bash
exec pty:true workdir:<repo-path> background:true command:"claude --dangerously-skip-permissions -p 'You are a skeptical spec reviewer. Your job is to challenge this [ARTIFACT TYPE] and find weaknesses.

## Your Job
1. Read the change artifacts: openspec/changes/[CHANGE_NAME]/
2. Read the existing specs: openspec/specs/[RELEVANT_SPEC]/spec.md
3. Explore the codebase — grep for patterns, read files that will be affected, verify claims
4. Then challenge. Based on what you actually found:
   - [2-4 specific questions relevant to this artifact type]

## [ARTIFACT TYPE] to Review
[Paste the full artifact content]

Rules:
- State APPROVED if satisfied
- Otherwise, list 2-5 specific challenges (not nitpicks)
- For each challenge, cite what you found in the code and suggest an alternative
- Be direct

When finished, run: openclaw system event --text \"Review complete: [APPROVED or NOT APPROVED with summary]\" --mode now'"
```

Claude Code can read any file in the repo, run grep, check git history, and verify assumptions — it's the most thorough reviewer.

### Option B: Subagent Review (lighter weight, for spec/doc changes)

Spawn a reviewer subagent using `sessions_spawn`. Include the repo path so it can explore:

```
You are a skeptical spec reviewer with full repo access.

## Repo
Path: [REPO_PATH]

## Project Context
[Brief project context]

## Existing Specs
Run `cat [REPO_PATH]/openspec/specs/[RELEVANT_SPEC]/spec.md` to see current requirements.

## [ARTIFACT TYPE] to Review
[Paste the full artifact content]

## Your Job
1. Explore first. Read relevant code and specs. Grep for patterns. Verify claims.
2. Then challenge based on what you found:
   - [2-4 specific questions]

Rules:
- APPROVED if satisfied, otherwise 2-5 challenges with code citations
- Be direct
```

### When to Use Which

- **Claude Code (Option A):** Code changes, complex refactors, anything where the reviewer needs deep codebase exploration, git history, or to run tests
- **Subagent (Option B):** Doc-only changes, spec rewrites, proposals where the artifact content is self-contained

**Key:** Either way, the reviewer must have access to the repo. Never review blind — always give the reviewer tools to verify claims independently.

### Artifact-Specific Review Focus

**Proposal:** Is the problem real? Grep for the patterns being discussed — is the "inconsistency" actually there? Are there simpler solutions? Is the scope right? Are the right specs identified? Check `openspec/specs/` for existing spec names.

**Design:** Will this actually work at implementation time? Read the files that will be modified. Are there hidden dependencies? Are alternatives properly considered? Are risks realistic?

**Specs:** Are requirements testable? Do scenarios cover edge cases? Is the delta format correct? Read the existing main spec to verify the MODIFIED section is accurate. Will the merged spec be valid?

**Tasks:** Are tasks small enough? Right order? Missing any steps? Can they be verified? Check that referenced files actually exist at the paths mentioned.

## Processing Feedback

For each reviewer challenge, the drafter must do one of:

1. **Accept and revise** — update the artifact, note what changed
2. **Reject with reasoning** — explain why the challenge doesn't apply: `Rejected: <reason>`
3. **Partially accept** — take the useful part, explain what was left out and why

After revising, resubmit to the reviewer. The loop continues until:
- Reviewer states **APPROVED**, or
- Drafter is confident all remaining concerns are addressed/dismissed with stated reasoning

## Logging

The workflow log should capture for each artifact:
```
### [Artifact Name]

**Draft:** [summary of what was written]

**Review Round 1:**
- Challenge: [reviewer's point] (based on: [what reviewer found in code])
  → Accepted: [revision made]
- Challenge: [reviewer's point]
  → Rejected: [reasoning]

**Review Round 2:** (if needed)
- APPROVED

**Final:** [written to path]
```

Or for skipped reviews:
```
### [Artifact Name]
Skipped review — trivial: [reasoning]
**Final:** [written to path]
```
