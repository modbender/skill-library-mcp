# Changelog

## v4.0.5 (2026-02-28)
### Fixed
- ClawHub metadata: proper `binaries` field with required/optional
- ClawHub metadata: proper `install.command` field
- SKILL.md frontmatter: added binaries, install, homepage
- Synced all metadata between manifest.json and SKILL.md

## v4.0.4 (2026-02-28)
### Fixed
- Batch/parallel working directory support
- Opencode/pi command fix (use `run` subcommand)
- Error handling per task with proper exit codes

## v4.0.0-4.0.3 (2026-02-28)
### Added
- Initial release: Enhanced agent orchestrator
- Commands: discover, health, run, batch, parallel, watch, kill, workflow, json
- 4 workflow presets: review, refactor, test, debug
- Support for ACP agents (opencode, pi), CLI agents (kimi, kilo), PTY agents (codex, claude)

## v3.0.0 (2026-02-28)
### Changed
- Generic auto-discovery approach
- Agent-agnostic design

## v2.0.0 (2026-02-28)
### Added
- Async multi-agent patterns

## v1.0.0 (2026-02-27)
### Added
- Initial acpx wrapper
