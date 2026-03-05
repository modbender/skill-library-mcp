---
name: archon-vault
description: Encrypted distributed storage using Archon DID vaults. Manage vaults, backup and restore workspace/config/memory with multi-party access control. Use for creating/managing DID vaults, backing up files, restoring from vault, disaster recovery, or managing vault contents and membership.
metadata:
  openclaw:
    requires:
      env:
        - ARCHON_WALLET_PATH
        - ARCHON_PASSPHRASE
      bins:
        - node
        - npx
        - tar
      anyBins:
        - zip
        - unzip
        - sha256sum
    primaryEnv: ARCHON_PASSPHRASE
    emoji: "💾"
---

# Archon Vault - Encrypted Distributed Storage

Manage DID vaults and backup/restore files. Data is encrypted client-side before transmission — only you (or vault members) can decrypt.

## Prerequisites

- Archon identity configured (`~/.archon.env` with wallet path and passphrase)
- Run `archon-keymaster` first to create your DID if you don't have one

## Backup Operations

### Backup Workspace to Vault

```bash
./scripts/backup/backup-to-vault.sh [vault-did]
```

Archives `~/clawd` and `~/.openclaw` to your encrypted vault. Respects `.backup-ignore` files.

### Restore from Vault

```bash
./scripts/backup/restore-from-vault.sh <backup-did> [target-dir]
```

### Verify Backup Integrity

```bash
./scripts/backup/verify-backup.sh <backup-did>
```

### Disaster Recovery

```bash
./scripts/backup/disaster-recovery.sh
```

Full recovery procedure with mnemonic.

## Vault Management

### Create Vault

```bash
./scripts/vaults/create-vault.sh <vault-name>
```

### Add/Remove Items

```bash
./scripts/vaults/add-vault-item.sh <vault-did> <item-did>
./scripts/vaults/remove-vault-item.sh <vault-did> <item-did>
./scripts/vaults/get-vault-item.sh <vault-did> <item-did>
./scripts/vaults/list-vault-items.sh <vault-did>
```

### Manage Vault Members (Multi-Party Access)

```bash
./scripts/vaults/add-vault-member.sh <vault-did> <member-did>
./scripts/vaults/remove-vault-member.sh <vault-did> <member-did>
./scripts/vaults/list-vault-members.sh <vault-did>
```

## Security Notes

1. **Backup scope**: Archives `~/clawd` and `~/.openclaw` by default. Review `.backup-ignore` to exclude sensitive items.

2. **Encryption**: All data encrypted before transmission to Archon gatekeeper/hyperswarm.

3. **Vault members**: Adding a member grants them decrypt access to vault contents.

4. **Recovery**: Your 12-word mnemonic is the master key. Store it offline.
