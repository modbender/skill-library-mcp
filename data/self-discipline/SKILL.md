---
name: Self Discipline
slug: self-discipline
version: 1.0.1
homepage: https://clawic.com/skills/self-discipline
description: Guarantee instruction compliance with root cause analysis, flow verification, and automated validators that make future failures impossible.
metadata: {"clawdbot":{"emoji":"⚔️","requires":{"bins":[]},"os":["linux","darwin","win32"],"configPaths":["~/self-discipline/"]}}
changelog: Initial release with severity detection, flow analysis, instruction verification, and validator generation.
---

Instructions written but never followed. Lessons logged but never read. The same mistakes repeated across sessions. This skill breaks that cycle permanently.

When something goes wrong — and the user makes it clear it cannot happen again — this skill doesn't just log it. It traces WHY the failure occurred, verifies the fix will actually be seen by future agents, and generates automated validators that make repetition impossible.

## When to Use

User is frustrated that the agent ignored instructions. Something critical happened that cannot repeat. User explicitly says "this can never happen again" or "I told you not to..." User explicitly invokes `/discipline` to ensure compliance on a rule.

## How It Works

```
         ┌──────────────────────────────────────────────┐
         │              DISCIPLINE TRIGGER              │
         └──────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
    ┌─────────┐         ┌──────────┐         ┌─────────┐
    │  USER   │         │ CRITICAL │         │ COMMAND │
    │  UPSET  │         │ FAILURE  │         │  USED   │
    └────┬────┘         └────┬─────┘         └────┬────┘
         │                   │                    │
         │ "I told you..."   │  Security breach,  │  /discipline
         │ "Why did you..."  │  data loss...      │
         │                   │                    │
         └───────────────────┴────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    SEVERITY     │
                    │  🔴 🟡 🟢       │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  ROOT CAUSE     │
                    │  5 Whys: Why    │
                    │  wasn't it      │
                    │  followed?      │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ FLOW VERIFY     │
                    │ Will next agent │
                    │ see the fix?    │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  VALIDATOR      │
                    │  Script that    │
                    │  blocks action  │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    COMPLETE     │
                    │ Logged+Enforced │
                    └─────────────────┘
```

## Setup

On first use, read `setup.md` for integration guidelines. Creates `~/self-discipline/` for rules, validators, and enforcement logs.

## Architecture

Memory lives in `~/self-discipline/`. See `memory-template.md` for structure.

```
~/self-discipline/
├── memory.md              # Status + severity thresholds + stats
├── rules.md               # Active discipline rules (ALWAYS loaded)
├── incidents.md           # Incident log with root cause analysis
├── validators/            # Executable validators
│   ├── pre-commit/        # Run before git commits
│   ├── pre-send/          # Run before sending messages
│   └── custom/            # Domain-specific validators
├── flow-analysis/         # Instruction flow traces
└── archive/               # Resolved incidents
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Severity assessment | `severity.md` |
| Root cause protocol | `root-cause.md` |
| Flow verification | `flow-verification.md` |
| Validator patterns | `validators.md` |

## Core Rules

### 1. Detect Severity Immediately

When triggered, assess severity FIRST:

| Level | Indicators | Response |
|-------|------------|----------|
| 🔴 CRITICAL | User angry, security risk, data loss, broken prod, financial impact | Full analysis + MANDATORY validator |
| 🟡 MEDIUM | User frustrated, wasted time, incorrect output | Full analysis + instruction fix |
| 🟢 LOW | User annoyed, preference violated | Log + monitor |

**Default to one level higher if uncertain.**

### 2. Root Cause Before Solution

Never jump to "I'll remember that." Instead:

1. **What exactly failed?** — Be specific
2. **What was the instruction?** — Quote it verbatim
3. **Where was the instruction?** — Path + line number
4. **Why wasn't it followed?** — 5 Whys:
   - Why? → Not loaded in context
   - Why? → File not in session's read path
   - Why? → No reference in AGENTS.md / system prompt
   - Why? → Setup assumed it would be read
   - Why? → No verification mechanism

### 3. Verify Flow Reachability (CRITICAL)

After identifying where the instruction SHOULD be, trace the actual agent flow:

```
START: New session begins
  ↓
READ: System prompt loaded
  ↓
READ: AGENTS.md (if exists)
  ↓
READ: MEMORY.md (if referenced)
  ↓
READ: Other files (if referenced)
  ↓
QUESTION: Is the instruction in ANY of these?
```

**If instruction is NOT in the flow:**
- The fix is NOT to "write it somewhere"
- The fix IS to add it to a file ALREADY in the flow
- OR add a reference to its location in a file ALREADY in the flow

### 4. User Consent Required

**NEVER modify files outside ~/self-discipline/ without explicit user permission.**

When suggesting changes to AGENTS.md, HEARTBEAT.md, or other files:

| Action | Requirement |
|--------|-------------|
| Create ~/self-discipline/ | Ask permission first |
| Edit AGENTS.md | Show exact changes, wait for approval |
| Add to HEARTBEAT.md | Show exact changes, wait for approval |
| Create validator script | Show script content, wait for approval |
| Edit any existing file | Backup first + user confirmation |

**Flow for external file changes:**
1. Explain WHY the change is needed
2. Show EXACTLY what will be added/changed
3. Wait for explicit "yes" / approval
4. Only then make the change

### 5. Generate Validators for Critical Issues

For 🔴 CRITICAL issues, create automated validators:

```bash
# Example: ~/self-discipline/validators/pre-send/no-secrets.sh
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: none
# External endpoints called: none
# Local files read: message content (stdin)
# Local files written: none

# Check for secrets before sending messages
if echo "$1" | grep -qE '(password|token|key)='; then
  echo "❌ BLOCKED: Message contains potential secret"
  echo "Rule: no-secrets-in-messages (from incident 2024-02-15)"
  exit 1
fi
```

**Validators must:**
- Exit 0 = pass, exit 1 = block
- Include the rule origin (incident reference)
- Never modify data, only check

### 6. Track Enforcement

In `~/self-discipline/memory.md`, maintain:

| Metric | Purpose |
|--------|---------|
| Active rules | Rules currently being enforced |
| Incidents by severity | Pattern detection |
| Validator triggers | How often rules catch violations |
| Streak | Days since last repeat violation |

### 7. Escalation Path

If the same rule is violated twice:

1. **First violation:** Full analysis + fix
2. **Second violation:** Promote to CRITICAL + mandatory validator
3. **Third violation:** STOP and ask user for intervention

## Severity Assessment Protocol

See `severity.md` for detailed criteria.

### Quick Assessment

| Question | If YES → |
|----------|----------|
| Is the user visibly upset? | +1 severity |
| Could this cause data loss? | Automatic CRITICAL |
| Could this cause security breach? | Automatic CRITICAL |
| Could this affect production? | Automatic CRITICAL |
| Has this happened before? | +1 severity |
| Did user use "never" or "always"? | +1 severity |

## The Flow Verification Process

See `flow-verification.md` for complete protocol.

### Why Instructions Get Ignored

| Cause | Frequency | Solution |
|-------|-----------|----------|
| Written in file not in load path | 60% | Move or add reference |
| Buried in long file, not seen | 20% | Move to top or separate file |
| Contradicted by other instruction | 10% | Resolve conflict explicitly |
| Context window overflow | 5% | Shorten, prioritize |
| Model genuinely forgot | 5% | Add validator |

### Verification Steps

1. **Identify all files in agent's load path** (system prompt, AGENTS.md, etc.)
2. **Check if instruction location is in that path**
3. **If not in path:** Find where to add reference
4. **If in path but buried:** Move to more prominent location
5. **If contradicted:** Resolve with explicit priority

## Validator Patterns

See `validators.md` for complete reference.

### Types

| Type | When Run | Examples |
|------|----------|----------|
| `pre-commit` | Before git commit | No secrets, no WIP |
| `pre-send` | Before message send | No secrets, format checks |
| `pre-action` | Before specific action | Confirm before delete |
| `periodic` | On heartbeat | State verification |

### Validator Template

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: [list]
# External endpoints called: [list or "none"]
# Local files read: [list]
# Local files written: [list or "none"]

# Validator: [rule-name]
# Created: YYYY-MM-DD
# Incident: [reference]
# Severity: CRITICAL

# [description of what this validates]

[validation logic]

if [condition that should fail]; then
  echo "❌ BLOCKED: [reason]"
  echo "Rule: [rule-name] (from incident [date])"
  exit 1
fi

exit 0
```

## Common Traps

| Trap | Consequence | Solution |
|------|-------------|----------|
| Writing rule in memory.md only | Future agent won't see it | Add to rules.md (always loaded) |
| "I'll remember" without verification | Same mistake in 3 sessions | Always verify flow reachability |
| Validator that modifies data | Unexpected side effects | Validators ONLY check, never modify |
| Not backing up before edits | Can't recover if wrong | ALWAYS backup before modifying |
| Skipping severity assessment | Under-responding to critical issues | Assess severity FIRST, always |
| Putting rules in wrong file | Rules not loaded | Only rules.md is guaranteed loaded |

## Commands

| Command | Action |
|---------|--------|
| `/discipline` | Start discipline process for last issue |
| `/discipline status` | Show active rules and stats |
| `/discipline verify [rule]` | Run flow verification for rule |
| `/discipline test [validator]` | Dry-run a validator |
| `/discipline history` | Show incident log |

## Security & Privacy

**Data that stays local:**
- All rules, incidents, and validators in `~/self-discipline/`
- No data sent to external services
- No telemetry or analytics

**This skill does NOT:**
- Make network requests
- Access credentials or secrets
- Modify files without explicit user permission
- Run validators without user approval
- Access files outside `~/self-discipline/` without asking

**File modifications outside ~/self-discipline/:**
- Only suggested when needed for rule visibility (e.g., AGENTS.md reference)
- Always shown to user first
- Require explicit approval before execution
- Include backup before any edit

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `reflection` — structured self-evaluation
- `memory` — persistent memory patterns
- `decide` — decision-making patterns
- `escalate` — know when to ask vs act
- `learning` — adaptive learning system

## Feedback

- If useful: `clawhub star self-discipline`
- Stay updated: `clawhub sync`
