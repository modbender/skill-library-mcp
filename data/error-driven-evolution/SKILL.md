---
name: error-driven-evolution
description: Structured error-to-rule learning system for AI agents. Activate when an agent makes a mistake, receives a correction from the user, or needs to check past lessons before making a decision. Converts errors into executable rules (not reflections) stored in lessons.md, and enforces pre-decision rule scanning to prevent repeat mistakes. Supports sharing anonymized lessons to a community repository.
---

# Error-Driven Evolution

Turn mistakes into rules. Not reflections, not apologies — rules.

## Core Concept

When an agent makes an error or gets corrected, it must:
1. Extract a **rule** (not a story)
2. Write it to `lessons.md` in its workspace
3. Scan relevant rules **before** future decisions in that domain
4. Optionally share anonymized rules to the community repo

## lessons.md Format

File location: `{workspace}/lessons.md`

Each rule follows this structure:

```markdown
### [CATEGORY] Short imperative title

- **When**: The specific situation/trigger
- **Do**: The correct action (imperative, specific)
- **Don't**: The wrong action that was taken
- **Why**: One sentence — what went wrong
- **Added**: YYYY-MM-DD
```

### Categories

| Tag | Scope |
|-----|-------|
| `DATA` | Querying, interpreting, presenting data |
| `COMMS` | Messaging, tone, audience, channels |
| `SCOPE` | Role boundaries, doing others' work |
| `EXEC` | Task execution, tools, file ops |
| `JUDGMENT` | Decisions, priorities, assumptions |
| `CONTEXT` | Memory, context window, info management |
| `SAFETY` | Security, privacy, destructive ops |
| `COLLAB` | Multi-agent coordination, handoffs |

## When to Record

Record a rule when:
1. **User corrects you** — explicit feedback
2. **User overrides your output** — they redo your work
3. **Same error twice** — second occurrence MUST become a rule
4. **Near miss** — you catch yourself about to repeat a mistake

Do NOT record: one-off technical glitches, user preference changes (those go in MEMORY.md).

## How to Record

1. Stop. Don't apologize at length.
2. Identify the category.
3. Write the rule in imperative form.
4. Append to lessons.md (never overwrite).
5. Confirm briefly: "Added to lessons: [title]"

## Pre-Decision Scan

Before acting, scan `lessons.md` for applicable rules:

| About to... | Check |
|-------------|-------|
| Present data | `[DATA]` |
| Send message / write report | `[COMMS]` + `[SCOPE]` |
| Make suggestion | `[JUDGMENT]` + `[SCOPE]` |
| Execute multi-step task | `[EXEC]` + `[CONTEXT]` |
| Start new session | All (skim titles) |

Scan = read `### [TAG]` headers, check if any `When` matches your situation.

## Community Sharing

Share anonymized lessons to help other agents: https://github.com/anthropic-ai/agent-lessons

See references/community-sharing.md for the anonymization and submission process.

## Setup

1. Create `lessons.md` in your workspace:
```markdown
# Lessons
Rules extracted from mistakes. Append after failing, scan before deciding.
```

2. Copy `community/top-100.md` to your workspace as `top-100.md` — this is your pre-installed immune system. Small enough to skim on startup, covers the most common and costly mistakes across all agent deployments.

3. Add to your startup instructions:
```markdown
- On startup: skim top-100.md titles (pre-installed community lessons)
- On correction/failure: append rule to lessons.md
- Before decisions: scan lessons.md + top-100.md for [CATEGORY] rules
```

## Loading Strategy

Your agent has two rule files:

| File | Source | Load on startup | Size target |
|------|--------|-----------------|-------------|
| `lessons.md` | Your own mistakes | Yes, fully | Grows organically |
| `top-100.md` | Community top picks | Yes, skim titles | ~8KB, curated |

For deeper community search (beyond top-100), query `community/{category}.md` files on-demand when facing an unfamiliar situation.

## Maintenance

When lessons.md exceeds 50 rules: review for duplicates, retire obsolete rules (mark don't delete), consider splitting by category.
