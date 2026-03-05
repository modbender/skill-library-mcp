# launchagent-manager

**OpenClaw skill: list/prune LaunchAgents and analyze config so the gateway LaunchAgent stays connected and tokens match.**

- **Config analysis:** Reads `openclaw.json`, finds the gateway LaunchAgent plist (e.g. ai.openclaw.gateway), checks if it's loaded and if the running gateway's auth matches config (via gateway-guard). Use `--config --fix` to load the plist and run gateway-guard ensure --apply when needed.
- **List/prune:** Classifies LaunchAgents as OpenClaw (keep) or other (prune). Can unload and optionally delete non-OpenClaw plists.

## Quick start

```bash
# Analyze config and gateway: ensure proper gateway LaunchAgent connected, tokens match
python3 workspace/skills/launchagent-manager/scripts/launchagent_manager.py --config

# Fix: load gateway plist if not loaded, sync auth if tokens mismatch
python3 workspace/skills/launchagent-manager/scripts/launchagent_manager.py --config --fix

# List (OpenClaw vs others)
python3 workspace/skills/launchagent-manager/scripts/launchagent_manager.py

# JSON
python3 workspace/skills/launchagent-manager/scripts/launchagent_manager.py --json

# See what would be removed (dry-run)
python3 workspace/skills/launchagent-manager/scripts/launchagent_manager.py --prune --dry-run

# Actually unload non-OpenClaw agents (plists kept)
python3 workspace/skills/launchagent-manager/scripts/launchagent_manager.py --prune --apply

# Unload and delete plist files (backups to OPENCLAW_HOME/backups/launchagents)
python3 workspace/skills/launchagent-manager/scripts/launchagent_manager.py --prune --apply --delete-plists
```

## OpenClaw = keep

- Label starts with `com.openclaw.` (e.g. com.openclaw.gateway-guard.watcher, com.openclaw.gateway-watchdog).
- ProgramArguments or plist path contains "openclaw".

All other LaunchAgents are considered non-OpenClaw and are unloaded (and optionally deleted) when you run --prune --apply.
