# SSH Batch Manager - README

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install cryptography sshpass

# Generate encryption key
python3 ssh-batch-manager.py generate-key

# Create configuration
python3 ssh-batch-manager.py create-config

# Generate SSH key pair
python3 ssh-batch-manager.py generate-ed25519
```

### Configuration

Edit `~/.openclaw/credentials/ssh-batch.json`:

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

### Usage

```bash
# Enable all servers (requires confirmation)
python3 ssh-batch-manager.py enable-all

# Disable all servers
python3 ssh-batch-manager.py disable-all

# Encrypt a password
python3 ssh-batch-manager.py encrypt "MyPassword123"
```

---

## ⚠️ CRITICAL SAFETY RULE

**Before executing ANY enable operation, MUST obtain explicit user confirmation.**

**Examples**:
- ✅ "enable ssh all" - OK
- ✅ "yes, execute" - OK
- ❌ Silent execution - PROHIBITED

---

## 📊 Features

- ✅ Intelligent connectivity pre-check
- ✅ Source identifier in authorized_keys
- ✅ AES-256 encryption
- ✅ SQLite + LRU cache storage
- ✅ Auto cleanup expired mappings

---

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `enable-all` | Distribute keys to all servers |
| `disable-all` | Remove keys from all servers |
| `encrypt <pwd>` | Encrypt a password |
| `generate-key` | Generate encryption key |
| `generate-ed25519` | Generate SSH key pair |

---

## 📖 Full Documentation

See [SKILL.md](SKILL.md) for complete usage guide and API reference.

---

*Version: 2.1.0 | Author: TK | Source: https://gitee.com/subline/onepeace*
