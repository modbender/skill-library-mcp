# OpenClaw CLI Command Map

## Table of Contents

- Global flags
- Command routing quick map
- Command families
- Common recipes
- Caution commands

## Global Flags

- `--dev`: Use dev profile and isolate under `~/.openclaw-dev`; default gateway port `19001`.
- `--profile <name>`: Isolate state/config under `~/.openclaw-<name>`.
- `--no-color`: Disable ANSI colors for logs/automation.
- `-h`, `--help`: Show help.
- `-V`, `--version`: Print version.

Prefer choosing profile flags before the command family:

```bash
openclaw --dev status
openclaw --profile staging gateway
```

## Command Routing Quick Map

- Run a single agent turn: `agent`
- Manage isolated agent runtimes: `agents`
- Diagnose health: `status`, `health`, `doctor`, `logs`
- Operate gateway runtime: `gateway`, `daemon`
- Operate headless node service: `node`, `nodes`
- Manage channel auth/connectivity: `channels`, `pairing`, `devices`, `qr`
- Send/read messages: `message`
- Model discovery/config: `models`
- Config/setup/onboarding: `setup`, `configure`, `config`, `onboard`
- Plugin/extension management: `plugins`
- Scheduled jobs: `cron`
- Security/audits: `security`, `approvals`, `sandbox`
- Live docs lookup: `docs`
- Open Control UI: `dashboard`, `tui`
- System/presence/events: `system`
- Local data lifecycle: `reset`, `uninstall`, `update`

For starred families, inspect subcommands first:

```bash
openclaw <family> --help
```

## Command Families

- `acp *`: Agent Control Protocol tooling.
- `agent`: Execute one agent turn via Gateway.
- `agents *`: Manage isolated agents, auth, routing, workspaces.
- `approvals *`: Manage exec approvals.
- `browser *`: Manage dedicated browser (Chrome/Chromium).
- `channels *`: Manage chat channel connections.
- `clawbot *`: Legacy command aliases.
- `completion`: Generate shell completions.
- `config *`: Non-interactive config helper commands.
- `configure`: Interactive setup wizard.
- `cron *`: Manage scheduler jobs.
- `daemon *`: Legacy alias for gateway service control.
- `dashboard`: Open Control UI with current token.
- `devices *`: Device pairing and token management.
- `directory *`: Lookup contact/group IDs for channels.
- `dns *`: DNS helpers for wide-area discovery.
- `docs`: Search live OpenClaw docs.
- `doctor`: Run health checks and quick fixes.
- `gateway *`: Run/inspect/query the WebSocket Gateway.
- `health`: Fetch health from running gateway.
- `hooks *`: Manage internal agent hooks.
- `logs`: Tail gateway file logs via RPC.
- `memory *`: Search/reindex memory files.
- `message *`: Send/read/manage messages.
- `models *`: Discover/scan/configure models.
- `node *`: Run/manage headless node host service.
- `nodes *`: Manage gateway-owned node pairing and commands.
- `onboard`: Interactive onboarding for gateway/workspace/skills.
- `pairing *`: Secure DM pairing flow.
- `plugins *`: Manage plugins/extensions.
- `qr`: Generate iOS pairing QR/setup code.
- `reset`: Reset local config/state (CLI remains installed).
- `sandbox *`: Manage sandbox containers.
- `security *`: Security tooling and local config audits.
- `sessions`: List stored conversation sessions.
- `setup`: Initialize local config and workspace.
- `skills *`: List and inspect available skills.
- `status`: Show channel health + recent recipients.
- `system *`: System events, heartbeat, presence.
- `tui`: Open terminal UI connected to Gateway.
- `uninstall`: Remove gateway service and local data.
- `update *`: Update OpenClaw and check channel status.
- `webhooks *`: Webhook integration helpers.

## Common Recipes

Inspect help for an area:

```bash
openclaw models --help
openclaw channels --help
```

Run gateway locally:

```bash
openclaw gateway --port 18789
openclaw --dev gateway
openclaw gateway --force
```

Perform channel login with logs:

```bash
openclaw channels login --verbose
```

Send a message with JSON output:

```bash
openclaw message send --target +15555550123 --message "Hi" --json
openclaw message send --channel telegram --target @mychat --message "Hi"
```

Run an agent turn and optionally deliver:

```bash
openclaw agent --to +15555550123 --message "Run summary" --deliver
```

Check runtime health:

```bash
openclaw status
openclaw health
openclaw doctor
```

## Caution Commands

- `openclaw reset`: destructive local state reset.
- `openclaw uninstall`: removes service + local data.
- `openclaw gateway --force`: forcefully clears port conflicts.

Always confirm intent before running caution commands.

## External Docs

- CLI docs: `https://docs.openclaw.ai/cli`
