---
name: openclaw
description: OpenClaw CLI wrapper and docs companion for gateway, channels, models, automation, and operational workflows.
---

# OpenClaw Skill

Local skill package for operating OpenClaw from the terminal.
This repository does not install platform dependencies by itself. It wraps the `openclaw` CLI and provides local reference docs aligned to `https://docs.openclaw.ai`.

## Scope
- Install and onboarding flows
- Gateway lifecycle and health operations
- Channel connection management
- Model listing, authentication, and aliases
- Scheduled automation and browser tooling
- Plugin management
- Deployment references (Docker, Nix, update, rollback)

## Prerequisites
Required:
- `openclaw` CLI available in `PATH`

Common external prerequisites (depends on feature):
- Node.js and npm (for install/update flows in official docs)
- Playwright system dependencies (for browser tooling)
- Platform-specific tools such as `imsg` (macOS iMessage channel)
- Private networking setup such as Tailscale (if remote node access is needed)

Environment variables used by OpenClaw runtime:
- `OPENCLAW_CONFIG_PATH`
- `OPENCLAW_STATE_DIR`
- `OPENCLAW_HOME`

## Security Boundaries
Default stance is least privilege.

Allowed by default:
- Read-only status and diagnostics (`status`, `doctor`, `version`, `gateway status`, `gateway health`)
- Config inspection and non-destructive operational checks

High-risk capabilities (explicit user approval required per action):
- Arbitrary shell execution (`exec` tool in upstream runtime)
- Elevated privilege flows
- Sub-agent spawning and delegated execution
- Plugin installation from untrusted sources
- Cron creation/modification
- Browser automation against remote websites
- Device pairing and sensor access (camera/audio/location)

Wrapper opt-in gate:
- Commands mapped to high-risk areas require `OPENCLAW_WRAPPER_ALLOW_RISKY=1`

## Non-goals
- This repo is not the OpenClaw runtime source code.
- This repo does not provision system packages automatically.
- This repo does not manage host networking, VPN, or mobile OS permissions.
- This repo does not authorize autonomous privileged execution.

## Unified Command Utility
Primary wrapper script:
`bash scripts/openclaw.sh [command] [args]`

### Command Mapping
The wrapper routes to official `openclaw` commands:

- `install|setup|doctor|status|reset|version|tui|dashboard`
  - Pass-through to `openclaw ...`
- `service ...`
  - `openclaw gateway service ...`
- `channel login <name>`
  - `openclaw channels login --channel <name>`
- `channel list`
  - `openclaw channels list`
- `channel logout <name>`
  - `openclaw channels logout --channel <name>`
- `channel pairing`
  - `openclaw pairing` (risky-gated)
- `model auth ...`
  - `openclaw models auth ...`
- `model alias ...`
  - `openclaw models aliases ...`
- `model scan|list|set ...`
  - `openclaw models ...`
- `cron ...`
  - `openclaw cron ...` (risky-gated)
- `browser ...`
  - `openclaw browser ...` (risky-gated)
- `plugin ...`
  - `openclaw plugins ...` (risky-gated)
- `msg ...`
  - `openclaw message send ...`
- `prose ...`
  - Enables `open-prose` plugin (risky-gated)

## Documentation
- `references/security-policy.md`: Guardrails and approval policy
- `references/prerequisites.md`: Dependency and capability boundaries
- `references/cli-full.md`: Consolidated CLI commands
- `references/config-schema.md`: Config and env variable references
- `references/nodes-platforms.md`: Platform and node notes
- `references/deployment.md`: Docker, Nix, update, rollback
- `references/advanced-tools.md`: Plugins, browser, gateway helpers
- `references/hubs.md`: Docs hub links

## Maintenance Notes
- Last docs normalization: 2026-02-17
- Source of truth: `https://docs.openclaw.ai`
