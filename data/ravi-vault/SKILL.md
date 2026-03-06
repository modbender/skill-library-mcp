---
name: ravi-vault
description: Store and retrieve key-value secrets — E2E encrypted vault for API keys and env vars. Do NOT use for website passwords (use ravi-passwords) or reading messages (use ravi-inbox).
---

# Ravi Vault

Store and retrieve key-value secrets (API keys, environment variables, tokens). All values are E2E encrypted — the CLI handles encryption/decryption transparently. Keys are stored in plaintext for lookup/filtering.

## Commands

```bash
# Store a secret (creates or updates)
ravi secrets set OPENAI_API_KEY "sk-abc123..." --json

# With optional notes
ravi secrets set STRIPE_SECRET_KEY "sk_live_..." --json

# Retrieve a secret by key
ravi secrets get OPENAI_API_KEY --json
# -> {"key": "OPENAI_API_KEY", "value": "sk-abc123...", "notes": "", ...}

# List all secrets (values redacted in list view)
ravi secrets list --json

# Delete a secret by key
ravi secrets delete OPENAI_API_KEY --json
```

## JSON Shapes

**`ravi secrets list --json`:**
```json
[
  {
    "uuid": "...",
    "key": "OPENAI_API_KEY",
    "notes": "",
    "created_dt": "2026-02-25T10:30:00Z",
    "updated_dt": "2026-02-25T10:30:00Z"
  }
]
```

**`ravi secrets get KEY --json`:**
```json
{
  "uuid": "...",
  "key": "OPENAI_API_KEY",
  "value": "sk-abc123...",
  "notes": "",
  "created_dt": "2026-02-25T10:30:00Z",
  "updated_dt": "2026-02-25T10:30:00Z"
}
```

## OpenClaw Integration

When an agent needs API keys or secrets at runtime, use Ravi Vault as the backing store:

```bash
# Store a key for the agent to use later
ravi secrets set OPENAI_API_KEY "sk-abc123..." --json

# At runtime, retrieve the key
API_KEY=$(ravi secrets get OPENAI_API_KEY --json | jq -r '.value')
curl -H "Authorization: Bearer $API_KEY" https://api.openai.com/v1/...

# Store multiple service keys
ravi secrets set ANTHROPIC_API_KEY "sk-ant-..." --json
ravi secrets set GITHUB_TOKEN "ghp_..." --json

# List all available keys
ravi secrets list --json | jq -r '.[].key'
```

## Important Notes

- **E2E encryption is transparent** — the CLI encrypts values before sending and decrypts on retrieval. You see plaintext.
- **Keys are unique per identity** — setting a key that already exists updates it.
- **Keys are plaintext** — only values and notes are E2E encrypted. Use descriptive key names like `OPENAI_API_KEY`, `STRIPE_SECRET_KEY`.
- **Always use `--json`** — human-readable output is not designed for parsing.

## Related Skills

- **ravi-passwords** — Store website credentials (domain + username + password, not key-value secrets)
- **ravi-login** — Signup workflows that may need API keys stored after registration
- **ravi-feedback** — Report vault issues or suggest improvements
