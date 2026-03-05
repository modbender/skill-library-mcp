---
name: memory-self-heal
version: 1.1.0
description: General-purpose self-healing loop that learns from past failures, retries safely, and records reusable fixes.
metadata:
  openclaw:
    emoji: "[HEAL]"
    category: resilience
---

# Memory Self-Heal Skill

Use this skill when the agent starts failing repeatedly, stalls, or keeps asking the user for steps that could be inferred from prior evidence.

## Goals

1. Recover execution without user micromanagement
2. Reuse previous fixes from memory/logs/tasks
3. Escalate only with minimal unblock input when truly blocked
4. Leave reusable evidence for future runs

## When To Trigger

Trigger when any of these appear:
- Same or similar error occurs 2+ times in one task
- Tool call fails due to argument mismatch, missing config, auth wall, or context overflow
- Agent claims completion without verifiable artifact
- Task progress stalls (no new artifact across 2 cycles)

## Inputs

- Current task objective
- Latest error/output
- Available evidence locations (memory, tasks, logs)

## Portable Evidence Scan Order

Scan these in order; skip missing paths silently:
1. `memory/` (or equivalent workspace memory path)
2. `tasks/` or queue files
3. runtime logs / channel logs
4. skill docs (`skills/*/SKILL.md`) for known fallback recipes
5. core docs (`TOOLS.md`, `CAPABILITIES.md`, `AGENTS.md`)

Shell examples (use whichever shell is active):

```powershell
# PowerShell
Get-ChildItem -Recurse memory, tasks -ErrorAction SilentlyContinue |
  Select-String -Pattern "error|blocked|retry|fallback|auth|token|proxy|timeout|context" -Context 2
```

```bash
# POSIX shell
rg -n "error|blocked|retry|fallback|auth|token|proxy|timeout|context" memory tasks 2>/dev/null
```

## Failure Classification

Classify first, then act:
- `syntax_or_args`: command syntax/argument mismatch
- `auth_or_config`: key/token/env/config missing or invalid
- `network_or_reachability`: timeout, DNS, handshake, region restrictions
- `ui_login_wall`: page requires manual login/attach
- `resource_limit`: context window, rate limit, memory pressure
- `false_done`: no artifact/evidence but reported complete
- `unknown`: no confident class

## Recovery Policy (3-Tier)

### Attempt 1: Direct Fix
- Apply best-known fix from memory for same class/signature
- Re-run the smallest validating action
- Record result

### Attempt 2: Safe Fallback
- Switch to alternate tool/path with lower fragility
- Narrow scope (smaller input, shorter query, one target)
- Re-run validation

### Attempt 3: Controlled Escalation
- Mark blocked with minimum unblock input
- Provide exact next action user must do (one command or one UI step)
- Do not loop further until new input arrives

## Safety Rules

- Never auto-run destructive operations without confirmation
- Never log secrets/tokens in memory files
- Max 3 retries per blocker signature per task
- Prefer deterministic steps over broad speculative retries

## Completion Contract

Do not claim done unless all are true:
- At least one artifact exists and is readable (file/link/output)
- The original task objective is explicitly mapped to artifact(s)
- No unresolved blocker for current objective

Required output block:

```markdown
DONE_CHECKLIST
- Objective met: yes/no
- Artifact: <path or URL or command output ref>
- Validation: <what was checked>
- Remaining blocker: <none or exact unblock input>
```

## Memory Writeback Template

Append one concise entry after each self-heal cycle:

```markdown
## Self-heal: <date-time> <short task>
- Signature: <normalized error signature>
- Class: <classification>
- Attempt1: <action> -> <result>
- Attempt2: <action> -> <result>
- Final: <success | blocked>
- Artifact/Evidence: <path|url|log ref>
- Reusable rule: <one-line rule>
```

## Generic Known Fixes (Seed Set)

- Command mismatch on Windows: prefer native PowerShell cmdlets
- Token mismatch/auth failure: verify active config source and token scope
- WebSocket/timeouts: test reachability + proxy/no_proxy consistency
- Context overflow: split task into smaller units and reduce payload
- False completion: enforce artifact validation before final response

## Integration Notes

- Works with autonomy/task-tracker skills but does not depend on them
- If a project has custom memory paths, adapt scan roots dynamically
- Keep entries short to avoid memory bloat
