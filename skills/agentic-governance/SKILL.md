---
name: agentic-governance
version: 1.3.0
description: Keep your constraints healthy — lifecycle management with automatic staleness detection
author: Live Neon <contact@liveneon.dev>
homepage: https://github.com/live-neon/skills/tree/main/agentic/governance
repository: leegitw/agentic-governance
license: MIT
tags: [agentic, governance, lifecycle, maintenance, health-checks, observability, compliance, staleness]
layer: governance
status: active
alias: gov
metadata:
  openclaw:
    requires:
      config:
        - .openclaw/governance.yaml
        - .claude/governance.yaml
      workspace:
        - output/governance/
        - output/constraints/
        - agentic/INDEX.md
---

# governance (治理)

Unified skill for constraint governance state, periodic reviews, index generation,
round-trip verification, and schema migration. Consolidates 6 granular skills.

**Trigger**: 定期保守 (periodic maintenance) or HEARTBEAT

**Source skills**: constraint-reviewer, index-generator, round-trip-tester, governance-state, slug-taxonomy, adoption-monitor (from safety)

## Installation

```bash
openclaw install leegitw/governance
```

**Dependencies**:
- `leegitw/constraint-engine` (for constraint data)
- `leegitw/failure-memory` (for observation data)

```bash
# Install full governance stack
openclaw install leegitw/context-verifier
openclaw install leegitw/failure-memory
openclaw install leegitw/constraint-engine
openclaw install leegitw/governance
```

**Standalone usage**: Index generation and round-trip verification work independently.
Full governance features require constraint-engine and failure-memory integration.

**Data handling**: This skill operates within your agent's trust boundary. When triggered,
it uses your agent's configured model for governance analysis and review. No external APIs
or third-party services are called. Results are written to `output/governance/` in your workspace.

## What This Solves

Constraints that never get reviewed become stale. Rules that never get challenged become dogma. This skill manages the lifecycle:

1. **State tracking** — know which constraints are active, suspended, or retired
2. **Periodic reviews** — 90-day gates to re-evaluate constraints against current evidence
3. **Index generation** — dashboards showing constraint health at a glance

**The insight**: Good governance is proactive. Constraints need maintenance, not just creation.

## Usage

```
/gov <sub-command> [arguments]
```

## Sub-Commands

| Command | CJK | Logic | Trigger |
|---------|-----|-------|---------|
| `/gov state` | 状態 | central_state, event→alert | HEARTBEAT |
| `/gov review` | 審査 | constraints.due→review_queue | HEARTBEAT |
| `/gov index` | 索引 | skills[]→INDEX.md | Explicit |
| `/gov verify` | 検証 | round_trip(source↔compiled)→sync✓∨drift✗ | Explicit |
| `/gov migrate` | 移行 | schema.v(n)→schema.v(n+1) | Explicit |

## Arguments

### /gov state

| Argument | Required | Description |
|----------|----------|-------------|
| --summary | No | Show summary only (default: full state) |
| --alerts | No | Show pending alerts only |

### /gov review

| Argument | Required | Description |
|----------|----------|-------------|
| --due | No | Show only due reviews (default) |
| --all | No | Show all constraints with review dates |
| --complete | No | Mark review as complete |

### /gov index

| Argument | Required | Description |
|----------|----------|-------------|
| --path | No | Output path (default: `agentic/INDEX.md`) |
| --format | No | Format: `markdown` (default), `json` |

### /gov verify

| Argument | Required | Description |
|----------|----------|-------------|
| source | Yes | Source file or directory |
| compiled | Yes | Compiled/generated file or directory |
| --strict | No | Fail on any difference |

### /gov migrate

| Argument | Required | Description |
|----------|----------|-------------|
| --to | Yes | Target schema version |
| --dry-run | No | Show changes without applying |

## Configuration

Configuration is loaded from (in order of precedence):
1. `.openclaw/governance.yaml` (OpenClaw standard)
2. `.claude/governance.yaml` (Claude Code compatibility)
3. Defaults (built-in)

## Core Logic

### Governance State Model

```
┌─────────────────────────────────────────┐
│           GOVERNANCE STATE               │
├─────────────────────────────────────────┤
│ Constraints:                             │
│   - Active: 5                           │
│   - Draft: 2                            │
│   - Retiring: 1                         │
│   - Retired: 12                         │
├─────────────────────────────────────────┤
│ Reviews:                                 │
│   - Due: 2 (approaching 90-day mark)    │
│   - Overdue: 0                          │
├─────────────────────────────────────────┤
│ Health:                                  │
│   - Circuit: CLOSED                     │
│   - Violations (30d): 3                 │
│   - Adoption rate: 85%                  │
├─────────────────────────────────────────┤
│ Alerts:                                  │
│   - [WARN] CON-001 due for review       │
│   - [INFO] 2 new observations eligible  │
└─────────────────────────────────────────┘
```

### Review Cycle

Constraints require periodic review. The review cadence is configurable (default: 90 days):

```yaml
# .openclaw/governance.yaml
governance:
  review_cadence_days: 90    # Default
  warning_threshold: 15      # Days before due to warn
```

| Days Since Last Review | Status | Action |
|------------------------|--------|--------|
| 0-75 | Current | No action |
| 76-90 | Approaching | Warning alert |
| 91+ | Overdue | Escalation alert |

> **⚠️ Advisory Only**: This review cycle is *not enforced programmatically*.
> Compliance relies on HEARTBEAT P3 checks and manual diligence.
> Automated enforcement (`/gov review --automated`) is planned for future release.
> See HEARTBEAT.md for current verification schedule.

### Adoption Monitoring

Track constraint adoption across sessions:

| Metric | Calculation | Target |
|--------|-------------|--------|
| Adoption rate | Sessions with constraint used / Total sessions | >80% |
| Violation rate | Violations / Checks | <5% |
| Override rate | Overrides / Violations | <20% |

### Slug Taxonomy

Standard slug prefixes for observations and constraints:

| Prefix | Domain | Examples |
|--------|--------|----------|
| `git-*` | Version control | git-commit-message, git-branch-naming |
| `test-*` | Testing | test-before-commit, test-coverage |
| `workflow-*` | Process | workflow-pr-review, workflow-deploy |
| `security-*` | Security | security-no-secrets, security-auth |
| `docs-*` | Documentation | docs-update-readme, docs-api |
| `quality-*` | Code quality | quality-lint, quality-format |

## Output

### /gov state output

```
[GOVERNANCE STATE]
Updated: 2026-02-15 10:30:00

=== Constraints ===
Active: 5 | Draft: 2 | Retiring: 1 | Retired: 12

=== Circuit Breaker ===
Status: CLOSED (healthy)
Violations (30d): 3

=== Reviews ===
Due: 2 constraints approaching 90-day mark
  - CON-20251120-001: "Always run tests" (day 87)
  - CON-20251125-003: "Lint before commit" (day 82)

=== Adoption ===
Rate: 85% (target: >80%)
Sessions tracked: 47

=== Alerts ===
[WARN] CON-20251120-001 due for review in 3 days
[INFO] 2 observations eligible for constraint generation
```

### /gov review output

```
[CONSTRAINT REVIEW QUEUE]

Due for review (2):

1. CON-20251120-001: "Always run tests before commit"
   Age: 87 days | Status: active
   Violations (90d): 2 | Overrides: 0
   Adoption: 92%

   Options:
   a) Renew for 90 days: /ce lifecycle CON-20251120-001 active
   b) Begin retirement: /ce lifecycle CON-20251120-001 retiring
   c) Immediate retire: /ce lifecycle CON-20251120-001 retired

2. CON-20251125-003: "Always lint before commit"
   Age: 82 days | Status: active
   Violations (90d): 5 | Overrides: 1
   Adoption: 78%

   [WARN] Below adoption target (80%)
   Consider: Clarify constraint or improve tooling
```

### /gov index output

```
[INDEX GENERATED]
Path: agentic/INDEX.md
Skills: 7
Updated: 2026-02-15 10:30:00

Contents:
- failure-memory (fm) - Core
- constraint-engine (ce) - Core
- context-verifier (cv) - Foundation
- review-orchestrator (ro) - Review
- governance (gov) - Governance
- safety-checks (sc) - Safety
- workflow-tools (wt) - Extensions
```

### /gov verify output

```
[ROUND-TRIP VERIFICATION]
Source: docs/constraints/
Compiled: output/constraints/

Status: ✓ IN SYNC

Files checked: 12
Matches: 12
Drifts: 0
```

### Example: Compliance Review

```
/gov review --all
[CONSTRAINT REVIEW QUEUE]

Compliance Status (SOC 2):

1. CON-20260101-001: "Always encrypt PII at rest"
   Age: 45 days | Status: active
   Compliance: SOC 2 CC6.1
   Violations (90d): 0 | Adoption: 100%
   ✓ Compliant

2. CON-20260115-002: "Always log authentication events"
   Age: 31 days | Status: active
   Compliance: SOC 2 CC6.2
   Violations (90d): 1 | Adoption: 98%
   ⚠ Review violation on 2026-02-01

Summary: 12 constraints | 11 compliant | 1 needs review
```

### Example: Security Audit Preparation

```
/gov state --summary
[GOVERNANCE STATE]
Updated: 2026-02-15 14:00:00

Audit Readiness:
  Security constraints: 8 active
  Last review: 2026-02-10
  Violations (90d): 2 (both resolved)
  Override rate: 5% (within policy)

Recommendation: Ready for external audit.
```

## Integration

- **Layer**: Governance
- **Depends on**: constraint-engine (for constraint data), failure-memory (for observation data)
- **Used by**: None (top-level governance)

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Invalid sub-command | List available sub-commands |
| No constraints found | Info: "No constraints in system" |
| State file corrupted | Rebuild from constraint files |
| Migration conflict | Show conflicts, require manual resolution |

## Next Steps

After invoking this skill:

| Condition | Action |
|-----------|--------|
| Reviews due | Process each review, update lifecycle |
| Alerts pending | Surface to user, track resolution |
| Index outdated | Regenerate INDEX.md |
| Drift detected | Investigate and reconcile |

## Workspace Files

This skill reads/writes:

```
output/
├── governance/
│   ├── state.json           # Central governance state
│   ├── reviews/             # Review records
│   │   └── YYYY-MM-DD.md
│   └── alerts.json          # Pending alerts
└── constraints/
    └── metadata.json        # Constraint metadata (adoption, violations)

agentic/
└── INDEX.md                 # Generated skill index
```

## Security Considerations

**What this skill accesses:**
- Configuration files in `.openclaw/governance.yaml` and `.claude/governance.yaml`
- Constraint data from `output/constraints/` (via constraint-engine)
- Observation data from `.learnings/` (via failure-memory)
- Its own output directory `output/governance/`
- Skill index file `agentic/INDEX.md`

**What this skill does NOT access:**
- Files outside declared workspace paths
- System environment variables
- Network resources or external APIs

**What this skill does NOT do:**
- Send data to external services
- Execute arbitrary code
- Modify files outside its workspace

**Dependency note:**
This skill reads data from `constraint-engine` and `failure-memory` skill workspaces.
Install the full governance stack for complete functionality.

## Acceptance Criteria

- [ ] `/gov state` shows complete governance overview
- [ ] `/gov state` surfaces alerts for due reviews
- [ ] `/gov review` lists constraints due for 90-day review
- [ ] `/gov review` provides clear renewal/retirement options
- [ ] `/gov index` generates skill index from SKILL.md files
- [ ] `/gov verify` detects drift between source and compiled
- [ ] `/gov migrate` handles schema version transitions
- [ ] Adoption metrics tracked and reported
- [ ] Workspace files follow documented structure

---

*Consolidated from 6 skills as part of agentic skills consolidation (2026-02-15).*
