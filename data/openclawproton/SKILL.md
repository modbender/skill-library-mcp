---
name: protonmail
description: >
  Protonmail integration via Proton Bridge + himalaya.
  Read, send, search, and organize Protonmail messages.
  Use when the user asks about Protonmail, Proton email, or their proton.me address.
metadata:
  openclaw:
    emoji: "🔒"
    primaryEnv: "PROTON_BRIDGE_PASSWORD"
    install: ["brew install himalaya"]
    requires:
      bins: ["python3", "himalaya", "protonmail-bridge"]
---

# Protonmail

Send, read, search, and organize Protonmail messages via Proton Bridge + himalaya.

**Script:** `scripts/proton.py`
**Config:** `config/config.json`

## First-time setup

When `config/config.json` is missing, the skill outputs `SETUP_REQUIRED` instead of running commands. Follow this two-step flow:

### Step 1: Install Proton Bridge

Proton Bridge runs locally and exposes standard IMAP/SMTP on localhost. It must be installed and logged in before the skill works.

1. Download the `.deb` from https://proton.me/bridge/install
2. Install: `sudo apt install ./protonmail-bridge_*.deb`
3. Set up `pass` for credential storage (Bridge requires it — see `references/setup.md` for details)
4. Log in via Bridge CLI: `protonmail-bridge --cli` then `login`
5. Run `info` inside the Bridge CLI to get the **Bridge password** (a generated string like `abcdefghijklmnop`)
6. Start Bridge as a systemd user service so it runs in the background

**The Bridge password is NOT your Proton account password.** It is a randomly generated credential that Bridge creates for local IMAP/SMTP access. You get it from the `info` command inside Bridge CLI.

Set the Bridge password in OpenClaw's secrets system:
> Use `/secret set PROTON_BRIDGE_PASSWORD` and paste the Bridge password from step 5.

### Step 2: Configure the skill

Ask the user for:
1. **Proton email address** (e.g., `you@proton.me` or `you@pm.me`)
2. **Display name** (for outgoing emails)

Then run:
```bash
python3 $PROTON setup configure --email USER_EMAIL --display-name "USER_NAME"
```

This writes `config/config.json`, generates the himalaya config, and verifies connectivity to Bridge.

## Quick reference

```bash
PROTON=~/.openclaw/workspace/skills/protonmail/scripts/proton.py

# Email
python3 $PROTON email list                                       # Latest 10
python3 $PROTON email list --count 20                            # Latest 20
python3 $PROTON email list --folder Sent                         # Sent folder
python3 $PROTON email list --unread                              # Unread only
python3 $PROTON email read <id>                                  # Read email by ID
python3 $PROTON email read <id> --folder Sent                    # Read from specific folder
python3 $PROTON email send <to> <subject> --body-stdin <<'EOF'    # Send email
body here
EOF
python3 $PROTON email reply <id> --body-stdin <<'EOF'            # Reply to email
body here
EOF
python3 $PROTON email search "from someone"                      # Search emails
python3 $PROTON email search "from someone" --folder Sent        # Search specific folder
python3 $PROTON email move <folder> <id>                         # Move email to folder
python3 $PROTON email move <folder> <id> --from Spam             # Move from specific folder
python3 $PROTON email delete <id>                                # Move to Trash
python3 $PROTON email delete <id> --folder Spam                  # Delete from specific folder

# Folder
python3 $PROTON folder purge <folder>                            # Purge all emails from folder

# Setup
python3 $PROTON setup configure --email X --display-name X       # Write configs
python3 $PROTON setup verify                                     # Smoke test Bridge + himalaya
python3 $PROTON --test                                           # Self-test
```

## Email

### Listing emails

```bash
python3 $PROTON email list                        # Latest 10
python3 $PROTON email list --count 20             # Latest 20
python3 $PROTON email list --folder Sent          # Sent folder
python3 $PROTON email list --unread               # Unread only
```

### Reading emails

```bash
python3 $PROTON email read 142                    # Read by ID from list output
python3 $PROTON email read 142 --folder Sent      # Read from a specific folder
```

**Note:** Email IDs are folder-specific. If you listed emails from `--folder Sent`, use `--folder Sent` when reading them too.

### Sending emails

**IMPORTANT:** Always use `--body-stdin` with a single-quoted heredoc (`<<'EOF'`). This prevents the shell from interpreting `$` signs, backticks, and other special characters in the email body. Without this, text like `$5,000` silently becomes `,000`.

```bash
python3 $PROTON email send "recipient@example.com" "Subject line" --body-stdin <<'EOF'
Body of the email.

The $5,000 payment is confirmed.
EOF
```

**Default From address:** Uses the `account_email` field in `config/config.json`.

**IMPORTANT:** Always ask permission before sending emails on behalf of the user.

### Replying to emails

**IMPORTANT:** Always use `--body-stdin` with a single-quoted heredoc, same as sending.

```bash
python3 $PROTON email reply 142 --body-stdin <<'EOF'
Thanks, that works for me.

The $500 deposit is fine.
EOF
```

### Searching emails

Uses himalaya query syntax (positional args). Defaults to INBOX, 50 results:
```bash
python3 $PROTON email search "from Alice"
python3 $PROTON email search "subject invoice"
python3 $PROTON email search "after 2026-02-01"
python3 $PROTON email search "from Alice and after 2026-01-01"
python3 $PROTON email search "subject receipt" --folder Sent     # Search specific folder
python3 $PROTON email search "from Alice" --count 100            # More results
```

### Moving emails

```bash
python3 $PROTON email move "Trash" 142
python3 $PROTON email move "Archive" 142
python3 $PROTON email move "INBOX" 142 --from Spam    # Move from a specific source folder
```

Protonmail folders: INBOX, Sent, Drafts, Trash, Spam, Archive, All Mail.

**Note:** Argument order is `<folder> <id>` (folder first, same as himalaya). Without `--from`, moves default to INBOX as the source folder.

### Deleting emails

```bash
python3 $PROTON email delete 142                       # Delete from INBOX (default)
python3 $PROTON email delete 142 --folder Spam         # Delete from specific folder
```

## Folder operations

### Purging a folder

Permanently deletes all emails in a folder. The folder itself remains but is emptied.

```bash
python3 $PROTON folder purge "Spam"
python3 $PROTON folder purge "Trash"
```

This is non-interactive (no confirmation prompt), so always confirm with the user before purging.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `SETUP_REQUIRED` output | `config/config.json` missing | Run setup configure (see above) |
| Connection refused on 1143/1025 | Bridge not running | Start Bridge: `systemctl --user start protonmail-bridge` |
| Authentication failed | Wrong password in secret | Get correct Bridge password: run `protonmail-bridge --cli` then `info` |
| `pass` errors on login | GPG key missing or has passphrase | Re-create GPG key with NO passphrase (see `references/setup.md`) |
| Emails not appearing | First sync still running | Wait 5-10 minutes after first Bridge login for mail to sync |
| STARTTLS certificate error | Bridge self-signed cert | IMAP uses `start-tls` with exported cert; SMTP uses `encryption.type = "none"` (localhost-only, safe) |

## Agent instructions

- **Bridge password != Proton password.** The Bridge password is a generated string from `protonmail-bridge --cli` > `info`. Never ask the user for their Proton account password.
- **`SETUP_REQUIRED` signal:** If any command outputs this, stop and walk the user through setup. Do not retry the command.
- **Bridge must be running.** If connection fails, check `systemctl --user status protonmail-bridge` first.
- **Self-signed certificates.** Bridge uses a self-signed TLS cert for localhost. IMAP uses `start-tls` with the exported cert for verification. SMTP uses `encryption.type = "none"` because it's localhost-only — Bridge handles the encrypted connection to Proton's servers.
- **First sync delay.** After initial Bridge login, it takes several minutes to sync all mail. Warn the user if they just set up Bridge and see no emails.
- **Always ask before sending.** Never send an email without explicit user confirmation.

## Notes

- **Config:** `config/config.json` — email address, display name, binary paths, himalaya config location.
- **Auth:** Bridge password entered via `/secret set PROTON_BRIDGE_PASSWORD`, written to `config/auth` (chmod 600) by setup, read by himalaya at runtime.
- **Ports:** Bridge defaults to IMAP 1143, SMTP 1025 on localhost.
- **Self-test:** `python3 $PROTON --test` — verifies config and Bridge connectivity.
- **Full setup guide:** See `references/setup.md` for Bridge installation and `pass` setup details.
