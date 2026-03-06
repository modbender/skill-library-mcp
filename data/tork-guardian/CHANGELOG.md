# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-02-06

### Added

- **Core governance**: TorkGuardian class with LLM request and tool call interception
- **PII redaction**: Automatic detection and redaction of emails, SSNs, phone numbers, credit cards
- **Compliance receipts**: Cryptographic audit trail for every governed interaction
- **Policy enforcement**: Configurable strict/standard/minimal policies
- **Shell command governance**: Block dangerous commands (rm -rf, chmod 777, fork bombs)
- **File access control**: Whitelist/blacklist paths to protect secrets and credentials
- **Network security**: Port binding validation, egress filtering, SSRF prevention against private networks
- **Reverse shell detection**: Pattern matching across 11+ shell signatures (bash, nc, python, perl, ruby, php, socat, mkfifo, powershell)
- **Network compliance receipts**: Timestamped audit trail for port binds, egress, DNS, and denied requests
- **Default + strict network policies**: Pre-configured for development and enterprise lockdown
- **NetworkMonitor**: Real-time connection tracking with anomaly detection
- **Security scanner**: 14 detection rules (SEC-001 through SEC-007, NET-001 through NET-007)
- **Risk scoring**: Severity-weighted scoring system (critical=25, high=15, medium=8, low=3), capped at 100
- **Verdict system**: Automatic classification as verified (< 30), reviewed (30-49), or flagged (>= 50)
- **Tork Verified badge system**: Generate markdown and JSON badges for skill READMEs
- **CLI**: `tork-scan` command with `--json`, `--verbose`, `--strict` flags
- **4 example configurations**: minimal, development, production, enterprise
- **104 tests**: Full coverage across network access, scanner rules, and badge generation
- **0 TypeScript errors**: Strict mode, full type safety
