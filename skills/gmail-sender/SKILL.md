# Gmail Sender Skill

Send emails via Gmail SMTP using Google App Password. Generic utility for alerts, notifications, and automated reports.

## Overview

A simple CLI tool to send emails through Gmail SMTP. No external dependencies beyond Python standard library.

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

Clone or copy this skill to your OpenClaw skills directory:
```bash
cp -r gmail-sender ~/.openclaw/workspace/skills/
```

Or use the CLI:
```bash
clawhub install gmail-sender
```

## Usage

```bash
# Make executable
chmod +x gmail-send

# Send email
./gmail-send "recipient@example.com" "Subject" "Body text"
```

### Examples

```bash
# Simple notification
./gmail-send "admin@example.com" "Server Alert" "CPU usage at 90%"

# Cron job integration
0 9 * * 1-5 ~/.openclaw/scripts/gmail-send "you@example.com" "Morning Report" "$(date)"
```

## Python Module Usage

```python
import subprocess

# Call from Python
subprocess.run([
    './gmail-send',
    'recipient@example.com',
    'Subject',
    'Body'
], env={'GMAIL_USER': '...', 'GMAIL_APP_PASSWORD': '...'})
```

## Security Notes

- Never commit App Passwords to version control
- Use environment variables, never hardcode credentials
- App Passwords are 16 characters (format: xxxx xxxx xxxx xxxx)
- Revoke app passwords if compromised

## Troubleshooting

**"535 5.7.8 Username and Password not accepted"**
- Verify App Password is correct (16 chars, no spaces)
- Make sure 2FA is enabled on your Google account

**"Could not connect"**
- Check firewall/network settings
- Gmail may block connections from unknown apps

## License

MIT

## Author

junkaixue
