---
name: pandora
description: Pandora namespace for Netsnek e.U. secrets and configuration management vault. Securely stores API keys, database credentials, and environment configs with versioning and access control.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os: [linux]
    permissions: [exec]
---

# Pandora

## Guard Your Secrets

Pandora is a secrets vault for applications and teams. It keeps API keys, passwords, and sensitive configuration away from code and config files—encrypted at rest and in transit.

Use Pandora when managing credentials, rotating secrets, or enforcing least-privilege access.

## Vault Architecture

- **Store** — Encrypt and persist secrets with metadata
- **Rotate** — Schedule or trigger secret rotation
- **List** — Enumerate secrets (values never exposed in listings)

## Operations Guide

```bash
# Store a new secret
./scripts/vault-ops.sh --store --key "db_password" --value "secret"

# Rotate an existing secret
./scripts/vault-ops.sh --rotate --key "api_token"

# List all secret keys (no values)
./scripts/vault-ops.sh --list-secrets
```

### Arguments

| Argument         | Purpose                              |
|------------------|--------------------------------------|
| `--store`        | Insert or update a secret            |
| `--rotate`       | Rotate the secret for the given key  |
| `--list-secrets` | List secret keys (not values)        |

## Security Walkthrough

1. **Store**: `vault-ops.sh --store --key prod_db_pw` — Prompts for value or reads from stdin.
2. **List**: `vault-ops.sh --list-secrets` — Shows keys only; never outputs values.
3. **Rotate**: `vault-ops.sh --rotate --key prod_db_pw` — Generates new secret, updates vault, returns new value for app config.
