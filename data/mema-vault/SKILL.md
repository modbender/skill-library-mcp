---
name: mema-vault
description: Secure credential manager using AES-256 (Fernet) encryption. Stores, retrieves, and rotates secrets using a mandatory Master Key. Use for managing API keys, database credentials, and other sensitive tokens.
metadata: {"openclaw":{"requires":{"env":["MEMA_VAULT_MASTER_KEY"]},"install":[{"id":"pip","kind":"exec","command":"pip install cryptography"}]}}
---

# Mema Vault

## Prerequisites
- **Master Key**: Must be set as an environment variable `MEMA_VAULT_MASTER_KEY`.
- **Dependencies**: Requires `cryptography` Python package.

## Core Workflows

### 1. Store a Secret
Encrypt and save a new credential.
- **Usage**: `python3 $WORKSPACE/skills/mema-vault/scripts/vault.py set <service> <user> <password> [--meta "info"]`

### 2. Retrieve a Secret
Fetch a credential. By default, the password is masked in output.
- **Usage**: `python3 $WORKSPACE/skills/mema-vault/scripts/vault.py get <service>`
- **Show Raw**: Use `--show` flag only when required for secure injection.

### 3. List Credentials
- **Usage**: `python3 $WORKSPACE/skills/mema-vault/scripts/vault.py list`

## Security Standards
- **Encryption**: AES-256 CBC via PBKDF2HMAC (480,000 iterations).
- **Masking**: Secrets are masked in standard logs/output unless explicitly requested.
- **Isolation**: The Master Key should never be stored in plaintext on disk.
