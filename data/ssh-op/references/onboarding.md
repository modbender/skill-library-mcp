# ssh-op onboarding (runbook)

This file is a runbook for onboarding. Follow it manually (or implement an interactive script later).

1) Prereqs
- `op whoami`
- `command -v ssh ssh-agent ssh-add`

2) Choose key source (1Password)
- Set in `../config.env`:
  - `SSH_OP_VAULT_NAME`
  - `SSH_OP_ITEM_TITLE`
  - `SSH_OP_KEY_FIELD` (default: `private key`)
  - optional `SSH_OP_KEY_FINGERPRINT_SHA256`

3) Validate
- Run: `../scripts/ssh-op --help`
- Run a connection test: `ssh-op <your-alias> -T` (or any safe ssh args)

4) Optional: manage ~/.ssh/config
- Put Host entries in `../hosts.conf`
- Run: `../scripts/ensure_ssh_config.py`
