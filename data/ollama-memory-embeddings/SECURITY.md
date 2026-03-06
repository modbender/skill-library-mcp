# Security and Behavior Notes

This skill is shell-based and modifies local OpenClaw config. It is designed to be bounded, explicit, and reversible.

## Safe defaults

- `install.sh` defaults:
  - `--restart-gateway no`
  - `--import-local-gguf no`
  - watchdog not installed unless `--install-watchdog` is provided
- Use `--dry-run` to preview planned writes and commands without changing anything.

## Entry points

- `install.sh` - install and configure memory embeddings provider
- `verify.sh` - endpoint and model verification only
- `enforce.sh` - idempotent config enforcement with lock protection
- `watchdog.sh` - optional drift healing and optional launchd install
- `audit.sh` - read-only report (no mutation)
- `uninstall.sh` - best-effort revert using latest config backup

## External commands used

- Required: `bash`, `node`, `curl`, `ollama`
- Optional: `openclaw`, `launchctl`, `plutil`, `systemctl`

## Files and paths touched

- Reads/writes OpenClaw config (default): `~/.openclaw/openclaw.json`
- Backup files: `~/.openclaw/openclaw.json.bak.*`
- Installed skill files: `~/.openclaw/skills/ollama-memory-embeddings/`
- Optional watchdog plist (macOS): `~/Library/LaunchAgents/bot.molt.openclaw.embedding-guard.plist`
- Optional watchdog logs: `~/.openclaw/logs/embedding-guard.*.log`

## Network behavior

- Intended endpoint is local loopback Ollama (`http://127.0.0.1:11434`).
- Verification calls the configured embeddings endpoint.
- No data upload behavior is implemented.

## Persistence behavior

- Persistence is optional and explicit via `watchdog.sh --install-launchd` (or `install.sh --install-watchdog`).
- Remove persistence via `watchdog.sh --uninstall-launchd` or `uninstall.sh`.
