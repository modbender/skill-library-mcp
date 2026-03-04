---
name: ssh-op
description: Use the ssh-op helper script to load an SSH private key from 1Password (op) into an in-memory ssh-agent and then run ssh. Use when connecting to hosts that require the 1Password-managed key, troubleshooting ssh-op, or onboarding a new machine by configuring the 1Password vault/item and adding SSH host aliases to ~/.ssh/config.
---

# ssh-op

`ssh-op` is a wrapper around `ssh` that:

- ensures an `ssh-agent` exists for the current shell
- loads an SSH key from 1Password via `op read ... | ssh-add -`
- then `exec`s `ssh` with your arguments

## Prerequisites

Fail-fast checks you can run:

```bash
command -v op ssh ssh-agent ssh-add
op whoami
```

If `op whoami` fails:

- Sign in to 1Password CLI (desktop integration / account sign-in), **or**
- If using a service account flow, ensure `OP_SERVICE_ACCOUNT_TOKEN` is set.

## Configuration (portable)

Machine-specific config lives alongside the skill:

- Example (do not edit): `~/.openclaw/skills/ssh-op/config.env.example`
- Real (machine-specific): `~/.openclaw/skills/ssh-op/config.env`

Required keys:

- `SSH_OP_VAULT_NAME` — 1Password vault containing the key
- `SSH_OP_ITEM_TITLE` — 1Password item title

Optional keys:

- `SSH_OP_KEY_FIELD` — defaults to `private key`
- `SSH_OP_KEY_FINGERPRINT_SHA256` — if set, skip re-loading when already in `ssh-agent`
- `SSH_OP_HOSTS_FILE` — defaults to `hosts.conf` (ssh config snippet filename)

SSH host entries (optional) live in:

- `~/.openclaw/skills/ssh-op/hosts.conf`

## Initialization / installation / onboarding

### Preferred (chat-first)

Because the primary interface is chat (Telegram), the preferred onboarding flow is:

1. Ask Boss the required questions in chat.
2. Write the real config file: `config.env`.
3. Run a smoke test (e.g. `ssh-op --help` and a safe `ssh-op -T <alias>`).

### Optional (terminal)

If you are running in a real terminal, you can use the interactive onboarding script:

```bash
~/.openclaw/skills/ssh-op/scripts/onboard.sh
```

(If you want a step-by-step runbook, see `references/onboarding.md`.)

### 1) Put the executable on PATH

Canonical executable lives inside the skill:

- `~/.openclaw/skills/ssh-op/scripts/ssh-op`

For convenience, create a symlink:

```bash
mkdir -p ~/.local/bin
ln -sf ~/.openclaw/skills/ssh-op/scripts/ssh-op ~/.local/bin/ssh-op
```

### 2) Configure which key to load

Run onboarding to populate the real config:

```bash
~/.openclaw/skills/ssh-op/scripts/onboard.sh
```

(Or edit `config.env` manually and set `SSH_OP_VAULT_NAME` / `SSH_OP_ITEM_TITLE`.)

Then validate:

```bash
ssh-op --help
# try a safe ssh command (or any host alias you have configured)
ssh-op -T <host-alias>
```

### 3) (Optional) Manage ~/.ssh/config host aliases

1. Put desired `Host` entries in `hosts.conf`
2. Apply them idempotently (adds/updates a managed block):

```bash
~/.openclaw/skills/ssh-op/scripts/ensure_ssh_config.py
```

This will update `~/.ssh/config` between:

- `# BEGIN ssh-op (managed)`
- `# END ssh-op (managed)`

## Usage

```bash
ssh-op <ssh-args...>
```

Examples:

```bash
ssh-op my-host-alias
ssh-op -T my-host-alias
ssh-op -L 8080:localhost:8080 my-host-alias
```

## Notes / behavior

- No private key is written to disk.
- `ssh-agent` lifetime is tied to the current shell unless you export `SSH_AUTH_SOCK` / `SSH_AGENT_PID`.

## Executables / bin placement

- Keep the canonical executable in the skill folder (`scripts/ssh-op`).
- Use a symlink (e.g. `~/.local/bin/ssh-op`) for convenience.
