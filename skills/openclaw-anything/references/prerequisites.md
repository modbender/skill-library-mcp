# OpenClaw Prerequisites

## Required
`openclaw` CLI in `PATH`

## Optional (feature-dependent)

| Dependency | For |
|-----------|-----|
| Node.js + npm | Install/update flows |
| Playwright deps | Browser tooling |
| Tailscale | Remote node access |
| Docker + Compose | Containerized deploy |
| Nix | Flake environments |
| CoreDNS | `dns setup --apply` (macOS, sudo) |
| Google Cloud creds | Gmail webhook |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENCLAW_CONFIG_PATH` | Override config file |
| `OPENCLAW_STATE_DIR` | Override state dir |
| `OPENCLAW_HOME` | Override home dir |
| `OPENCLAW_GATEWAY_TOKEN` | Gateway token |
| `OPENCLAW_GATEWAY_PASSWORD` | Gateway password |
| `OPENCLAW_LOAD_SHELL_ENV=1` | Import shell env |
| `OPENCLAW_AGENT_DIR` | Agent context scope |
| `NO_COLOR=1` | Disable ANSI |
| `OPENCLAW_WRAPPER_ALLOW_RISKY=1` | Wrapper high-risk gate |

## Capability Boundaries
- Low-risk by default: read, list, status, search, logs, docs
- High-risk: see `security-policy.md`
- Wrapper: `OPENCLAW_WRAPPER_ALLOW_RISKY=1` for risky command groups
