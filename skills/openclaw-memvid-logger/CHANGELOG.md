# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.5] - 2026-02-22

### Fixed
- **Memvid Tag Format:** Updated `build_tags()` to use `KEY=VALUE` format for Memvid 2.0+ compatibility
  - Old: `--tag "user,telegram"` (comma-separated)
  - New: `--tag "role=user" --tag "source=telegram"` (multiple flags)
  - Fixes "invalid value for --tag" error

### Changed
- **Documentation - Environment Variables:** Added clear instructions to use `/etc/environment` instead of `.bashrc`/`.profile`
  - OpenClaw runs as a background service and doesn't inherit shell profiles
  - System-wide environment via `/etc/environment` is required
- **Documentation - Hook Format:** Clarified that OpenClaw 2026.2.12+ requires JavaScript (`.js`) handlers, not TypeScript (`.ts`)
- **Documentation - Troubleshooting:** Added comprehensive troubleshooting section covering:
  - Environment variables not persisting
  - Hook registered but not logging
  - Memvid tag format errors
  - Free tier limits
  - Full diagnostic checklist

### Compatibility
- Verified with OpenClaw 2026.2.12
- Verified with Memvid CLI 2.0+

## [1.2.4] - 2026-02-20

### Changed
- **Search Mode Default:** Updated documentation to recommend `--mode neural` as the default search mode
- **Performance Guidance:** Clarified latency trade-offs (~200ms neural vs ~8ms lexical) with recommendation to accept neural for accuracy
- **Search Policy:** Changed from "start with lex, fallback to neural" to "always use neural unless speed is critical"

### Documentation
- Updated Search Performance Guide in SKILL.md
- Added Search Usage section to README.md with neural as default
- Clarified when to use each search mode (neural/lex/hybrid)

## [1.2.3] - 2026-02-19

### Changed
- **Version Cohesion:** All files synchronized to v1.2.3
- **Documentation Consistency:** README and SKILL.md now have matching content
- **Security Improvements:** Generic paths (no hardcoded user directories), install script asks permission
- **Registry Compliance:** Complete metadata for ClawHub transparency

### Added
- **Privacy Documentation:** Comprehensive Security & Privacy Notice explaining data capture scope
- **Role Tagging:** Distinguishes user, assistant, agent:*, system, and tool messages
- **Three Storage Modes:** API mode (single file), Free mode (50MB), Sharding mode (monthly rotation)

## [1.0.0] - 2026-02-19

### Added
- Initial release of Unified Logger
- Dual-output logging (JSONL + Memvid)
- Automatic hook integration with OpenClaw
- Semantic search via Memvid CLI
- Environment variable configuration
- Installation script
- Comprehensive documentation

### Features
- Zero data loss - raw conversation text preserved
- Instant searchability - every message indexed
- Crash resilience - append-only writes
- Configurable paths via environment variables
- Silent failure - never breaks OpenClaw conversations

[1.2.4]: https://github.com/stackBlock/openclaw-memvid-logger/releases/tag/v1.2.4
[1.2.3]: https://github.com/stackBlock/openclaw-memvid-logger/releases/tag/v1.2.3
[1.0.0]: https://github.com/openclaw/unified-logger/releases/tag/v1.0.0
