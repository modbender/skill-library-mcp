# Setting Up the Daily Digest Cron Job

To have your digest generated automatically every morning, add a cron job to OpenClaw.

## Example Cron Command

Run this command in your OpenClaw terminal to schedule the digest for 8:00 AM daily:

```bash
openclaw cron add --name "Morning Digest" --schedule "0 8 * * *" --task "Use the daily-digest skill to generate my morning report and log it." --sessionTarget "isolated"
```

## How it Works

1.  **Trigger**: At 8:00 AM, OpenClaw spawns an isolated agent session.
2.  **Execution**: The agent retrieves your emails, calendar, and news.
3.  **Logging**: The agent runs the `digest.js` script to save the stylized report to `~/.openclaw/cron/DailyDigest_logs/`.
4.  **Notification**: The agent uses the `message` tool to send a summary to your Telegram, WhatsApp, or Webchat channel. Since `sessionTarget` is `isolated`, you'll also get the standard completion announcement.

## Customization

You can adjust the `--task` prompt to prioritize specific info, e.g.:
`--task "Run daily-digest. Prioritize tech news and any emails from my manager."`
