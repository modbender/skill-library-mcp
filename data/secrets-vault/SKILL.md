---
name: secrets-vault
description: Secure sensitive data management with AES-256-GCM encryption. Store API keys, database credentials, passwords, and certificates.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
    primaryEnv: SECRETS_VAULT_PASSWORD
    emoji: "\U0001F512"
    homepage: https://github.com/lobsterai/secrets-vault
---

# Secrets Vault

Secure storage and management for sensitive data including API keys, database credentials, passwords, and certificates.

## Features

- **AES-256-GCM Encryption** - Military-grade encryption for all stored secrets
- **Master Password Protection** - Single password to unlock all secrets
- **Auto Environment Injection** - Load secrets as environment variables for development
- **Secure Sharing** - Time-limited, one-time share links
- **Password Auditing** - Strength checking and breach detection
- **Cross-Device Sync** - Encrypted vault file can be synced across devices

## Quick Start

### Prerequisites

```bash
pip install cryptography
```

### Initialize Vault

```bash
python ~/.secrets-vault/scripts/secrets_manager.py init
```

### Basic Usage

```bash
# Unlock vault
python ~/.secrets-vault/scripts/secrets_manager.py unlock

# Add secret interactively
python ~/.secrets-vault/scripts/secrets_manager.py add

# List all secrets
python ~/.secrets-vault/scripts/secrets_manager.py list

# Get secret details
python ~/.secrets-vault/scripts/secrets_manager.py get api.openai --show

# Lock vault
python ~/.secrets-vault/scripts/secrets_manager.py lock
```

## Core Capabilities

### 1. Secret Storage

Store different types of sensitive data:

**API Keys / Tokens**
```bash
python scripts/secrets_manager.py add api.openai \
  --type api_key \
  --key sk-xxxxxxxx \
  --tags openai,gpt
```

**Database Credentials**
```bash
python scripts/secrets_manager.py add db.production \
  --type database \
  --host db.example.com \
  --port 5432 \
  --database myapp \
  --username admin \
  --password secret123
```

**Username/Password**
```bash
python scripts/secrets_manager.py add github \
  --type password \
  --username myuser \
  --password mypassword
```

### 2. Environment Injection

Automatically inject secrets as environment variables:

```bash
# Export as shell variables
python scripts/inject_env.py --shell

# Generate .env file
python scripts/inject_env.py --file .env

# Run command with injected secrets
python scripts/inject_env.py --run "python app.py"

# Filter specific secrets
python scripts/inject_env.py --names api.openai,database --shell

# Add prefix
python scripts/inject_env.py --prefix APP_ --shell
```

Output format:
```bash
export API_OPENAI_KEY="sk-xxxxxxxx"
export DATABASE_HOST="db.example.com"
export DATABASE_USERNAME="admin"
```

### 3. Secure Sharing

Create time-limited, encrypted share links:

```bash
# Create share from vault secret
python scripts/share.py share api.openai --hours 24 --views 1

# Get shared content
python scripts/share.py get abc123 --code ABCD1234

# List active shares
python scripts/share.py list

# Revoke share
python scripts/share.py revoke abc123
```

Share features:
- Access code required for decryption
- Configurable expiration time
- View count limits
- Auto-destruction after max views

### 4. Password Auditing

Audit password security:

```bash
# Audit all passwords in vault
python scripts/audit.py vault

# Check single password
python scripts/audit.py check

# Generate strong password
python scripts/audit.py generate --length 24
```

Audit report includes:
- Weak passwords detection
- Common/breached password detection
- Password age tracking
- Duplicate password detection
- Overall risk assessment

### 5. Cross-Device Sync

The vault file is stored at `~/.secrets-vault/vault.enc` and can be synced:

- **iCloud**: Move to iCloud Drive and symlink
- **Dropbox/Google Drive**: Move vault file and update path
- **Git**: For advanced users (ensure .gitignore for other files)

```bash
# Example: Move to iCloud
mv ~/.secrets-vault ~/Library/Mobile\ Documents/com~apple~CloudDocs/
ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/.secrets-vault ~/.secrets-vault
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `secrets_manager.py` | Main vault management (init, add, get, list, delete) |
| `inject_env.py` | Environment variable injection |
| `share.py` | Secure sharing functionality |
| `audit.py` | Password security auditing |
| `crypto_utils.py` | Encryption utilities |

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Master Password                       │
└─────────────────────┬───────────────────────────────────┘
                      │ PBKDF2-HMAC-SHA256 (600k iterations)
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 Encryption Key (256-bit)                 │
└─────────────────────┬───────────────────────────────────┘
                      │ AES-256-GCM
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Encrypted Vault (vault.enc)                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │API Keys │ │ DB Creds│ │Passwords│ │  Certs  │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
└─────────────────────────────────────────────────────────┘
```

**Key Security Features:**
- PBKDF2 with 600,000 iterations (OWASP recommended)
- AES-256-GCM authenticated encryption
- Random salt per encryption
- File permissions restricted to owner (600)

## File Locations

```
~/.secrets-vault/
├── vault.enc          # Encrypted secrets storage
├── config.json        # Vault configuration
└── shares/            # Active share metadata
```

## Automation & CI/CD

For automated environments, use environment variables:

```bash
# Set master password (for scripts)
export SECRETS_VAULT_PASSWORD="your-master-password"

# Or use password file
export SECRETS_VAULT_PASSWORD_FILE="/secure/path/password"

# Then run without prompts
python scripts/inject_env.py --file .env
```

**Security Note:** Only use this in secure CI/CD environments. Never commit password files to version control.

## Best Practices

1. **Strong Master Password** - Use 20+ characters with mixed types
2. **Regular Audits** - Run `audit.py vault` monthly
3. **Unique Passwords** - Never reuse passwords across services
4. **Limit Sharing** - Use short expiration and single-view shares
5. **Backup Vault** - Keep encrypted backup in secure location
6. **Lock After Use** - Always lock vault when done

## Troubleshooting

**"Cryptography library not installed"**
```bash
pip install cryptography
```

**"Vault not found"**
```bash
# Initialize first
python scripts/secrets_manager.py init
```

**"Decryption failed"**
- Verify master password is correct
- Check vault file isn't corrupted
- Ensure vault was created with same password

**Environment variables not injected**
- Verify vault is unlocked
- Check secret names match filter
- Ensure correct prefix formatting
