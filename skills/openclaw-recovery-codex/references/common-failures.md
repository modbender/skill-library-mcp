# Common OpenClaw Failures & Recovery Patterns

## 1. Gateway ECONNREFUSED
**Symptom**: `openclaw status` shows "unreachable (connect failed: connect ECONNREFUSED)"
**Cause**: Gateway process not running
**Fix**: Start via service manager (schtasks/launchctl/systemctl) or run `openclaw gateway run`

## 2. spawn EPERM (Windows)
**Symptom**: `service.runtime.status: "unknown"`, detail mentions "spawn EPERM"
**Cause**: Multiple Scheduled Tasks competing for same port, or Task To Run path is wrong
**Fix**: Inventory all OpenClaw tasks, delete stale ones, keep exactly 1 Gateway task

## 3. Config BOM (Windows)
**Symptom**: `Config invalid`, JSON parse error, "Unexpected token" at position 0
**Cause**: PowerShell or editors adding UTF-8 BOM to openclaw.json
**Fix**: Remove BOM with node one-liner (see SKILL.md Phase 4)

## 4. Channel Down (Telegram/Discord)
**Symptom**: Channel shows "error" or empty in status
**Cause**: Token expired, network issue, or Gateway just restarted
**Fix**: `openclaw status --deep` for probe details, verify token in config

## 5. Webhook Pipeline Dead
**Symptom**: GitHub [auto] Issues not triggering automation
**Cause**: Webhook relay process (:18790 or custom port) not running, or Tailscale Funnel down
**Fix**: Start webhook relay, verify Tailscale funnel

## 6. Port Conflict
**Symptom**: "port busy" with multiple PIDs, or Gateway fails to bind
**Cause**: Old process still holding port, or duplicate startup
**Fix**: Identify stale PIDs, kill old one, restart correct service

## 7. Heartbeat Config Error
**Symptom**: `Unrecognized key: "enabled"` in config validation
**Cause**: Using `{ "enabled": false }` instead of omitting the key
**Fix**: Remove the heartbeat object entirely from the agent config

## 8. ACL/Permission Issues (Windows)
**Symptom**: CRITICAL in security audit, "writable by others"
**Cause**: Permissions too broad after install or config changes
**Fix**: icacls to restrict (MUST be run by human, not agent)

## 9. fts unavailable
**Symptom**: `[memory] fts unavailable: no such module: fts5`
**Cause**: SQLite binary doesn't include fts5 extension
**Impact**: Full-text search disabled, vector search still works
**Fix**: OpenClaw update may include fixed binary, or rebuild SQLite with fts5

## 10. npm/pnpm Update Fails (EBUSY)
**Symptom**: `EBUSY: resource busy or locked` during openclaw update
**Cause**: Gateway process holds DLL/file locks
**Fix**: Stop Gateway first (human action), then update, then restart
