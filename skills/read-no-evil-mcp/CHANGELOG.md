# Changelog

## [0.3.1] - 2026-02-17

### Fixed
- CLI argument order: global options (`--server`, `--timeout`) now work in any position, not just before the subcommand ([#7](https://github.com/thekie/read-no-evil-clawbot-skill/pull/7))
- `send` command: `--to` and `--cc` are now correctly passed as lists to the MCP server, fixing sends to multiple recipients ([#8](https://github.com/thekie/read-no-evil-clawbot-skill/pull/8))

### Added
- `list` command now displays an unread indicator (`*`) next to unseen messages ([#9](https://github.com/thekie/read-no-evil-clawbot-skill/pull/9))

## [0.3.0] - 2026-02-16

### Changed
- **Breaking**: Switched from library integration to a Docker-hosted read-no-evil-mcp server accessed via MCP Streamable HTTP protocol ([#2](https://github.com/thekie/read-no-evil-clawbot-skill/pull/2))
- `rnoe-mail.py` rewritten as a zero-dependency MCP HTTP client (Python stdlib only)
- New flag-driven setup scripts (`setup-config.py`, `setup-server.sh`) designed for LLM agent invocation
- SMTP configuration is now optional (only required when send permission is enabled)
- Docker image pinned to `:0.3` matching read-no-evil-mcp v0.3 features

## [0.2.0] - 2026-02-05

### Added
- Initial public release as an OpenClaw skill
- GitHub Actions workflow for ClawHub publishing
- Pinned to read-no-evil-mcp v0.2.0

### Changed
- Renamed Clawdbot to Clawbot
- Renamed ClawdHub to ClawHub
