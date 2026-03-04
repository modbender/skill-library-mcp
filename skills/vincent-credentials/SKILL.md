---
name: Vincent - Credentials for agents
description: |
  Secure credential management for agents. Use this skill when users need to store API keys,
  passwords, OAuth tokens, or SSH keys and write them to .env files without exposing values.
  Triggers on "store credentials", "API key", "manage secrets", "write to env", ".env file",
  "credential", "password", "token storage".
allowed-tools: Read, Write, Bash(npx:*, curl:*)
version: 1.0.0
author: HeyVincent <contact@heyvincent.ai>
license: MIT
homepage: https://heyvincent.ai
source: https://github.com/HeyVincent-ai/Vincent
metadata:
  clawdbot:
    homepage: https://heyvincent.ai
    requires:
      config:
        - ${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/credentials
        - ./credentials
---

# Vincent - Credentials for agents

Use this skill to securely manage credentials that your application needs — API keys, passwords, OAuth tokens, SSH keys, or structured username/password pairs. The agent creates a secret, the user (or agent) sets the value, and the agent uses the CLI to write it directly to a `.env` file. **The credential value never appears in the agent's context or stdout.**

This is useful when the agent is building something that needs credentials (e.g. a third-party API key). Instead of the user pasting the credential into chat (where it enters the agent's context), they set it via the Vincent dashboard, and the agent writes it to the `.env` file using the CLI.

All commands use the `@vincentai/cli` package. API keys are stored and resolved automatically — you never handle raw keys or file paths.

## Security Model

This skill is designed for **keeping credentials out of the agent's context window**.

**How it works:** The `secret env` CLI command fetches the credential from the Vincent server and writes it directly to a `.env` file on disk. The value is never printed to stdout and never appears in the agent's conversation context. Many agent frameworks blacklist reading `.env` files, so even though the file is on disk, the agent cannot read it back. The application the agent is building reads the `.env` file normally at runtime.

**No environment variables are required** because this skill uses agent-first onboarding: the agent creates its own credential secret at runtime by calling the Vincent API, which returns a scoped API key. The CLI stores the returned API key automatically during creation. The config paths where the key is persisted (`${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/credentials/` or `./credentials/`) are declared in this skill's metadata.

**Overwrite guard:** Once a value is set by an agent's API key, only that same API key can overwrite it. This prevents other agents or keys from tampering with the credential. The guard is enforced atomically at the database level.

**All API calls go exclusively to `heyvincent.ai`** over HTTPS/TLS. No other endpoints, services, or external hosts are contacted.

**Key lifecycle:**

- **Creation**: The agent runs `secret create` with `--type CREDENTIALS` — the CLI stores the API key automatically and returns a `keyId` and `claimUrl`.
- **Value set**: The user sets the credential value via the dashboard after claiming, or the agent sets it via the REST API.
- **Write to .env**: The agent runs `secret env` to write the value to a `.env` file without exposing it.
- **Claim**: The human operator uses the claim URL to take ownership and manage the secret from the dashboard.
- **Revocation**: The secret owner can revoke the agent's API key at any time from `https://heyvincent.ai`.

## Secret Types

| Type | Value format | Use case |
|---|---|---|
| `API_KEY` | Non-empty string | Third-party API keys |
| `SSH_KEY` | Non-empty string | SSH private keys |
| `OAUTH_TOKEN` | Non-empty string | OAuth access/refresh tokens |
| `CREDENTIALS` | JSON object with `password` or `secret` | Username/password, key/secret pairs |

All four types support the same create, set, and `env` workflow.

### CREDENTIALS Value Format

The `CREDENTIALS` value must be a JSON object containing at least one of:

- `password` (string) — e.g. `{"username": "alice", "password": "hunter2"}`
- `secret` (string) — e.g. `{"accountId": "acct-1", "secret": "top-secret"}`

Additional fields are preserved as-is. All values are limited to 16KB.

## Quick Start

### 1. Check for Existing Keys

Before creating a new secret, check if one already exists:

```bash
npx @vincentai/cli@latest secret list --type CREDENTIALS
```

If a key is returned, use its `id` as the `--key-id` for subsequent commands. If no keys exist, create a new secret.

### 2. Create a Credentials Secret

```bash
npx @vincentai/cli@latest secret create --type CREDENTIALS --memo "Acme API credentials"
```

Returns `keyId` (use for all future commands), `claimUrl` (share with the user), and `secretId`.

After creating, tell the user:

> "Here is your credentials claim URL: `<claimUrl>`. Use this to claim ownership and set the credential value at https://heyvincent.ai."

### 3. Set the Credential Value

**Option A: User sets via dashboard (recommended)**

The user claims the secret using the claim URL, then sets the credential value from the dashboard. This keeps the value completely out of the agent's hands.

**Option B: Agent sets via REST API**

For agent-first workflows where the agent has the credential (e.g. it obtained an API key from a service):

```bash
curl -X PATCH https://heyvincent.ai/api/secrets/<SECRET_ID>/value/agent \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"value": {"username": "alice", "password": "hunter2"}}'
```

For simple string types (`API_KEY`, `SSH_KEY`, `OAUTH_TOKEN`):

```bash
curl -X PATCH https://heyvincent.ai/api/secrets/<SECRET_ID>/value/agent \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"value": "sk-my-third-party-api-key"}'
```

### 4. Write to .env File

Once the value is set (by the user or the agent), use the CLI to write it to a `.env` file. **The value is never printed to stdout.**

```bash
# Write an API_KEY secret as an env var
npx @vincentai/cli@latest secret env --key-id <KEY_ID> --env-var ACME_API_KEY

# For CREDENTIALS: extract a specific field
npx @vincentai/cli@latest secret env --key-id <KEY_ID> --env-var DB_PASSWORD --field password

# Write to a specific path (default: ./.env)
npx @vincentai/cli@latest secret env --key-id <KEY_ID> --env-var SERVICE_TOKEN --path ./config/.env
```

The command outputs a confirmation JSON (without the value) so the agent knows it succeeded:

```json
{
  "written": "ACME_API_KEY",
  "path": "/path/to/.env",
  "type": "API_KEY"
}
```

**Flags:**

| Flag | Required | Description |
|---|---|---|
| `--env-var` | Yes | Environment variable name (e.g. `MY_API_KEY`) |
| `--path` | No | Path to `.env` file (default: `./.env`) |
| `--key-id` | No | API key ID (auto-discovered if only one credential key exists) |
| `--field` | No | For `CREDENTIALS` type: extract a specific JSON field instead of writing the full JSON |

**Behavior:**

- Creates the `.env` file if it doesn't exist (with `0600` permissions)
- Updates the variable in-place if it already exists in the file
- Appends a new line if the variable doesn't exist
- Values with special characters are automatically quoted

### 5. Use in Your Application

Your application reads the `.env` file normally:

```bash
# Node.js with dotenv
require('dotenv').config()
const apiKey = process.env.ACME_API_KEY

# Python with python-dotenv
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('ACME_API_KEY')
```

## Example: Full Workflow

```bash
# 1. Agent creates a CREDENTIALS secret
npx @vincentai/cli@latest secret create --type CREDENTIALS --memo "Acme service credentials"
# → keyId: abc-123, claimUrl: https://heyvincent.ai/claim/...

# 2. Tell the user to claim and set the value via the dashboard

# 3. Once set, write individual fields to .env
npx @vincentai/cli@latest secret env --key-id abc-123 --env-var ACME_USERNAME --field username
npx @vincentai/cli@latest secret env --key-id abc-123 --env-var ACME_PASSWORD --field password

# Result in .env:
# ACME_USERNAME=alice
# ACME_PASSWORD=hunter2
```

## Output Format

The `secret env` command outputs a confirmation JSON (without the credential value):

```json
{
  "written": "ACME_API_KEY",
  "path": "/path/to/.env",
  "type": "API_KEY"
}
```

The `secret create` command returns:

```json
{
  "keyId": "abc-123",
  "claimUrl": "https://heyvincent.ai/claim/...",
  "secretId": "sec-456"
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Check that the key-id is correct; re-link if needed |
| `403 Overwrite Rejected` | A different API key set this credential's value | Secret owner must manage from the dashboard |
| `404 Value Not Set` | Credential value hasn't been set yet | User must set the value via dashboard or agent sets via REST API |
| `Key not found` | API key was revoked or never created | Re-link with a new token from the secret owner |

## Re-linking (Recovering API Access)

If the agent loses its API key, the secret owner can generate a **re-link token** from the frontend. The agent then exchanges this token for a new API key.

```bash
npx @vincentai/cli@latest secret relink --token <TOKEN_FROM_USER>
```

The CLI exchanges the token for a new API key, stores it automatically, and returns the new `keyId`. Re-link tokens are one-time use and expire after 10 minutes.

## Important Notes

- **The credential value never enters the agent's context.** The `secret env` command writes directly to a file — it does not print the value to stdout.
- Many agent frameworks (OpenClaw, Claude Code, etc.) blacklist reading `.env` files, providing an additional layer of protection.
- Always share the claim URL with the user after creating a secret.
- The 16KB size limit applies to the serialized value.
- If the overwrite is rejected with a `403`, it means a different API key set the value. The secret owner can manage this from the dashboard.
