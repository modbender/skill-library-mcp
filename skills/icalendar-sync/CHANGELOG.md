```markdown
# Changelog

All notable changes to iCloud Calendar Sync will be documented in this file.

## [2.2.6] - 2026-02-12

### Security
- Fixed critical metadata inconsistency in CLAWHUB_METADATA.yaml
- Added explicit required environment variables declaration
- Enhanced security documentation with credential handling best practices

### Changed
- Updated SKILL.md with comprehensive security warnings
- Clarified CLI password exposure risks
- Documented plaintext .env file limitations for production
- Added Docker secrets usage examples

### Fixed
- Registry metadata now correctly reflects ICLOUD_USERNAME and ICLOUD_APP_PASSWORD as required

## [2.2.5] - 2026-02-10

### Added
- Initial iCloud CalDAV synchronization support
- Multi-language support
- Keyring-based credential storage
- Docker deployment support

### Features
- List calendar events
- Create events
- Sync with iCloud CalDAV server
- Support for Linux, macOS, Windows

## [2.2.0] - Earlier versions

See individual version documentation for details.