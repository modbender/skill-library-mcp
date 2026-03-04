# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Security hardening following ClawHub scanner feedback:
  - Removed insecure TLS bypass configuration
  - Enforced localhost-only Bridge host policy
  - Hardened IMAP search query parsing and input sanitization
- README now includes a clear Security Feedback Response section with remediation details

### Added
- Initial project structure
- IMAP client foundation for reading ProtonMail emails
- SMTP client foundation for sending emails via Bridge
- Tool definitions for OpenClaw integration
- Comprehensive documentation (README, SKILL.md, CONTRIBUTING)
- Security policy (SECURITY.md)
- Code of Conduct
- MIT License
- TypeScript build configuration
- Example configuration files
- Environment variable support (PROTONMAIL_ACCOUNT, PROTONMAIL_BRIDGE_PASSWORD)
- Proper OpenClaw skill config format (`skills.entries.protonmail`)

### Changed
- Updated nodemailer to v8.0.1 (security fixes)
- Installation script now copies files instead of symlinking
- Config reads from environment variables (OpenClaw standard pattern)
- Made config parameter optional (reads from env vars)
- Metadata in SKILL.md now single-line JSON (OpenClaw requirement)

### Fixed
- Added missing @types/mailparser dependency
- Security vulnerabilities in nodemailer
- Installation path (now uses ~/.openclaw/skills/protonmail)
- Config format (now uses skills.entries.* structure)
- Build errors due to missing type definitions

### Notes
- This is a pre-release version
- Core IMAP/SMTP implementations are in progress
- Not yet ready for production use

## [0.1.1] - 2026-02-26

### Security
- Removed insecure TLS override behavior
- Enforced localhost-only Bridge host policy
- Hardened IMAP search query parsing/sanitization

### Documentation
- Added explicit Security Feedback Response details in README
- Added security advisory (`docs/SECURITY-ADVISORY-2026-02-26.md`)
- Added upgrade notice directing `0.1.0` users to patch release

## [0.1.0] - 2026-02-16

### Initial Release
- Project created and published to GitHub
- Foundation laid for ProtonMail integration via Proton Mail Bridge
- Community-driven development begins

---

## Versioning Guide

- **MAJOR** version when making incompatible API changes
- **MINOR** version when adding functionality in a backwards compatible manner
- **PATCH** version when making backwards compatible bug fixes

## Links

- [Latest Release](https://github.com/rvacyber/openclaw-protonmail-skill/releases/latest)
- [All Releases](https://github.com/rvacyber/openclaw-protonmail-skill/releases)
- [Issue Tracker](https://github.com/rvacyber/openclaw-protonmail-skill/issues)
