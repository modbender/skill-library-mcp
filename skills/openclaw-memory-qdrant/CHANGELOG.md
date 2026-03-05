# Changelog

All notable changes to this project will be documented in this file.

## [1.0.15] - 2026-02-17

### Added
- **Custom Storage Path**: New `storagePath` configuration option
  - Allows users to specify custom directory for storing memories
  - Supports `~` for home directory
  - Defaults to `~/.openclaw-memory/` if not specified

## [1.0.14] - 2026-02-17

### Changed
- **BREAKING**: `persistToDisk` now defaults to `true` (was `false`)
- Disk persistence is now the default behavior for better user experience
- Set `persistToDisk: false` to use volatile memory mode

## [1.0.13] - 2026-02-17

### Added
- **Disk Persistence**: New `persistToDisk` configuration option for memory mode
  - Memories are saved to `~/.openclaw-memory/` and survive restarts
  - Only applies when using in-memory mode (no qdrantUrl configured)
  - Automatic save on store/delete operations
  - Automatic load on plugin initialization

### Changed
- Memory mode now supports persistent storage without requiring external Qdrant server
- Enhanced logging to show persistence status on startup

## [1.0.12] - 2026-02-17

### Documentation
- Added prominent privacy warning at top of SKILL.md about autoCapture PII risks
- Clarified that PII capture only occurs if user explicitly enables `allowPIICapture`
- Enhanced visibility of privacy implications for ClawHub users

## [1.0.11] - 2026-02-17

### Added
- **PII Protection**: New `allowPIICapture` configuration option (default: false)
  - autoCapture now automatically skips text containing emails or phone numbers
  - Users must explicitly enable `allowPIICapture` to capture PII
  - Clear privacy warnings in UI and documentation

### Changed
- **BREAKING**: Removed PII patterns (emails, phone numbers) from automatic capture triggers
- autoCapture now only triggers on semantic patterns (preferences, decisions, facts)
- `detectCategory` no longer uses PII patterns for entity detection
- Enhanced privacy documentation with clear warnings and use case guidance

### Security
- **Privacy Enhancement**: PII is now protected by default, addressing ClawHub security review feedback
- Added `containsPII()` function to detect and filter sensitive information
- Logs warning when PII is detected and skipped during autoCapture

### Documentation
- Updated SKILL.md with clear privacy warnings and PII protection explanation
- Updated README.md with detailed `allowPIICapture` usage guidance
- Added use case recommendations (personal vs shared environments)

## [1.0.10] - 2026-02-17

### Fixed
- **P1-13**: CLI search command now uses `SIMILARITY_THRESHOLDS.LOW` constant instead of hardcoded 0.3
- **P1-14**: Fixed regex inconsistency in `detectCategory` - phone number regex now has length limit (10-13 digits) and word boundary
- **P1-15**: Email regex now consistent between `shouldCapture` and `detectCategory` (strict anchored pattern)

### Added
- **P2-16**: Embeddings initialization with retry mechanism (3 attempts with exponential backoff)
- **P2-20**: Input sanitization function to remove HTML tags, control characters, and normalize whitespace
- **P2-21**: Qdrant connection health check on plugin startup (non-blocking, logs warnings if connection fails)

### Security
- Enhanced ReDoS protection with word boundaries in phone number regex
- Input sanitization prevents XSS and injection attacks in stored memories
- All regex patterns now have proper length limits and boundaries

### Testing
- Added comprehensive self-validation test suite (29 tests, 100% pass rate)
- Tests cover: input sanitization, category detection, capture filtering, ReDoS protection, edge cases, Chinese language support

## [1.0.9] - 2026-02-17

### Added
- **Configurable memory limit**: New `maxMemorySize` config option (default: 1000, range: 100-1000000)
  - Users can now customize the maximum number of memories in in-memory mode
  - LRU eviction automatically removes oldest memories when limit is reached
  - Set to 999999 for unlimited storage (no automatic deletion)
  - Only applies to in-memory mode, external Qdrant has no limit
  - Documented in README.md and openclaw.plugin.json with clear help text

### Changed
- Improved startup log to show configured memory limit or "unlimited" status
- Added warning in README about potential memory exhaustion with unlimited mode

## [1.0.8] - 2026-02-17

### Fixed
- **P0 - Memory leak**: Added MAX_MEMORY_STORE_SIZE (1000) limit with LRU eviction for in-memory mode
- **P0 - Version inconsistency**: Synced openclaw.plugin.json version with package.json
- **P1 - ReDoS vulnerability**: Improved regex patterns to prevent catastrophic backtracking
  - Phone number regex: limited to 10-13 digits
  - Email regex: more strict pattern with anchors
- **P1 - Error information leakage**: Changed console.error to api.logger.error
- **P1 - Log level**: Changed frequent info logs to debug level (autoRecall, autoCapture)

### Changed
- Extracted magic numbers to SIMILARITY_THRESHOLDS constant for better maintainability
- Improved code consistency across all search operations

### Security
- Reduced ReDoS attack surface with stricter regex patterns
- Better error handling to prevent information disclosure

## [1.0.7] - 2026-02-17

### Changed
- Optimized SKILL.md following ClawHub best practices
- Shortened description to meet 200-character limit
- Added homepage field pointing to GitHub repository
- Moved detailed installation notes from SKILL.md to README.md
- Simplified SKILL.md Installation section with link to README
- Removed redundant `primaryEnv: null` from metadata

### Documentation
- Enhanced README.md with comprehensive installation requirements
- Added platform-specific build tool instructions
- Added troubleshooting section for common installation issues
- Documented Node.js version requirement (≥18.17)
- Listed all network access requirements and native dependencies

## [1.0.6] - 2026-02-17

### Documentation
- Added comprehensive "Installation Notes" section to SKILL.md
- Documented first-time setup requirements (model download, native dependencies)
- Added platform-specific build tool requirements (Windows/macOS/Linux)
- Clarified Node.js version requirement (≥18.17)
- Listed all network access requirements for transparency
- Provided recommended installation commands for reproducible builds

## [1.0.5] - 2026-02-17

### Internal
- Version skipped due to publishing conflict

## [1.0.4] - 2026-02-16

### Fixed
- Synced local and remote file inconsistencies (autoCapture default, version numbers)
- Added PII warning to autoCapture uiHints and SKILL.md documentation
- Clarified that autoCapture trigger patterns match emails and phone numbers

### Changed
- uiHints labels changed to English for consistency
- Improved autoCapture help text with explicit PII capture warning
- Version bump: openclaw.plugin.json 1.0.0 -> 1.0.4

## [1.0.3] - 2026-02-16

### Documentation
- Simplified SKILL.md following high-star skill patterns
- Added "Use when" statement for clarity
- Condensed features, configuration, and usage sections
- Removed verbose FAQ and implementation details
- Improved description and tags for better discoverability

## [1.0.2] - 2026-02-16

### Documentation
- Added comprehensive Privacy & Security section to README and SKILL.md
- Clarified data storage modes (in-memory vs Qdrant)
- Documented network access behavior (Transformers.js model download)
- Added detailed configuration options with privacy notes
- Included security recommendations for production use

## [1.0.1] - 2026-02-16

### Security
- Removed development documentation files (CODE_REVIEW.md, PHASE*.md, etc.)
- Removed test files that duplicated source code
- Fixed @xenova/transformers version (3.3.1 -> 2.17.2)
- Removed unintended openai dependency from package-lock.json
- Changed autoCapture default from true to false (opt-in for privacy)

### Changed
- Cleaned up repository structure for production use

## [1.0.0] - 2026-02-16

### Added
- Initial release
- Local semantic memory with Qdrant (in-memory mode)
- Transformers.js for local embeddings (Xenova/all-MiniLM-L6-v2)
- Three core tools: `memory_store`, `memory_search`, `memory_forget`
- Automatic memory capture via lifecycle hooks
- Zero-configuration setup

### Technical
- ES6 module system
- Factory function pattern for tool exports
- Compatible with OpenClaw plugin architecture
