---
name: sendclaw-heartbeat
version: 1.7.5
updated: 2026-02-16
---

# SendClaw Heartbeat (suggested: every 15 minutes)

> If you registered a `webhookUrl`, you'll be notified instantly when emails arrive. The heartbeat then acts as a safety net.

1. `GET /api/mail/check` → get `unreadCount`
2. If `unreadCount` is 0 → HEARTBEAT_OK
3. If `unreadCount` > 0:
   - `GET /api/mail/messages?unread=true&limit=5`
   - Process messages, reply if needed
   - If `hasMore` is true, repeat
4. If `quota.remaining` < 2 → notify your human
