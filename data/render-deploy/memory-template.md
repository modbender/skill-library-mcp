# Memory Template - Render Deploy

Create `~/render-deploy/memory.md` with this structure:

```markdown
# Render Deploy Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
<!-- Preferred deployment method and Render workspace scope -->
<!-- Git provider, branch conventions, and rollout expectations -->

## Deployment Preferences
<!-- Blueprint vs Direct Creation defaults -->
<!-- Preferred validation depth and handoff style -->

## Environment Inventory
<!-- Required env var names, ownership, and source (dashboard, generated, db reference) -->

## Notes
<!-- Durable observations only -->

---
*Updated: YYYY-MM-DD*
```

## deployment-notes.md Template

Create `~/render-deploy/deployment-notes.md`:

```markdown
# Deployment Notes

## YYYY-MM-DD - Project
Method: blueprint | direct-creation | dashboard-image
Workspace: ...
Repo: ...
Services: ...
Datastores: ...
Result: success | blocked | failed
Summary: ...
```

## env-inventory.md Template

Create `~/render-deploy/env-inventory.md`:

```markdown
# Environment Inventory

| Variable | Scope | Source | Secret | Last Checked |
|----------|-------|--------|--------|--------------|
| DATABASE_URL | web | fromDatabase | no | YYYY-MM-DD |
| JWT_SECRET | web | dashboard | yes | YYYY-MM-DD |
```

## incident-log.md Template

Create `~/render-deploy/incident-log.md`:

```markdown
# Incident Log

## INC-001
Date: YYYY-MM-DD
Failure class: build | startup | health | runtime
Signature: ...
Root cause: ...
Fix: ...
Verification: pending | passed | failed
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Default mode | Keep learning deploy constraints over time |
| `complete` | Stable context | Reuse known method/workspace defaults |
| `paused` | User wants fewer prompts | Apply known defaults with minimal setup questions |
| `never_ask` | User rejected setup prompts | Stop integration prompts and run only on explicit requests |
