# Changelog: Gumroad Pro

## [1.2.9] - 2026-02-14
### Fixed
- **Packaging Coherence**: Reconciled "packaging drift" by synchronizing versioning and metadata across `package.json`, `_meta.json`, and `SKILL.md`.
- **Manifest Standards**: Added missing `homepage` links and strictly declared `GUMROAD_ACCESS_TOKEN` as a required environment variable for registry-level transparency.

## [1.2.5] - 2026-02-14
### Added
- Feature: **Product-Specific Sales View**. You can now view a filtered list of transactions directly from any product's management menu.
- **Improved Pagination**: Removed 10-item slicing in Sales menu to show full API pages (20 items). Optimized navigation row to consistently offer a "First Page" return path.
- Created `package.json` for formal Node.js structure.
- Created `references/handler-guide.md` for AI interaction protocols.
- Created `references/ui-rendering.md` for adaptive button documentation.
- Created `references/api-reference.md` for detailed CLI command specifications.

### Changed
- **Security**: Refactored `handler.js` to use native `https` over `spawnSync` (removes broad environment forwarding).
- **Privacy**: Transitioned multi-step state from `pending_input.json` (on-disk) to `ctx.session` (in-memory).
- **Authentication**: Standardized on `GUMROAD_ACCESS_TOKEN` with a fallback to `API_KEY`.
- **OpenClaw Integration**: Added `primaryEnv` metadata to `_meta.json` for `apiKey` convenience.
- **AI Protocol**: Updated `SKILL.md` to prioritize `handler.js` (GUI) over CLI.

### Removed
- Deleted root `CHANGELOG.md` (moved to references).
- Deleted `pending_input.json` (state is now session-scoped).
- Removed legacy token fallback logic.
