---
name: a2a-vault
description: "Zero-knowledge secrets management via PassBox — store, retrieve, rotate, and inject credentials securely."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔐",
        "requires": {},
        "install":
          [
            {
              "id": "plugin",
              "kind": "node",
              "package": "@a2a/openclaw-plugin",
              "label": "Install A2A Corp plugin",
            },
          ],
      },
  }
---

# A2A Vault (PassBox)

Zero-knowledge secrets management. Store API keys, tokens, and credentials with client-side encryption. The server never sees plaintext values.

## Quick Start

Store a secret:

```
Use passbox_set_secret with vault "my-project", key "API_KEY", value "sk-abc123"
```

Retrieve a secret:

```
Use passbox_get_secret with vault "my-project", key "API_KEY"
```

## Available Tools

### Secret Operations

| Tool | Description |
|------|-------------|
| `passbox_get_secret` | Retrieve and decrypt a secret |
| `passbox_set_secret` | Create or update a secret (encrypted before upload) |
| `passbox_list_secrets` | List secret names (values not returned) |
| `passbox_delete_secret` | Delete a secret |
| `passbox_rotate_secret` | Trigger manual secret rotation |

### Vault Management

| Tool | Description |
|------|-------------|
| `passbox_list_vaults` | List all available vaults |
| `passbox_list_environments` | List environments (dev, staging, prod) |
| `passbox_get_environment` | Get all secrets in an environment |

### .env Integration

| Tool | Description |
|------|-------------|
| `passbox_diff_env` | Compare local .env with vault secrets |
| `passbox_import_env` | Import .env file into vault |

## Workflows

### Set up project credentials

1. `passbox_list_vaults` — see existing vaults
2. `passbox_set_secret` — store each credential
3. `passbox_list_secrets` — verify all keys are stored

### Sync .env with vault

1. Read your local .env file
2. `passbox_diff_env` — see what's different
3. `passbox_import_env` — push local secrets to vault

### Environment promotion

1. `passbox_get_environment` for "dev"
2. Review values
3. `passbox_set_secret` for each key in "staging"

### Credential injection

Use with `a2a_secure_execute` to automatically inject secrets:

```
Use a2a_secure_execute with toolId "my-api-tool" and input { "apiKey": "{{API_KEY}}" }, vault "my-project"
```

The `{{API_KEY}}` placeholder is resolved from PassBox before execution.

## Security Model

- **Client-side encryption**: Values are encrypted before leaving your device
- **Zero-knowledge**: The server stores only ciphertext
- **Environment isolation**: dev/staging/prod secrets are fully separated
- **Audit trail**: All access is logged
- **Secret rotation**: Built-in rotation support with webhooks
