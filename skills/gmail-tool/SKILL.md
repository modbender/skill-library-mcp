# Gmail Tool

Send and read emails via Gmail using App Password. CLI utility for automated alerts, notifications, and email monitoring.

## Overview

A CLI tool to send and read emails through Gmail. Combines SMTP (send) and IMAP (read) in one utility.

## Requirements

- Python 3.6+
- Gmail account with App Password enabled

## Setup

1. Enable 2-Factor Authentication on your Google Account:
   - Go to https://myaccount.google.com/security

2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Copy the 16-character password (no spaces)

3. Set environment variables:
```bash
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="xxxxxxxxxxxxxxxx"
```

## Installation

```bash
# Clone or copy to skills directory
cp -r gmail-tool ~/.openclaw/workspace/skills/

# Or use ClawHub
clawhub install gmail-tool
```

## Usage

### Send Email
```bash
chmod +x gmail-tool
./gmail-tool send "recipient@example.com" "Subject" "Body text"
```

### Read Emails
```bash
# Read last 5 emails
./gmail-tool read

# Read last 10 emails
./gmail-tool read 10
```

### Examples

```bash
# Send notification
./gmail-tool send "admin@example.com" "Alert" "Server down!"

# Check inbox
./gmail-tool read 3

# Cron job - check and alert
0 9 * * 1-5 ./gmail-tool read 1 | grep -q "Important" && ./gmail-tool send "you@example.com" "Check Email" "Found important email"
```

## Commands

| Command | Usage |
|---------|-------|
| `send <to> <subject> <body>` | Send an email |
| `read [count]` | Read last N emails (default: 5) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| GMAIL_USER | Yes | Your Gmail address |
| GMAIL_APP_PASSWORD | Yes | 16-char App Password |

## Security Notes

- Never commit App Passwords to version control
- Use environment variables, never hardcode credentials
- App Passwords are 16 characters (no spaces)
- Revoke app passwords if compromised

## Troubleshooting

**Send failed: "535 5.7.8 Username and Password not accepted"**
- Verify App Password is correct
- Make sure 2FA is enabled

**Read failed: "Too many simultaneous connections"**
- Gmail limits IMAP connections. Wait and retry.

## License

MIT

## Author

junkaixue
