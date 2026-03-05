# Changelog

## [3.0.4] - 2026-02-16

### Security
- Registry manifest transparency: moved install/env metadata to `metadata.openclaw.install` and `metadata.openclaw.requires.env` so ClawHub-visible fields match behavior.
- DB root enforcement hardened: removed `RESEARCHVAULT_PORTAL_ALLOW_ANY_DB` bypass and introduced `RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS` as the only DB root policy input.
- OpenClaw DB scope tightened: `RESEARCHVAULT_PORTAL_SCAN_OPENCLAW=1` only takes effect when `~/.openclaw/workspace` is inside allowed DB roots.
- Secrets handling hardened: portal secret persistence/write APIs are disabled; provider secrets are env-only and subprocess injection remains explicit opt-in via `RESEARCHVAULT_PORTAL_INJECT_SECRETS=1`.
- Portal auth consistency: backend remains strict on `RESEARCHVAULT_PORTAL_TOKEN`; `start_portal.sh` now always initializes/exports the token from `.portal_auth` and avoids printing tokenized URLs unless explicitly requested.
- Added regression tests for DB root enforcement, OpenClaw scan gating, token strictness, and env-only secret/injection behavior.

## [2.6.2] - 2026-02-10

### Security
- **SSRF Hardening**: Implemented strict DNS resolution and IP verification in `scuttle`. Blocks private, local, and link-local addresses by default.
- **Service Isolation**: Moved background services (MCP, Watchdog) to `scripts/services/` to reduce default capability surface.
- **Transparency**: Added `SECURITY.md` and updated `SKILL.md` manifest to explicitly declare optional environment variables.
- **Model Gating**: Explicitly set `disable-model-invocation: true` at the registry manifest level to prevent autonomous AI side-effects.

### Added
- `--allow-private-networks` flag for `vault scuttle` to allow fetching from local addresses when explicitly requested by user.
- Comprehensive provenance info: `LICENSE`, `CONTRIBUTING.md`, and project `homepage`.

### Fixed
- Registry metadata mismatch: standardized frontmatter keys for ClawHub compatibility.
- Removed `uv` requirement from primary installation path.
