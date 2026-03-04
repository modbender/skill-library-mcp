# Changelog

## [2.0.0] - 2026-02-18

### Added
- Lifecycle hooks: `pre-compaction`, `post-compaction`, `session-start` for fully automatic state management.
- Schema validation for state writes.
- Atomic file writes with `.tmp` cleanup.
- Dynamic workspace resolution (respects `OPENCLAW_WORKSPACE`).
- Comprehensive test suite.

### Changed
- Removed reliance on `memoryFlush.prompt` and AGENTS.md rules for automation.
- Updated documentation to reflect hook-based operation.
- Bumped Node.js engine to >=18.
- Renamed `discoverFromSessions` parameters to accept options.

### Fixed
- Race condition potential during concurrent writes (atomicity).
- YAML parsing edge cases with body containing `---`.

## [1.0.1] - 2026-02-14

### Changed
- Clarified optional configuration and privacy implications.
- Improved error messages.

### Fixed
- Tightened file parsing to handle body with `---` delimiters.

## [1.0.0] - 2026-02-14

### Added
- Initial release: tools `session_state_read`, `session_state_write`, `session_state_discover`.
- CLI `session-state`.
- Manual or semi-automatic state maintenance via AGENTS.md rules.