# Security Policy: Mema Vault

## Cryptography
- **Algorithm**: AES-256-CBC (via Python `cryptography` Fernet).
- **Key Derivation**: PBKDF2HMAC-SHA256.
- **Iterations**: 480,000.
- **Salt**: Random 16-byte salt, stored in `data/salt.bin`.

## Storage
- **Primary Backend**: Local SQLite database (`data/vault.db`).
- **Persistence**: All encrypted credentials and metadata are stored locally in the workspace.
- **No External Dependencies**: This version does not use Redis or cloud storage to ensure zero-network footprint.

## Access Control
- **Master Key**: Required for all read/write operations.
- **Process Isolation**: Secrets are only decrypted in memory during the execution of the `vault` script.
- **Output Masking**: Passwords are masked unless the `--show` flag is explicitly provided.

## Logging & Auditing
- **Audit Logs**: Access events (SET/GET) are logged to the console.
- **No Secret Logging**: The logic strictly prevents raw secrets from being written to any log file.
