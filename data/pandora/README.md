# Pandora

**Secrets, safely stored.**

## Threat Model

Pandora protects against:

- Secrets in source control
- Unencrypted config files
- Overly broad access to credentials
- Stale or leaked keys (via rotation)

## Installation

1. Install Pandora via ClawHub.
2. Configure vault backend (local file, KMS, or remote vault).
3. Set access policies before storing production secrets.

## Vault Commands

- `--store` — Add or update secrets
- `--rotate` — Rotate secrets on schedule or on demand
- `--list-secrets` — Enumerate keys (values never displayed)
