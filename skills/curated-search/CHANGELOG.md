# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.org/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.7] - 2026-02-18

### Fixed

- **Security manifests:** Added security manifest headers to all executable scripts (`scripts/search.js`, `scripts/crawl.js`, `scripts/validate-config.js`, `scripts/health-check.js`, `scripts/curated_search`, `scripts/publish-clean.sh`) declaring environment variables, external endpoints, and file access patterns
- **Compliance:** Updated to meet ClawHub security guidelines for script documentation

---

## [1.0.6] - 2026-02-18

### Fixed

- **Publishing compliance:** Added required sections to `SKILL.md` (External Endpoints, Security & Privacy, Model Invocation Note, Trust Statement)
- **Updated frontmatter:** Added `version`, `author`, `license`, `homepage`, and `emoji` to meet ClawHub manifest standards
- **Removed conflicting manifest:** Deleted `skill.json` to avoid duplicate manifest issues; `SKILL.md` is now the sole source of truth
- **Improved .clawhubignore:** Excluded root-level test files (`test*.js`, `test-indexer.js`, `test-mini.js`) and `jest.config.js` to prevent “suspicious” flags from unused code in the bundle
- **Removed unused test artifacts** from packaging

---

## [1.0.5] - 2026-02-14

### Security
- Added `metadata.openclaw.requires.bins: ["node"]` to SKILL.md to declare Node.js runtime requirement
- This resolves ClawHub security scan "suspicious" flag due to missing required binaries declaration

## [1.0.4] - 2026-02-14

### Security
- **Removed legacy network server component** (`src/search-api.js`) that was never used but present in repo, reducing attack surface
- Updated README.md to remove legacy references
- Improved `.clawhubignore` to exclude internal audit files (`*AUDIT*.md`, `*CRITICAL*.md`, `SYS_*`, `YACY_*`, etc.)
- No functional changes to the search tool

## [1.0.3] - 2026-02-14

### Security
- Fixed accidental inclusion of internal audit documents in published package
- Updated `.clawhubignore` to exclude `*AUDIT*.md`, `*CRITICAL*.md`, `SYS_*`, `YACY_*`, and related internal notes
- No functional changes to the skill itself

## [1.0.0] - 2025-02-12

### Added
- First public release of Curated Search
- Domain-restricted crawling with curated whitelist
- Full-text search over MiniSearch index
- OpenClaw native integration
- Configurable crawl parameters (depth, delay, timeout)
- Content extraction with site-specific selectors
- Robots.txt compliance and rate limiting
- State checkpointing and resume
- Health monitoring and graceful shutdown
- Jest test suite with coverage targets
- Comprehensive documentation (README, SKILL, deployment)

---

**Note:** This changelog starts with the initial release (1.0.0). Future updates will list changes under `[Unreleased]` and move versions downward.
