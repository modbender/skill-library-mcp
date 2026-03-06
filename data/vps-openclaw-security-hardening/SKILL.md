---
name: vps-openclaw-security-hardening
description: Production-ready security hardening for VPS running OpenClaw AI agents. Includes SSH hardening (custom port), firewall, audit logging, credential management, and intelligent alerting. Follows BSI IT-Grundschutz and NIST guidelines with minimal resource overhead.
version: 1.0.6
author: OpenClaw Community
homepage: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening
metadata:
  openclaw:
    emoji: 🛡️
    requires:
      bins: ["ssh", "ufw", "auditd", "systemctl", "apt-get"]
      optional: ["fail2ban"]
      os: ["ubuntu", "debian"]
    tags: ["security", "hardening", "vps", "audit", "monitoring", "firewall", "ssh", "fail2ban"]
    install: "SSH_PORT=4848 ./scripts/install.sh"
    verify: "./scripts/verify.sh"
    warning: "DO NOT use on machines with sensitive personal data. Use dedicated VPS only. Test in VM first."
---

# VPS Security Hardening for OpenClaw

Production-ready security hardening for AI agent deployments on VPS.

## ⚠️ CRITICAL WARNINGS

**DO NOT run OpenClaw on servers/machines with sensitive personal data.** Use a dedicated machine (VPS, bare-metal, or on-premise server dedicated to OpenClaw).

**Supported OS:** Ubuntu 20.04+, Debian 11+. Not for Windows (use WSL2) or macOS.

## ⚠️ Choose Your SSH Port First

**You must choose a custom SSH port (1024-65535) before installing.** This makes you conscious of the security decision.

```bash
# Choose your port (example: 4848)
export SSH_PORT=4848

# Install
cd ~/.openclaw/skills/vps-openclaw-security-hardening
sudo ./scripts/install.sh

# Verify
./scripts/verify.sh

# Test SSH (new terminal)
ssh -p ${SSH_PORT} root@your-vps-ip
```

## What It Does

| Layer | Protection | Implementation |
|-------|------------|----------------|
| **Network** | Firewall, SSH hardening | UFW, custom port (your choice), key-only |
| **System** | Auto-updates, monitoring | unattended-upgrades, auditd |
| **Secrets** | Credential management | Centralized .env, 600 permissions |
| **Monitoring** | Audit logging, alerting | Kernel-level audit, multi-channel alerts |

## Requirements

- **OS:** Ubuntu 20.04+ or Debian 11+ (Linux only)
- **NOT supported:** Windows (use WSL2), macOS
- Root access
- Existing SSH key authentication
- Alert channel (optional): Telegram, Discord, Slack, Email, or Webhook
- **Custom SSH port of your choice (1024-65535)**

## Security Changes

### SSH
- Port: 22 → ${SSH_PORT} (your choice, 1024-65535)
- Auth: Keys only (no passwords)
- Root login: Disabled
- Max retries: 3
- Fail2ban: Brute-force protection

### Firewall
- Default: Deny incoming
- Allow: Your chosen SSH port only

### Services
- CUPS (printing): Stopped & disabled
- Fail2ban: Intrusion detection enabled
- Auto-updates: Security patches automatic

### Monitoring
- Credential file access tracking
- SSH config change detection
- Privilege escalation alerts
- Daily security briefing

## Resource Usage

| Component | RAM | Disk |
|-----------|-----|------|
| Auditd | ~2 MB | 40 MB max |
| UFW | ~1 MB | Negligible |
| Scripts | ~5 MB | Negligible |
| **Total** | **<10 MB** | **<50 MB** |

## Files

- `scripts/install.sh` - Main installation
- `scripts/verify.sh` - Verify installation
- `scripts/rollback-ssh.sh` - Emergency rollback
- `scripts/critical-alert.sh` - Telegram alerts
- `scripts/daily-briefing.sh` - Daily reports
- `rules/audit.rules` - Audit configuration

## Documentation

See [README.md](README.md) for full documentation.

## License

MIT - See LICENSE file
