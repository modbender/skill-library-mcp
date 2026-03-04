# OpenClaw Advanced Tools — Operational Notes

For full command syntax, see `references/cli-full.md`.
This file adds operational context not found in CLI reference.

## Gateway RPC Methods
Use `openclaw gateway call <method> [--params <json>]` for direct RPC:
- `config.apply`: validate → write → restart → wake
- `config.patch`: merge partial update → restart → wake
- `config.get`: read current config
- `update.run`: run update → restart
- `logs.tail`: tail logs (param: `{"sinceMs": 60000}`)
- `status`: get runtime status
- `secrets.reload`: re-resolve secret refs

## Browser Operational Notes
- Profile `openclaw` = isolated managed Chrome. Profile `chrome` = existing Chrome via extension relay.
- Extension: `openclaw browser extension install` → load unpacked in `chrome://extensions`.
- Remote browser: set `gateway.nodes.browser.mode` + `gateway.nodes.browser.node` in config.
- All interaction commands accept `--target-id <id>` for multi-tab control.
- Memory files: `MEMORY.md` and `memory/*.md` in workspace root.

## Nodes Exec Behavior
- `nodes run` reads `tools.exec.*` config + agent-level overrides.
- Uses `exec.approval.request` before invoking `system.run`.
- `--raw` runs via `/bin/sh -lc` (Unix) or `cmd.exe /c` (Windows).
- Windows node hosts: `cmd.exe /c` wrapper always requires approval event with allowlist.
- `--node` omittable when `tools.exec.node` is set in config.
- Node hosts ignore `PATH` overrides; `tools.exec.pathPrepend` not applied.

## Cron Delivery
- `--announce`: announce to channel. `--deliver` / `--no-deliver` control message delivery.
- `--at` + `--keep-after-run`: one-time job that persists after execution.
- `cron.sessionRetention` (default 24h) prunes completed run sessions.
- Run logs: `~/.openclaw/cron/runs/<jobId>.jsonl`.

## Secrets Workflow
Recommended: `audit --check` → `configure` → `audit --check` (verify clean).
- Finding codes: `PLAINTEXT_FOUND`, `REF_UNRESOLVED`, `REF_SHADOWED`, `LEGACY_RESIDUE`.
- `secrets apply` is one-way (no rollback). Use `--dry-run` first.
- Scrub options auto-enabled: `scrubEnv`, `scrubAuthProfilesForProviderTargets`, `scrubLegacyAuthJson`.

## Security Audit Fix Scope
`security audit --fix` will:
- Flip `groupPolicy="open"` → `"allowlist"`
- Set `logging.redactSensitive` → `"tools"`
- Tighten file permissions on state/config

`--fix` will NOT: rotate tokens, disable tools, change bind/auth/network.

## Bundled Hooks
Enable: `openclaw hooks enable <name>`. Require gateway restart.
- `session-memory`: saves context on `/new` → `memory/YYYY-MM-DD-slug.md`
- `bootstrap-extra-files`: injects `AGENTS.md`/`TOOLS.md` on agent bootstrap
- `command-logger`: logs to `~/.openclaw/logs/commands.log` (JSONL)
- `boot-md`: runs `BOOT.md` on gateway startup

## Config Hot Reload
`gateway.reload.mode`: `hybrid` (default) | `hot` | `restart` | `off`
- Hot-apply: channels, agents, models, routing, hooks, cron, tools, browser, skills, etc.
- Restart required: gateway.*, discovery, plugins, gateway.remote
