# Changelog

All notable changes to the Coder Workspaces skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.5] - 2026-02-06

### Changed
- Restructured skill to follow standard CLI documentation patterns
- Setup section now shows environment configuration (matches hass-cli style)
- Commands no longer reference environment variables directly

## [1.5.4] - 2026-02-06

### Changed
- Install instructions now point only to official Coder docs

## [1.5.3] - 2026-02-06

### Added
- Context note clarifying commands run in isolated Coder workspaces, not host

## [1.5.2] - 2026-02-06

### Changed
- Rewrote skill for agent (not user) as audience
- Agent now attempts CLI install/auth fixes before asking user
- Preset handling: try without, use default if exists, ask user only if needed

### Removed
- Brew install metadata (agent learns install from Coder docs)

## [1.5.1] - 2026-02-06

### Changed
- Task states timing now notes dependency on template configuration

## [1.5.0] - 2026-02-06

### Removed
- `scripts/setup.sh` — CLI installation is now user responsibility (see docs)
- `scripts/authenticate.sh` — login command documented in SKILL.md instead
- `scripts/list-presets.sh` — presets visible in Coder web UI

### Changed
- Skill now follows standard pattern: documents usage, doesn't install software
- Added `metadata.openclaw.install` for brew install hint
- No scripts remain — pure documentation skill

## [1.4.1] - 2026-02-06

### Changed
- `scripts/setup.sh` now downloads binary directly instead of executing remote install script

### Security
- Removed shell script piping pattern that triggered security scanners

## [1.4.0] - 2026-02-06

### Added
- `scripts/authenticate.sh` — Login with session token (separate from install)

### Changed
- `scripts/setup.sh` now only installs/updates CLI (no longer handles auth)
- Setup and auth are now independent tools for targeted troubleshooting

## [1.3.1] - 2026-02-06

### Added
- `scripts/setup.sh` — Install CLI from instance URL and verify authentication in one step

### Changed
- README now instructs installing CLI from your Coder instance URL (ensures version match)
- README restructured around the setup script workflow
- SKILL.md references setup script for initial setup

### Security
- Removed inline curl/API examples from SKILL.md (credential pattern flagged by security scanner)
- SKILL.md now references helper scripts without exposing token-handling patterns
- Helper scripts retained as tools (not agent-loaded content)

## [1.3.0] - 2026-02-06

### Added
- Helper script `scripts/list-presets.sh` to discover available presets for templates
- Complete "Task Creation Workflow" section with step-by-step instructions

### Changed
- Restructured AI Coding Tasks section around the full workflow

## [1.2.1] - 2026-02-06

### Changed
- Cleaned up description to remove implementation details
- Simplified README with cleaner formatting
- Replaced table with bullet list for task timing
- Removed redundant sections and improved readability

## [1.2.0] - 2026-02-06

### Changed
- Restructured skill to separate agent instructions from setup documentation
- Setup instructions moved to README.md (for humans)
- SKILL.md now assumes coder CLI is pre-installed and authenticated

### Removed
- Helper script with curl commands (security scanner flagged patterns)
- Reference files with API examples (redundant with official Coder docs)

### Security
- Removed all curl and credential-sending patterns from agent-loaded files
- Skill no longer contains install or authentication instructions

## [1.1.0] - 2026-02-06

### Added
- Initial public release of Coder Workspaces skill for OpenClaw
- Workspace lifecycle management: list, create, start, stop, restart, delete
- SSH and command execution in workspaces
- AI coding agent task management for Claude Code, Aider, Goose, and others
- Helper script (coder-helper.sh) for common operations
- Comprehensive CLI command reference documentation
- Coder Tasks deep-dive guide
- Setup guide with agent workflow checklist
- Troubleshooting guide for authentication issues
- GitHub Actions workflow for automated ClawHub publishing on tagged releases
