# Memory Template - Security Best Practices

Create `~/security-best-practices/memory.md` with this structure:

```markdown
# Security Best Practices Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
<!-- Threat model and business constraints -->
<!-- Critical systems and data sensitivity notes -->

## Review Preferences
<!-- Preferred severity threshold and report depth -->
<!-- Preferred remediation style (minimal diff vs broader refactor) -->

## Exceptions
<!-- Accepted risk items and review deadlines -->

## Notes
<!-- Stable observations only -->

---
*Updated: YYYY-MM-DD*
```

## findings-log.md Template

Create `~/security-best-practices/findings-log.md`:

```markdown
# Findings Log

## YYYY-MM-DD - [Scope]
Finding ID: SEC-001
Severity: Critical | High | Medium | Low
Location: path/to/file:line
Status: open | accepted-risk | fixed | verified
Summary: ...
Impact: ...
Fix plan: ...
Verification: pending | passed | failed
```

## exceptions.md Template

Create `~/security-best-practices/exceptions.md`:

```markdown
# Security Exceptions

## EXC-001
Scope: service/module
Risk accepted: ...
Reason: ...
Owner: ...
Approved on: YYYY-MM-DD
Review by: YYYY-MM-DD
Compensating controls: ...
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Default mode | Keep learning project-specific constraints |
| `complete` | Stable context | Reuse preferences with minimal prompts |
| `paused` | User wants fewer prompts | Keep applying known rules, no setup prompts |
| `never_ask` | User rejected integration prompts | Stop integration prompts and run on explicit requests |
