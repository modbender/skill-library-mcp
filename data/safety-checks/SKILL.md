---
name: safety-checks
version: 1.5.2
description: Verify before you trust — model pinning, fallbacks, and runtime safety validation
author: Live Neon <contact@liveneon.dev>
homepage: https://github.com/live-neon/skills/tree/main/agentic/safety-checks
repository: leegitw/safety-checks
license: MIT
tags: [agentic, safety, validation, model-pinning, fallback, runtime-verification, cache, guardrails]
layer: safety
status: active
alias: sc
metadata:
  openclaw:
    requires:
      config:
        - .openclaw/safety-checks.yaml
        - .claude/safety-checks.yaml
      workspace:
        - output/safety/
---

# safety-checks (安全)

Unified skill for runtime safety verification including model version pinning,
fallback chain validation, cache staleness detection, and cross-session state checks.
Consolidates 4 granular skills into a single safety verification suite.

**Trigger**: 事前検証 (pre-flight) or HEARTBEAT

**Source skills**: model-pinner, fallback-checker, cache-validator, cross-session-safety-check (from extensions)

## Installation

```bash
openclaw install leegitw/safety-checks
```

**Dependencies**: `leegitw/constraint-engine` (for enforcement integration)

```bash
# Install with dependencies
openclaw install leegitw/context-verifier
openclaw install leegitw/failure-memory
openclaw install leegitw/constraint-engine
openclaw install leegitw/safety-checks
```

**Standalone usage**: Model pinning and cache checks work independently.
Full integration with constraint enforcement requires constraint-engine.

**Data handling**: This skill performs local-only operations. All checks (model version comparison,
cache age verification, file lock detection) are local file/metadata operations — no data is sent
to any model, API, or external service. Results are written to `output/safety/` in your workspace.

## What This Solves

AI systems can silently degrade — model versions drift, caches go stale, sessions accumulate state. This skill catches these issues before they cause problems:

1. **Model pinning** — verify you're using the model you expect
2. **Fallback validation** — ensure degraded-mode paths exist and work
3. **Cache checks** — detect stale or corrupted cached data
4. **Session hygiene** — identify cross-session state contamination

**The insight**: Runtime verification catches what static rules miss. Check the system state, not just the configuration.

## Usage

```
/sc <sub-command> [arguments]
```

## Sub-Commands

| Command | CJK | Logic | Trigger |
|---------|-----|-------|---------|
| `/sc model` | 機種 | model.version→pinned✓∨drift✗ | HEARTBEAT |
| `/sc fallback` | 代替 | chain.exists→safe✓∨missing✗ | HEARTBEAT |
| `/sc cache` | 快取 | response.age>TTL→stale✗ | HEARTBEAT |
| `/sc session` | 会話 | cross_session.state→clean✓∨interference✗ | HEARTBEAT |

## Arguments

### /sc model

| Argument | Required | Description |
|----------|----------|-------------|
| --expected | No | Expected model version (default: from config) |
| --strict | No | Fail on any version mismatch |

### /sc fallback

| Argument | Required | Description |
|----------|----------|-------------|
| --chain | No | Specific fallback chain to check in config |

**Note**: This command validates that fallback configurations exist in your config file.
It does NOT make network calls or test actual connectivity. It's a config file audit.

### /sc cache

| Argument | Required | Description |
|----------|----------|-------------|
| --ttl | No | TTL in seconds (default: 3600) |
| --clear | No | Clear stale cache entries |

### /sc session

| Argument | Required | Description |
|----------|----------|-------------|
| --check-state | No | Check for state leakage between sessions |
| --clear-state | No | Clear any leaked state |

## Configuration

Configuration is loaded from (in order of precedence):
1. `.openclaw/safety-checks.yaml` (OpenClaw standard)
2. `.claude/safety-checks.yaml` (Claude Code compatibility)
3. Defaults (built-in)

## Core Logic

### Model Version Pinning

Ensures AI model version matches expected configuration.

**How it works**: This skill compares the model version reported in your agent's session
metadata (e.g., the model name in API responses or agent headers) against the expected
version in your config file. It does NOT call the model API to check — it reads the
version string that your agent runtime already exposes.

**Model version format**: `{provider}-{model}-{version}-{date}`

Examples:
- `anthropic-opus-4-5-20251101`
- `openai-gpt-4-turbo-20250301`
- `google-gemini-2-pro-20260101`

```yaml
# .openclaw/safety-checks.yaml
model:
  expected: "anthropic-opus-4-5-20251101"  # Provider-neutral format
  strict: true
```

| Condition | Result |
|-----------|--------|
| Version matches | ✓ Pinned |
| Version differs, strict=false | ⚠ Warning |
| Version differs, strict=true | ✗ Fail |

### Fallback Chain Validation

**Config audit only** — verifies fallback entries exist in your config file. This does NOT
make network calls or test actual connectivity.

Checks that your `safety-checks.yaml` declares fallback configurations:

```yaml
# Example config entries this command validates exist:
fallbacks:
  model: ["primary-model", "fallback-model", "cached"]
  storage: ["primary-path", "backup-path"]
```

| Check | What It Validates |
|-------|-------------------|
| Model fallbacks | Config lists alternative models |
| Storage fallbacks | Config lists backup paths |

### Cache Staleness Detection

Prevents use of outdated cached data:

| Age | TTL | Status |
|-----|-----|--------|
| < TTL | Any | ✓ Fresh |
| > TTL | Not critical | ⚠ Stale warning |
| > TTL | Critical | ✗ Stale fail |

### Cross-Session State

Detects state leakage between sessions:

| Check | Exact File Checked | Risk |
|-------|-------------------|------|
| File locks | `.openclaw/safety-checks.lock` | Resource contention |
| Workspace temp files | `output/safety/temp-*` | Disk exhaustion |
| Skill config | `.openclaw/safety-checks.yaml` values | Configuration drift |

**Scope**: Checks are limited to this skill's own files only. This skill does NOT scan
directories, does NOT read other skills' config files, and does NOT access files outside
the specific paths listed above.

## Output

### /sc model output (pinned)

```
[MODEL CHECK]
Status: ✓ PINNED

Expected: anthropic-opus-4-5-20251101
Actual:   anthropic-opus-4-5-20251101

Model version matches configuration.
```

### /sc model output (drift)

```
[MODEL CHECK]
Status: ✗ VERSION DRIFT

Expected: anthropic-opus-4-5-20251101
Actual:   anthropic-opus-4-5-20251201

WARNING: Model version has changed.
This may affect behavior consistency.

Action: Update expected version in settings, or investigate change.
```

### /sc fallback output

```
[FALLBACK CHECK]
Status: ✓ CONFIGURED

Config file: .openclaw/safety-checks.yaml

Fallback entries found:
  ✓ model.fallbacks: 3 entries defined
  ✓ storage.fallbacks: 2 entries defined

Note: This validates config entries exist, not actual connectivity.
  ✓ Tertiary (memory) - 4GB free
```

### /sc cache output

```
[CACHE CHECK]
Status: ⚠ STALE ENTRIES FOUND

Cache Statistics:
  Total entries: 156
  Fresh (< 1h): 142
  Stale (> 1h): 14
  Critical stale: 0

Stale entries:
  - api_response_auth (age: 2h 15m)
  - user_preferences (age: 1h 30m)
  - ...

Action: Run /sc cache --clear to remove stale entries.
```

### /sc session output (clean)

```
[SESSION CHECK]
Status: ✓ CLEAN

No cross-session interference detected.

Checks passed:
  ✓ No stale lock file (.openclaw/safety-checks.lock)
  ✓ No orphan temp files (output/safety/temp-*)
  ✓ Config file valid (.openclaw/safety-checks.yaml)
```

### /sc session output (interference)

```
[SESSION CHECK]
Status: ✗ INTERFERENCE DETECTED

Issues found:

1. Stale file lock:
   File: .openclaw/safety-checks.lock
   Owner: PID 12345 (not running)
   Action: Remove lock with /sc session --clear-state

2. Orphan temp files (3):
   output/safety/temp-*.log
   Age: > 24 hours
   Action: Remove with /sc session --clear-state

Run /sc session --clear-state to remediate.
```

## Integration

- **Layer**: Safety
- **Depends on**: constraint-engine (for enforcement integration)
- **Used by**: constraint-engine (for pre-action safety checks), governance (for health monitoring)

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Invalid sub-command | List available sub-commands |
| Config not found | Use defaults, warn user |
| Network unavailable | Skip remote checks, warn |
| Permission denied | Error with remediation steps |

## Next Steps

After invoking this skill:

| Condition | Action |
|-----------|--------|
| Model drift | Alert user, suggest config update |
| Fallback missing | Alert user, suggest setup |
| Cache stale | Offer to clear, or auto-clear if configured |
| Session interference | Clear state, log incident |

## Workspace Files

This skill reads/writes only within declared paths:

```
.openclaw/
├── safety-checks.yaml     # Primary config (read)
└── cache/
    └── staleness.log      # Cache check history (read/write)

.claude/
└── safety-checks.yaml     # Claude Code config (read)

output/
└── safety/
    ├── model-checks.log   # Model version history (write)
    ├── fallback-tests.log # Fallback test results (write)
    └── session-state.log  # Session state log (write)
```

**Note**: This skill does NOT read `.claude/settings.json` or any other tool's configuration.

## HEARTBEAT Integration

These checks should run periodically via HEARTBEAT:

```markdown
## P1: Critical (Every Session)
- [ ] Model version pinned? → /sc model
- [ ] Session state clean? → /sc session

## P2: Important (Weekly)
- [ ] Fallback chains healthy? → /sc fallback
- [ ] Cache fresh? → /sc cache
```

## Examples

### Model Drift Detection

```
/sc model --strict
[MODEL CHECK]
Status: ⚠ VERSION DRIFT

Expected: anthropic-opus-4-5-20251101
Actual:   anthropic-opus-4-5-20260101

Model version changed. Review CHANGELOG for behavior changes.
```

### Cache Cleanup

```
/sc cache --clear
[CACHE CHECK]
Status: ✓ CLEANED

Removed 14 stale entries from .openclaw/cache/
Freed: 2.3 MB
```

## Security Considerations

**Local-only processing**: All safety checks are local file and metadata operations. No data is
sent to any LLM, API, or external service. The "agent's model" is only used to interpret your
commands — not to process or transmit your data.

**Exact files accessed (read):**
- `.openclaw/safety-checks.yaml` — your skill configuration
- `.claude/safety-checks.yaml` — alternate config location
- `.openclaw/cache/staleness.log` — cache check history (if exists)

**Exact files written:**
- `output/safety/*.log` — check results and history

This skill does NOT scan directories or read other skills' config files.

**What this skill does NOT access:**
- Other skills' configuration files
- System environment variables
- `.claude/settings.json` or other tool configs
- Any files outside the three config paths listed above
- Network resources or external APIs

**What this skill does NOT do:**
- Send data to any model or external service
- Modify files outside `output/safety/`
- Execute arbitrary code

**Data handling:**
- All checks are read-only except for `--clear` operations on its own cache/output
- Results are written to `output/safety/` only
- No data leaves the local machine

**Model version clarification:**
The `/sc model` command compares the expected version in your config against the model
version string reported by your agent runtime (e.g., in session metadata or API headers).
It does NOT make API calls to verify the model — it reads information your agent already has.

**Provenance note:**
This skill is developed by Live Neon (https://github.com/live-neon/skills) and published
to ClawHub under the `leegitw` account. Both refer to the same maintainer.

## Acceptance Criteria

- [ ] `/sc model` verifies model version matches config
- [ ] `/sc model` warns or fails on version drift based on strict setting
- [ ] `/sc fallback` verifies fallback config entries exist in config file
- [ ] `/sc cache` detects entries older than TTL
- [ ] `/sc cache --clear` removes stale entries
- [ ] `/sc session` detects cross-session state leakage
- [ ] `/sc session --clear-state` remediates found issues
- [ ] All checks integrated with HEARTBEAT

---

*Consolidated from 4 skills as part of agentic skills consolidation (2026-02-15).*
