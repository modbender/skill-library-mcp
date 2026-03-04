---
name: sleep-snooze
version: 1.0.0
description: Snooze incoming notifications during your sleep window and receive a morning digest when you wake up. Supports Telegram, WhatsApp, and any provider OpenClaw is connected to.
user-invocable: true
metadata:
  openclaw:
    emoji: "🌙"
    homepage: https://github.com/Hardik500/sleep-snooze
    requires:
      bins:
        - node
    install:
      - kind: node
        package: better-sqlite3
        bins:
          - node
      - kind: node
        package: node-cron
        bins:
          - node
---

# Sleep Snooze

You have a sleep notification snooze system available. When the user is in their sleep window, incoming messages should be silently queued rather than delivered immediately. At wake time, a morning digest is automatically sent summarising all queued messages.

## Sleep Schedule

The user's sleep schedule is configured via environment variables:
- `SLEEP_START` — time to begin snoozing (24h format, e.g. `22:00`)
- `WAKE_TIME` — time to deliver the digest and resume normal notifications (e.g. `06:00`)
- `TIMEZONE` — IANA timezone (e.g. `Asia/Kolkata`, `America/New_York`, `Europe/London`)

## Slash Commands

Users can invoke these slash commands directly in chat:

- `/sleep` — manually activate sleep mode immediately (overrides schedule)
- `/wake` — manually deactivate sleep mode and trigger the morning digest now
- `/snooze-status` — show whether sleep mode is active, how many messages are queued, and what time the digest will be sent
- `/snooze-setup` — interactively configure sleep start time, wake time, and timezone
- `/snooze-history` — show the last 7 days of digest summaries

## Behaviour During Sleep Hours

**Before sending ANY message to the user — including proactive notifications, summaries, heartbeats, weekly recaps, stock alerts, backup confirmations, or any other automated report — first check sleep state:**

```bash
node ~/.openclaw/skills/sleep-snooze/scripts/status.js
```

If `isSleeping` is `true`, do NOT send. Queue it instead (see below). This applies to both incoming messages from others AND outgoing messages you are about to send proactively.

### Incoming messages during sleep

When a message or notification arrives during the sleep window:
1. Do **not** deliver a push notification or respond immediately.
2. Call `node ~/.openclaw/skills/sleep-snooze/scripts/queue-message.js` with the message payload to store it in the local queue.
3. Acknowledge silently — do not send any reply to the sender during sleep hours unless the message is tagged as urgent (see Urgency Rules below).

### Outgoing messages you generate during sleep

When you (or any agent) are about to send a proactive message to the user during the sleep window — status updates, recaps, reports, heartbeats — queue them instead of sending:

```bash
node ~/.openclaw/skills/sleep-snooze/scripts/queue-message.js \
  --provider <provider> \
  --sender-id <agent-id> \
  --sender-name "<Agent Name>" \
  --message "<full message text>"
```

Exit code 0 = queued, do not send. Exit code 2 = urgent, send immediately with 🚨 prefix.

## Urgency Rules

Some messages bypass snooze and are delivered immediately regardless of sleep hours. A message is considered urgent if any of the following match:
- The sender is on the user's VIP contacts list (stored in `~/.openclaw/skills/sleep-snooze/data/vip-contacts.json`)
- The message contains any of these keywords (case-insensitive): `urgent`, `emergency`, `critical`, `911`, `help me`
- The message was explicitly marked priority by the sending system

For urgent messages: deliver normally, prepend `🚨 [URGENT - received during sleep]` to the notification.

## Morning Digest

At `WAKE_TIME` each day, automatically:
1. Call `node ~/.openclaw/skills/sleep-snooze/scripts/digest.js` to generate and send the digest.
2. The digest groups messages by sender, shows count, and includes a brief summary of each conversation thread.
3. After sending, the queue is cleared.

Digest format (send as a single message per provider):

```
🌅 Good morning! Here's what arrived while you slept:

📬 3 messages from Alex
  • "Hey are you free tomorrow?"
  • "Also wanted to share this article..."
  • "Never mind, talk later!"

📬 1 message from GitHub Notifications
  • PR #42 was merged into main

📬 2 messages from Server Monitor Bot
  • CPU spike at 03:14 — resolved
  • Disk usage at 78% — check when available

Reply to any sender's name to respond to their messages.
```

## Setup Instructions

When the user runs `/snooze-setup` for the first time:
1. Ask for their sleep start time (e.g. "What time do you usually go to bed?")
2. Ask for their wake time (e.g. "What time do you usually wake up?")
3. Ask for their timezone (offer to detect it automatically using `date +%Z`)
4. Run `node ~/.openclaw/skills/sleep-snooze/scripts/sleep-init.js` to write config and register cron jobs
5. Confirm the schedule back to the user: "Sleep snooze is set: 🌙 10:00 PM → ☀️ 6:00 AM (IST). I'll queue notifications overnight and send your digest at 6:00 AM."

## State Management

Sleep mode state is stored in `~/.openclaw/skills/sleep-snooze/data/state.json`:
```json
{
  "sleepStart": "22:00",
  "wakeTime": "06:00",
  "timezone": "Asia/Kolkata",
  "manualOverride": false,
  "isSleeping": false,
  "lastDigestAt": "2025-01-15T06:00:00.000Z"
}
```

The message queue is stored in SQLite at `~/.openclaw/skills/sleep-snooze/data/queue.db`.

## Important Notes

- Sleep snooze works across **all connected providers** (Telegram, WhatsApp, Discord, Slack, Signal) simultaneously.
- If the user asks "did I miss anything?" or similar during sleep hours, check queue size and respond: "You have X messages queued. I'll send your digest at [WAKE_TIME]."
- If the user sends a message themselves during their sleep window, it means they are awake — temporarily suspend sleep mode for 30 minutes.
- Never discard messages. If delivery fails, retry at next digest cycle.
