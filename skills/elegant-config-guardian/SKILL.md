---
name: elegant-config-guardian
description: Safely apply OpenClaw config changes with automatic rollback and ack timeout guard. Use when editing ~/.openclaw/openclaw.json, restarting gateway, enabling cross-context routing, or any risky runtime config change that must auto-revert if health checks or explicit ack are missing.
---

# Elegant Config Guardian

Use `scripts/safe_apply.sh` to enforce: backup → apply → restart → health check → optional ack wait → rollback on failure.

## Run

```bash
bash scripts/safe_apply.sh \
  --config ~/.openclaw/openclaw.json \
  --apply-cmd 'python3 /tmp/patch.py' \
  --ack-timeout 60 \
  --require-ack
```

## Ack mode

When `--require-ack` is enabled, the script prints an ack token file path.
A successful manual ack is:

```bash
touch <ack-file-path>
```

If timeout expires without ack, rollback is triggered automatically.

## Defaults

- Health probe command: `openclaw gateway status` and require `RPC probe: ok`
- Restart command: `openclaw gateway restart`
- Backup file: `<config>.bak.YYYYmmdd-HHMMSS`

## Recommended workflow

1. Prepare a deterministic patch command (`--apply-cmd`).
2. Run with `--require-ack --ack-timeout 45` for production changes.
3. Verify health.
4. Ack explicitly only after end-to-end validation.
5. Let timeout auto-rollback if validation cannot complete in time.
