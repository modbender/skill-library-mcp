# Changelog

All notable changes to the VibeTrading Global Signals skill will be documented in this file.

## [1.1.0] - 2026-02-12

### Changed
- **BREAKING CHANGE**: Updated API base URL from `https://datahub-prd.fmcp.xyz/api/v1` to `https://vibetrading.dev/api/v1`
- Updated all script files to use the new API endpoint
- Updated SKILL.md documentation with new API examples
- Updated README.md with new debug commands
- Updated package.json version to 1.1.0

### Fixed
- Resolved API connectivity issues (original domain was returning 521 errors)
- Improved proxy support with https-proxy-agent dependency

### Added
- Better error handling for API responses
- Enhanced console output formatting
- Support for all signal types: NEWS_ANALYSIS, FUNDING_RATE, TECHNICAL_INDICATOR, WHALE_ACTIVITY

### Notes
- The original API server (datahub-prd.fmcp.xyz) was experiencing downtime
- New API endpoint provides the same functionality with improved reliability
- No authentication required - API remains open and accessible

## [1.0.0] - 2026-02-11

### Added
- Initial release of VibeTrading Global Signals skill
- Three main scripts:
  - `get_latest_signals.js` - Get latest signals for multiple symbols
  - `get_signals_by_symbol.js` - Get signals for a specific symbol
  - `get_signals_by_type.js` - Get signals by symbol and type
- Support for four signal types
- Beautiful console output with sentiment analysis
- OpenClaw skill metadata integration