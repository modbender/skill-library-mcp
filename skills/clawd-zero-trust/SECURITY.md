# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | ✅ Active  |
| 1.0.x   | ⚠️ Critical fixes only |
| < 1.0   | ❌ No longer supported |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report privately via email: **info@blocksoft.tech**

Include:
- Description of the vulnerability
- Steps to reproduce
- Impact assessment (what can an attacker achieve?)
- Your suggested fix (optional but appreciated)

### What to expect

| Timeline | Action |
|----------|--------|
| 48 hours | Acknowledgement of your report |
| 7 days   | Initial assessment and severity classification |
| 30 days  | Fix developed and tested |
| 90 days  | Public disclosure (coordinated with reporter) |

We follow responsible disclosure. If you report a valid vulnerability, we will credit you in the release notes unless you prefer to remain anonymous.

## Scope

**In scope:**
- `egress-filter.sh` — firewall policy logic, rollback paths, hash gate bypass
- `harden.sh` — config mutation, privilege escalation vectors
- `audit.sh` — false-positive suppression that could hide real threats
- `release-gate.sh` — gate bypass that could allow unsigned/untested code to ship

**Out of scope:**
- Vulnerabilities in UFW, OpenClaw, or third-party dependencies
- Issues requiring physical access to the host
- Social engineering

## Security Design

This skill is security infrastructure. It has been audited through a dual-model review process (GPT-5.3 + Sonnet 4.6) before each release. All known false positives are documented in `references/false-positives.md`.

Known non-Human Identity (NHI) patterns that may trigger security scanners but are intentional:
- `openclaw-agentsandbox` — legitimate OAuth key generation
- `secureclaw` — legitimate auditing engine

See `references/false-positives.md` for details.
