# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2026-02-20

### Fixed
- **ClawHub Publication Issues**: Addressed VirusTotal scan concerns
  - fail2ban now marked as optional (was incorrectly listed as required)
  - Added missing cron scripts: `audit-log-monitor.sh`, `weekly-report.sh`
  - **SAFER rollback**: Only resets SSH port, keeps key-only authentication
    - Does NOT re-enable password authentication
    - Does NOT re-enable root login
  - Added explicit "test in VM first" warning

### Security
- Rollback script no longer degrades security posture
- Maintains defense-in-depth even during emergency recovery

## [1.0.5] - 2026-02-10

### Changed
- Removed specific company names from examples (kept generic "Cloud VPS")

## [1.0.4] - 2026-02-10

### Changed
- Clarified machine requirements: VPS, bare-metal, or on-premise servers are all acceptable
- As long as the machine is dedicated to OpenClaw and doesn't contain sensitive data

## [1.0.3] - 2026-02-10

### Added
- **CRITICAL WARNINGS**: Added prominent security warnings
  - DO NOT use on machines with sensitive personal data
  - OS support clearly documented (Ubuntu/Debian only)
  - Windows/macOS explicitly not supported
- **Fail2ban**: Intrusion detection and brute-force protection
- **CUPS**: Printing service automatically stopped and disabled
- **Service hardening**: Documentation of disabled services

### Security
- Defense-in-depth improvements with fail2ban
- Clear warnings about data isolation requirements

## [1.0.2] - 2026-02-10

### Changed
- Multi-channel alerting support (Telegram, Discord, Slack, Email, Webhook)
- Generic alert architecture replacing Telegram-only

## [1.0.1] - 2026-02-10

### Changed
- SSH port is now user-configurable (1024-65535) instead of hardcoded 6262
- Users must consciously choose their port via SSH_PORT environment variable
- Updated documentation with clear port selection guidance
- Added contributing section with contact information

## [1.0.0] - 2026-02-10

### Added
- Initial release of VPS Security Hardening skill
- SSH hardening: custom port (user-defined, 1024-65535), key-only auth, root disabled
- UFW firewall: default deny, SSH port only
- Auditd logging: credential monitoring, SSH config tracking
- Automatic updates via unattended-upgrades
- Telegram alerting for critical security events
- Daily security briefing with risk scoring
- Resource-conscious design (<30MB RAM, <50MB disk)
- Complete documentation and troubleshooting guide
- Verification and rollback scripts

### Security
- Implements BSI IT-Grundschutz controls
- Follows NIST Cybersecurity Framework
- Defense-in-depth architecture

[1.0.5]: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening/releases/tag/v1.0.5
[1.0.4]: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening/releases/tag/v1.0.4
[1.0.3]: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening/releases/tag/v1.0.3
[1.0.2]: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening/releases/tag/v1.0.2
[1.0.1]: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening/releases/tag/v1.0.1
[1.0.0]: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening/releases/tag/v1.0.0
