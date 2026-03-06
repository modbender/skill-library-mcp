---
name: Ravenclaw Operations Skill
description: "For users to use this skill: 1. They must have Ravenclaw installed
  locally 2. Ravenclaw must be running 3. Configuration via environment or
  RAVENCLAWURL"
---

# Ravenclaw Operations Skill

**Category:** Email Automation / Communication

**Description:** Operate the Ravenclaw Email Bridge — send emails, schedule future emails, check inbox, and manage email workflows. Forward POP3 emails to Discord webhooks with scheduled sending capabilities.

**Maintainer:** Ibrahim Qureshi (@ibrahimq21)

**Tags:** email, discord, webhook, automation, smtp, pop3, scheduled

---

## Capabilities

- Send immediate emails via SMTP
- Schedule emails for future delivery
- Check inbox and unread emails
- Trigger manual email checks
- View scheduled email queue
- Cancel scheduled emails
- Health checks and statistics

---

## Requirements

### Local Setup (for direct operation)

**Ravenclaw must be running:**
```bash
# Start Ravenclaw bridge
cd path/to/ravenclaw
python ravenclaw.py

# Default port: 5002
```

**Environment variables:**
- `RAVENCLAW_URL` (optional): Custom URL for Ravenclaw API (default: `http://localhost:5002`)

### Community Sharing

For users to use this skill:
1. They must have Ravenclaw installed locally
2. Ravenclaw must be running
3. Configuration via environment or `RAVENCLAW_URL`

---

## Commands

### Send Email

Send an immediate email.

**Pattern:**
```
send email to [recipient] with subject [subject] and body [body]
```

**Example:**
```
send email to manager@company.com with subject "Leave Request" and body "I would like to take leave tomorrow."
```

**Parameters:**
- `recipient` (required): Email address
- `subject` (required): Email subject line
- `body` (required): Email content

**API Call:** `POST /send`

---

### Schedule Email

Schedule an email to be sent at a specific time.

**Pattern:**
```
schedule email to [recipient] with subject [subject] and body [body] at [time]
```

**Example:**
```
schedule email to hr@company.com with subject "Leave Application" and body "Requesting leave for next Monday" at "2026-02-23T09:00:00"
```

**Parameters:**
- `recipient` (required): Email address
- `subject` (required): Email subject line
- `body` (required): Email content
- `time` (required): ISO-8601 timestamp (e.g., `2026-02-23T09:00:00`)

**API Call:** `POST /schedule`

**Tips:**
- Use format: `YYYY-MM-DDTHH:MM:SS`
- Time must be in the future
- High priority emails get more retry attempts

---

### List Scheduled Emails

View all scheduled emails.

**Pattern:**
```
list scheduled emails
show scheduled emails
```

**API Call:** `GET /schedule/list`

**Response includes:**
- Total emails
- Pending count
- Full list with status, target time, recipient

---

### Cancel Scheduled Email

Cancel a pending scheduled email.

**Pattern:**
```
cancel scheduled email [id]
```

**Example:**
```
cancel scheduled email sched_20260223100000_0
```

**API Call:** `POST /schedule/cancel/<id>`

---

### Check Inbox

Trigger a manual inbox check.

**Pattern:**
```
check inbox
check emails
```

**API Call:** `POST /check`

**Behavior:**
- Fetches new emails from POP3 server
- Forwards to Discord (if configured)
- Updates inbox JSON

---

### View Unread Emails

Get list of unread emails.

**Pattern:**
```
show unread emails
get unread
```

**API Call:** `GET /unread`

---

### View All Inbox

Get all emails from inbox.

**Pattern:**
```
show inbox
list emails
```

**API Call:** `GET /inbox`

---

### Health Check

Check Ravenclaw status.

**Pattern:**
```
ravenclaw status
ravenclaw health
```

**API Call:** `GET /health`

**Response:**
- Running status
- Account info
- Email counts
- Domain configuration

---

### Statistics

View processing statistics.

**Pattern:**
```
ravenclaw stats
email statistics
```

**API Call:** `GET /stats`

**Includes:**
- Total emails
- Unread count
- Pending scheduled emails
- Allowed domains

---

## Configuration Examples

### Direct Operation (when Ravenclaw is local)

```yaml
# No special config needed
# Uses http://localhost:5002 by default
```

### Custom URL

```bash
# Set environment variable
export RAVENCLAW_URL="http://your-server:5002"
```

### Ravenclaw .env Configuration

```env
# Required
EMAIL_HOST=mail.yourdomain.com
EMAIL_USERNAME=your@email.com
EMAIL_PASSWORD=yourpassword

# Optional
DOMAIN_FILTER=yourdomain.com
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
BRIDGE_PORT=5002
```

---

## Use Cases

### Leave Requests
```
schedule email to manager@company.com with subject "Leave Request - March 2-6" and body "Dear Manager,\n\nI would like to request leave..." at "2026-02-16T10:00:00"
```

### Meeting Reminders
```
schedule email to team@company.com with subject "Meeting Tomorrow" and body "Don't forget about the sync meeting at 10 AM" at "2026-02-17T09:00:00"
```

### Auto-Notifications
```
send email to alerts@company.com with subject "System Alert" and body "CPU usage exceeded 90%"
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Ravenclaw not running | Start Ravenclaw: `python ravenclaw.py` |
| Domain not allowed | Recipient domain not in filter | Update `DOMAIN_FILTER` in .env |
| target_time must be in future | Scheduled time passed | Use future timestamp |
| SMTP failed | Email server error | Check .env credentials |

---

## Troubleshooting

**Ravenclaw not responding:**
```bash
# Check if running
curl http://localhost:5002/health

# Start Ravenclaw
cd path/to/ravenclaw
python ravenclaw.py
```

**Emails not sending:**
- Verify SMTP credentials in `.env`
- Check domain is in `DOMAIN_FILTER`
- Review `ravenclaw.log`

**Scheduled emails not sent:**
- Ravenclaw must be running for scheduled sending
- Check `/schedule/list` for status
- Ensure `target_time` is in ISO-8601 format

---

## Files

- **SKILL.md** — This documentation
- **skill.yaml** — Skill definition (if needed)
- **ops.sh** — Helper operations (optional)

---

## Integration Notes

This skill requires:
1. Ravenclaw server running locally
2. SMTP/POP3 access configured in `.env`
3. Network access to `localhost:5002`

For community sharing, users need their own Ravenclaw instance with their own email credentials.

---

## Related

- **Ravenclaw Repo:** https://github.com/ibrahimq21/ravenclaw
- **Documentation:** See `README.md` in Ravenclaw repo
