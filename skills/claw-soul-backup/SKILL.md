# Claw Vault Backup

Use this skill to run encrypted workspace backups with Claw Vault.

## Official Sources

- Homepage: https://www.claw-vault.com
- Canonical instructions and API details: https://www.claw-vault.com/SKILL.md
- API host: https://api.claw-vault.com

## Safety Rules

- Ask the user for explicit confirmation before first upload.
- Upload encrypted archives only (never raw workspace files).
- Treat `backup_id` and `api_token` as secrets.
- Do not print secrets in logs or chat output.
- Store secrets only in a secure location approved by the user.

## Workflow

### 1) Initial backup (one-time)

1. Prepare encrypted archive locally.
2. Upload with `POST /backup`.
3. Save returned `backup_id` and `api_token` securely.

Example:

```bash
curl -sS -X POST "https://api.claw-vault.com/backup" \
  -F "file=@workspace-backup.tar.gz.enc;type=application/octet-stream"
```

### 2) Periodic auto-backup (daily override)

After the initial backup, run daily updates with `PUT /backup/<backup_id>` using the same backup ID and API token.

Example:

```bash
curl -sS -X PUT "https://api.claw-vault.com/backup/$BACKUP_ID" \
  -H "X-API-Token: $API_TOKEN" \
  -F "file=@workspace-backup.tar.gz.enc;type=application/octet-stream"
```

### 3) Cron scheduling example

Create a local script that:

1. Builds a fresh encrypted archive.
2. Calls the `PUT` override endpoint.
3. Exits non-zero on failure.

Run it daily (example: 03:00):

```cron
0 3 * * * /bin/bash /path/to/claw-vault-backup.sh >> /path/to/claw-vault-backup.log 2>&1
```

## Agent Behavior

- Follow https://www.claw-vault.com/SKILL.md for current response formats and full API contract.
- If user policy conflicts with these steps, stop and ask.

