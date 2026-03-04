---
name: pi-workflow
description: Workflow orchestration for Pi's task management, self-improvement, and code quality standards. Use when starting new projects, managing multi-step tasks (3+ steps or architectural decisions), capturing lessons from mistakes, writing verifiable code, or establishing quality gates before completion. Includes planning templates, progress tracking, bug fixing autonomy, and a lessons capture system to prevent repeated mistakes.
---

# Pi Workflow Orchestration

This skill provides Pi's structured approach to task management, quality assurance, and continuous self-improvement.

## Core Workflows

### 1. Plan Node Default
Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions):
- Write detailed specs upfront to reduce ambiguity
- If something goes sideways, STOP and re-plan immediately—don't keep pushing
- Use plan mode for verification steps, not just building

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One tack per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with metadata (Priority, Status, Area, Pattern-Key)
- Log command failures to `tasks/errors.md` for diagnosis patterns
- Log feature requests to `tasks/feature_requests.md` for future work
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant projects
- Track recurring patterns with Recurrence-Count (bump priority at ≥3 occurrences)

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes—don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests—then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## File Organization

- `tasks/todo.md` — active sprint (current project)
- `tasks/lessons.md` — corrections, insights, best practices (structured)
- `tasks/errors.md` — command failures, API errors, exceptions (NEW)
- `tasks/feature_requests.md` — missing capabilities, feature requests (NEW)
- `memory/YYYY-MM-DD.md` — session logs (daily)
- `MEMORY.md` — your curated memories (maintained by user)

See [WORKFLOW_ORCHESTRATION.md](references/workflow_orchestration.md) for detailed reference.

See [LESSONS.md](references/lessons.md) for philosophy and framing.

See [PHASE1-PHASE2-ENHANCED-LESSONS.md](references/phase1-phase2-enhanced-lessons.md) for structured lesson format and file separation.

See [LESSONS_UPDATE_GUIDE.md](references/lessons_update_guide.md) for syncing lessons from workspace to skill.

## Capturing Lessons

### Lessons Format (Phase 1+2 Enhanced)

Each lesson gets structured metadata for filtering and recurring pattern detection:

```markdown
## [LRN-YYYYMMDD-XXX] rule_name (category)

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending | in_progress | resolved | promoted
**Area**: backend | infra | tests | docs | config
**Pattern-Key**: category.pattern_name (optional, for recurring detection)

### Summary
One-line description

### Details
Full context and examples

### Applied to
Projects or files where this was used

### Metadata
- Source: correction | insight | user_feedback
- Related Files: path/to/file
- Tags: tag1, tag2
- See Also: LRN-20250225-001 (if related to existing entry)
- Recurrence-Count: 1 (increment if you see it again)
- First-Seen: 2025-02-23
- Last-Seen: 2025-02-23
```

### Errors & Features (NEW)

Log failures and feature gaps separately for better organization:

**Errors** (`tasks/errors.md`):
- Command failures, API errors, exceptions
- Include reproducibility, environment, suggested fix

**Features** (`tasks/feature_requests.md`):
- Missing capabilities, things you wish existed
- Include complexity estimate and suggested implementation

### Syncing to Skill

Periodically merge workspace lessons into the published skill:

```bash
# From openclaw-workflow repo
python3 scripts/sync_lessons.py --workspace ~/.openclaw/workspace

# Dry run (preview changes)
python3 scripts/sync_lessons.py --workspace ~/.openclaw/workspace --dry-run
```

This merges workspace lessons into `references/lessons.md` for version control and sharing.

## Hooks (Optional)

Enable automatic bootstrap reminders for self-improvement:

```bash
openclaw hooks enable pi-workflow
```

This injects a reminder at session start showing:
- When to log lessons/errors/features
- Format and metadata fields
- Recurring pattern detection
- Promotion paths

See `hooks/openclaw/HOOK.md` for details.

---

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Minimal code impact.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
