---
name: dead-or-not
description: |
  A "life check" skill that periodically checks if the user is still responsive. 
  If the user hasn't messaged for a set time, it asks if they're okay, and if no reply, 
  sends an email to emergency contacts. User can customize email content, SMTP settings, 
  and check time. Use when: (1) Creating a "DeadOrNot" app (2) Daily health check 
  (3) Auto-notify on unresponsive users (4) Setting up check-in reminders
---

# DeadOrNot

Daily check to see if user is still responsive - asks if okay, sends email if no reply.

## How It Works

1. User messages → updates last_seen timestamp
2. Cron runs daily → sets check_flag if timeout exceeded
3. Agent reads check_flag → asks user if they're okay
4. No reply → calls send_mail.py to notify emergency contact

## Quick Start

### 1. Initialize

```bash
mkdir -p ~/.openclaw/apps/deadornot
```

### 2. Configure

Create config file `~/.openclaw/apps/deadornot/config`:

```bash
NOTIFY_EMAIL=your_email@example.com
MESSAGE=User is unresponsive, please check on them!
TIMEOUT_HOURS=24
ASK_HOUR=10
SMTP_SERVER=smtp.qq.com
SMTP_PORT=465
SMTP_EMAIL=your_qq@qq.com
SMTP_PASSWORD=your_auth_code
```

### 3. Set up Cron

```bash
crontab -l | { cat; echo "0 0 * * * /path/to/check.sh >> /path/to/log.txt 2>&1"; } | crontab -
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| TIMEOUT_HOURS | 24 | Hours without message before check |
| NOTIFY_EMAIL | - | Emergency contact (required) |
| MESSAGE | "User is unresponsive!" | Email content |
| ASK_HOUR | 10 | When to ask (0-23) |
| SMTP_SERVER | smtp.qq.com | SMTP server |
| SMTP_PORT | 465 | SMTP port |
| SMTP_EMAIL | - | Sender email |
| SMTP_PASSWORD | - | SMTP auth code |
