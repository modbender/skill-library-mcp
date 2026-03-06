# SPIRIT Cron Setup Guide

## Option 1: System Crontab (Recommended for Servers)

```bash
# Edit crontab
crontab -e

# Add entries (adjust path as needed):

# Sync every 15 minutes
*/15 * * * * /root/.openclaw/workspace/spirit-skill/scripts/spirit-sync-cron.sh

# Sync hourly with custom message
0 * * * * cd ~ && [ -d .spirit ] && spirit backup --message "Hourly checkpoint" 2>/dev/null

# Sync daily at 2 AM
0 2 * * * cd ~ && [ -d .spirit ] && spirit backup --message "Daily backup" 2>/dev/null
```

## Option 2: OpenClaw Cron Integration

For agents running on OpenClaw-managed hosts:

### Using sessions_spawn (Isolated Agent)

```bash
openclaw cron add \
  --name spirit-auto-sync \
  --schedule "*/15 */1 * * *" \
  --sessionTarget isolated \
  --agentTurn "Run spirit sync for automatic state preservation."
```

### Using systemEvent (Main Session Wake)

```bash
# Creates a system event every 15 minutes that wakes the main agent
openclaw cron add \
  --name spirit-reminder \
  --schedule "*/15 */1 * * *" \
  --sessionTarget main \
  --systemEvent "SPIRIT: Time for auto-sync checkpoint"
```

Then in your agent logic, respond to "SPIRIT:" messages by running `spirit sync`.

## Option 3: SPIRIT Built-in Auto-Backup

```bash
# Enable SPIRIT's own auto-backup daemon
spirit autobackup --interval=15m

# Check status
spirit autobackup --status

# Disable
spirit autobackup --disable
```

## Monitoring

Check sync logs:

```bash
# View cron sync log
tail -f ~/.spirit/.cron-sync.log

# View OpenClaw cron runs
openclaw cron runs --jobId <job-id>

# List all Spirit backups
spirit status
```

## Troubleshooting

### Cron not running
- Check `which spirit` — is it in PATH?
- Test manually: `/root/.openclaw/workspace/spirit-skill/scripts/spirit-sync-cron.sh`

### Sync failing
- Check `~/.spirit/` exists and is initialized
- Verify git remote: `cd ~/.spirit && git remote -v`
- Check credentials (PAT/SSH key)

### Conflicts
- SPIRIT handles merge conflicts via `git pull --rebase`
- If conflicts persist, resolve manually: `cd ~/.spirit && git status`
