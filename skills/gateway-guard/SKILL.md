---
name: gateway-guard
displayName: Gateway Guard
description: Ensures OpenClaw gateway auth consistency and can auto-prompt "continue" when a run error (Unhandled stop reason: error) appears in gateway logs. Use when checking or fixing gateway token/password mismatch, device_token_mismatch errors, or before delegating to sub-agents.
---

# Gateway Guard

## Description

Ensures OpenClaw gateway auth consistency and can auto-prompt "continue" when a run error (Unhandled stop reason: error) appears in gateway logs. Use when checking or fixing gateway token/password mismatch, device_token_mismatch errors, or before delegating to sub-agents.

Ensures OpenClaw gateway auth consistency and can auto-prompt "continue" when a run error (Unhandled stop reason: error) appears in gateway logs. Use when checking or fixing gateway token/password mismatch, device_token_mismatch errors, or before delegating to sub-agents.

# Gateway Guard

Keeps OpenClaw gateway authentication in sync with `openclaw.json`. Use when the user or agent sees gateway auth issues, `device_token_mismatch`, or needs to ensure the gateway is running with the correct token/password before spawning sub-agents.

**Metadata:** This skill uses `always: false` in `_meta.json`. It is **not** forced into every agent run; the orchestrator invokes it when needed (e.g. before delegating to sub-agents). Optional persistence (LaunchAgent) is installed only when you run the install scripts; see "Before installing" below.


## Before installing

- **Backup `openclaw.json`** — The script may add or correct `gateway.auth` (token/password) when missing or wrong. Make a copy before running `ensure --apply`.
- **Test read-only first** — Run `python3 scripts/gateway_guard.py status --json` and `python3 scripts/gateway_guard.py ensure --json` (without `--apply`) to see what it would do before allowing restarts or config writes.
- **Understand `continue` delivery** — The watcher can run `openclaw agent --message continue --deliver` when a run error appears in `gateway.log`. Confirm that automatically sending that message is acceptable in your environment.
- **LaunchAgent is optional** — Persistence (watcher every 30s) is installed only if you run `install_watcher.sh`. The installer copies the plist from the skill directory into `~/Library/LaunchAgents` and runs `launchctl load`; only run it if you accept that. The plist **is included** in this package: `scripts/com.openclaw.gateway-guard.watcher.plist` (and `scripts/com.openclaw.gateway-guard.continue-on-error.plist`). Ensure `OPENCLAW_HOME` and `OPENCLAW_BIN` resolve to your intended paths before installing the watcher.
- **Try in a non-production environment first** if you are unsure.


## Package contents (file manifest)

Included in this skill so installers do not error:

- `scripts/gateway_guard.py` — Main script (status, ensure, continue-on-error, watch).
- `scripts/install_watcher.sh` — Installs the single combined LaunchAgent (token sync + continue-on-error).
- `scripts/install_continue_on_error.sh` — Redirects to `install_watcher.sh`.
- `scripts/com.openclaw.gateway-guard.watcher.plist` — LaunchAgent plist template (install_watcher.sh copies and substitutes paths).
- `scripts/com.openclaw.gateway-guard.continue-on-error.plist` — Legacy plist (optional; install_watcher.sh replaces with the combined watcher).


## Usage

- User or logs report "Gateway auth issue", "device_token_mismatch", or "unauthorized"
- Before running the router and `sessions_spawn` (orchestrator flow): check gateway status first
- After installing or updating OpenClaw: verify gateway and config match
- When the TUI disconnects or won't connect: fix auth and restart gateway
- **Run error (Unhandled stop reason: error):** run `continue-on-error --loop` (e.g. via LaunchAgent or cron) so the guard auto-sends "continue" to the agent when this appears in `gateway.log`

```bash
python3 <skill-dir>/scripts/gateway_guard.py status [--json]
python3 <skill-dir>/scripts/gateway_guard.py ensure [--apply] [--wait] [--json]
python3 <skill-dir>/scripts/ensure_gateway_then.sh [command ...]
python3 <skill-dir>/scripts/gateway_guard.py continue-on-error [--once] [--loop] [--interval 30] [--json]
```

- **status** — Report whether the running gateway's auth matches `openclaw.json`. Exit 0 if ok, 1 if mismatch.
- **ensure** — Same check; if mismatch and `--apply`, restart the gateway with credentials from config. Writes `gateway.auth` to `openclaw.json` **only when it is missing or wrong** (never overwrites correct config). Use **`--wait`** after `--apply` to block until the gateway port is open (up to 30s), so clients can connect immediately after.
- **ensure_gateway_then.sh** — Detect and connect automatically: ensures the gateway is running (starts it if needed, waits for port), then runs your command. Example: `ensure_gateway_then.sh openclaw tui` or `ensure_gateway_then.sh` (just ensure and wait).
- **continue-on-error** — When `gateway.log` contains **Unhandled stop reason: error** (run error), send **continue** to the agent via `openclaw agent --message continue --deliver`. Use `--once` to check once and exit, or `--loop` to run every `--interval` seconds. Cooldown 90s between triggers. State: `logs/gateway-guard.continue-state.json`.
- **watch** — Single combined daemon (one LaunchAgent). Each run: (0) **token sync** — `ensure --apply` so gateway auth matches config (prevents device_token_mismatch); (1) gateway back → what-just-happened summary; (2) continue-on-error check. **Install one daemon:** `bash <skill-dir>/scripts/install_watcher.sh` (or `install_continue_on_error.sh`). This unloads the old separate what-just-happened and continue-on-error LaunchAgents and loads `com.openclaw.gateway-guard.watcher` so users only need one. For periodic gateway recovery (check every 10s, restart if not ok), use the separate **gateway-watchdog** skill.


## Behavior

- Reads `openclaw.json` → `gateway.auth` (token or password) and `gateway.port`.
- Compares with the process listening on that port (and optional guard state file).
- If `ensure --apply`: restarts gateway via `openclaw gateway stop` then `openclaw gateway --port N --auth token|password --token|--password SECRET`.
- If token is missing in config (token mode only): generates a token, writes it to config once, then proceeds. Does not overwrite config when it is already correct.
- **continue-on-error:** Tails `OPENCLAW_HOME/logs/gateway.log` for the string `Unhandled stop reason: error`. When found (and not in cooldown), runs `openclaw agent --message continue --deliver` so the agent receives "continue" and can resume. Run `install_continue_on_error.sh` to install a LaunchAgent that checks every 30s. If the error appears in the TUI but the watcher never triggers, the gateway may not be writing run errors to `gateway.log` — ensure run/stream errors are logged there.


## JSON output (for orchestration)

- **status --json** / **ensure --json**: `ok`, `secretMatchesConfig`, `running`, `pid`, `reason`, `recommendedAction`, `configPath`, `authMode`, `gatewayPort`. When not ok, `recommendedAction` is "run gateway_guard.py ensure --apply and restart client session".


## Requirements

- OpenClaw `openclaw.json` with `gateway.auth` (mode `token` or `password`) and `gateway.port`.
- **CLI / system:** `openclaw` CLI on PATH (for `ensure --apply` and continue-on-error); `lsof` and `ps` (macOS/Unix); `launchctl` on macOS when using the LaunchAgent install scripts.
- **Environment (optional):** `OPENCLAW_HOME` — OpenClaw home directory (default: `~/.openclaw`). `OPENCLAW_BIN` — Path or name of `openclaw` binary (default: `openclaw`).


## Privileged actions (what you accept)

This skill may: **read and modify `openclaw.json`** (including writing `gateway.auth` when missing or wrong); **write state and log files** under `OPENCLAW_HOME/logs/`; **restart the gateway** via the OpenClaw CLI; and, if the watcher is installed, **invoke `openclaw agent --message continue --deliver`** automatically when a run error is detected. These are privileged local actions; run only if you accept them.
