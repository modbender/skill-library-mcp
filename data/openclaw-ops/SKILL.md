---
name: openclaw-ops
version: 1.2.1
description: Use when diagnosing, repairing, or maintaining an OpenClaw Gateway on the same machine. Designed for rescue agents to fix a down gateway or check operational health. Supports Linux (systemd) and macOS (launchd).
repository: https://github.com/dinstein/openclaw-ops-skill
requirements:
  - Shell access on the same machine as the OpenClaw Gateway
  - Read/write access to ~/.openclaw/ (config, agents, sessions)
  - Read access to systemd user service config (Linux) or LaunchAgents (macOS)
  - Node.js 18+ and npm (for openclaw CLI)
  - Optional: Tailscale CLI (for reverse proxy troubleshooting)
security_notes:
  - This skill instructs the agent to read and modify OpenClaw config files
  - The agent will access env files containing tokens (but is instructed never to print them)
  - Config edits are always preceded by timestamped backups
  - Destructive operations require user confirmation
---

# OpenClaw Operations

## Design Philosophy

This skill serves **two core scenarios** and nothing else:

1. **Rescue** — The main OpenClaw Gateway is down or broken. You (the rescue agent) need to diagnose the root cause, fix it, and bring the gateway back online.
2. **Health Check** — The main OpenClaw Gateway is running. You need to verify its operational health, clean up resources, or perform maintenance tasks like upgrades.

**What this skill is NOT for:**
- Day-to-day business configuration (adding channels, configuring agents, setting up integrations)
- Application-level issues (agent behavior, prompt tuning, skill management)
- Initial deployment or first-time setup (use `openclaw daemon install` and `openclaw configure`)

**Principle:** Diagnose → Judge → Act → Verify. Never skip steps.

## Platform Detection

Detect the platform first — commands differ between Linux (systemd) and macOS (launchd):

```bash
OS=$(uname -s)  # "Linux" or "Darwin"
echo "Platform: $OS"
```

## Port Detection

Do NOT assume port 18789. Detect the actual configured port first:

```bash
PORT=$(openclaw config get gateway.port 2>/dev/null | grep -oE '[0-9]+')
PORT=${PORT:-18789}  # fallback to default only if config unavailable
echo "Gateway port: $PORT"
```

Use `$PORT` in all port-related commands throughout this guide.

---

# Scenario A: Rescue (Gateway Down)

Follow these sections in order when the main gateway is not running.

## A1. Assess the Situation

```bash
# Is the service running at all?
# Linux:
systemctl --user status openclaw-gateway
# macOS:
launchctl list | grep openclaw

# Is the process alive?
pgrep -af openclaw

# Is the port listening?
# Linux:
ss -tlnp | grep $PORT
# macOS:
lsof -iTCP:$PORT -sTCP:LISTEN
```

## A2. Check Logs for Root Cause

**Linux:**
```bash
journalctl --user -u openclaw-gateway --since "1 hour ago" --no-pager | grep -iE "error|crash|fatal|SIGTERM|OOM"

# Last 50 lines for context
journalctl --user -u openclaw-gateway -n 50 --no-pager
```

**macOS:**
```bash
LOG_DIR="$HOME/.openclaw/logs"
grep -iE "error|crash|fatal" "$LOG_DIR/gateway.log" | tail -20
tail -50 "$LOG_DIR/gateway.log"

# Also check unified log
log show --predicate 'process == "node"' --last 1h | grep -iE "error|crash|fatal"
```

### Common crash patterns

| Log pattern | Meaning | Fix |
|------------|---------|-----|
| `EADDRINUSE` | Port already in use | Find conflicting process: `ss -tlnp \| grep $PORT` (Linux) or `lsof -iTCP:$PORT` (macOS), kill it or change port |
| `ENOMEM` / `JavaScript heap` | Out of memory | Check `free -h` (Linux) / `vm_stat` (macOS), kill memory hogs or increase Node heap |
| `SyntaxError` in config | Bad JSON in openclaw.json | See A3 Config Repair |
| `MODULE_NOT_FOUND` | Missing dependency | `cd $(npm root -g)/openclaw && npm install --production` |
| `Invalid token` / `401` / `403` | Auth failure | Check tokens in env file or systemd drop-in |
| `ECONNREFUSED` | Upstream unreachable | Check network, Tailscale, API endpoints |

## A3. Config Repair

**Always backup first:**
```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%s)
```

**JSON syntax validation:**
```bash
python3 -c "import json; json.load(open('$HOME/.openclaw/openclaw.json'))"
```

Common JSON issues: trailing comma, missing quotes, unescaped characters. The error message shows line/position.

**Config schema validation:**
```bash
openclaw config get gateway  # check gateway config section
openclaw config get channels  # check channels config section
```

**Common config errors:**

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "device identity mismatch" | Service env token ≠ config token | Sync tokens between env file and openclaw.json |
| Agent not routing | `bindings` misconfigured | Bindings go at top-level, not inside `agents.list[].routing` |

**After fixing, validate:**
```bash
python3 -c "import json; json.load(open('$HOME/.openclaw/openclaw.json')); print('JSON OK')"
openclaw status
```

## A4. Check Resources

```bash
# Disk space
df -h ~

# Memory (Linux)
free -h
# Memory (macOS)
vm_stat | head -5

# Node.js available?
node -v
which openclaw
openclaw --version
```

## A5. Restart and Verify

Only restart **after identifying and fixing the root cause**.

**Linux:**
```bash
systemctl --user restart openclaw-gateway
sleep 3
systemctl --user status openclaw-gateway
journalctl --user -u openclaw-gateway -n 20 --no-pager
```

**macOS:**
```bash
launchctl kickstart -k "gui/$(id -u)/com.openclaw.gateway"
sleep 3
launchctl list | grep openclaw
tail -20 ~/.openclaw/logs/gateway.log
```

**If service won't start at all:**
```bash
# Manual foreground start for better error output
openclaw gateway start
```

**Final verification:**
```bash
openclaw status
openclaw doctor --non-interactive
```

---

# Scenario B: Health Check (Gateway Running)

Follow these sections for routine operational checks on a running gateway.

## B1. Quick Health Check

```bash
# Comprehensive check — start here
openclaw doctor

# If issues found, auto-fix safe ones
openclaw doctor --fix
```

## B2. Update & Upgrade

```bash
# Check versions
CURRENT=$(openclaw --version)
LATEST=$(npm view openclaw version)
echo "Current: $CURRENT  Latest: $LATEST"
```

**Perform update:**
```bash
# 1. Save doctor baseline
openclaw doctor --non-interactive 2>&1 | tee /tmp/doctor-before.txt

# 2. Backup config
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.pre-upgrade.$(date +%s)

# 3. Update
npm update -g openclaw
openclaw --version

# 4. Restart
# Linux:
systemctl --user restart openclaw-gateway
# macOS:
launchctl kickstart -k "gui/$(id -u)/com.openclaw.gateway"

# 5. Compare doctor output
sleep 5
openclaw doctor --non-interactive 2>&1 | tee /tmp/doctor-after.txt
diff /tmp/doctor-before.txt /tmp/doctor-after.txt
```

**Rollback:**
```bash
npm install -g openclaw@<previous_version>
cp ~/.openclaw/openclaw.json.pre-upgrade.<timestamp> ~/.openclaw/openclaw.json
# Restart (platform-appropriate command above)
```

## B3. Session & Disk Cleanup

```bash
# Check disk usage per agent
for agent_dir in ~/.openclaw/agents/*/; do
    agent=$(basename "$agent_dir")
    size=$(du -sh "$agent_dir/sessions/" 2>/dev/null | cut -f1)
    count=$(find "$agent_dir/sessions/" -name "*.jsonl" 2>/dev/null | wc -l)
    echo "$agent: $size ($count transcripts)"
done

# Auto-fix orphans
openclaw doctor --fix

# Manual cleanup: old transcripts (>30 days)
find ~/.openclaw/agents/*/sessions/ -name "*.jsonl" -mtime +30 -exec ls -lh {} \;
# Review, then delete if safe:
find ~/.openclaw/agents/*/sessions/ -name "*.jsonl" -mtime +30 -delete
```

## B4. Backup

```bash
BACKUP_DIR=~/openclaw-backup-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

# Core files
cp ~/.openclaw/openclaw.json "$BACKUP_DIR/"
[ -f ~/.openclaw/env ] && cp ~/.openclaw/env "$BACKUP_DIR/" || echo "No env file (tokens may be in systemd drop-in or plist)"
cp -r ~/.openclaw/agents "$BACKUP_DIR/"
cp -r ~/.openclaw/devices "$BACKUP_DIR/"
cp -r ~/.openclaw/workspace "$BACKUP_DIR/"

# Service config
if [ "$(uname -s)" = "Linux" ]; then
    cp ~/.config/systemd/user/openclaw-gateway.service "$BACKUP_DIR/" 2>/dev/null
    cp -r ~/.config/systemd/user/openclaw-gateway.service.d "$BACKUP_DIR/" 2>/dev/null
elif [ "$(uname -s)" = "Darwin" ]; then
    cp ~/Library/LaunchAgents/com.openclaw.gateway.plist "$BACKUP_DIR/" 2>/dev/null
fi

echo "Backup saved to $BACKUP_DIR"
```

## B5. Tailscale Serve Check

If OpenClaw uses Tailscale Serve as reverse proxy:

```bash
tailscale status
tailscale serve status
curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/healthz || echo "Gateway not reachable on localhost"
```

**Reconfigure if broken:**
```bash
tailscale serve reset
tailscale serve https / http://localhost:$PORT
tailscale serve status
```

---

# Reference

## Troubleshooting Quick Index

| Symptom | Path |
|---------|------|
| Gateway won't start | A1 → A2 → A3 → A5 |
| Gateway crashed | A2 (logs) → A4 (resources) → A3 (config) → A5 (restart) |
| Config broken after edit | A3 → A5 |
| Disk filling up | B3 |
| After upgrade something broke | B2 (rollback) |
| Tailscale not proxying | B5 |

## `openclaw doctor` Reference

| Flag | Effect |
|------|--------|
| (none) | Interactive health check |
| `--fix` | Apply safe repairs (orphan cleanup, stale locks) |
| `--force` | Aggressive repairs (may overwrite custom service config) |
| `--deep` | Scan system for extra gateway installs |
| `--non-interactive` | No prompts, safe migrations only |

**`--fix` repairs:** orphan transcripts, stale session locks, legacy key migration.
**`--fix` does NOT:** modify openclaw.json, change service files (unless `--force`), delete workspace files.

## Key Commands

| Command | Purpose |
|---------|---------|
| `openclaw status` | Quick status: running, version, basic info |
| `openclaw doctor` | Deep health check: state, channels, plugins, skills |
| `openclaw doctor --fix` | Health check + auto-repair safe issues |
| `openclaw gateway start` | Start gateway in foreground (for debugging) |
| `openclaw daemon install` | Install as persistent service (systemd/launchd) |
| `openclaw daemon restart` | Restart the service |
| `openclaw config get <path>` | Read config value |
| `openclaw config set <path> <value>` | Write config value |

## Safety Rules

1. **Always check logs before changing anything** — understand the problem first
2. **Always backup before editing config** — `cp` with timestamp suffix
3. **Always validate JSON after editing** — one bad comma kills the service
4. **Never print secrets** — check env file exists, don't cat it
5. **Never delete workspace files** — use `trash` if you must remove something
6. **Always verify after restart** — status + logs, don't assume it worked
7. **Destructive operations require confirmation** — ask the user before wiping data

## File Layout

```
~/.openclaw/
├── openclaw.json              # Main config
├── openclaw.json.bak          # Auto-backup
├── env                        # Environment variables (secrets)
├── logs/                      # macOS: launchd log output
├── agents/                    # Per-agent configs
│   └── <agent>/agent/
│       ├── auth-profiles.json
│       └── models.json
├── devices/
│   └── paired.json
├── workspace/                 # Agent workspace
└── sessions/                  # Session logs

# Linux:
~/.config/systemd/user/
├── openclaw-gateway.service
└── openclaw-gateway.service.d/
    └── env.conf

# macOS:
~/Library/LaunchAgents/
└── com.openclaw.gateway.plist
```
