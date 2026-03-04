# Changelog

All notable changes to the Porkbun DNS skill will be documented in this file.

## [1.0.0] - 2026-02-10

### Added
- Initial release of Porkbun DNS management skill
- CLI tool `scripts/porkbun-dns.js` for all DNS operations
- Support for common record types: A, AAAA, CNAME, MX, TXT, NS, ALIAS, SRV, TLSA, CAA, HTTPS, SVCB, SSHFP
- Domain listing and status checking
- DNS record create, read, update, delete (CRUD) operations
- Batch operations: edit/delete by type and subdomain
- Configuration via environment variables or config file
- Full SKILL.md documentation with examples

### Features
- **Ping**: Test API connection
- **List domains**: View all domains with status and expiration
- **Records**: Get all DNS records for a domain
- **Create**: Add new DNS records with full control (type, name, content, TTL, priority)
- **Edit**: Update records by ID or by type/subdomain
- **Delete**: Remove records by ID or by type/subdomain
- **Get**: Retrieve specific records with filtering by type and/or name

### Documentation
- Complete SKILL.md with API reference and usage examples
- README.md with quick start guide
- Inline tool help (`node porkbun-dns.js --help`)

---

## [1.0.1] - 2026-02-11

### Added
- `package.json` with complete OpenClaw skill metadata
- `CHANGELOG.md` for version tracking
- `LICENSE` (MIT) for proper licensing

### Changed
- `package.json` now explicitly declares required environment variables (`PORKBUN_API_KEY`, `PORKBUN_SECRET_API_KEY`)
- Documented config file path: `~/.config/porkbun/config.json`
- Updated `README.md` with enhanced installation instructions
- Added references to CHANGELOG, LICENSE, and package.json in README

### Security
- Addressed security scanner recommendations by transparently declaring credential requirements
- Clearly documented where credentials are stored and how they're used

---

## [Unreleased]

### Planned
- DNS record validation before submission
- Bulk record import/export
- DNSSEC management support
- Zone file import/export
- Webhook notifications for DNS changes
- Rate limit handling

---

## Version Guidelines

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Backwards-compatible functionality additions
- **PATCH** version: Backwards-compatible bug fixes

## Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerabilities