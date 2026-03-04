---
name: failure-memory
version: 1.5.0
description: Stop making the same mistakes — turn failures into patterns that prevent recurrence
author: Live Neon <contact@liveneon.dev>
homepage: https://github.com/live-neon/skills/tree/main/agentic/failure-memory
repository: leegitw/failure-memory
license: MIT
tags: [agentic, memory, learning, self-improving, error-tracking, observability, patterns, adaptive, feedback]
layer: core
status: active
alias: fm
metadata:
  openclaw:
    requires:
      config:
        - .openclaw/failure-memory.yaml
        - .claude/failure-memory.yaml
      workspace:
        - .learnings/
        - .learnings/observations/
---

# failure-memory (記憶)

Unified skill for failure detection, observation recording, memory search, and pattern convergence.
Consolidates 10 granular skills into a single coherent memory system.

**Trigger**: 失敗発生 (failure occurred)

**Source skills**: failure-tracker, observation-recorder, memory-search, topic-tagger, failure-detector, evidence-tier, effectiveness-metrics, pattern-convergence-detector, positive-framer, contextual-injection

## Installation

```bash
openclaw install leegitw/failure-memory
```

**Dependencies**: `leegitw/context-verifier` (for file change detection)

```bash
# Install with dependencies
openclaw install leegitw/context-verifier
openclaw install leegitw/failure-memory
```

**Standalone usage**: This skill can function independently for basic failure tracking.
For full lifecycle management, install the complete suite (see [Neon Agentic Suite](../README.md)).

**Data handling**: This skill operates within your agent's trust boundary. When triggered,
it uses your agent's configured model for failure detection and pattern recording. No external APIs
or third-party services are called. Results are written to `.learnings/` in your workspace.

## What This Solves

AI systems often make the same mistakes repeatedly — deleting working code, missing edge cases, forgetting context. This skill turns failures into learning by:

1. **Detecting failures** when they happen (not after)
2. **Recording observations** with R/C/D counters (Recurrence/Confirmations/Disconfirmations)
3. **Finding patterns** within the workspace's `.learnings/` directory
4. **Promoting to constraints** when evidence threshold is met

**The insight**: Systems learn better from consequences than instructions. A failure that happened teaches more than a rule that might apply.

> **Scope note**: Pattern detection operates within the current workspace only. Observations
> are stored in `.learnings/` and searched locally. No cross-project data access occurs.

## Usage

```
/fm <sub-command> [arguments]
```

## Sub-Commands

| Command | CJK | Logic | Trigger |
|---------|-----|-------|---------|
| `/fm detect` | 検出 | fail∈{test,user,API}→record | Next Steps (auto) |
| `/fm record` | 記録 | pattern→obs, R++∨C++∨D++ | Next Steps (auto) |
| `/fm search` | 索引 | query(pattern∨tag∨slug)→obs[] | Explicit |
| `/fm classify` | 分類 | obs→tier∈{N=1:弱,N=2:中,N≥3:強} | Explicit |
| `/fm status` | 状態 | eligible:R≥3∧C≥2, recent:30d | Explicit |
| `/fm refactor` | 整理 | obs[]→merge∨split∨restructure | Explicit |
| `/fm converge` | 収束 | pattern[]→detect(similarity≥0.8) | Explicit |

## Arguments

### /fm detect

| Argument | Required | Description |
|----------|----------|-------------|
| type | Yes | Failure type: `test`, `user`, `api`, `error` |
| context | No | Additional context for the failure |

### /fm record

| Argument | Required | Description |
|----------|----------|-------------|
| pattern | Yes | Pattern description or observation ID |
| counter | No | Counter to increment: `R` (default), `C`, or `D` |

### /fm search

| Argument | Required | Description |
|----------|----------|-------------|
| query | Yes | Search pattern, tag, or slug |
| status | No | Filter by status: `pending`, `eligible`, `all` (default) |

### /fm classify

| Argument | Required | Description |
|----------|----------|-------------|
| observation | Yes | Observation ID or pattern |

### /fm status

| Argument | Required | Description |
|----------|----------|-------------|
| --eligible | No | Show only eligible observations (R≥3 ∧ C≥2) |
| --recent | No | Show only observations from last 30 days |

### /fm refactor

| Argument | Required | Description |
|----------|----------|-------------|
| observations | Yes | Comma-separated observation IDs |
| action | Yes | Action: `merge`, `split`, `restructure` |

### /fm converge

| Argument | Required | Description |
|----------|----------|-------------|
| --threshold | No | Similarity threshold (default: 0.8) |

## Detection Triggers

These patterns indicate when `/fm detect` should be invoked (user or orchestrator triggers):

| Pattern | Source | Action |
|---------|--------|--------|
| `test.exit_code != 0` | Tool output | `/fm detect test` |
| "Actually...", "No, that's wrong" | User message | `/fm record correction` |
| "I meant...", "Not X, Y" | User message | `/fm record correction` |
| API 4xx/5xx response | Tool output | `/fm detect api` |
| "error:", "failed", "Exception" | Tool output | `/fm detect error` |
| Deployment rollback | CI/CD output | `/fm detect deployment` |
| Database migration failed | Tool output | `/fm detect migration` |

### Example: API Failure Detection

```
[DETECTED] api failure
Pattern: payment-api-timeout
Context: Payment API returned 504 after 30s
Observation: OBS-20260215-002
R: 1 → 3
Status: Eligible for constraint (R≥3)
```

### Example: Deployment Failure Detection

```
[DETECTED] deployment failure
Pattern: staging-healthcheck-fail
Context: Staging deployment failed health check on /api/health
Observation: OBS-20260215-003
R: 1 → 2
Status: Monitoring (R<3)
```

## Core Logic

### R/C/D Counters

| Counter | Meaning | Updated By |
|---------|---------|------------|
| **R** (Recurrence) | Auto-detected occurrences | `/fm detect`, `/fm record` |
| **C** (Confirmations) | Human-verified true positives | Human via `/fm record C` |
| **D** (Disconfirmations) | Human-verified false positives | Human via `/fm record D` |

### Evidence Tiers

| Tier | Criteria | Meaning |
|------|----------|---------|
| 弱 (weak) | N=1 | Single occurrence, may be noise |
| 中 (emerging) | N=2 | Pattern emerging, monitor |
| 強 (strong) | N≥3 | Established pattern, actionable |

### Slug Taxonomy

Observations are tagged with slugs: `git-*`, `test-*`, `workflow-*`, `security-*`, `docs-*`, `quality-*`

### Metrics

- `prevention_rate`: Failures prevented / Total potential failures
- `false_positive_rate`: D / (C + D)

## Output

### /fm detect output

```
[DETECTED] test failure
Pattern: lint-before-commit
Observation: OBS-20260215-001
R: 1 → 2
Status: Monitoring (R<3)
```

### /fm status output

```
=== Failure Memory Status ===

Eligible for constraint (R≥3 ∧ C≥2):
- OBS-20260210-003: lint-before-commit (R=4, C=2, D=0)
- OBS-20260212-007: test-before-push (R=3, C=3, D=1)

Recent (last 30d): 12 observations
Pending review: 3 observations
```

## Configuration

Configuration is loaded from (in order of precedence):
1. `.openclaw/failure-memory.yaml` (OpenClaw standard)
2. `.claude/failure-memory.yaml` (Claude Code compatibility)
3. Defaults (built-in)

```yaml
# .openclaw/failure-memory.yaml
detection:
  auto_detect: true          # Enable automatic failure detection
  patterns:                   # Custom detection patterns
    - "FATAL:"
    - "CRITICAL:"
thresholds:
  eligibility_R: 3           # Recurrence threshold (default: 3)
  eligibility_C: 2           # Confirmation threshold (default: 2)
  false_positive_max: 0.2    # Max D/(C+D) ratio (default: 0.2)
```

## Integration

- **Layer**: Core
- **Depends on**: context-verifier (for file change detection)
- **Used by**: constraint-engine (for eligibility checks), governance (for state queries)

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Invalid sub-command | List available sub-commands |
| Missing observation ID | Error with usage example |
| No matches found | "No observations match query" |
| Duplicate detection | Increment R counter, don't create new observation |

## Next Steps

After invoking this skill:

| Condition | Action |
|-----------|--------|
| R incremented | Check eligibility: R≥3 ∧ C≥2 → notify user |
| R≥3 ∧ C≥2 | Suggest `/ce generate` for constraint |
| Pattern recurring | Link with `See Also`, bump priority |
| Always | Update `.learnings/ERRORS.md` or `.learnings/LEARNINGS.md` |

## Workspace Files

This skill reads/writes:

```
.learnings/
├── ERRORS.md        # [ERR-YYYYMMDD-XXX] command failures
├── LEARNINGS.md     # [LRN-YYYYMMDD-XXX] corrections, best practices
└── observations/    # Individual observation files
    └── OBS-YYYYMMDD-XXX.md
```

## Security Considerations

**What this skill accesses:**
- Configuration files in `.openclaw/failure-memory.yaml` and `.claude/failure-memory.yaml`
- Tool output and user messages in the current session (for failure detection)
- Its own workspace directory `.learnings/` (read/write)

**What this skill does NOT access:**
- Files outside declared workspace paths
- System environment variables
- Other projects or sessions (observations are workspace-local)
- Network resources or external APIs

**What this skill does NOT do:**
- Send data to external services
- Access "across sessions and projects" beyond the current workspace
- Execute arbitrary code or run external commands

**Data scope clarification:**
- "Failure detection" scans tool output and user messages within the current agent session
- Observations are stored in `.learnings/` within the current workspace only
- No cross-project or cross-session data access occurs
- Pattern matching is local to the configured workspace

**Detection trigger clarification:**
The "Detection Triggers" table describes patterns that indicate when this skill should be
invoked. The agent can auto-invoke `/fm detect` when these patterns are detected, or users
can invoke manually. This enables true agentic behavior — failures are captured automatically.

**Provenance note:**
This skill is developed by Live Neon (https://github.com/live-neon/skills) and published
to ClawHub under the `leegitw` account. Both refer to the same maintainer.

## Acceptance Criteria

- [ ] `/fm detect` creates or updates observation with R++
- [ ] `/fm record` supports R, C, D counter updates
- [ ] `/fm search` finds observations by pattern, tag, or slug
- [ ] `/fm classify` returns correct tier based on N count
- [ ] `/fm status` shows eligible observations
- [ ] `/fm refactor` merges/splits observations correctly
- [ ] `/fm converge` detects similar patterns (≥0.8 similarity)
- [ ] Detection triggers work for test failures, user corrections, API errors
- [ ] Workspace files follow self-improving-agent format

---

*Consolidated from 10 skills as part of agentic skills consolidation (2026-02-15).*
