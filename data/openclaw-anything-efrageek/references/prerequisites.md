# OpenClaw Prerequisites and Capability Boundaries

Last verified: 2026-02-17.
Source of truth: `https://docs.openclaw.ai`.

## Required
- `openclaw` CLI installed and accessible in `PATH`

## Optional or Feature-dependent
- Node.js and npm: install/update workflows
- Playwright OS dependencies: managed browser features
- `imsg` on macOS: iMessage channel integrations
- Tailscale or equivalent private networking: remote/mobile node access
- Docker Engine + Compose: containerized deployments
- Nix: flake-based environments

## Runtime Environment Variables
- `OPENCLAW_CONFIG_PATH`
- `OPENCLAW_STATE_DIR`
- `OPENCLAW_HOME`

## Capability Boundaries
Low-risk by default:
- status checks
- diagnostics
- read-focused configuration inspection

High-risk (explicit approval required):
- arbitrary shell execution features in upstream runtime
- elevated mode
- sub-agent execution with inherited environment
- browser automation, plugin install/enable, cron mutation
- device pairing and sensor-enabled features

Wrapper-level control:
- `OPENCLAW_WRAPPER_ALLOW_RISKY=1` is required for risky command groups in `scripts/openclaw.sh`.

## What This Repo Provides
- Local docs and references
- A shell wrapper (`scripts/openclaw.sh`) that routes commands to `openclaw`

## What This Repo Does Not Provide
- Binary installation of OpenClaw itself
- Automatic OS package provisioning
- Host-level network/VPN setup
- Mobile platform permissions and device configuration
- Automatic approval for privileged actions
