---
name: ravi-identity
description: Check Ravi auth status and get your agent identity (email, phone, owner name). Do NOT use for reading messages (use ravi-inbox), sending email (use ravi-email-send), or credentials (use ravi-passwords or ravi-vault).
---

# Ravi Identity

You have access to `ravi`, a CLI that gives you your own phone number, email address, and credential vault.

## Prerequisites

### Install the CLI

If `ravi` is not installed, tell the user to install it:

```bash
brew install ravi-hq/tap/ravi
```

### Check authentication

Verify you're authenticated before using any command:

```bash
ravi auth status --json
```

If `"authenticated": false`, tell the user to run `ravi auth login` (requires browser interaction — you cannot do this yourself).

## Your Identity

```bash
# Your email address (use this for signups)
ravi get email --json
# → {"id": 1, "email": "janedoe@ravi.app", "created_dt": "..."}

# Your phone number (use this for SMS verification)
ravi get phone --json
# → {"id": 1, "phone_number": "+15551234567", "provider": "twilio", "created_dt": "..."}

# The human who owns this account
ravi get owner --json
# → {"first_name": "Jane", "last_name": "Doe"}
```

## Switching Identities

Ravi supports multiple identities. Each identity has its own email, phone, and vault.

### Listing identities

```bash
ravi identity list --json
```

### Setting an identity for this project

Use this when the user wants a different identity for a specific project:

1. List identities: `ravi identity list --json`
2. Set for this project (per-directory override):
   - `mkdir -p .ravi && echo '{"identity_uuid":"<uuid>","identity_name":"<name>"}' > .ravi/config.json`
   - Add `.ravi/` to `.gitignore`

All `ravi` commands in this directory will use the specified identity.

### Switching identity globally

```bash
ravi identity use "<name-or-uuid>"
```

### Creating a new identity

Only create a new identity when the user explicitly asks for one (e.g., for a
separate project that needs its own email/phone). New identities require a paid
plan and take a moment to provision.

```bash
ravi identity create --name "Project Name" --json
```

## Important Notes

- **Always use `--json`** — all commands support it. Human-readable output is not designed for parsing.
- **Auth is automatic** — token refresh happens transparently. If you get auth errors, ask the user to re-login.
- **Identity resolution** — `.ravi/config.json` in CWD takes priority over `~/.ravi/config.json`.
- **Identities are permanent** — each identity has its own email, phone, and vault. Don't create new identities unless the user asks for it.

## Related Skills

- **ravi-inbox** — Read SMS and email messages
- **ravi-email-send** — Compose, reply, forward emails
- **ravi-email-writing** — Write professional emails with proper formatting and tone
- **ravi-passwords** — Store and retrieve website credentials (domain + username + password)
- **ravi-vault** — Store and retrieve key-value secrets (API keys, env vars)
- **ravi-login** — Sign up for and log into services, handle 2FA/OTPs
- **ravi-feedback** — Send feedback, report bugs, request features
