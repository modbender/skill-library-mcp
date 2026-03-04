# Changelog

All notable changes to this project will be documented in this file.

## [1.0.1] - 2026-02-17
### Fixed
- Removed redundant generated images from `assets/` directory.
- Cleaned up project root to ensure only essential files are packaged.

## [1.0.0] - 2026-02-17
### Added
- Professional horizontal PPT-style reporting.
- 30-day SVG trend lines and model efficiency metrics.
- Anthropic prompt caching (read/write) savings tracking.
- Multi-dimensional charts for token breakdown and provider distribution.
- SQLite persistence layer for fast querying.
- Automatic session log detection for OpenClaw/Clawdbot.

### Changed
- **Major Rename**: Project changed from `llm-cost-monitor` to `usage-visualizer` to better reflect focus on usage analytics and high-fidelity visualization.
- Refactored project structure: moved assets to `/assets`, cleaned up redundant scripts.
- Updated documentation and skill metadata for improved discovery.
