---
name: god-mode-manager
description: Manage and secure local high-privilege storage serving workflows. Use when creating, starting, stopping, or hardening a full-drive file server and related operational controls.
---

# God Mode Manager

Use this skill to operate a hardened local storage manager.

## Start Point

1. Confirm target root path and port.
2. Confirm auth token strategy.
3. Run server script in `scripts/`.
4. Validate local-only reachability and auth.

## Default Run Command

```bash
node scripts/server.cjs
```

## Runtime Environment

- `GOD_MODE_ROOT`: root path to expose (default `C:\`).
- `GOD_MODE_HOST`: bind host (default `127.0.0.1`).
- `GOD_MODE_PORT`: bind port (default `8888`).
- `GOD_MODE_TOKEN`: access token.
- `GOD_MODE_TOKEN_REQUIRED`: `true` by default.

## Operational Rules

- Keep server bound to loopback unless explicitly required.
- Require token auth for non-debug usage.
- Refuse path traversal outside configured root.
- Prefer structured JSON listings for automation.

## Files

- `scripts/server.cjs`: server implementation.
- `references/ops.md`: ops notes and runbook.
