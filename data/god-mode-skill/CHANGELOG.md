# Changelog

All notable changes to god-mode will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-01

**🎉 Published on ClawHub:** https://www.clawhub.ai/InfantLab/god-mode

### Added
- Multi-project status overview with activity-based sorting
- Incremental sync with SQLite cache (90-day window)
- GitHub provider with full API integration
- Azure DevOps provider with pagination support
- LLM-powered agent instruction analysis
- OpenClaw integration mode (uses OpenClaw's LLM)
- Standalone mode (supports Anthropic, OpenAI, OpenRouter APIs)
- Interactive recommendation application
- Monthly activity review command (`god review`)
- Activity logging for transparency
- JSON output mode for all commands (`--json`)
- Project management (add/remove/list)
- Configuration via `~/.config/god-mode/config.yaml`

### Fixed
- Azure DevOps pagination (now fetches >100 commits correctly)
- Status display for projects with commits >7 days old
- PR/issue timestamp conversion (ISO → Unix epoch)

### Documentation
- Comprehensive SKILL.md with usage examples
- TESTING.md with full test results (47/47 tests passed)
- Monthly review cron job example
- Agent analysis workflow documentation

### Known Limitations
- OpenClaw agent analysis doesn't auto-cache responses
- GitLab provider not yet implemented (v0.2.0)

## [Unreleased]

### Planned for v0.2.0
- Context save/restore
- Activity summaries (`god today`, `god week`)
- `god agents generate` for bootstrapping new projects
- Month-over-month trend analysis in reviews
- Contributor spotlight feature

[0.1.0]: https://github.com/InfantLab/god-mode-skill/releases/tag/v0.1.0
