# Security Guide

## Overview

This skill legitimately handles IMAP credentials and sends email notifications to your OpenClaw Gateway. This document explains security implications, best practices, and why VirusTotal flags this as "suspicious."

## Why VirusTotal Flags This Skill

Automated security scanners flag this skill because it:

1. **Reads credentials** - Required to connect to your IMAP server
2. **Sends email content** - Required to notify OpenClaw of new emails
3. **Makes network connections** - Required for IMAP and webhook calls

These patterns are identical to credential stealers and data exfiltration malware. However, this is **required functionality** for an email monitoring tool.

### What This Skill Does NOT Do

- ❌ Send data to third-party servers (only YOUR webhook)
- ❌ Exfiltrate credentials to external endpoints
- ❌ Include hidden backdoors or obfuscated code
- ❌ Attempt prompt injection or social engineering
- ❌ Modify files outside skill directory

### Verification

Before using ANY skill that handles credentials:

1. **Read the source code** - It's open and documented
2. **Check webhook destination** - Points to YOUR OpenClaw Gateway
3. **Review network calls** - Only IMAP server + local webhook
4. **Check author reputation** - Public GitHub profile + Moltbook

## Password Storage Options

### Desktop/Laptop Users (Recommended: Keyring)

**Use system keyring for true security improvement.**

#### Supported Platforms

- **macOS**: Uses Keychain (OS-level encryption, user session)
- **Linux Desktop**: GNOME Keyring, KDE Wallet (user session)
- **Windows**: Credential Manager (OS-level encryption)

#### Setup

```bash
pip3 install keyring --user --break-system-packages
./imap-idle setup  # Wizard will ask about keyring
```

#### Security Benefits

- ✅ OS-level encryption (real improvement)
- ✅ No plain text passwords in config files
- ✅ Tied to user session (auto-lock when logged out)
- ✅ Audit trail through OS keychain logs

#### When It Works Best

- OpenClaw running on your personal machine
- You log in interactively (not headless/always-on)
- System has secure keychain backend available

---

### Headless Servers (File Permissions + Encryption)

**Keyring on headless servers requires master password → no real security benefit over file permissions.**

#### Why Keyring Doesn't Help

- Headless servers have no user session keychain
- `keyrings.alt.file.EncryptedKeyring` requires master password
- Master password must be stored somewhere → same problem as config password
- Auto-start requires non-interactive auth → defeats purpose

#### Best Practices for Servers

**1. File Permissions (Essential)**

```bash
# Config file readable only by user
chmod 600 ~/.openclaw/imap-idle.json

# Verify
ls -l ~/.openclaw/imap-idle.json
# Should show: -rw------- (600)
```

**2. User Isolation**

```bash
# Run as dedicated user (not root)
sudo useradd -r -s /bin/false clawdbot
sudo -u clawdbot ./imap-idle start
```

**3. Disk Encryption**

Use full-disk encryption or encrypted partition:
- **Linux**: LUKS / dm-crypt
- **Cloud**: EBS encryption, encrypted volumes
- **Physical**: BIOS/UEFI disk encryption

**4. Access Control**

```bash
# Restrict SSH access to specific users
# /etc/ssh/sshd_config
AllowUsers admin
DenyUsers clawdbot  # Service user cannot SSH

# Use SSH keys, disable password auth
PasswordAuthentication no
```

**5. Monitoring**

```bash
# Monitor config file access
auditctl -w ~/.openclaw/imap-idle.json -p rwa -k imap-config

# Review audit logs
ausearch -k imap-config
```

---

### Docker / Containers (Secrets Management)

**Use container secrets, not environment variables.**

#### Docker Secrets

```yaml
# docker-compose.yml
services:
  imap-idle:
    image: your-imap-idle-image
    secrets:
      - imap_config
    environment:
      CONFIG_PATH: /run/secrets/imap_config

secrets:
  imap_config:
    file: ./imap-idle.json
```

#### Kubernetes Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: imap-idle-config
type: Opaque
stringData:
  config.json: |
    {
      "accounts": [...],
      "webhook_url": "...",
      "webhook_token": "..."
    }
```

#### Best Practices

- ✅ Use secrets management (Docker Secrets, K8s Secrets, Vault)
- ✅ Rotate credentials regularly
- ✅ Limit container capabilities (`CAP_DROP=ALL`)
- ✅ Read-only root filesystem where possible
- ❌ Never use environment variables for passwords (visible in `docker inspect`)

---

## Comparison Table

| Deployment | Best Method | Security Level | Auto-Start | Notes |
|------------|-------------|----------------|------------|-------|
| **macOS Desktop** | Keyring (Keychain) | ⭐⭐⭐⭐⭐ | ✅ | OS-level encryption, user session |
| **Linux Desktop** | Keyring (GNOME/KDE) | ⭐⭐⭐⭐⭐ | ✅ | OS-level encryption, user session |
| **Windows Desktop** | Keyring (Credential Mgr) | ⭐⭐⭐⭐⭐ | ✅ | OS-level encryption, user session |
| **Headless Linux** | File permissions + disk encryption | ⭐⭐⭐ | ✅ | Keyring adds no benefit here |
| **Docker** | Secrets management | ⭐⭐⭐⭐ | ✅ | Use Docker Secrets, not env vars |
| **Kubernetes** | K8s Secrets + RBAC | ⭐⭐⭐⭐ | ✅ | Central secrets management |
| **Cloud VPS** | Disk encryption + IAM | ⭐⭐⭐⭐ | ✅ | Provider-level encryption |

---

## Threat Model

### What This Protects Against

✅ **Casual file access** - Config file readable only by owner  
✅ **Disk theft** (with encryption) - Encrypted at rest  
✅ **Process inspection** - Passwords not in environment variables  
✅ **Accidental exposure** - No passwords in logs  

### What This Does NOT Protect Against

❌ **Root/admin compromise** - Root can access keyring/config  
❌ **Memory dumps** - Passwords in memory during connection  
❌ **Process debugging** - `gdb` can extract passwords  
❌ **Malware on same system** - Can intercept credentials  

**Reality check:** If an attacker has root or can run arbitrary code on your system, all bets are off. Focus on:
1. Preventing initial compromise (updates, firewall, least privilege)
2. Detection and response (monitoring, logging)
3. Damage limitation (user isolation, network segmentation)

---

## Migration Guide

### From Config File to Keyring (Desktop)

```bash
# 1. Install keyring
pip3 install keyring --user --break-system-packages

# 2. Store passwords in keyring
python3 -c "
import keyring, getpass, json
from pathlib import Path

config_path = Path.home() / '.openclaw' / 'imap-idle.json'
config = json.loads(config_path.read_text())

for account in config['accounts']:
    username = account['username']
    password = account['password']
    keyring.set_password('imap-idle', username, password)
    print(f'✅ Stored password for {username}')
"

# 3. Remove passwords from config
python3 -c "
import json
from pathlib import Path

config_path = Path.home() / '.openclaw' / 'imap-idle.json'
config = json.loads(config_path.read_text())

for account in config['accounts']:
    if 'password' in account:
        del account['password']

config_path.write_text(json.dumps(config, indent=2))
print('✅ Passwords removed from config file')
"

# 4. Test
./imap-idle start
./imap-idle logs
```

### Rollback (Keyring to Config)

```bash
# 1. Retrieve passwords from keyring
python3 -c "
import keyring, json
from pathlib import Path

config_path = Path.home() / '.openclaw' / 'imap-idle.json'
config = json.loads(config_path.read_text())

for account in config['accounts']:
    username = account['username']
    password = keyring.get_password('imap-idle', username)
    if password:
        account['password'] = password
        print(f'✅ Restored password for {username}')

config_path.write_text(json.dumps(config, indent=2))
"

# 2. Delete from keyring (optional)
python3 -c "
import keyring, json
from pathlib import Path

config_path = Path.home() / '.openclaw' / 'imap-idle.json'
config = json.loads(config_path.read_text())

for account in config['accounts']:
    username = account['username']
    try:
        keyring.delete_password('imap-idle', username)
        print(f'✅ Removed {username} from keyring')
    except:
        pass
"
```

---

## Security Checklist

### Initial Setup

- [ ] Read source code before running
- [ ] Verify webhook URL points to YOUR OpenClaw Gateway
- [ ] Check `scripts/listener.py` for network calls
- [ ] Review author's reputation (GitHub, Moltbook)

### Desktop Deployment

- [ ] Install keyring support
- [ ] Run setup wizard with keyring enabled
- [ ] Verify passwords stored in system keychain
- [ ] Remove passwords from config file

### Server Deployment

- [ ] Set file permissions: `chmod 600 ~/.openclaw/imap-idle.json`
- [ ] Run as dedicated non-root user
- [ ] Enable disk encryption (LUKS/dm-crypt)
- [ ] Configure firewall (allow only IMAP + webhook)
- [ ] Monitor config file access (auditctl)

### Container Deployment

- [ ] Use secrets management (not env vars)
- [ ] Drop unnecessary capabilities
- [ ] Read-only root filesystem where possible
- [ ] Network policies (limit egress)

### Ongoing Maintenance

- [ ] Rotate IMAP passwords regularly
- [ ] Monitor listener logs for anomalies
- [ ] Keep dependencies updated (`pip list --outdated`)
- [ ] Review access logs periodically

---

## Reporting Security Issues

**Found a vulnerability?** Please report responsibly:

1. **DO NOT** open a public GitHub issue
2. Contact: security disclosure via GitHub Security Advisories
3. Or DM on Discord: @topitip
4. Or Moltbook: @Arkasha

We will respond within 48 hours and coordinate disclosure timeline.

---

## Credits

Security design influenced by:
- @eudaemon_0's supply chain attack analysis on Moltbook
- OWASP security guidelines for credential storage
- Linux hardening best practices (Red Hat, Ubuntu security guides)

---

## License

This security documentation is part of the imap-idle skill and follows the same MIT license.
