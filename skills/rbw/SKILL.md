---
name: rbw
description: Securely interact with Bitwarden/Vaultwarden vaults using rbw CLI. Use when retrieving credentials, managing vault items, or integrating secrets into scripts/systemd services. Handles authentication, field access, and non-interactive operation patterns.
---

## Quick Reference

```bash
rbw unlock                                          # unlock vault
rbw list                                            # list all items
rbw list --fields "name,folder"                     # list with folders
rbw get item_name                                   # get password
rbw get --folder folder_name item_name              # get from folder
rbw get --folder folder_name item_name --field url  # get specific field
rbw sync                                            # sync vault
```

## Command Syntax

### get

```bash
rbw get [OPTIONS] <NAME> [USER]

Options:
  --folder <FOLDER>  Folder to search in
  --field <FIELD>    Specific field to retrieve (omit for password)
  --full             Include notes in output
  --raw              Output as JSON
  --clipboard        Copy result to clipboard
```

`<NAME>` is a positional argument. `[USER]` disambiguates when multiple items share the same name. All option flags (`--folder`, `--field`, etc.) must precede the positional arguments.

```bash
rbw get --folder homelab portainer
rbw get --folder homelab portainer --field url
rbw get my_password
rbw get --folder work email user@example.com   # USER disambiguation
```

### list

```bash
rbw list [OPTIONS]

Options:
  --fields <FIELDS>  Fields to display: id, name, user, folder, type
  --raw              Output as JSON
```

Note: `rbw list` does **not** support `--folder` filtering. Use `rbw list --fields "name,folder"` and grep if needed.

```bash
rbw list --fields "name,folder"
rbw list --raw | jq
```

### add

```bash
rbw add [OPTIONS] <NAME> [USER]

Options:
  --folder <FOLDER>  Folder for the new entry
  --uri <URI>        URI for the entry
```

rbw will prompt for the password inline. Notes (if any) open in `$EDITOR`.

```bash
rbw add --folder homelab my_service admin_user
rbw add --folder homelab --uri https://example.com my_service
```

## Field Names

Field names are **case-sensitive** and must match exactly as defined in Vaultwarden.

```bash
rbw get --folder homelab item                      # password (no --field)
rbw get --folder homelab item --field Username     # default Username field (capital U)
rbw get --folder homelab item --field database     # custom field
rbw get --folder homelab item --field api_key      # custom field
```

To inspect all fields on an item:
```bash
rbw get --folder homelab item --raw | jq
```

## Authentication

### Interactive

```bash
# Check status (exits 0 if unlocked, non-zero if locked)
rbw unlocked

# Unlock (prompts for master password)
rbw unlock
```

### Non-Interactive (Systemd/Scripts)

> **Security note:** This pattern stores your master password in a plaintext file. Even with `600` permissions and `root:root` ownership, this is a security tradeoff. For higher-security environments, consider systemd's native `LoadCredential=` mechanism instead.

**1. Create a pinentry wrapper** (`~/.local/bin/pinentry-rbw-systemd`):

```bash
#!/usr/bin/env bash
if [ -n "$RBW_MASTER_PASSWORD" ]; then
    echo "OK Pleased to meet you"
    while IFS= read -r line; do
        case "$line" in
            GETPIN)
                echo "D $RBW_MASTER_PASSWORD"
                echo "OK"
                ;;
            BYE)
                echo "OK closing connection"
                exit 0
                ;;
            *)
                echo "OK"
                ;;
        esac
    done
else
    exec /usr/bin/pinentry-curses "$@"
fi
```

**2. Configure rbw to use it:**

```bash
chmod +x ~/.local/bin/pinentry-rbw-systemd
rbw config set pinentry ~/.local/bin/pinentry-rbw-systemd
rbw config show   # verify
```

**3. Store master password** (`/etc/systemd/rbw-credentials.conf`, `root:root`, `chmod 600`):

```
RBW_MASTER_PASSWORD=your_master_password_here
```

**4. Systemd service:**

```ini
[Service]
User=tripleight
EnvironmentFile=/etc/systemd/rbw-credentials.conf
ExecStart=/path/to/script.sh
```

**5. Script pattern:**

```bash
#!/usr/bin/env bash
set -euo pipefail

if ! rbw unlocked 2>/dev/null; then
    rbw unlock || { echo "ERROR: Failed to unlock rbw" >&2; exit 1; }
fi

rbw sync

USERNAME=$(rbw get --folder homelab service_name --field Username 2>/dev/null \
  || { echo "ERROR: Cannot read username (homelab/service_name)" >&2; exit 1; })
PASSWORD=$(rbw get --folder homelab service_name 2>/dev/null \
  || { echo "ERROR: Cannot read password (homelab/service_name)" >&2; exit 1; })

curl -u "$USERNAME:$PASSWORD" https://api.example.com
```

## Vaultwarden Item Setup

A typical item used with rbw:

```
Folder:   homelab
Name:     postgres_backup
Type:     Login
Username: postgres          ← accessed with --field Username
Password: **********        ← accessed without --field

Custom fields:
  database  production      ← accessed with --field database
  host      db.example.com
  port      5432
```

Corresponding script access:

```bash
USERNAME=$(rbw get --folder homelab postgres_backup --field Username)
PASSWORD=$(rbw get --folder homelab postgres_backup)
DATABASE=$(rbw get --folder homelab postgres_backup --field database)
HOST=$(rbw get --folder homelab postgres_backup --field host)
PORT=$(rbw get --folder homelab postgres_backup --field port)
```

## Error Handling

Always check exit codes and provide actionable error messages:

```bash
VALUE=$(rbw get --folder homelab item --field field 2>/dev/null \
  || { echo "ERROR: Cannot read 'field' from vault (homelab/item)" >&2; exit 1; })

if [ -z "$VALUE" ]; then
    echo "ERROR: Field is empty in vault" >&2
    exit 1
fi
```

## Troubleshooting

**"agent is locked"** — run `rbw unlock`.

**"field not found"** — field names are case-sensitive. Inspect the item with `rbw get item --raw | jq` to see exact names. Then run `rbw sync` to ensure the vault is current.

**Systemd service fails to unlock:**
1. Verify `/etc/systemd/rbw-credentials.conf` exists with the correct password
2. Check permissions: `sudo ls -l /etc/systemd/rbw-credentials.conf` (expect `root:root 600`)
3. Verify pinentry config: `rbw config show`
4. Test manually: `sudo -u tripleight bash -c 'export RBW_MASTER_PASSWORD=...; rbw unlock'`

**Item not found** — check folder and item names with `rbw list --fields "name,folder"`, then `rbw sync`.

## Best Practices

Always sync before reading to ensure the latest vault state. Always check unlock status before attempting reads to avoid unnecessary prompts. Handle errors explicitly with useful messages. Never hardcode secrets — use rbw for everything. Keep systemd credential files `600 root:root`. Use folders to organise items across environments (production, staging, homelab, etc.).
