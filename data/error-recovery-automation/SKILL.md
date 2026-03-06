---
name: error-recovery-automation
description: "Standardize handling of common OpenClaw errors (gateway restart, browser service unavailable, cron failures) with automated recovery steps. Use when you need to automate detection and recovery from known failure modes, reducing manual intervention and increasing system resilience."
---

# Error Recovery Automation Skill

This skill provides patterns for automating the detection and recovery of common OpenClaw errors: gateway unresponsiveness, browser service failures, cron scheduler issues, and other recurring problems. It builds on health‑monitoring and system‑diagnostics by adding **automated recovery workflows** that can be triggered by cron jobs, heartbeat checks, or external monitoring.

## When to use

- A service (gateway, browser, cron) fails intermittently and you want to automate its restart.
- You are setting up proactive monitoring and need a recovery plan beyond just detection.
- You want to reduce the manual steps required when “Läuft alles?” reveals a failure.
- You need to ensure critical OpenClaw components stay running with minimal user intervention.
- You are asked to “create a skill for error recovery automation” (this is that skill).

## Core patterns

### 1. Error Detection Patterns

Before automating recovery, you must reliably detect the error. Use these detection methods:

**Gateway unresponsive:**
- `openclaw gateway status` returns non‑zero exit code or shows `"running": false`.
- Gateway logs (`~/.openclaw/logs/gateway.err.log`) contain recent `CRITICAL` or `ERROR` entries.
- HTTP health endpoint (if configured) returns non‑2xx status.

**Browser service unavailable:**
- `openclaw browser --browser-profile openclaw status --json` shows `"running": false` or CDP not ready.
- Browser logs contain connection timeouts or Chrome process failures.
- Simple page load via `curl` to CDP endpoint fails.

**Cron scheduler not running:**
- `openclaw cron status` returns `"running": false` or error.
- Cron logs show no recent activity.
- Scheduled jobs are not triggered (check `openclaw cron list` for missed runs).

**Memory search disabled:**
- `memory_search` tool returns “disabled” or native‑module error.
- `openclaw doctor --fix` reports better‑sqlite3 mismatch.

**Permission errors:**
- File operations fail with `EACCES`/`EPERM`.
- Logs indicate permission denied on specific paths (archive, logs, config).

### 2. Automated Recovery Steps

For each error type, define a recovery script that attempts to restore service automatically. The script should:

1. **Detect** the error (using the patterns above).
2. **Attempt recovery** (restart service, fix permissions, rebuild module).
3. **Verify** recovery (re‑run detection after a short wait).
4. **Report outcome** (exit code 0 for success, non‑zero for persistent failure).

#### Gateway Recovery Script Template

```bash
#!/bin/bash
set -e

SERVICE="gateway"
MAX_ATTEMPTS=2
SLEEP_SECONDS=5

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

check() {
  openclaw gateway status > /dev/null 2>&1
}

restart() {
  openclaw gateway restart
  sleep "$SLEEP_SECONDS"
}

attempt=0
while [ $attempt -lt $MAX_ATTEMPTS ]; do
  if check; then
    log "$SERVICE is healthy"
    exit 0
  fi
  log "$SERVICE is unhealthy, restarting (attempt $((attempt+1))/$MAX_ATTEMPTS)..."
  restart
  ((attempt++))
done

log "$SERVICE could not be recovered after $MAX_ATTEMPTS attempts"
exit 1
```

#### Browser Service Recovery Script Template

```bash
#!/bin/bash
set -e

SERVICE="browser"
PROFILE="openclaw"
MAX_ATTEMPTS=2
SLEEP_SECONDS=8

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

check() {
  openclaw browser --browser-profile "$PROFILE" status --json 2>&1 | grep -q '"running":true'
}

restart() {
  openclaw browser --browser-profile "$PROFILE" stop
  sleep 2
  openclaw browser --browser-profile "$PROFILE" start
  sleep "$SLEEP_SECONDS"
}

attempt=0
while [ $attempt -lt $MAX_ATTEMPTS ]; do
  if check; then
    log "$SERVICE ($PROFILE) is healthy"
    exit 0
  fi
  log "$SERVICE ($PROFILE) is unhealthy, restarting (attempt $((attempt+1))/$MAX_ATTEMPTS)..."
  restart
  ((attempt++))
done

log "$SERVICE ($PROFILE) could not be recovered after $MAX_ATTEMPTS attempts"
exit 1
```

#### Cron Scheduler Recovery Script Template

```bash
#!/bin/bash
set -e

SERVICE="cron"
MAX_ATTEMPTS=1
SLEEP_SECONDS=3

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

check() {
  openclaw cron status 2>&1 | grep -q '"running":true'
}

restart() {
  # Cron is restarted automatically when gateway restarts.
  # If cron is not running, restart gateway.
  openclaw gateway restart
  sleep "$SLEEP_SECONDS"
}

attempt=0
while [ $attempt -lt $MAX_ATTEMPTS ]; do
  if check; then
    log "$SERVICE scheduler is running"
    exit 0
  fi
  log "$SERVICE scheduler is not running, restarting gateway (attempt $((attempt+1))/$MAX_ATTEMPTS)..."
  restart
  ((attempt++))
done

log "$SERVICE scheduler still not running after $MAX_ATTEMPTS attempts"
exit 1
```

#### Memory Search Recovery Script Template

```bash
#!/bin/bash
set -e

SERVICE="memory_search"
MAX_ATTEMPTS=1

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

check() {
  openclaw memory search --query "test" 2>&1 | grep -q -v "disabled\|Module did not self-register"
}

restart() {
  # Try rebuilding better‑sqlite3
  cd "$(dirname "$(which openclaw)")/../lib/node_modules/openclaw"
  npm rebuild better-sqlite3
  # Restart gateway to pick up the rebuilt module
  openclaw gateway restart
  sleep 5
}

attempt=0
while [ $attempt -lt $MAX_ATTEMPTS ]; do
  if check; then
    log "$SERVICE is functional"
    exit 0
  fi
  log "$SERVICE is disabled, rebuilding native module (attempt $((attempt+1))/$MAX_ATTEMPTS)..."
  restart
  ((attempt++))
done

log "$SERVICE could not be recovered after $MAX_ATTEMPTS attempts"
exit 1
```

### 3. Integration with Cron for Automated Recovery

Once you have a recovery script, schedule it as a cron job that runs **only when the service is likely to fail** (e.g., every 30 minutes for browser, every hour for gateway). Use an isolated agent session to execute the script and announce failures.

**Example cron job for browser recovery:**

```bash
openclaw cron add \
  --name "Browser‑Recovery‑Automation" \
  --schedule 'every 30 minutes' \
  --session isolated \
  --payload '{"kind":"agentTurn","message":"Run browser recovery automation script","model":"default","thinking":"low"}' \
  --delivery '{"mode":"announce","channel":"telegram"}'
```

**Agent response inside isolated session:** The agent reads the script (or inline logic) and executes it via `exec`. If the script exits with 0, the agent announces success; if non‑zero, the cron delivery forwards the failure message.

**Alternative:** You can embed the recovery logic directly in the agent’s response (without a separate script) for simplicity, but a script is easier to test and reuse.

### 4. Escalation When Automation Fails

If automated recovery fails after the maximum attempts, escalate:

- **Log the failure** in `memory/YYYY‑MM‑DD.md` with tag `error‑recovery‑failed`.
- **Add a task** to `inbox/agent‑aufgaben.md` for manual diagnosis.
- **Send a high‑priority notification** (if supported) to the user.
- **Fallback to a safe state** (e.g., disable the problematic component if possible).

Example escalation snippet:

```bash
if [ $? -ne 0 ]; then
  echo "Browser recovery failed. Adding manual diagnosis task."
  # Append to agent-aufgaben.md
  echo "| 99 | Diagnose browser recovery failure – automated recovery failed after 2 attempts | ⬜ |" >> inbox/agent-aufgaben.md
  # Store in memory
  echo "## [error] Browser recovery automation failed" >> memory/$(date +%Y-%m-%d).md
  echo "Date: $(date +%Y-%m-%d)" >> memory/$(date +%Y-%m-%d).md
  echo "Tags: error, browser, recovery-failed" >> memory/$(date +%Y-%m-%d).md
  echo "Browser recovery script exited with code $?. Manual intervention required." >> memory/$(date +%Y-%m-%d).md
fi
```

### 5. Testing Recovery Scripts

Before deploying a recovery script as a cron job, test it manually:

1. **Simulate the failure** (e.g., kill the gateway process, stop the browser service).
2. **Run the recovery script** and verify it detects the failure and restarts the service.
3. **Check that the service is functional** after recovery.
4. **Verify logs** for any unintended side effects.

**Example test command:**

```bash
# Stop browser service
openclaw browser --browser-profile openclaw stop

# Run recovery script
./scripts/browser-recovery.sh

# Verify browser is running
openclaw browser --browser-profile openclaw status --json | grep '"running":true'
```

## Examples

### Example 1: Gateway Recovery Automation

Script: `scripts/gateway-recovery.sh` (see template above). Cron schedule: every 1 hour. Announce only on failure.

### Example 2: Browser Recovery Automation

Script: `scripts/browser-recovery.sh` (see template above). Cron schedule: every 30 minutes. Announce only on failure.

### Example 3: Combined Health‑Check + Recovery

A single script that checks multiple services and recovers any that are unhealthy. Useful for a comprehensive “keep‑alive” cron job.

```bash
#!/bin/bash
set -e

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

# Check gateway
if ! openclaw gateway status > /dev/null 2>&1; then
  log "Gateway unhealthy, restarting..."
  openclaw gateway restart
  sleep 5
fi

# Check browser
if ! openclaw browser --browser-profile openclaw status --json 2>&1 | grep -q '"running":true'; then
  log "Browser unhealthy, restarting..."
  openclaw browser --browser-profile openclaw stop
  sleep 2
  openclaw browser --browser-profile openclaw start
  sleep 8
fi

log "All services healthy"
exit 0
```

Schedule this script every 30 minutes with an isolated agentTurn job.

## Anti‑Patterns

- **Over‑aggressive recovery:** Restarting a service too frequently can cause instability. Set reasonable intervals (≥30 minutes) and maximum attempts (≤2).
- **Silent recovery:** If recovery succeeds but you never hear about it, you might not know the service was failing. At minimum, log recovery events to memory/ files.
- **No verification:** Restarting a service without verifying it actually recovered can mask deeper issues. Always re‑check after restart.
- **Hard‑coded assumptions:** Avoid assuming a specific Node version, path, or user ID. Use environment variables or detect them at runtime.
- **Ignoring dependencies:** Browser depends on gateway; restarting browser while gateway is down will fail. Check dependencies in order.
- **Automating unsafe actions:** Do not automate deletion of logs, modification of critical configs, or any irreversible action without a rollback plan.

## Related Patterns

- **Health‑Monitoring skill** – proactive health checks and monitoring.
- **System‑Diagnostics skill** – diagnosing root causes of failures.
- **Cron‑Job Creation playbook** – creating scheduled jobs.
- **Gateway Health Check and Recovery playbook** – specific to gateway.
- **Browser Service Health Monitoring and Recovery playbook** – specific to browser.
- **Maintenance Execution playbook** – incorporating recovery into regular maintenance.

## References

- `scripts/gateway-recovery.sh` (template)
- `scripts/browser-recovery.sh` (template)
- `scripts/cron-recovery.sh` (template)
- `skills/health-monitoring/SKILL.md`
- `skills/system-diagnostics/SKILL.md`
- `docs/MAINTENANCE.md`
- `memory/patterns/playbooks.md`
- `openclaw cron --help`
- `openclaw gateway --help`
- `openclaw browser --help`

## Skill Integration

When an OpenClaw error occurs (gateway, browser, cron, memory search), read this skill to create or run an automated recovery script. Store successful recovery patterns in `memory/patterns/tools.md`. Update `pending.md` if automation fails and manual intervention is needed.

This skill increases autonomy by providing standardized, automated recovery workflows for common failures, reducing the need for manual intervention and increasing system resilience.