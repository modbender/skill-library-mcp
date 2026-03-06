---
name: ssh-batch-manager
description: Batch SSH key management. Distribute/remove SSH keys to/from multiple servers with intelligent connectivity pre-check and source tracking.
homepage: https://gitee.com/subline/onepeace/tree/develop/src/skills/ssh-batch-manager
metadata:
  {
    "openclaw":
      {
        "emoji": "🔑",
        "requires": { "bins": ["ssh", "ssh-copy-id", "sshpass"], "python_packages": ["cryptography"] },
        "install":
          [
            {
              "id": "python",
              "kind": "pip",
              "package": "cryptography",
              "label": "Install cryptography library",
            },
            {
              "id": "sshpass",
              "kind": "apt",
              "package": "sshpass",
              "label": "Install sshpass for password-based SSH",
            },
            {
              "id": "post-install",
              "kind": "script",
              "script": "post-install.sh",
              "label": "Configure and auto-start Web UI service",
            },
          ],
      },
  }
---

# SSH Batch Manager

## ⚠️ CRITICAL SAFETY RULE

**EN: Before executing ANY enable operation (enable-all, enable-single, etc.), the agent MUST obtain explicit user confirmation via message. NEVER execute enable operations without explicit user approval.**

**Reason**: Enable operations modify SSH access on remote servers. Unauthorized execution could cause security issues or service disruptions.

**Confirmation examples**:
- ✅ "enable ssh all" - Explicit command
- ✅ "yes, execute enable-all" - Explicit confirmation
- ❌ Silent execution - **PROHIBITED**
- ❌ Inferring user intent - **PROHIBITED**

---

Batch management of SSH key-based authentication.

## 🚀 Installation

### Via Clawhub (Auto-Start Enabled)

```bash
# Install skill
clawhub install ssh-batch-manager

# Post-install script automatically:
# ✅ Configure systemd service
# ✅ Start Web UI service  
# ✅ Enable auto-start on boot
# ✅ No manual configuration needed!
```

### Manual Installation

```bash
# Install dependencies
pip install cryptography sshpass

# Generate encryption key
python3 ssh-batch-manager.py generate-key

# Create configuration
python3 ssh-batch-manager.py create-config

# Generate SSH key pair
python3 ssh-batch-manager.py generate-ed25519

# Run post-install script (auto-start Web UI)
cd ~/.openclaw/workspace/skills/ssh-batch-manager
bash post-install.sh
```

---

## 🌐 Web UI

**Auto-started on installation!**

**Access**: http://localhost:8765

**Features**:
- ⚡ Quick operations (Enable All / Disable All)
- 🔑 SSH public key management (Read/Copy/Download)
- 🖥️ Server list management
- 🔐 Encryption tools
- 📝 Real-time operation logs

**Manual Start** (if needed):
```bash
python3 serve-ui.py
```

---

## Features

- ✅ **Intelligent connectivity pre-check** - Skip servers that are already accessible (40x faster)
- ✅ **Source identifier** - Add source info to authorized_keys for audit trail
- ✅ **Mandatory safety confirmation** - Require explicit user approval before enable operations
- ✅ **SQLite + LRU cache** - High-performance mapping storage
- ✅ **Auto cleanup** - Expired entries removed automatically
- ✅ **Auto-start Web UI** - Web interface starts automatically on installation

## Commands

### SSH Key Management

| Command | Description |
|---------|-------------|
| `enable-all` | Distribute public key to all configured servers |
| `disable-all` | Remove public key from all servers |
| `enable <user@host> [port]` | Distribute to single server |
| `disable <user@host> [port]` | Remove from single server |

### Encryption Tools

| Command | Description |
|---------|-------------|
| `encrypt <password>` | Encrypt a password |
| `encrypt-file <file>` | Encrypt file (output to `.enc`) |
| `decrypt-file <file>` | Decrypt file |
| `generate-key` | Generate encryption key |
| `generate-ed25519` | Generate ed25519 SSH key pair |

## Configuration

**Location**: `~/.openclaw/credentials/ssh-batch.json`

**Format**:
```json
{
  "version": "2.0",
  "auth_method": "password",
  "servers": [
    {
      "user": "root",
      "host": "10.8.8.81",
      "port": 22,
      "auth": "password",
      "password": "AES256:encrypted_password_here"
    }
  ]
}
```

## Security Notes

- ✅ Passwords stored with AES-256 encryption
- ✅ Key file permissions: 600
- ✅ Config file permissions: 600
- ✅ Web UI auto-starts with systemd
- ⚠️ Never commit keys to git
- ⚠️ Rotate keys periodically

## Performance

| Operation | Latency |
|-----------|---------|
| Hot query (cache) | < 0.1ms |
| Cold query (SQLite) | ~0.5ms |
| Write | < 2ms |
| Max records | 100,000+ |

**v2.1 improvements**:
- First run: ~8s (8 servers)
- Repeated runs: ~2s (all skipped)
- **40x faster** for repeated executions

## Source Identifier

When distributing keys, adds source info to `authorized_keys`:

```
ssh-ed25519 AAAAC3... ssh-batch-manager from mls at 2026-03-03 17:30:00
```

**Fields**:
- `ssh-batch-manager` - Tool identifier
- `from mls` - Source hostname
- `at 2026-03-03 17:30:00` - Distribution timestamp

## Version History

### v2.1.0 (2026-03-03)
- **CRITICAL**: Require explicit user confirmation before enable operations
- Intelligent connectivity pre-check (skip already accessible servers)
- Add source identifier to authorized_keys
- Clean test configurations (production servers only)
- Performance improvement: 40x faster for repeated runs
- **Auto-start Web UI service on installation**

### v2.0 (2026-03-03)
- JSON configuration format
- Support key-based authentication
- Mixed mode support (password + key)
- ed25519 key support (Ubuntu/Alpine compatible)

### v1.0 (2026-03-03)
- Initial release
- Enable/Disable all support
- AES-256 encryption
- Batch operations

## Repository

**Source**: https://gitee.com/subline/onepeace/tree/develop/src/skills/ssh-batch-manager

**License**: MIT

**Author**: TK

**Issues**: https://gitee.com/subline/onepeace/issues

## Related Skills

- `sensitive-data-masker` - Intelligent sensitive data detection and masking
- `healthcheck` - Security hardening and audits
