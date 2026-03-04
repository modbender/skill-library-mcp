# Troubleshooting

## Common Issues

### Guardian reports timeout but gateway is running

The guardian polls `openclaw health --json`. If the health endpoint returns an error
or the response doesn't contain `"status": "ok"`, the guardian considers the restart
incomplete.

**Fix**: Check `openclaw doctor` output. Common causes:
- Config validation error (invalid JSON in openclaw.json)
- Missing environment variables (API keys, tokens)
- Port conflict (another process on the same port)

### Lock file prevents restart

If a previous restart failed and the lock wasn't cleaned up:

```bash
rm -f /tmp/restart-guard.lock
```

Or use `--force` flag with `restart.py`.

### Guardian can't send notifications

If both primary (openclaw message) and fallback (direct API) fail:
1. Check that the notification config is correct
2. For Telegram: verify `TELEGRAM_BOT_TOKEN` env var is set and chat_id is correct
3. For Slack/Discord: verify webhook URL env var is set
4. Check guardian log for error details

### Restart succeeds but verification fails

The `verify` commands in the context file may have incorrect expectations.
Check:
1. Is the `expect` string actually in the command output?
2. Does the command require the full PATH? (guardian runs in a minimal environment)
3. Is there a timing issue? (config may take a moment to propagate)

### Config backup/rollback

If restart fails and you need to rollback:

```bash
cp ~/.openclaw/custom/restart-guard-work/restart-backup/openclaw.json ~/.openclaw/openclaw.json
openclaw gateway restart  # or manually: openclaw gateway stop && openclaw gateway start
```

## Guardian Process

The guardian is spawned as a fully detached process (nohup + setsid) so it survives
the gateway restart. It:

1. Records the gateway PID before restart
2. Polls `openclaw health --json` every N seconds
3. On success: notifies, cleans up lock, exits 0
4. On timeout: runs diagnostics, notifies with error info, cleans up lock, exits 1

The guardian writes its own log to `<context_dir>/guardian.log`.
