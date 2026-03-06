---
name: phoenix-loop
description: "Turn agent failures into permanent improvements. Auto-diagnose
  blocked tasks, extract lessons, and wire them into reusable skills.
  Privacy-first: all data stays local."
---


# Phoenix Loop

Rise from failures. Complete tasks persistently.

When the agent encounters blockers, failures, or repeated friction, this skill starts a self-healing loop: Diagnose -> Extract -> Crystallize -> Verify.

## Core Mechanism

### 1. Diagnose

```powershell
# Read recent blocked items
Get-Content memory/blocked-items.md | Select-String "Blocker" -Context 3

# Extract failure patterns
Get-Content memory/tasks.md | Select-String "Status: failed" -Context 5
```

**Diagnosis Checklist**:
- [ ] Is the failure cause clearly stated?
- [ ] Were at least 2 solution paths attempted?
- [ ] Is minimum unblock input defined?

### 2. Extract

Extract reusable patterns from failures:

```markdown
## Failure Pattern: {pattern_name}
- Trigger: {when_this_happens}
- Root Cause: {root_cause}
- Solution: {fix_steps}
- Verification: {verification_criteria}
```

### 3. Crystallize

Write the lesson to a local skill:

```
skills/local/{pattern_name}-recovery.md
```

**Skill Template**:
```markdown
# {Pattern Name} Recovery

## Trigger
When {condition} happens

## Steps
1. {step_1}
2. {step_2}
3. {step_3}

## Verification
- [ ] {check_1}
- [ ] {check_2}

## Fallback
If failed, execute {fallback_action}
```

### 4. Verify

Next time a similar issue occurs:
1. Search `skills/local/` for matching skills
2. Execute recovery steps
3. Log result to `memory/{date}.md`
4. Update skill if needed

## Privacy Security

**All data stored locally**:
- NO external logging of failure data
- NO API keys or tokens in skill files
- NO upload of user task content
- Only pattern names and solution steps recorded
- Skills stored in `skills/local/` local directory

**Sensitive Data Filter**:
Before writing to any memory or skill, check and remove:
- `apiKey`, `token`, `secret`, `password`
- `Bearer `, `sk-`, `OPENCLAW_`
- Personal emails, phones, addresses

## Executable Completion Criteria

A phoenix-loop task is complete if and only if:

| Criteria | Verification Command |
|----------|---------------------|
| Failure pattern named | `Select-String "Failure Pattern" memory/blocked-items.md` |
| Local skill created | `Test-Path skills/local/{name}-recovery.md` |
| Skill has trigger section | `Select-String "## Trigger" skills/local/{name}.md` |
| Skill has verification steps | `Select-String "## Verification" skills/local/{name}.md` |
| Memory updated | `Select-String "phoenix-loop" memory/{today}.md` |
| Privacy check passed | Skill file contains no `apiKey|token|secret` |

## Usage Example

### Scenario: Missing API Key Blocks Task

**1. Diagnose**:
```
Blocker: Missing Brave API key
Attempted: web_search (failed)
Unblock Input: User runs `openclaw configure --section web`
```

**2. Extract Pattern**:
```
Failure Pattern: missing-api-key
Trigger: Tool requires unconfigured API key
Solution: 1. Detect missing key 2. Return config command 3. Provide fallback
```

**3. Crystallize Skill**:
```markdown
# Missing API Key Recovery

## Trigger
When tool returns "missing_*_api_key" error

## Steps
1. Extract required key name
2. Return config command: openclaw configure --section {section}
3. Provide manual fallback option

## Verification
- [ ] User receives clear config instructions
- [ ] At least 1 alternative provided
```

**4. Verify**:
Next time an API key issue occurs, auto-apply this skill.

## Heartbeat Integration

Add to `HEARTBEAT.md`:

```markdown
## Self-Check (Every 24 Hours)
1. Check `memory/blocked-items.md` for blockers older than 24h
2. Run phoenix-loop diagnosis on each long-term blocker
3. If reusable pattern found, create or update skill
```

## Rollback

If the skill causes issues:

```powershell
# Disable skill (rename)
Rename-Item skills/local/{name}-recovery.md skills/local/{name}-recovery.md.disabled

# Delete skill
Remove-Item skills/local/{name}-recovery.md
```

## References

- `memory/blocked-items.md` - Blocker records
- `memory/tasks.md` - Task history
- `skills/local/` - Local skill library

---

Rise stronger from every failure.
