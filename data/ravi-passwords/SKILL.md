---
name: ravi-passwords
description: Store and retrieve website credentials — E2E encrypted password manager for domain/username/password entries. Do NOT use for API keys/secrets (use ravi-vault) or reading messages (use ravi-inbox).
---

# Ravi Passwords

Store and retrieve passwords for services you sign up for. All fields are E2E encrypted — the CLI handles encryption/decryption transparently.

## Commands

```bash
# Create entry (auto-generates password if --password not given)
ravi vault create example.com --json
ravi vault create example.com --username "me@ravi.app" --password 'S3cret!' --json

# List all entries
ravi vault list --json

# Retrieve (decrypted)
ravi vault get <uuid> --json

# Update
ravi vault edit <uuid> --password 'NewPass!' --json

# Delete
ravi vault delete <uuid> --json

# Generate a password without storing it
ravi vault generate --length 24 --json
# -> {"password": "xK9#mL2..."}
```

**Create flags:** `--username`, `--password`, `--notes`, `--generate`, `--length` (default 16), `--no-special`, `--no-digits`, `--exclude-chars`

## JSON Shapes

**`ravi vault list --json`:**
```json
[
  {
    "uuid": "uuid",
    "domain": "example.com",
    "username": "me@ravi.app",
    "created_dt": "2026-02-25T10:30:00Z"
  }
]
```

**`ravi vault get <uuid> --json`:**
```json
{
  "uuid": "uuid",
  "domain": "example.com",
  "username": "me@ravi.app",
  "password": "S3cret!",
  "notes": "",
  "created_dt": "2026-02-25T10:30:00Z"
}
```

## Important Notes

- **E2E encryption is transparent** — the CLI encrypts vault fields before sending and decrypts on retrieval. You see plaintext.
- **Domain cleaning** — `ravi vault create` auto-cleans URLs to base domains (e.g., `https://mail.google.com/inbox` becomes `google.com`).
- **Always use `--json`** — human-readable output is not designed for parsing.

## Related Skills

- **ravi-vault** — Store API keys and env vars (key-value secrets, not website credentials)
- **ravi-login** — End-to-end signup/login workflows that store credentials here
- **ravi-identity** — Get your email address for the username field
- **ravi-feedback** — Report password manager issues or suggest improvements
