---
name: constraint-engine
version: 1.3.0
description: Learn from consequences, not instructions — generate and enforce constraints from experience
author: Live Neon <contact@liveneon.dev>
homepage: https://github.com/live-neon/skills/tree/main/agentic/constraint-engine
repository: leegitw/constraint-engine
license: MIT
tags: [agentic, guardrails, enforcement, rules, circuit-breaker, self-improving, prevention, validation]
layer: core
status: active
alias: ce
metadata:
  openclaw:
    requires:
      config:
        - .openclaw/constraint-engine.yaml
        - .claude/constraint-engine.yaml
      workspace:
        - output/constraints/
        - output/hooks/
---

# constraint-engine (制約)

Unified skill for constraint generation, pre-action checking, circuit breaker management,
and constraint lifecycle. Consolidates 7 granular skills into a single enforcement system.

**Trigger**: 行動前∨閾値到達 (pre-action or threshold reached)

**Source skills**: constraint-generator, circuit-breaker, emergency-override, constraint-lifecycle, constraint-versioning, positive-framer (partial), contextual-injection (partial)

## Installation

```bash
openclaw install leegitw/constraint-engine
```

**Dependencies**: `leegitw/failure-memory` (for eligibility data)

```bash
# Install with dependencies
openclaw install leegitw/context-verifier
openclaw install leegitw/failure-memory
openclaw install leegitw/constraint-engine
```

**Standalone usage**: Requires failure-memory for constraint generation from observations.
For full lifecycle management, install the complete suite (see [Neon Agentic Suite](../README.md)).

**Data handling**: This skill operates within your agent's trust boundary. When triggered,
it uses your agent's configured model for constraint checking and generation. No external APIs
or third-party services are called. Results are written to `output/constraints/` in your workspace.

## What This Solves

Instructions get ignored. Rules get forgotten. Documentation goes unread. This skill takes a different approach — constraints generated from actual failures:

1. **Generate constraints** from observations that meet the eligibility threshold (`R≥3 ∧ C≥2`)
2. **Enforce constraints** at runtime with a circuit breaker (CLOSED → OPEN → HALF-OPEN)
3. **Manage lifecycle** from proposal through adoption to retirement

**The insight**: A constraint born from "this actually broke" carries more weight than "this might break." Consequences teach better than instructions.

## Usage

```
/ce <sub-command> [arguments]
```

## Sub-Commands

| Command | CJK | Logic | Trigger |
|---------|-----|-------|---------|
| `/ce check` | 検査 | action→constraints[]→pass∨block | Next Steps (auto) |
| `/ce generate` | 生成 | eligible(obs)→constraint | Next Steps (auto) |
| `/ce status` | 状態 | active[], circuit∈{CLOSED,OPEN,HALF} | Explicit |
| `/ce override` | 上書 | constraint→bypass(temp), audit.log++ | Explicit |
| `/ce lifecycle` | 周期 | state∈{draft→active→retiring→retired} | Explicit |
| `/ce version` | 版本 | constraint→v++, history.preserve | Explicit |
| `/ce threshold` | 閾値 | user∨context→custom_threshold | Explicit |

## Arguments

### /ce check

| Argument | Required | Description |
|----------|----------|-------------|
| action | Yes | Action to check against constraints |
| --severity | No | Minimum severity to check: `critical`, `important`, `minor` (default: all) |

### /ce generate

| Argument | Required | Description |
|----------|----------|-------------|
| observation | Yes | Observation ID or pattern to generate constraint from |
| --force | No | Generate even if eligibility criteria not met |

### /ce status

| Argument | Required | Description |
|----------|----------|-------------|
| --circuit | No | Show circuit breaker status only |
| --active | No | Show active constraints only |

### /ce override

| Argument | Required | Description |
|----------|----------|-------------|
| constraint | Yes | Constraint ID to override |
| reason | Yes | Reason for override (logged for audit) |
| --duration | No | Override duration (default: "session") |

### /ce lifecycle

| Argument | Required | Description |
|----------|----------|-------------|
| constraint | Yes | Constraint ID |
| state | Yes | Target state: `draft`, `active`, `retiring`, `retired` |

### /ce version

| Argument | Required | Description |
|----------|----------|-------------|
| constraint | Yes | Constraint ID |
| --bump | No | Version bump type: `major`, `minor`, `patch` (default: minor) |

### /ce threshold

| Argument | Required | Description |
|----------|----------|-------------|
| --R | No | Custom recurrence threshold (default: 3) |
| --C | No | Custom confirmation threshold (default: 2) |
| --reset | No | Reset to default thresholds |

## Configuration

Configuration is loaded from (in order of precedence):
1. `.openclaw/constraint-engine.yaml` (OpenClaw standard)
2. `.claude/constraint-engine.yaml` (Claude Code compatibility)
3. Defaults (built-in)

```yaml
# .openclaw/constraint-engine.yaml
thresholds:
  R: 3                       # Recurrence threshold (default: 3)
  C: 2                       # Confirmation threshold (default: 2)
  false_positive_max: 0.2    # Max D/(C+D) ratio (default: 0.2)
circuit_breaker:
  critical_threshold: 3      # Violations to trip for CRITICAL
  important_threshold: 5     # Violations to trip for IMPORTANT
  minor_threshold: 10        # Violations to trip for MINOR
  window_days: 30            # Violation window (default: 30 days)
lifecycle:
  review_reminder_days: 80   # Days before 90-day review to remind
```

## Core Logic

### Eligibility Criteria

Observation becomes eligible for constraint when:

```
R≥3 ∧ C≥2 ∧ D/(C+D)<0.2 ∧ sources≥2
```

| Criterion | Meaning |
|-----------|---------|
| R≥3 | At least 3 recurrences |
| C≥2 | At least 2 human confirmations |
| D/(C+D)<0.2 | False positive rate under 20% |
| sources≥2 | Observed by at least 2 different sources |

### Positive Reframing

Constraints are automatically reframed positively:

| Negative | Positive |
|----------|----------|
| "Don't commit without tests" | "Always run tests before commit" |
| "Don't push to main directly" | "Always create PR for main changes" |
| "Don't deploy without review" | "Always get code review before deployment" |
| "Don't skip migrations" | "Always run database migrations before release" |

### Example: Code Review Constraint

```
[CHECK BLOCKED] deploy production
Constraint violated: CON-20260212-005
  "Always get code review approval before production deployment"
  Severity: CRITICAL

Action: Request review via /ro twin, then retry deployment.
```

### Example: Deployment Gate Constraint

```
[CHECK PASSED] deploy staging
Active constraints checked: 3
  ✓ CON-20260210-001: Tests pass
  ✓ CON-20260211-002: Staging smoke test
  ✓ CON-20260212-003: Database migration verified
All constraints satisfied. Proceeding to staging.
```

### Circuit Breaker States

| State | Meaning | Behavior |
|-------|---------|----------|
| CLOSED | Normal operation | Constraints enforced |
| OPEN | Circuit tripped | Block all related actions |
| HALF-OPEN | Testing recovery | Allow limited actions |

### Circuit Breaker Thresholds

| Severity | Threshold | Window |
|----------|-----------|--------|
| CRITICAL | 3 violations | 30 days |
| IMPORTANT | 5 violations | 30 days |
| MINOR | 10 violations | 30 days |

### Constraint Lifecycle

```
draft → active → retiring → retired
  │        │         │
  └────────┴─────────┴── 90-day review gates
```

## Output

### /ce check output (pass)

```
[CHECK PASSED] git commit -m "feature"
Active constraints checked: 5
All constraints satisfied.
```

### /ce check output (block)

```
[CHECK BLOCKED] git commit -m "feature"

Constraint violated: CON-20260210-001
  "Always run tests before commit"
  Severity: CRITICAL

Action: Run tests first, then retry commit.
Override: /ce override CON-20260210-001 "emergency hotfix"
```

### /ce status output

```
=== Constraint Engine Status ===

Circuit Breaker: CLOSED (healthy)

Active Constraints (5):
- CON-20260210-001: Always run tests before commit [CRITICAL]
- CON-20260212-003: Always lint before commit [IMPORTANT]
- ...

Draft Constraints (2):
- CON-20260215-001: Pending approval

Violations (30d): 2
```

### /ce generate output

```
[CONSTRAINT GENERATED]

From: OBS-20260210-003 (lint-before-commit)
ID: CON-20260215-001
Text: "Always run lint before commit"
Severity: IMPORTANT
Status: draft

Next: Review and approve with /ce lifecycle CON-20260215-001 active
```

## Integration

- **Layer**: Core
- **Depends on**: failure-memory (for eligibility data)
- **Used by**: governance (for constraint reviews), safety-checks (for enforcement)

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Invalid sub-command | List available sub-commands |
| Constraint not found | Error with suggestion to search |
| Ineligible observation | Show missing criteria, suggest /fm status |
| Circuit OPEN | Block action, show recovery guidance |
| Override without reason | Require reason for audit trail |

## Next Steps

After invoking this skill:

| Condition | Action |
|-----------|--------|
| Constraint generated | Add to `output/constraints/draft/`, notify user |
| Constraint activated | Move to `output/constraints/active/` |
| Action blocked | Log to `output/hooks/blocked.log`, explain why |
| Circuit OPEN | Surface to user with recovery guidance |
| Override used | Audit log entry, temporary bypass only |

## Workspace Files

This skill reads/writes:

```
output/
├── constraints/
│   ├── draft/           # Pending constraints
│   │   └── CON-YYYYMMDD-XXX.md
│   ├── active/          # Enforced constraints
│   │   └── CON-YYYYMMDD-XXX.md
│   ├── retired/         # Historical constraints
│   │   └── CON-YYYYMMDD-XXX.md
│   └── metadata.json    # VFM scoring data
└── hooks/
    └── blocked.log      # Actions blocked by constraints
```

## Security Considerations

**What this skill accesses:**
- Configuration files in `.openclaw/constraint-engine.yaml` and `.claude/constraint-engine.yaml`
- Observation data from failure-memory (via `.learnings/` directory)
- Its own output directories `output/constraints/` and `output/hooks/`

**What this skill does NOT access:**
- Files outside declared workspace paths
- System environment variables
- Network resources or external APIs

**What this skill does NOT do:**
- Send data to external services
- Execute arbitrary code
- Modify files outside its workspace

**Dependency note:**
This skill reads observation data from `failure-memory` skill's workspace (`.learnings/`).
Install `leegitw/failure-memory` for full constraint generation functionality.
Without failure-memory, constraint generation will have no observation data to process.

**Audit logging:**
Override actions are logged to `output/hooks/blocked.log` for audit purposes.
Logs are stored locally in the workspace only.

## Acceptance Criteria

- [ ] `/ce check` validates action against active constraints
- [ ] `/ce check` blocks when constraint violated, shows reason
- [ ] `/ce generate` creates constraint from eligible observation
- [ ] `/ce generate` applies positive reframing
- [ ] `/ce status` shows circuit breaker state and active constraints
- [ ] `/ce override` creates temporary bypass with audit log
- [ ] `/ce lifecycle` transitions constraint through states
- [ ] `/ce version` increments constraint version preserving history
- [ ] Circuit breaker trips at severity-appropriate thresholds
- [ ] Workspace files follow documented structure

---

*Consolidated from 7 skills as part of agentic skills consolidation (2026-02-15).*
