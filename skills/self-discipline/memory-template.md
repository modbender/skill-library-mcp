# Memory Template — Self Discipline

## ~/self-discipline/memory.md

```markdown
# Self Discipline Memory

## Status
status: active
version: 1.0.0
last: YYYY-MM-DD
integration: auto | ask-first | critical-only

## Severity Thresholds
auto_validator: critical  # When to auto-create validators
escalate_to_user: medium  # When to involve user in fix
repeat_threshold: 2       # Violations before promotion

## Statistics
total_incidents: 0
critical_incidents: 0
active_rules: 0
validators_created: 0
streak_days: 0            # Days since repeat violation
last_violation: never

## Integration
activation_mode: auto     # auto | on-trigger | manual
validator_creation: ask   # auto | ask | manual
backup_before_edit: true

---
*Updated: YYYY-MM-DD*
```

## ~/self-discipline/rules.md

```markdown
# Active Discipline Rules

**This file is ALWAYS loaded. Rules here are enforced every session.**

<!-- Format for each rule -->
<!--
## [Rule ID] — [Short Name]
severity: critical | medium | low
created: YYYY-MM-DD
incident: [reference to incidents.md]
validator: [path or "none"]

**Rule:** [What must happen / must not happen]

**Origin:** [What went wrong that created this rule]

**Enforcement:**
- [How this is checked]
- [What blocks if violated]
-->

---

## Example: SEC-001 — No Secrets in Messages
severity: critical
created: 2024-02-15
incident: INC-001
validator: validators/pre-send/no-secrets.sh

**Rule:** Never send passwords, tokens, API keys, or URLs containing credentials in messages.

**Origin:** Accidentally sent preview URL with ?pass= parameter to Telegram.

**Enforcement:**
- Pre-send validator checks for secret patterns
- Blocked with explanation if found

---

*Add new rules below. Most recent first.*
```

## ~/self-discipline/incidents.md

```markdown
# Incident Log

<!-- Format for each incident -->
<!--
## INC-XXX | YYYY-MM-DD | [severity]

**What happened:** [Brief description]

**Root cause analysis:**
1. Why? [immediate cause]
2. Why? [underlying cause]
3. Why? [deeper cause]
4. Why? [systemic cause]
5. Why? [root cause]

**Instruction location:** [Where the rule was / should have been]

**Flow analysis:**
- Agent load path: [files loaded]
- Instruction reachable: yes | no
- Fix applied: [what was changed]

**Prevention:**
- Rule created: [rule ID]
- Validator: [path or "none"]
- Verified working: yes | pending

**Status:** resolved | monitoring | recurring
-->

---

*Most recent incidents first.*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `active` | Skill is operational | Full discipline system enabled |
| `paused` | Temporarily disabled | Log incidents but don't analyze |
| `learning` | First week of use | Extra verbose about what it's doing |

## Integration Modes

| Mode | Behavior |
|------|----------|
| `auto` | Activate on any detected mistake |
| `on-trigger` | Only when user seems frustrated |
| `manual` | Only on explicit `/discipline` command |

## Key Principles

- **rules.md is sacred** — ALWAYS loaded, keep it concise
- **incidents.md is detailed** — Full analysis for reference
- **validators/ is code** — Executable checks
- **memory.md is stats** — Preferences and metrics
