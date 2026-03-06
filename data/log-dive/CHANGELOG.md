# Changelog

All notable changes to **log-dive** will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.1] — 2026-02-16

### Added
- Discord v2 delivery guidance in `SKILL.md` for OpenClaw v2026.2.14+:
  - Compact first response for incident log triage
  - Component-style quick actions
  - Numbered fallback when components are unavailable
- `discord` and `discord-v2` tags in skill metadata

### Changed
- Metadata normalization: `author` set to `CacheForge`.
- README: added "OpenClaw Discord v2 Ready" compatibility section.
- `log-dive.sh` version bumped to `0.1.1`.

### Fixed
- `log-dive-cw.sh`: added URL scheme validation for `AWS_ENDPOINT_URL` (http/https only).

## [0.1.0] — 2026-02-15

### Added
- Initial release
- **Loki backend** — LogQL queries via `logcli` with HTTP API fallback (`curl`)
- **Elasticsearch backend** — Query DSL via `curl`, supports OpenSearch
- **CloudWatch backend** — Filter patterns via `aws logs` CLI
- Backend auto-detection from environment variables
- Subcommands: `search`, `backends`, `indices`/`labels`, `tail`
- Natural language → query translation guide in SKILL.md
- Smart output limiting (default 200 lines)
- Read-only safety: no write/delete/admin operations
- URL scheme validation (http/https only)
- Safe JSON construction via `jq --arg`
- Structured Markdown output format
- SECURITY.md with threat model and data handling policy

---

*Powered by Anvil AI 🤿*
