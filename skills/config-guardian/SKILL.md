---
name: config-guardian
description: Safe OpenClaw config updates with automatic backup, validation, and rollback. For agent use - prevents invalid config updates.
---

# Config Guardian

## Overview
**For Agent use only.** Safe config updates with automatic backup, validation, and rollback. Prevents the agent from updating non-existent keys or invalid values.

## When to Use
Use this skill **every time** you need to update `openclaw.json`. Prevents:
- Updating non-existent config keys
- Using invalid values
- Breaking the gateway with bad config

## Workflow: Atomic Apply (Default)

For all config changes - handles everything in one command:

```bash
./scripts/atomic_apply.sh <config_path> <new_value>
# Example: ./scripts/atomic_apply.sh "agents.defaults.model.primary" "minimax-portal/MiniMax-M2.5"
```

**What it does:**
1. Creates timestamped backup automatically
2. Applies change via `openclaw config set <path> <value>`
3. Validates with `openclaw doctor --non-interactive`
4. **Auto-rollback** if validation fails
5. Trap ensures rollback even on crash

**Backup location:**
```
~/.openclaw/config-guardian-backups/
```

## Guardrails
- **Never** restart or apply config without explicit user approval
- **Always** use `atomic_apply.sh`
- If validation fails -> config auto-rolled back, don't force it

## Scripts
| Script | Purpose |
|--------|---------|
| `atomic_apply.sh` | Default - all-in-one safe apply |
| `validate_config.sh` | Validate via OpenClaw doctor |
| `restore_config.sh` | Manual restore from backup |
