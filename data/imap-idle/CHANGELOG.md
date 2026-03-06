# Changelog

All notable changes to this project will be documented in this file.

## [1.4.0] - 2026-02-11

### Fixed
- **Removed personalized hardcoded behavior** - Generalized GitHub notification handling to work for any user
  - Removed hardcoded email check (`a.parmeev@jakeberrimor.com`)
  - Removed hardcoded mention pattern (`@arkasha-ai`)
  - Now detects GitHub notifications generically for any account
- **Removed duplicate/dead code** - Cleaned up unused functions at end of file
- **Improved GitHub notification detection** - Generic pattern matching for mentions, reviews, assignments

### Changed
- GitHub notifications now use generic detection patterns instead of hardcoded usernames
- Batch notification text changed from Russian to English for broader audience
- Notification icons and formatting remain the same

### Security
- Addressed ClawHub security scan concerns about personalized code
- No behavior changes for end users - skill works the same, just more generic

## [1.3.0] - 2026-02-06

### Added
- Keyring support for secure password storage
- SECURITY.md with deployment best practices
- Debouncing to batch rapid email notifications

### Changed
- Improved GitHub notification formatting
- Better UID tracking to prevent duplicates

## [1.2.0] - 2026-02-05

### Added
- GitHub notification special handling
- Smart batching for multiple emails

## [1.1.0] - 2026-02-04

### Added
- UID tracking to prevent duplicate webhooks
- Exponential backoff for reconnects

## [1.0.0] - 2026-02-03

### Added
- Initial release
- IMAP IDLE monitoring for multiple accounts
- OpenClaw webhook integration
- Debounced notifications
