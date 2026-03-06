# gateway-guard

**OpenClaw skill: keep gateway auth in sync with config.**

Detects and fixes gateway auth drift (running process vs `openclaw.json`). Writes `gateway.auth` to config **only when it’s missing or wrong**, so you get a stable token and no unnecessary restarts.

## What it does

- **Check** — `status` reports whether the gateway’s auth matches `openclaw.json`.
- **Fix** — `ensure --apply` restarts the gateway with credentials from config and (if needed) writes correct auth to config once.
- **Safe writes** — Only updates `gateway.auth` when incorrect; never overwrites a correct config.

Use it when you see `device_token_mismatch`, “Gateway auth issue”, or before delegating to sub-agents so the gateway is in a known-good state.

## Install

**ClawHub:** Update `clawhub install` and ClawHub links when the new ClawHub instance is live.

**From ClawHub (if published):**

```bash
npm install -g clawhub
clawhub install gateway-guard
```

**From GitHub:**

```bash
git clone https://github.com/YOUR_ORG/gateway-guard.git
# Copy into your OpenClaw workspace:
cp -r gateway-guard ~/.openclaw/workspace/skills/
# Or link:
ln -s /path/to/gateway-guard ~/.openclaw/workspace/skills/gateway-guard
```

**Manual:** Copy this folder into your OpenClaw workspace `skills/` directory (e.g. `~/.openclaw/workspace/skills/gateway-guard/`).

## Before installing

- **Metadata:** This skill uses **`always: false`** (in `_meta.json`). It is not forced into every agent run; the orchestrator invokes it when needed. Registry and repo metadata are aligned on this.
- **Backup `openclaw.json`** — The script may add or correct `gateway.auth` when missing or wrong. Copy the file before running `ensure --apply`.
- **Test read-only first** — Run `python3 scripts/gateway_guard.py status --json` and `python3 scripts/gateway_guard.py ensure --json` (without `--apply`) to see what would happen.
- **Continue delivery** — The optional watcher runs `openclaw agent --message continue --deliver` when a run error appears in `gateway.log`. Confirm that automatic delivery is acceptable in your setup.
- **LaunchAgent is optional** — Persistence is installed only when you run `install_watcher.sh`. The **plist is included** in this package: `scripts/com.openclaw.gateway-guard.watcher.plist`. The installer copies it to `~/Library/LaunchAgents` and runs `launchctl load`. Ensure `OPENCLAW_HOME` and `OPENCLAW_BIN` are correct before installing.
- **Non-production first** — Try in a safe environment if unsure.

## Auto-connect (detect and connect automatically)

To avoid **connection refused** when the gateway isn't running, use the wrapper so the gateway is started (and ready) before your client connects:

```bash
# Ensure gateway is up, then start the TUI (or Control UI, etc.)
$OPENCLAW_HOME/workspace/skills/gateway-guard/scripts/ensure_gateway_then.sh openclaw tui
# Or just wake the gateway and wait until it's listening
$OPENCLAW_HOME/workspace/skills/gateway-guard/scripts/ensure_gateway_then.sh
```

The script runs `gateway_guard.py ensure --apply --wait` (start if needed, wait up to 30s for the port), then runs your command if you passed one.

## Package contents (file manifest)

- `scripts/gateway_guard.py` — Main script (ensure supports `--wait`).
- `scripts/ensure_gateway_then.sh` — Wrapper: ensure gateway then run optional command.
- `scripts/install_watcher.sh` — Installs the combined LaunchAgent.
- `scripts/install_continue_on_error.sh` — Redirects to install_watcher.sh.
- `scripts/com.openclaw.gateway-guard.watcher.plist` — LaunchAgent plist (included; installer copies and substitutes paths).
- `scripts/com.openclaw.gateway-guard.continue-on-error.plist` — Legacy plist (optional).

## Quick start

From the skill directory or with absolute path:

```bash
# Check (machine-readable)
python3 scripts/gateway_guard.py status --json

# Fix if mismatch (restart gateway with config auth; write config only if wrong)
python3 scripts/gateway_guard.py ensure --apply --json
```

Use the **absolute path** when running from the TUI or another cwd:

```bash
python3 ~/.openclaw/workspace/skills/gateway-guard/scripts/gateway_guard.py status --json
```

## Requirements

- OpenClaw `openclaw.json` with `gateway.auth` (token or password) and `gateway.port`.
- `openclaw` CLI on PATH (for `ensure --apply`).

For automatic recovery every 10s (check gateway, restart if not ok), use the separate **gateway-watchdog** skill (`workspace/skills/gateway-watchdog/`); it calls this guard script and can run as a LaunchAgent.

## Options

| Command     | Options   | Description |
|------------|-----------|-------------|
| `status`   | `--json`  | Check consistency; exit 0 if ok, 1 if mismatch. |
| `ensure`   | `--apply` | Fix by restarting gateway with config auth. |
| `ensure`   | `--json`  | Emit JSON result for orchestration. |

## GitHub repo

1. Create a new repository (e.g. `gateway-guard`) on GitHub. Do **not** add a README or .gitignore (this skill has its own).
2. From this skill directory (the repo root):

   ```bash
   git init
   git add SKILL.md README.md scripts/ .gitignore
   git commit -m "Initial gateway-guard skill"
   git branch -M main
   git remote add origin https://github.com/YOUR_ORG/gateway-guard.git
   git push -u origin main
   ```

3. Replace `YOUR_ORG` with your GitHub username or org. Others can install with:

   ```bash
   git clone https://github.com/YOUR_ORG/gateway-guard.git
   cp -r gateway-guard ~/.openclaw/workspace/skills/
   ```

## ClawHub

Publish so others can install with `clawhub install gateway-guard`:

```bash
npm install -g clawhub
clawhub login   # if needed
cd /path/to/gateway-guard   # this skill folder as root
clawhub publish .
```

The skill slug will be `gateway-guard`. After publishing, users run:

```bash
clawhub install gateway-guard
```

## License

MIT (or your choice).
