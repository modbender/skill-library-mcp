# Changelog

All notable changes to the Vibe Check skill will be documented in this file.

## [Unreleased]

### Fixed
- `analyze.sh`: `fix` field is now included in prompt schema only when `--fix` is enabled.
- `vibe-check.sh`: hard fail with clear errors when `--branch`, `--output`, or `--max-files` are missing values.
- `git-diff.sh`: hard fail with clear error when `--branch` is missing a value.
- `report.sh`: clearer message when `--fix` is enabled but no patch suggestions are present.

### Added
- `LICENSE`, `SECURITY.md`, and `TESTING.md` for publish parity with other CacheForge skills.

### Changed
- README footer now uses public-safe, non-numeric claims language aligned with claims SOT.

## [0.1.1] — 2026-02-16

### Added
- Discord v2 delivery guidance in `SKILL.md` for OpenClaw v2026.2.14+ channels:
  - Compact first response for Discord
  - Component-style quick actions for follow-up workflows
  - Fallback numbered actions when components are unavailable

### Changed
- README: added "OpenClaw Discord v2 Ready" section and feature callout.
- `SKILL.md` metadata tags now include `discord` and `discord-v2`.

## [0.1.0] — 2026-02-15

### Added
- Initial release of Vibe Check — code quality auditor for vibe coding sins
- 8 sin categories: error handling, duplication, dead code, input validation, magic values, test coverage, naming quality, security
- Weighted scoring system (0-100) with letter grades (A-F)
- LLM-powered analysis via Anthropic Claude or OpenAI GPT-4o
- Heuristic fallback analysis when no LLM API key is available
- Single file analysis mode
- Recursive directory scanning (with smart exclusions for node_modules, dist, __pycache__, etc.)
- Git diff mode (`--diff HEAD~N`, `--staged`, `--branch`)
- Fix mode (`--fix`) — generates unified diff patches for each finding
- Beautiful Markdown report with:
  - Overall score and letter grade
  - Score breakdown table by category
  - ASCII bar charts
  - Top findings by severity (critical/warning/info)
  - Per-file breakdown table
  - Copy-pasteable shields.io badge
- Supported languages: Python, TypeScript, JavaScript
- SKILL.md with trigger keywords for agent integration
