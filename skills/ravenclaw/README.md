# Ravenclaw Operations Skill

**OpenClaw Skill for Ravenclaw Email Bridge Management**

---

## What This Skill Does

This skill lets you operate the [Ravenclaw Email Bridge](https://github.com/ibrahimq21/ravenclaw) through natural language commands:

- Send emails via SMTP
- Schedule emails for future delivery
- Check inbox and unread emails
- View and cancel scheduled emails
- Monitor system health

---

## Installation

### For OpenClaw Users

1. This skill comes pre-installed with OpenClaw
2. Configure Ravenclaw URL (optional):
   ```bash
   export RAVENCLAW_URL="http://localhost:5002"
   ```

### For Community Sharing

1. Copy the `ravenclaw/` folder to your OpenClaw skills directory:
   ```
   ~/.openclaw/skills/  # Linux/Mac
   %USERPROFILE%\.openclaw\skills\  # Windows
   ```

---

## Quick Start

### 1. Start Ravenclaw

```bash
cd /path/to/ravenclaw
python ravenclaw.py
```

### 2. Configure .env

```env
EMAIL_HOST=mail.yourdomain.com
EMAIL_USERNAME=your@email.com
EMAIL_PASSWORD=yourpassword
DOMAIN_FILTER=yourdomain.com
```

### 3. Use the Skill

**Natural language commands:**

```
send email to manager@company.com with subject "Leave Request" and body "Taking leave tomorrow"

schedule email to hr@company.com with subject "Leave Application" and body "Requesting Feb 20-24 off" at "2026-02-16T09:00:00"

show inbox
list unread emails
check inbox
show scheduled emails
```

---

## Available Commands

| Command | Description |
|---------|-------------|
| `send email to [to] with subject [sub] and body [body]` | Send immediate email |
| `schedule email to [to] with subject [sub] and body [body] at [time]` | Schedule for future |
| `list scheduled emails` | Show pending scheduled emails |
| `cancel scheduled email [id]` | Cancel a scheduled email |
| `check inbox` | Trigger manual email fetch |
| `show unread emails` | List unread messages |
| `show inbox` | List all emails |
| `ravenclaw status` | Health check |

---

## Examples

### Send Leave Request
```
send email to manager@company.com with subject "Leave Request - Feb 20" and body "I would like to take a day off on February 20th for personal reasons."
```

### Schedule Reminder
```
schedule email to myself@company.com with subject "Meeting Reminder" and body "Team sync at 3 PM" at "2026-02-17T14:00:00"
```

### Check Status
```
ravenclaw status
```

---

## Time Format

For scheduled emails, use ISO-8601 format:
```
YYYY-MM-DDTHH:MM:SS
```

Examples:
- `2026-02-20T09:00:00` — February 20, 2026 at 9 AM
- `2026-12-25T00:00:00` — December 25, 2026 at midnight

---

## Troubleshooting

**"Connection refused"**
- Ravenclaw not running → Start with `python ravenclaw.py`

**"Domain not allowed"**
- Recipient domain not in `DOMAIN_FILTER` → Update .env

**"target_time must be in the future"**
- Use a future timestamp in ISO-8601 format

---

## Files

- `SKILL.md` — Full skill documentation
- `ops.sh` — CLI helper script (Linux/Mac)
- `README.md` — This file

---

## Links

- **Ravenclaw Repo:** https://github.com/ibrahimq21/ravenclaw
- **OpenClaw Docs:** https://docs.openclaw.ai
- **Report Issues:** https://github.com/ibrahimq21/ravenclaw/issues

---

**Maintained by:** Ibrahim Qureshi (@ibrahimq21)
