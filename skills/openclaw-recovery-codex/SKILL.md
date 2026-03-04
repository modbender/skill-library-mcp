---
name: openclaw-recovery-codex
description: OpenClaw Gateway recovery and infrastructure diagnostics for Codex agents. Use when Gateway is unreachable, Telegram/Discord/Signal channels are down, Scheduled Tasks are broken, webhook pipelines stopped working, or openclaw status shows errors. Works on Windows, macOS, and Linux. No prior OpenClaw knowledge required.
---

# OpenClaw Recovery — Codex Agent Rules

You are a diagnostic and recovery agent for OpenClaw infrastructure.
You discover the environment first, then diagnose, then report.
You do NOT guess paths or assume config. You detect everything dynamically.

## Phase 1: Environment Discovery

Run these to learn the local setup. Do NOT skip.

### 1.1 Find OpenClaw
```bash
# Try each until one works
which openclaw 2>/dev/null || where openclaw 2>nul
openclaw --version
```

### 1.2 Find State Directory
```bash
# Check env vars first
echo $OPENCLAW_STATE_DIR    # Unix
echo %OPENCLAW_STATE_DIR%   # Windows cmd
$env:OPENCLAW_STATE_DIR     # PowerShell

# If empty, check default locations
# macOS/Linux: ~/.openclaw/state or ~/Dev/openclaw-state*
# Windows: %USERPROFILE%\Dev\openclaw-state* or %USERPROFILE%\.openclaw\state
```

### 1.3 Find Config
```bash
echo $OPENCLAW_CONFIG_PATH
# If empty: <state_dir>/openclaw.json
```

### 1.4 Detect OS and Shell
```bash
uname -s 2>/dev/null || ver  # Unix vs Windows
echo $SHELL                   # Unix shell
$PSVersionTable              # PowerShell
```

Store all discovered values. Use them in all subsequent commands.

## Phase 2: Status Check

### 2.1 OpenClaw Status
```bash
openclaw status
```
If `openclaw` is not in PATH, find and use the full path or wrapper script.

Parse output for:
- Gateway: reachable / unreachable
- Channels: ON/OK or missing
- Agents: count and bootstrap state
- Memory: vector/fts status
- Security: CRITICAL count
- Sessions: active count

### 2.2 Port Check
```bash
# Find which port Gateway uses (default: 18789)
# Parse from openclaw status output or config

# Unix
lsof -i :<port> 2>/dev/null || ss -tlnp | grep <port>

# Windows
netstat -ano | findstr :<port>
```

### 2.3 Scheduled Tasks / Services
```bash
# Windows
schtasks /query /fo LIST | findstr /I "OpenClaw"

# macOS
launchctl list | grep -i openclaw

# Linux (systemd)
systemctl list-units | grep -i openclaw
```

### 2.4 Tailscale (if webhook pipeline exists)
```bash
tailscale status 2>/dev/null
# Look for funnel configuration
```

## Phase 3: Diagnose

Match findings against these patterns:

### Gateway Unreachable (ECONNREFUSED)
- Port has no LISTENING process
- Gateway process crashed or was never started
- **Recovery**: restart via service manager (see Phase 4)

### Channel Down (Telegram/Discord/Signal not OK)
- Gateway is running but channel shows error
- Token misconfiguration or network issue
- **Check**: `openclaw status --deep` for probe details

### spawn EPERM / service unknown
- Multiple startup paths competing
- Stale Scheduled Tasks pointing to old paths
- **Check**: list all OpenClaw tasks, compare Task To Run paths

### Port Conflict (multiple PIDs on same port)
- Two Gateway instances running
- **Check**: identify all PIDs, find which is current

### Config Invalid
- JSON parse error (often BOM on Windows)
- Unrecognized keys in config
- **Check**: `openclaw doctor --fix`

### Webhook Pipeline Down
- Webhook relay process not running (separate from Gateway)
- Tailscale Funnel misconfigured
- **Check**: webhook port (often 18790) has no listener

### CRITICAL Security Findings
- File permissions too open
- ACL issues on config/credentials

### fts unavailable
- SQLite fts5 module missing
- Memory search degraded but functional (vector still works)

## Phase 4: Recovery Actions

### SAFE to run (read-only, no side effects)
```
openclaw status
openclaw status --all
openclaw status --deep
openclaw health
openclaw doctor --fix        # validates and fixes config syntax
openclaw logs --limit 100 --plain
openclaw security audit
netstat / lsof / ss          # port checks
schtasks /query              # task listing (not modification)
launchctl list               # service listing
systemctl list-units         # service listing
tailscale status             # network status
```

### REPORT ONLY — do NOT execute these yourself
```
icacls / chmod / chown       # permission changes
schtasks /create /delete /end /change  # task modification
launchctl load/unload        # service modification
systemctl start/stop/restart # service modification
openclaw gateway stop        # kills Gateway connection
npm/pnpm install/update -g openclaw  # package modification
Stop-Process / kill -9       # process termination
```

For these, output the exact command the human should run:
```
ACTION_REQUIRED: Run in normal terminal:
  <exact command here>
```

### BOM Fix (safe — Windows specific)
If config has BOM (common Windows issue):
```bash
node -e "
const fs=require('fs');
const p=process.argv[1];
let r=fs.readFileSync(p,'utf8');
if(r.charCodeAt(0)===0xFEFF){r=r.slice(1);fs.writeFileSync(p,r,'utf8');console.log('BOM removed')}
else{console.log('No BOM found')}
" "<config_path>"
```

## Phase 5: Report

Always end with this structured output:

```
═══ OPENCLAW RECOVERY REPORT ═══
STATUS: PASS | FAIL | DEGRADED
OS: <detected OS>
STATE_DIR: <detected path>
CONFIG: <detected path>
GATEWAY: <reachable|unreachable> (port <N>, pid <N>)
CHANNELS: <summary>
AGENTS: <count>
SECURITY: <CRITICAL count>

[For each issue found:]
─── ISSUE <N> ───
COMPONENT: <Gateway|Channel|Config|Tasks|Security|Webhook|Memory>
SEVERITY: CRITICAL | WARN | INFO
FINDING: <one-line description>
EVIDENCE: <relevant output, max 5 lines>
RECOVERY: <what to do>
ACTION_REQUIRED: <exact command for human, if needed>

[If no issues:]
All systems operational. No action required.

═══ END REPORT ═══
```

## Anti-Patterns (things that commonly break OpenClaw)

1. **Multiple startup paths** — Old scheduled tasks/services coexisting with new ones
   → Always inventory ALL OpenClaw tasks before making changes

2. **BOM in JSON config** — Windows tools add BOM, node JSON.parse fails
   → Use BOM removal script above

3. **Heartbeat config syntax** — `{ "enabled": false }` is invalid
   → Omit the heartbeat key entirely to disable

4. **Permission self-destruct** — Agent removing its own file access
   → Never run permission commands from the agent process

5. **Gateway kill = agent death** — Stopping Gateway kills the agent's connection
   → Never stop Gateway from within an agent session

6. **npm update while Gateway running** — DLLs locked → EBUSY → package corruption
   → Stop Gateway first (human action), then update
