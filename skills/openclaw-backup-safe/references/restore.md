# Restore OpenClaw from Backup

## Safe Restore

```bash
# 1. Stop OpenClaw
openclaw gateway stop

# 2. Keep current data as safety copy
if [ -d ~/.openclaw ]; then
  mv ~/.openclaw ~/.openclaw-pre-restore-$(date +%Y%m%d-%H%M%S)
fi

# 3. Extract backup
cd ~
tar -xzf ~/openclaw-backups/openclaw-YYYY-MM-DD_HHMM.tar.gz

# 4. Start OpenClaw
openclaw gateway start

# 5. Verify
openclaw status
```

## Rollback if Restore Fails (No Destructive Delete)

```bash
# 1. Stop service
openclaw gateway stop

# 2. Move failed restore out of the way (if present)
if [ -d ~/.openclaw ]; then
  mv ~/.openclaw ~/.openclaw-failed-restore-$(date +%Y%m%d-%H%M%S)
fi

# 3. Put previous directory back
mv ~/.openclaw-old ~/.openclaw

# 4. Start service again
openclaw gateway start
```

## What Is in a Backup

```
~/.openclaw/
├── openclaw.json      # Main config
├── credentials/       # API keys, tokens
├── agents/            # Agent configs, auth
├── workspace/         # Memory, SOUL.md, files
├── telegram/          # Telegram session
└── cron/              # Scheduled tasks
```

## Excluded from Backup

- `completions/` - API response cache (regenerated)
- `*.log` - log files
