# Skill Safe Install (L0)

A strict L0-grade secure installation workflow for OpenClaw skills.

## What it solves
When users say **"install skill"**, the agent must not do direct install only.
It must run a full 6-step process:

1. Duplicate check
2. Search
3. Security review (`clawhub inspect`)
4. Sandbox install (isolated workdir)
5. Formal install
6. Whitelist update (with explicit user authorization)

## Why this matters
- Prevents blind installs
- Provides auditable risk checks
- Enforces explicit authorization before JSON config edits

## Core command pattern
```bash
TMP=$(mktemp -d)
clawhub --workdir "$TMP" --dir skills install <slug>
```

## Version
- v2.1.0: L0 trigger hardening, sandbox fallback clarified, output template standardized.
