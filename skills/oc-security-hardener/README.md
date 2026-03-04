# Security Hardener

Automated security auditing and hardening for OpenClaw deployments.

## Features

- **10-Point Security Audit** — Covers gateway, auth, exec, permissions, sessions
- **Auto-Fix** — Apply recommended fixes with automatic backup
- **Secret Scanner** — Detect exposed API keys and tokens in config files
- **Permission Checker** — Verify file permissions on sensitive config files
- **Security Score** — 0-100 score with severity ratings
- **Report Generation** — Markdown report for documentation and compliance
- **No Dependencies** — Pure Python, works on any OpenClaw install

## Installation

```bash
clawhub install security-hardener
```

## Usage

```bash
# Audit (safe, read-only)
python scripts/hardener.py audit

# Fix issues
python scripts/hardener.py fix

# Generate report
python scripts/hardener.py report -o security-audit.md
```

## Why This Matters

After the ClawHavoc incident (341 malicious skills discovered on ClawHub), security is the #1 concern for OpenClaw deployments. This skill helps you:
- Identify common misconfigurations
- Apply community-recommended security settings
- Generate compliance documentation
- Monitor security posture over time

## License

MIT

## Author

Built by OpenClaw Setup Services — Professional AI agent security consulting.

**Need a comprehensive security audit?** Contact us for custom security assessments ($500-$1,200).
