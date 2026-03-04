---
name: host-hardening
description: Harden an OpenClaw Linux server with SSH key-only auth, UFW firewall, fail2ban brute-force protection, and credential permissions. Use when setting up a new OpenClaw instance, auditing server security, or after a security incident.
---

# Host Hardening

Secure a Linux server running OpenClaw in under 2 minutes.

## SSH — Key-Only Auth

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

```bash
apt-get install -y fail2ban
systemctl enable --now fail2ban
```

Default config protects SSH. For custom jails: `/etc/fail2ban/jail.local`.

## OpenClaw Credentials

```bash
chmod 700 ~/.openclaw/credentials
```

## OpenClaw Gateway Service

Auto-restart on reboot:

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
- Always verify you have key-based SSH access before disabling password auth
