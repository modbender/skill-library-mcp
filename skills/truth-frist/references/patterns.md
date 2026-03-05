# Patterns

## Template: Model Check

Claims to verify:
- Which model is configured
- Which model is active (if runtime state exists)

Evidence commands:
- Prefer repo-local config when present (`./openclaw.json`), otherwise use global (`~/.openclaw/openclaw.json`).
- `rg -n "model|provider" ~/.openclaw/openclaw.json`
- `rg -n "model|provider" ./openclaw.json`
- `rg -n "model|provider" .env`
- `rg -n "model|provider" config/`
- `openclaw gateway status`

Report:
- `Verified`: cite file path + key line(s) or command output.
- `Inferred`: cite partial signals (e.g., config only, no runtime state).
- `Unknown`: provide exact next-step command to check runtime.

## Template: Config Check

Claims to verify:
- A config value (e.g., `streamMode`) is set to a specific value

Evidence commands:
- Prefer repo-local config when present (`./openclaw.json`), otherwise use global (`~/.openclaw/openclaw.json`).
- `rg -n "streamMode" ~/.openclaw/openclaw.json`
- `rg -n "streamMode" ./openclaw.json`
- `rg -n "streamMode" config/`
- `rg -n "streamMode" .env`

Report:
- Cite the exact file path and line(s) containing the value.
- If multiple files conflict, list each and mark the claim `Unknown` until precedence is confirmed.

## Template: Service Check

Claims to verify:
- A service is running, reachable, or connected

Evidence commands:
- `openclaw gateway status`
- `rg -n "gateway|service" logs/`
- `ls /mnt` and `mount` (for mounts)
- `ss -lntp` or `lsof -i` (for open ports)

Report:
- `Verified` only with direct status or log evidence.
- `Unknown` if no direct status exists; include the next-step command.

## Common Evidence Commands (OpenClaw)

- `openclaw gateway status`
- `rg -n "streamMode" ~/.openclaw/openclaw.json`
- `rg -n "streamMode" ./openclaw.json`
- `rg -n "model|provider" ~/.openclaw/openclaw.json`
- `rg -n "model|provider" ./openclaw.json`
- `rg -n "gateway" logs/`
- `rg -n "error|warn" logs/`
- `ls -la` and `stat <path>` for existence and timestamps
