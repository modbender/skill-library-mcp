# Phase 1 + 2: Enhanced Lesson Capture

## Overview

Phase 1 + 2 enhances the self-improvement system with structured metadata and file separation.

- **Phase 1**: Add metadata fields to `tasks/lessons.md` (Priority, Status, Area, Pattern-Key, Recurrence-Count)
- **Phase 2**: Separate errors and feature requests into dedicated files

## Why This Matters

| Problem | Solution |
|---------|----------|
| Lessons get lost or forgotten | Add Status field to track resolution |
| Can't filter by area (backend vs infra) | Add Area field for organization |
| Recurring mistakes pile up | Add Recurrence-Count + Pattern-Key to detect patterns |
| Error logs and feature gaps mixed with lessons | Separate files for clear intent |

## Phase 1: Structured Metadata

### Lesson Entry Format

```markdown
## [LRN-YYYYMMDD-XXX] lesson_name (category)

**Logged**: 2025-02-23T18:00:00Z
**Priority**: low | medium | high | critical
**Status**: pending | in_progress | resolved | promoted
**Area**: backend | infra | tests | docs | config
**Pattern-Key**: error_handling.wrap_risky_code_only (optional)

### Summary
One-line description

### Details
Full context, code examples, explanations

### Applied to
Projects where you used this lesson

### Metadata
- Source: correction | insight | user_feedback
- Related Files: path/to/file
- Tags: tag1, tag2
- See Also: LRN-20250225-001 (link to related entries)
- Recurrence-Count: 1 (how many times you've seen this)
- First-Seen: 2025-02-23
- Last-Seen: 2025-02-23
```

### ID Format

Format: `LRN-YYYYMMDD-XXX`
- **LRN**: Entry type (Lesson)
- **YYYYMMDD**: Date captured
- **XXX**: Sequential number (001, 002) or random 3 chars

Examples: `LRN-20250223-001`, `LRN-20250225-A3F`

### Category Options

- **correction**: User corrected you ("No, that's wrong...")
- **insight**: Something you discovered works well
- **knowledge_gap**: You learned something you didn't know
- **best_practice**: Pattern that prevents bugs

### Priority Guidelines

| Priority | When |
|----------|------|
| **critical** | Blocks work, security issue, data loss risk |
| **high** | Significant impact, recurring issue, affects many workflows |
| **medium** | Moderate impact, workaround exists |
| **low** | Minor inconvenience, edge case, nice-to-have |

### Status Values

| Status | Meaning |
|--------|---------|
| **pending** | Captured but not yet actioned |
| **in_progress** | You're actively working on preventing this |
| **resolved** | You fixed the root cause or pattern |
| **promoted** | Moved to AGENTS.md, SOUL.md, or TOOLS.md |

### Area Tags

Use to filter lessons by codebase region:

| Area | Scope |
|------|-------|
| `backend` | API, services, business logic |
| `infra` | CI/CD, Docker, cloud, deployment |
| `tests` | Testing, test utilities, coverage |
| `docs` | Documentation, comments, READMEs |
| `config` | Configuration, environment, settings |

### Pattern-Key (Optional)

Stable identifier for recurring patterns. Format: `category.pattern_name`

**Purpose**: Deduplication across time. If you see the same mistake again, search for its Pattern-Key and increment Recurrence-Count.

**Example**:
- `error_handling.wrap_risky_code_only`
- `git.auth_configuration`
- `testing.edge_case_omission`

### Recurrence Tracking

When you capture the same lesson multiple times:

1. Search existing entries: `grep "Pattern-Key: error_handling" tasks/lessons.md`
2. If found:
   - Increment `Recurrence-Count`
   - Update `Last-Seen`
   - Add `See Also` links to related entries
3. If not found:
   - Create new entry with `Recurrence-Count: 1`

**Promotion Trigger**: When `Recurrence-Count >= 3` over a 30-day window, consider promoting to a permanent rule in AGENTS.md or SOUL.md.

### Example: Complete Lesson Entry

```markdown
## [LRN-20250223-001] Wrap Only Risky Code, Not Everything (correction)

**Logged**: 2025-02-23T18:00:00Z
**Priority**: medium
**Status**: pending
**Area**: backend
**Pattern-Key**: error_handling.wrap_risky_code_only

### Summary
Wrap only risky code in try-catch, not entire methods or safe operations.

### Details
Wrapping validation logic that intentionally throws exceptions creates unnecessary rethrow paths. Instead:
- Use direct throws for validation you control
- Wrap only operations that can unexpectedly fail
- Let safe operations execute without wrapping

### Applied to
- NovelGlide CFI Parser (Phase 1 review)
- Regex parsing operations
- Input validation flows

### Metadata
- Source: correction (feedback from Kai)
- Related Files: novelglide-flutter/reader_engine/...
- Tags: exception, dart, pattern
- See Also: —
- Recurrence-Count: 1
- First-Seen: 2025-02-23
- Last-Seen: 2025-02-23
```

## Phase 2: File Separation

### Three Files, Clear Intent

```
tasks/
├── lessons.md          # Corrections, insights, best practices
├── errors.md           # Command failures, API errors, exceptions
└── feature_requests.md # Missing capabilities, feature gaps
```

### lessons.md: Patterns & Rules

**When to log here:**
- User corrects you ("That's wrong...")
- You discover a better pattern
- You learn something new about the system

**Format**: Structured metadata as above

**Example entry**: "Wrap Only Risky Code" lesson

---

### errors.md: Failures & Diagnosis

**When to log here:**
- Command returns non-zero exit code
- API returns unexpected error
- Exception thrown unexpectedly
- Tool integration fails

**Format**:
```markdown
## [ERR-YYYYMMDD-XXX] tool_or_service_name

**Logged**: 2025-02-26T10:00:00Z
**Priority**: high
**Status**: pending
**Reproducible**: yes | no | unknown
**Area**: infra | config | tests

### Summary
Brief description of failure

### Error Output
```
Actual error message / stack trace
```

### Context
- Command/operation attempted
- Environment (OS, versions, etc.)
- What triggered it

### Suggested Fix
If known, how to resolve

### Metadata
- Related Files: path/to/file
- Tags: git, auth, integration
- See Also: ERR-20250225-001
- Recurrence-Count: 1
- First-Seen: 2025-02-26
- Last-Seen: 2025-02-26
```

**Status Options**:
- `pending` — Not yet diagnosed
- `in_progress` — Investigating
- `resolved` — Fixed or workaround found
- `monitored` — Known issue, watching pattern

---

### feature_requests.md: Capability Gaps

**When to log here:**
- "I wish Tool X could also do Y"
- "There's no way to do Z"
- Missing integration or workflow

**Format**:
```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: 2025-02-26T10:00:00Z
**Priority**: medium
**Status**: pending
**Frequency**: first_time | recurring | blocker
**Area**: backend | infra | docs

### Requested Capability
What you wanted to do

### Context
Why you needed it, what problem it solves

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
How this could be built

### Metadata
- Related Files: path/to/file
- Tags: feature, automation
- See Also: FEAT-20250225-001
- Related Features: other_feature_name
```

**Frequency Options**:
- `first_time` — One-off request
- `recurring` — Come up repeatedly
- `blocker` — Blocking work right now

---

## Workflow Integration

### When to Capture

| Trigger | File | Example |
|---------|------|---------|
| User says "you're wrong" | `lessons.md` | Exception handling pattern |
| Command fails with error | `errors.md` | Git auth failure |
| Tool lacks capability | `feature_requests.md` | "Add Slack integration" |
| You discover a pattern | `lessons.md` | "Async always needs error handling" |
| API returns unexpected response | `errors.md` | Binance API rate limit behavior |

### Review Schedule

**Daily**: During work, capture lessons/errors/features as they happen

**Weekly**: Review `tasks/` files:
- Mark resolved items
- Increment Recurrence-Count for repeated issues
- Link related entries with `See Also`

**Monthly**: Sync to skill:
```bash
cd /Volumes/Transcend/GitHub/openclaw-workflow
python3 scripts/sync_lessons.py --workspace ~/.openclaw/workspace
```

**Quarterly**: Review all entries for promotion candidates (Recurrence-Count ≥ 3)

### Promotion Path

When a lesson becomes broadly applicable:

1. **Identify candidate**: Recurrence-Count ≥ 3 or high priority
2. **Promote to AGENTS.md**: Add as workflow guideline
   - Format: Short rule, not verbose explanation
   - Example: "Always wrap only risky code in try-catch blocks"
3. **Update entry**: Set `Status: promoted`
4. **Remove from workspace** (optional): Keep or archive as reference

### Example: Promotion to AGENTS.md

**From lessons.md** (verbose):
> Wrap only risky code in try-catch, not entire methods...

**To AGENTS.md** (concise):
```markdown
## Error Handling

- **Wrap only risky operations**: try-catch wraps code that can unexpectedly fail
- **Direct throws for validation**: Use direct throw for checks you control
- Example: Wrap `.allMatches()` (risky), not `if (isEmpty)` (validation)
```

---

## Tools & Automation

### Phase 1+2 Doesn't Require Hooks

Unlike the full self-improving-agent skill, Phase 1+2 is **manual and lightweight**:
- ✅ No shell hooks needed
- ✅ No automatic reminders
- ✅ No file watching

You simply capture lessons as you work.

**Optional Future**: Add hooks via self-improving-agent skill if you want automatic reminders.

### Sync Script

Openclaw-workflow includes `scripts/sync_lessons.py` to merge workspace lessons into the published skill:

```bash
# Preview
python3 scripts/sync_lessons.py --workspace ~/.openclaw/workspace --dry-run

# Apply
python3 scripts/sync_lessons.py --workspace ~/.openclaw/workspace

# Commit and push
git add references/lessons.md
git commit -m "Update lessons: [description]"
git push
```

---

## Quick Reference

| File | Purpose | ID Prefix | Status Options |
|------|---------|-----------|-----------------|
| `tasks/lessons.md` | Rules & patterns | LRN | pending \| in_progress \| resolved \| promoted |
| `tasks/errors.md` | Failures & diagnosis | ERR | pending \| in_progress \| resolved \| monitored |
| `tasks/feature_requests.md` | Capability gaps | FEAT | pending \| in_progress \| on_roadmap |

---

## Summary

- **Phase 1** adds metadata (Priority, Status, Area, Pattern-Key) for better filtering and recurring pattern detection
- **Phase 2** separates lessons, errors, and features into three files with clear intent
- No automation required—just structured markdown
- Review periodically to promote high-value lessons to permanent rules
- Sync monthly to skill repository for version control
