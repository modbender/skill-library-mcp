# Changelog: TeraBox Link Extractor

## [1.4.0] - 2026-02-14
### Fixed
- **Total Audit Remediation**: Forced perfectly synchronized metadata state across all manifest files (`package.json`, `_meta.json`, `SKILL.md`).
- **Standardized Credentials**: Purged all legacy `API_KEY` and `apiKey` identifiers. The skill now strictly uses `TERABOX_API_KEY`.
- **Informed Consent Protocol**: Implemented mandatory user permission step in `SKILL.md` instructions to protect privacy.
- **Auto-Trigger Refactor**: Removed redundant automatic execution from `handler.js` to ensure the AI follows the consent protocol.

## [1.3.8] - 2026-02-14
### Fixed
- **Documentation**: Purged stale "Gumroad" references from `api-reference.md` and updated it to reflect the current XAPIverse implementation.
- **Character Encoding**: Fixed broken emoji icons in the extraction report.
- **Standardization**: Performed a final, conclusive purger of legacy `API_KEY` references in favor of the standardized `TERABOX_API_KEY`.

## [1.3.7] - 2026-02-14
### Fixed
- **Registry Synchronization**: Added `openclaw` metadata field to `package.json` to eliminate discrepancy between registry-level and package-level declarations.
- **Documentation**: Corrected internal relative links in `SKILL.md` to ensure they resolve correctly across all platform views.

## [1.3.6] - 2026-02-14
### Fixed
- **Audit Compliance**: Resolved "Suspicious" rating by implementing a **Informed Consent Protocol**. The AI is now instructed to ask for permission before transmitting URLs to the third-party API.
- **Metadata Alignment**: Synchronized `package.json`, `_meta.json`, and `SKILL.md` to ensure consistent declarations of `node` and `TERABOX_API_KEY`.
- **Credential Standardization**: Unified all secret handling to `TERABOX_API_KEY`, removing inconsistent fallback naming.
- **Documentation**: Updated configuration guides to match actual secret mapping in `openclaw.json`.

## [1.3.5] - 2026-02-14
### Fixed
- **Environment Validation**: Removed `API_KEY` from the hard `requires.env` list to prevent platform validation errors on systems where only `TERABOX_API_KEY` is configured.

## [1.3.4] - 2026-02-14
### Added
- **Strict AI Protocol**: Optimized `SKILL.md` with assertive instructions to ensure the LLM triggers extraction automatically and uses the mandatory text-only reporting format for all asset metadata and links.

## [1.3.3] - 2026-02-14
### Fixed
- **Missing Metadata**: Restored `Duration` to the extraction report and CLI output. 
- **Enhanced Details**: Added `Type` and `Quality` metadata to the markdown report to provide more context for extracted assets.

## [1.3.2] - 2026-02-14
### Added
- **Dynamic Resolution Support**: Refactored the stream link generator to dynamically iterate over all available resolutions (360p, 480p, 720p, etc.) provided by the API, rather than relying on hardcoded checks.

## [1.3.1] - 2026-02-14
### Changed
- **Text-Only Response**: Replaced the interactive button UI with a comprehensive text-only report. Extraction results now include names, sizes, durations, and all available stream/download links directly in the message body for easier sharing and accessibility.
- **Removed Interactivity**: Stripped out `tb:main`, `tb:ask_url`, and button-based download triggers in favor of a lean, protocol-driven extraction flow.

## [1.3.0] - 2026-02-14
### Changed
- **Modular Architecture**: Eliminated `spawnSync` from `handler.js`. Core extraction and download logic is now modularized in `extract.js` and called directly as async functions. This significantly improves performance and stability in multi-user environments.

## [1.2.9] - 2026-02-14
### Added
- **Adaptive UI**: Created `handler.js` for interactive, button-based link extraction via the OpenClaw GUI.
- **Formal Structure**: Added `package.json` for standardized Node.js project management.
- **Reference Docs**: Established `references/` directory with `api-reference.md` and `changelog.md`.

### Fixed
- **Packaging Coherence**: Synchronized versioning across all manifests and source code to v1.2.9.
- **Security Hardening**: Implemented strict path isolation for downloads and improved credential handling for `TERABOX_API_KEY`.
- **OpenClaw Compliance**: Updated `SKILL.md` frontmatter with load-time metadata (`requires` blocks).
