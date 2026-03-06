---
name: near-email-reporter
description: Send NEAR reports and alerts via email with SMTP configuration, scheduling, and automatic reporting.
---
# NEAR Email Reporter Skill

Send NEAR transaction reports via email with scheduling.

## Description

This skill allows you to configure email settings, send NEAR transaction reports, set up alerts, and schedule periodic email reports. Uses standard SMTP with secure configuration storage.

## Features

- Configure SMTP email settings
- Send transaction reports via email
- Set up alerts for specific events
- Schedule periodic reports
- Secure configuration storage

## Commands

### `near-email setup [options]`
Configure email settings.

**Options:**
- `--host <host>` - SMTP server host
- `--port <port>` - SMTP server port (default: 587)
- `--user <user>` - SMTP username
- `--pass <pass>` - SMTP password
- `--from <email>` - From email address
- `--secure` - Use SSL/TLS (default: false)

**Example:**
```bash
near-email setup --host smtp.gmail.com --port 587 --user myemail@gmail.com --pass mypassword --from myemail@gmail.com
```

### `near-email report <account_id> [recipient]`
Send a transaction report for an account.

**Parameters:**
- `account_id` - NEAR account to report on
- `recipient` - Email recipient (optional, uses default)

### `near-email alert <account_id> <threshold> [recipient]`
Set up balance alert for an account.

**Parameters:**
- `account_id` - NEAR account to monitor
- `threshold` - Balance threshold (in NEAR)
- `recipient` - Email recipient (optional)

### `near-email schedule <account_id> <cron_expr> [recipient]`
Schedule periodic email reports.

**Parameters:**
- `account_id` - NEAR account to report on
- `cron_expr` - Cron expression (e.g., "0 9 * * *" for daily at 9am)
- `recipient` - Email recipient (optional)

## Configuration

Email settings are stored in `~/.near-email/config.json` with secure permissions.

## Requirements

- SMTP email account (Gmail, SendGrid, etc.)
- Node.js for running the scripts

## Notes

- For Gmail, use App Passwords: https://myaccount.google.com/apppasswords
- Configuration file is stored securely with limited permissions

## References

- Nodemailer: https://nodemailer.com/
- NEAR RPC API: https://docs.near.org/api/rpc
