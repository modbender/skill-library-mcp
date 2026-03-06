# Changelog

## [3.0.5] - 2026-02-16

### Security
- Manifest coherence hardening: removed the frontmatter install action from `SKILL.md`, leaving installation as explicit documentation-only shell steps.
- Removed Portal OpenClaw workspace DB behavior: paths under `~/.openclaw/workspace` are denylisted and cannot be discovered or selected, even when custom DB roots are configured.
- Removed Portal provider secret injection behavior: Portal no longer forwards provider secrets into vault subprocess environments.
- Updated portal diagnostics/frontend/docs to match the stricter defaults and removed stale OpenClaw/injection status surfaces.
- Added/updated regression tests covering OpenClaw path denylisting and no-secret-injection subprocess behavior.

## [3.0.4] - 2026-02-16

### Security
- Registry manifest transparency: moved install/env metadata to `metadata.openclaw.install` and `metadata.openclaw.requires.env` so ClawHub-visible fields match behavior.
- DB root enforcement hardened: removed `RESEARCHVAULT_PORTAL_ALLOW_ANY_DB` bypass and introduced `RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS` as the only DB root policy input.
- OpenClaw DB scope tightened with explicit gating under allowed DB roots.
- Secrets handling hardened: portal secret persistence/write APIs are disabled; provider secrets are env-only.
- Portal auth consistency: backend remains strict on `RESEARCHVAULT_PORTAL_TOKEN`; `start_portal.sh` now always initializes/exports the token from `.portal_auth` and avoids printing tokenized URLs unless explicitly requested.
- Added regression tests for DB root enforcement, token strictness, and env-only secret behavior.

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
