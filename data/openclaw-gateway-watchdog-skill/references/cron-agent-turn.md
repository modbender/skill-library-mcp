# Cron Agent Turn Template

Use this template for the internal OpenClaw cron path.

```text
Run bash {baseDir}/scripts/gateway-watchdog.sh.

Rules:
1) Do not send normal "all good" heartbeats.
2) Only announce when status changes to degraded/critical or recovers to healthy.
3) Include: source, reason, consecutive failures, and whether restart was attempted.
4) Keep output short and ops-friendly.
```

Example job:

```bash
openclaw cron add \
  --name "gateway-watchdog-internal" \
  --cron "*/1 * * * *" \
  --session isolated \
  --message "Run bash {baseDir}/scripts/gateway-watchdog.sh. Announce only state changes." \
  --announce \
  --channel discord \
  --to "channel:<your_channel_id>" \
  --best-effort-deliver
```
