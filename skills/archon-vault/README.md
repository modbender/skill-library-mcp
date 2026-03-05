# Archon Vault

Encrypted distributed storage using Archon DID vaults.

## Features

- **Vault Management** — Create vaults, manage items and members
- **Multi-Party Access** — Share vaults with other DIDs
- **Encrypted Backups** — Backup workspace/config to your vault
- **Disaster Recovery** — Restore everything from your 12-word mnemonic

## Requirements

- Node.js (for `npx @didcid/keymaster`)
- Archon identity configured (`~/.archon.env`)
- `tar` (required), `zip`/`unzip`/`sha256sum` (optional)

## Quick Start

```bash
# Create a vault
./scripts/vaults/create-vault.sh --alias my-vault

# Add files
./scripts/vaults/add-vault-item.sh my-vault document.pdf

# Backup workspace
./scripts/backup/backup-to-vault.sh

# Restore from backup
./scripts/backup/restore-from-vault.sh
```

## Scripts

### Vault Management (`scripts/vaults/`)
- `create-vault.sh` — Create new vault
- `add-vault-item.sh` — Add file to vault
- `get-vault-item.sh` — Retrieve file from vault
- `list-vault-items.sh` — List vault contents
- `remove-vault-item.sh` — Remove file from vault
- `add-vault-member.sh` — Grant access to another DID
- `list-vault-members.sh` — List vault members
- `remove-vault-member.sh` — Revoke member access

### Backup Operations (`scripts/backup/`)
- `backup-to-vault.sh` — Backup workspace and config
- `restore-from-vault.sh` — Restore from vault
- `verify-backup.sh` — Verify backup integrity
- `disaster-recovery.sh` — Full recovery from mnemonic

## Security

- All data encrypted client-side before transmission
- Only you (and vault members) can decrypt
- Respects `.backup-ignore` files for exclusions
- Uses Archon gatekeeper + hyperswarm DHT for storage

## Related Skills

- `archon-keymaster` — Core DID identity and credentials
- `archon-cashu` — Cashu ecash operations
