# Backup Setup — Conversational Guide

This is the flow the agent should follow when a user asks to set up backups.

---

## Step 1: Welcome

> I'll help you set up OpenClaw backups. Here's what gets backed up:
>
> - **Configuration** — gateway settings, environment
> - **Workspace** — skills, memory, notes, everything in `~/.openclaw/workspace/`
> - **Credentials** — API keys, tokens (in full mode)
>
> Backups are created locally first at `~/backups/openclaw/`, then optionally uploaded to cloud storage.

---

## Step 2: Encryption Passphrase

> Backups are **encrypted by default** with AES-256 (GPG symmetric). You'll need a passphrase.
>
> **You'll need a passphrase to encrypt your backups.** This is required for full backups (which include API keys and credentials). Store it somewhere safe — a password manager, written down, anywhere outside this server.
>
> If you'd prefer not to set a passphrase, we can use **portable mode** instead — it skips credentials entirely so encryption is optional. Good for migrating your agent's memory and config to a new machine, but you'd need to re-enter API keys.
>
> What passphrase would you like to use?

Save the passphrase to `~/.openclaw/credentials/backup/backup-passphrase` (mode 600).

**Important:** If no passphrase is provided and the user wants full backups, do NOT proceed. Full-mode backups contain credentials and must be encrypted. Either get a passphrase or switch to portable mode.

If they choose portable/unencrypted, set `encrypt: false` and `mode: "portable"` in config.

---

## Step 3: Backup Mode

> **Backup modes:**
> - **Full** (default) — Everything including credentials. Always encrypted. Best for disaster recovery.
> - **Portable** — Skips credentials directory. Can be unencrypted. Best for migrating to a new machine.
>
> Which mode? (full/portable)

Update `config.json` with the chosen mode.

---

## Step 4: Schedule

> **How often should backups run?**
> - **Daily** (recommended) — via cron job
> - **Weekly** — once a week
> - **Manual** — only when you run it yourself
>
> I recommend daily — backups are small and old ones are auto-cleaned after 30 days.

Update `config.json` with the schedule. If daily/weekly, set up a cron job:

```bash
# Daily at 3 AM
0 3 * * * ~/.openclaw/workspace/skills/backup/scripts/backup.sh >> ~/backups/openclaw/backup.log 2>&1

# Weekly on Sunday at 3 AM
0 3 * * 0 ~/.openclaw/workspace/skills/backup/scripts/backup.sh >> ~/backups/openclaw/backup.log 2>&1
```

If they also want cloud upload after backup, chain the scripts:
```bash
0 3 * * * ~/.openclaw/workspace/skills/backup/scripts/backup.sh >> ~/backups/openclaw/backup.log 2>&1 && ~/.openclaw/workspace/skills/backup/scripts/upload.sh >> ~/backups/openclaw/upload.log 2>&1
```

---

## Step 5: Cloud Destinations

> **Where should backups be uploaded?** (optional — local backups always happen)
>
> Available destinations:
> 1. **Amazon S3** — reliable, pay-per-use
> 2. **Cloudflare R2** — S3-compatible, no egress fees
> 3. **Backblaze B2** — cheapest storage
> 4. **Google Cloud Storage** — if you're in the GCP ecosystem
> 5. **Google Drive** — free tier available, familiar
> 6. **rsync** — any SSH server
> 7. **None** — local only for now
>
> You can pick multiple. Which ones?

---

## Step 6: Configure Each Destination

For each chosen destination, refer to `destinations.md` for the specific setup instructions.

General flow per destination:
1. Check if the required CLI tool is installed (offer to install if not)
2. Ask for the required credentials/config
3. Save credentials to `~/.openclaw/credentials/backup/<provider>-credentials`
4. Add the destination entry to `config.json`
5. Run `test-backup.sh` to verify connectivity

---

## Step 7: Run Test

> Let me run a quick test to make sure everything works...

```bash
~/.openclaw/workspace/skills/backup/scripts/test-backup.sh
```

Report results. If anything fails, help debug.

---

## Step 8: Confirm & Summary

> ✓ **Backup setup complete!**
>
> **Configuration:**
> - Mode: [full/portable]
> - Encryption: [yes/no]
> - Schedule: [daily/weekly/manual]
> - Local storage: ~/backups/openclaw/ (retained 30 days)
> - Cloud destinations: [list or "none"]
>
> **Quick commands:**
> - Run backup now: `~/.openclaw/workspace/skills/backup/scripts/backup.sh`
> - Upload to cloud: `~/.openclaw/workspace/skills/backup/scripts/upload.sh`
> - Restore: `~/.openclaw/workspace/skills/backup/scripts/restore.sh <file>`
> - Test setup: `~/.openclaw/workspace/skills/backup/scripts/test-backup.sh`
