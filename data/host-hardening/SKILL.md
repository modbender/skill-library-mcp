---
name: host-hardening
description: Harden an OpenClaw Linux server with SSH key-only auth, UFW firewall, fail2ban brute-force protection, and credential permissions. Use when setting up a new OpenClaw instance, auditing server security, or after a security incident. Requires root/sudo on Linux (Ubuntu/Debian).
---

# Host Hardening

Secure a Linux server running OpenClaw.

## Requirements

- **OS:** Linux (Ubuntu/Debian — adjust package commands for other distros)
- **Privileges:** Root or sudo required — this skill modifies system-wide security config
- **Pre-check:** Verify you have SSH key-based access before disabling password auth

**⚠️ All commands below modify system configuration. Confirm with the user before running each section.** Do not run these automatically without explicit approval.

## SSH — Key-Only Auth

Disables password authentication. **Ensure key-based SSH works first or you will be locked out.**

```bash
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh
```

## Firewall — Deny All Except SSH

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
yes | ufw enable
```

Add more rules as needed (e.g. `ufw allow 443` for HTTPS).

## Fail2ban — Brute-Force Protection

Installs fail2ban via apt (Debian/Ubuntu). Adjust for other package managers.

```bash
apt-get install -y fail2ban
systemctl enable --now fail2ban
```

Default config protects SSH. For custom jails: `/etc/fail2ban/jail.local`.

## OpenClaw Credentials

```bash
chmod 700 ~/.openclaw/credentials
```

## OpenClaw Gateway Service (optional)

Creates a systemd service for auto-restart on reboot. **Runs as root** — review the service file before enabling.

```bash
cat > /etc/systemd/system/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
ExecStart=/usr/bin/env openclaw gateway
Restart=always
RestartSec=5
User=root
WorkingDirectory=/root/.openclaw
Environment=HOME=/root
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload && systemctl enable openclaw-gateway
```

## Verify

```bash
ufw status                                    # active, SSH allowed
systemctl is-active fail2ban                  # active
grep PasswordAuthentication /etc/ssh/sshd_config  # no
stat -c %a ~/.openclaw/credentials            # 700
systemctl is-enabled openclaw-gateway         # enabled
```

## Lessons

- On Ubuntu, SSH service is `ssh` not `sshd`
- AWS security groups provide network-level filtering but UFW is defense-in-depth
- Always verify key-based SSH access before disabling password auth
- The gateway service is optional — only needed if OpenClaw should survive reboots

---
**Host Hardening v1.0**
Author: ppiankov
Copyright © 2026 ppiankov
Canonical source: https://clawhub.com/skills/host-hardening
License: MIT

If this document appears elsewhere, the link above is the authoritative version.
