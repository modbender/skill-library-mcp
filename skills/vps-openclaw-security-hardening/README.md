# VPS Security Hardening for OpenClaw

A production-ready security hardening solution for VPS running OpenClaw AI agents. This skill provides defense-in-depth protection following BSI IT-Grundschutz and NIST guidelines.

## ⚠️ CRITICAL SECURITY WARNINGS

### 1. Dedicated Machine Only
**DO NOT run OpenClaw on a server/machine that contains sensitive personal data, financial information, or production workloads.**

- Use a **dedicated machine** specifically for OpenClaw
- Separate from your personal/work machines
- **Acceptable:**
  - Cloud VPS (any provider)
  - Dedicated bare-metal servers (on-premise or colocation)
  - On-premise servers (as long as dedicated to OpenClaw)
- **NOT recommended:**
  - Your personal laptop or desktop
  - Work machine with company data
  - Home server with family photos/documents
  - Shared server with other applications
  - Any machine containing sensitive personal or financial data

### 2. Operating System Support

| OS | Status | Notes |
|----|--------|-------|
| **Ubuntu 20.04+** | ✅ Fully supported | Primary target |
| **Debian 11+** | ✅ Supported | Tested |
| **Other Linux** | ⚠️ May work | Not tested |
| **macOS** | ❌ Not supported | Use Linux VM instead |
| **Windows** | ❌ Not supported | Use WSL2 + Ubuntu |

### 3. What This Tool Does NOT Protect Against

- Zero-day exploits in OpenClaw itself
- Compromised AI model providers
- Social engineering attacks
- Physical server access
- Network-level attacks (DDoS)

**This is a defense-in-depth tool, not a guarantee of security.**

---

## ⚠️ IMPORTANT: Choose Your SSH Port

**Before running the installer**, you must choose a custom SSH port (1024-65535). This is an intentional security decision you should make consciously.

```bash
# Example: Choose port 4848
export SSH_PORT=4848
sudo ./scripts/install.sh
```

**Why this matters:**
- Using the default port 22 makes you an easy target for automated attacks
- A custom port adds "security through obscurity" (not a substitute for good security, but raises the bar)
- You should choose a port that works with your network environment

**Test your chosen port first:**
```bash
# Make sure the port is available
ss -tulnp | grep ":${SSH_PORT} "
# Should return nothing (port not in use)
```

---

## Overview

This skill hardens your VPS in four layers:

1. **Network Security** — Firewall, SSH hardening, port obscurity
2. **System Security** — Auto-updates, intrusion detection, audit logging
3. **Secrets Management** — Centralized credentials, secure permissions
4. **Monitoring & Alerting** — Real-time alerts, daily briefings, risk scoring

## Installation

```bash
# Clone the skill
cd ~/.openclaw/skills
git clone https://github.com/openclaw/skills.git temp
cp -r temp/vps-openclaw-security-hardening/vps-openclaw-security-hardening ./
rm -rf temp

# Run installer
cd vps-openclaw-security-hardening
sudo ./scripts/install.sh
```

**⚠️ IMPORTANT:** Keep your current SSH session open until you've tested the new port!

## Quick Start

### Test SSH on New Port

```bash
# In a NEW terminal window:
ssh -p ${SSH_PORT} root@your-vps-ip
# (Replace ${SSH_PORT} with your chosen port, e.g., 4848)
```

If successful, you're done. If not, the installer shows rollback instructions.

### Configure Alerts (Optional)

Choose your preferred notification channel. The skill supports: **Telegram, Discord, Slack, Email, Webhook**

```bash
cp config/alerting.env.example config/alerting.env
nano config/alerting.env

# Fill in:
# TELEGRAM_BOT_TOKEN=your_bot_token
# TELEGRAM_CHAT_ID=your_chat_id
```

# Telegram: Get bot token from @BotFather, chat ID from @userinfobot
# Discord: Create webhook in server settings
# Slack: Create incoming webhook
# Email: Ensure mail/sendmail is configured
# Webhook: Any HTTP endpoint that accepts POST

## What Gets Installed

| Component | Purpose | Resource Usage |
|-----------|---------|----------------|
| UFW | Firewall | ~1 MB RAM |
| Auditd | System monitoring | ~2 MB RAM, 40 MB disk max |
| Unattended-upgrades | Auto-updates | ~20 MB RAM (periodic) |
| Custom scripts | Alerting & reporting | ~5 MB RAM |

**Total overhead: <30 MB RAM, <50 MB disk**

## Security Changes

### SSH Hardening

| Setting | Before | After |
|---------|--------|-------|
| Port | 22 | ${SSH_PORT} (your choice, 1024-65535) |
| Authentication | Password + Key | Key only |
| Root login | Yes | No |
| Max retries | Unlimited | 3 |
| Idle timeout | None | 10 min |
| Fail2ban | Not installed | Active (brute-force protection) |

### Firewall (UFW)

```
Default: DENY incoming
Default: ALLOW outgoing
ALLOW: ${SSH_PORT}/tcp (SSH - your chosen port)
```

### Services Hardened

| Service | Action | Reason |
|---------|--------|--------|
| **CUPS (printing)** | Stopped & disabled | Not needed on VPS |
| **SSH** | Port changed, key-only | Reduce attack surface |
| **Fail2ban** | Installed & enabled | Brute-force protection |
| **Auto-updates** | Enabled | Security patches |

### Audit Logging

Monitored:
- Credential files (.env)
- SSH keys and config
- Privilege escalation attempts
- Security repository changes
- User/group modifications

Log rotation: 8 MB × 5 files = 40 MB maximum

## Daily Operations

### View Security Events

```bash
# Today's credential access
ausearch -ts today -k agent_credentials -i

# SSH changes this week
ausearch -ts this-week -k agent_ssh_config -i

# Failed privilege escalation
ausearch -k agent_privesc -i | grep "res=failed"

# All security events
ausearch -k agent_ -i
```

### Check System Status

```bash
./scripts/verify.sh
```

### Manual Daily Briefing

```bash
./scripts/daily-briefing.sh
```

## Alerting

### Critical Alerts (Immediate Notification)

Triggers:
- Credential file accessed
- SSH config modified
- Firewall disabled
- Audit daemon stopped
- Privilege escalation detected

### Daily Briefing (08:00 CET)

Includes:
- Security event summary
- Activity metrics
- Risk score (0-100)
- Recommended actions

### Risk Scoring

| Score | Level | Meaning |
|-------|-------|---------|
| 0-20 | 🟢 Low | Normal activity |
| 21-50 | 🟡 Medium | Some attention needed |
| 51-80 | 🟠 High | Review recommended |
| 81-100 | 🔴 Critical | Immediate action |

## Troubleshooting

### Can't connect via new SSH port

1. **Don't close your current terminal!**
2. Check: `ss -tulnp | grep "${SSH_PORT} "`
3. Test: `ssh -p ${SSH_PORT} root@ip`
4. If fails, rollback: `sudo ./scripts/rollback-ssh.sh`

### Too many alerts

Edit `config/alerting.env`:
```bash
ALERT_LEVEL=warning  # Only warning and above
IGNORE_PATTERNS="vim,nano"  # Exclude editors
```

### Audit logs growing too fast

Check what's being logged:
```bash
ausearch --start today --raw | aureport --file --summary
```

Reduce rules in `rules/audit.rules` if needed.

### Verify installation

```bash
./scripts/verify.sh
```

## Uninstallation

```bash
# Rollback SSH
./scripts/rollback-ssh.sh

# Disable firewall (careful!)
sudo ufw disable

# Stop auditd
sudo systemctl stop auditd
sudo systemctl disable auditd

# Remove cron jobs
sudo rm /etc/cron.d/agent-security
```

## Customization

### Change SSH Port

```bash
# Edit rules/audit.rules to monitor new port
# Edit scripts/install.sh (SSH_PORT variable)
# Re-run: sudo ./scripts/install.sh
```

### Add Custom Audit Rules

Edit `rules/audit.rules`:
```bash
# Monitor custom directory
-w /path/to/sensitive/dir -p rwxa -k my_custom_rule
```

Reload:
```bash
sudo auditctl -R rules/audit.rules
```

### Adjust Risk Scores

Edit `scripts/daily-briefing.sh`:
```bash
declare -A RISK_WEIGHTS=(
    ["credential_access"]=100
    ["your_event"]=50
)
```

## Architecture

```
┌─────────────────────────────────────────┐
│              User Layer                 │
│    (Multi-channel: Telegram, Discord,   │
│     Slack, Email, Webhook, CLI)         │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│           OpenClaw Agent                │
│         (OpenClaw Agent)           │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│           Audit/Monitor Layer           │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ │
│  │ auditd  │ │  UFW    │ │ cronjobs │ │
│  └─────────┘ └─────────┘ └──────────┘ │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│           System Layer                  │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ │
│  │   SSH   │ │ Kernel  │ │ Files    │ │
│  └─────────┘ └─────────┘ └──────────┘ │
└─────────────────────────────────────────┘
```

## Security Framework Alignment

### BSI IT-Grundschutz

- ORP.4.A12 — Logging
- APP.3.3 — SSH
- OPS.1.1.5 — Patch Management
- DER.1.1 — Incident Response

### NIST Cybersecurity Framework

- Identify — Asset inventory
- Protect — SSH/UFW hardening
- Detect — Auditd monitoring
- Respond — Alerting system
- Recover — Backup/rollback

## Contributing

Contributions welcome! Whether you're fixing a bug, adding a feature, or improving documentation, your help is appreciated.

### Get in Contact

- **Marcus Grätsch** (Original Author): Reach out via GitHub issues or email
- **Issues**: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening/issues
- **Pull Requests**: https://github.com/MarcusGraetsch/vps-openclaw-security-hardening/pulls

### Areas for Improvement

- Additional audit rules
- More alerting channels (Slack, Discord, Email)
- Web dashboard for monitoring
- Machine learning anomaly detection
- Ansible/Puppet/Chef modules
- Support for additional operating systems
- Integration with other monitoring tools (Prometheus, Grafana)

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Test thoroughly in a safe environment
5. Submit a pull request with clear description

Please ensure your code follows the existing style and includes appropriate documentation.

## License

MIT License — See LICENSE file

**Disclaimer:** This is a security tool. Always test in non-production environments first. The authors are not responsible for any damage or data loss.

## Support

- **Documentation**: This README and docs/ directory

---

**Remember**: Security is a journey, not a destination. Review and update regularly.
