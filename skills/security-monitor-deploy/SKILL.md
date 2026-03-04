---
name: security-monitor
description: Comprehensive security audit for OpenClaw deployments. Checks Docker port bindings, SSH config, openclaw.json settings, file permissions, exposed services, and firewall rules. Scores your deployment 0-100 with actionable recommendations. Use for security hardening and compliance checks.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Docker, OpenClaw gateway, Linux
metadata: {"openclaw": {"emoji": "\ud83d\udee1\ufe0f", "requires": {"bins": ["docker"]}, "homepage": "https://www.agxntsix.ai"}}
---

# Security Monitor 🛡️

**Comprehensive security audit for OpenClaw deployments.**

Scans your Docker configuration, SSH settings, firewall rules, OpenClaw config, and file permissions. Produces a security score (0-100) with actionable recommendations.

## Quick Start

```bash
# Run full audit
bash {baseDir}/scripts/security_audit.sh

# JSON output
bash {baseDir}/scripts/security_audit.sh --json

# Specific checks only
bash {baseDir}/scripts/security_audit.sh --check docker
bash {baseDir}/scripts/security_audit.sh --check ssh
bash {baseDir}/scripts/security_audit.sh --check config
bash {baseDir}/scripts/security_audit.sh --check files
bash {baseDir}/scripts/security_audit.sh --check network
```

## What It Checks

### OpenClaw Config (25 points)
- `allowInsecureAuth` must be `false`
- `dmPolicy` must not be open/allow-all
- Port bindings must use `127.0.0.1`
- API keys not hardcoded in config
- Secure model permissions

### Docker Security (25 points)
- All port bindings use `127.0.0.1` (not `0.0.0.0`)
- No privileged containers (except necessary)
- Docker socket permissions
- Container resource limits
- No `--net=host` unless needed

### SSH Configuration (20 points)
- Root login disabled (`PermitRootLogin no`)
- Password authentication disabled
- Key-based auth only
- Non-standard port (bonus)
- Fail2ban or similar active

### Network & Services (15 points)
- No unnecessary exposed ports
- Firewall active (ufw/iptables)
- Only expected services listening
- HTTPS/TLS termination configured

### File Permissions (15 points)
- openclaw.json not world-readable
- SSH keys proper permissions (600)
- .env files not world-readable
- Docker socket permissions
- No sensitive files in /tmp

## Scoring

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | 🟢 Excellent | Production-ready |
| 70-89 | 🟡 Good | Minor improvements needed |
| 50-69 | 🟠 Fair | Several issues to address |
| 0-49 | 🔴 Critical | Immediate action required |

## Output Example

```
═══ Security Audit Report ═══
Date: 2026-02-15 00:30:00

[CONFIG] ✅ allowInsecureAuth: false
[CONFIG] ✅ dmPolicy: allowlist
[CONFIG] ✅ Ports bound to 127.0.0.1
[DOCKER] ✅ All containers bind to 127.0.0.1
[DOCKER] ⚠️  No resource limits on openclaw container
[SSH]    ✅ Root login disabled
[SSH]    ✅ Password auth disabled
[NET]    ✅ UFW active
[FILES]  ✅ Config file permissions OK

Score: 92/100 — 🟢 Excellent
Issues: 1 warning

Recommendations:
  1. Add resource limits to Docker containers
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
