---
name: email-otp
description: Create temporary email addresses and monitor for registration OTP codes or validation links
version: 1.0.0
metadata:
  author: etopro
---

# Email OTP Skill

A skill for creating temporary email addresses and automatically extracting OTP codes and validation links from incoming emails. Uses the free mail.tm API (no API key required).

## When to Use This Skill

Invoke this skill when the user asks to:
- Create a temporary email address
- Get a disposable email for signup/verification
- Check for OTP (one-time password) codes
- Wait for email verification links
- Monitor an inbox for authentication codes

## Quick Start

```bash
# Create a new temporary email
python3 scripts/tempmail_otp.py create

# Monitor for OTP codes (5 minute timeout)
python3 scripts/tempmail_otp.py check

# List current account and messages
python3 scripts/tempmail_otp.py list
```

## Commands

### Create Account

```bash
python3 scripts/tempmail_otp.py create [OPTIONS]
```

**Options:**
- `-e, --email ADDRESS` - Custom full email address
- `-d, --domain DOMAIN` - Specific domain to use
- `-p, --password PASSWORD` - Account password (auto-generated if not specified)
- `--json` - Output as JSON

**Example:**
```bash
python3 scripts/tempmail_otp.py create --domain "marcilzo.com"
```

### Check for OTP/Links

```bash
python3 scripts/tempmail_otp.py check [OPTIONS]
```

**Options:**
- `--timeout SECONDS` - Max seconds to wait (default: 300)
- `--poll SECONDS` - Poll interval in seconds (default: 3)
- `--sender EMAIL` - Only accept emails from this sender
- `--subject TEXT` - Only accept emails with this in subject
- `--pattern REGEX` - Custom regex pattern for OTP extraction
- `--once` - Exit after first OTP found
- `--json` - Output messages as JSON

**Examples:**
```bash
# Wait up to 2 minutes for OTP
python3 scripts/tempmail_otp.py check --timeout 120

# Only accept emails from noreply@example.com
python3 scripts/tempmail_otp.py check --sender "noreply@example.com"

# Exit immediately after finding OTP
python3 scripts/tempmail_otp.py check --once
```

### List Account and Messages

```bash
python3 scripts/tempmail_otp.py list
```

Shows the current account details and all messages in the inbox with extracted links.

### List Available Domains

```bash
python3 scripts/tempmail_otp.py domains [--json]
```

## Output Files

When an OTP or link is found, the script automatically saves them to the unified state directory:

- `~/.tempmail_otp/last_otp` - Contains the last extracted OTP code
- `~/.tempmail_otp/last_link` - Contains the first interesting validation link found
- `~/.tempmail_otp/account.json` - Account credentials (JWT token, email, password)

All state files are stored in `~/.tempmail_otp/` with restricted permissions (0600).

## OTP Detection Patterns

The script automatically detects OTP codes using these patterns:
- 6-8 digit numbers (most common)
- 4 digit numbers
- "code: XXXXXX" format
- "verification: XXXXXX" format
- "otp: XXXXXX" format

## Link Extraction

The script extracts all HTTP/HTTPS links from email HTML, filtering out:
- Unsubscribe links
- Tracking links
- Image files (.png, .jpg, .gif)

## State Management

All state is stored in a unified directory: `~/.tempmail_otp/`

- `account.json` - Account credentials and JWT token (created by `create` command)
- `last_otp` - Most recent OTP code extracted (created by `check` command)
- `last_link` - First validation link extracted (created by `check` command)

Files have restricted permissions (0600) for security. The `check` and `list` commands automatically use stored credentials.

### Design Rationale

The unified state directory follows best practices for CLI tools:

1. **No project pollution** - No temporary files are created in your working directory
2. **Predictable location** - All state is in one place, easy to find and clean up
3. **Cross-session persistence** - Works from any directory on your system
4. **Permission safety** - Sensitive credentials have proper file permissions

To reset all state: `rm -rf ~/.tempmail_otp/`

## Typical Workflow

1. **Create account** - Generate a new temporary email address
2. **Use email** - Provide the email during service signup
3. **Monitor inbox** - Run the check command to wait for OTP/link
4. **Extract code** - OTP is automatically displayed and saved to `~/.tempmail_otp/last_otp`
5. **Verify** - Use the OTP or link to complete verification

## Example Session

```bash
# Create a temp email
$ python3 scripts/tempmail_otp.py create
Email: a3b7c9d4@marcilzo.com
Password: f8e4d2a1-1234-5678-9abc-123456789abc
Domain: marcilzo.com

Account saved to /home/user/.tempmail_otp/account.json

# In another terminal, wait for OTP
$ python3 scripts/tempmail_otp.py check --once
Monitoring: a3b7c9d4@marcilzo.com
Timeout: 300s | Poll interval: 3s
--------------------------------------------------

📧 New email from: noreply@service.com
   Subject: Your verification code

✅ OTP FOUND: 842197
OTP saved to /home/user/.tempmail_otp/last_otp
--------------------------------------------------
```

## Error Handling

- If email address is already taken, the script automatically retries with a new username
- Network errors are logged and the script continues polling
- Invalid account state prompts to recreate the account

## API

This skill uses the mail.tm REST API:
- Base URL: `https://api.mail.tm`
- Authentication: JWT Bearer token
- No API key required

## Notes

- Temporary emails may expire after inactivity periods
- Some services may block temporary email domains
- The script automatically handles account creation and JWT token management
- OTP patterns cover most common formats, but custom regex can be provided via `--pattern`
