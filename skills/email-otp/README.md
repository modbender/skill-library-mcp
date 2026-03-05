# Email OTP Skill

A Python CLI tool and OpenClaw/Claude skill for creating temporary email addresses and automatically extracting OTP codes and validation links from incoming emails.

## Features

- **Free temporary email** - Uses mail.tm API (no API key required)
- **Automatic OTP extraction** - Detects 4-8 digit verification codes
- **Validation link extraction** - Extracts and saves verification URLs
- **Real-time monitoring** - Polls inbox for new messages with configurable timeout
- **Sender/subject filtering** - Only process emails from specific senders or with specific subjects
- **Unified state management** - All credentials and outputs stored in `~/.tempmail_otp/`

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)
- Internet connection for mail.tm API

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/skill-email-otp.git
cd skill-email-otp
```

2. Make the script executable (optional):
```bash
chmod +x scripts/tempmail_otp.py
```

3. (Optional) Install as a skill for OpenClaw/Claude:
   - Copy to `~/.openclaw/skills/email-otp/` or `~/.claude/skills/email-otp/`

## Quick Start

```bash
# Create a new temporary email
python3 scripts/tempmail_otp.py create

# Use the displayed email for signup, then monitor for OTP
python3 scripts/tempmail_otp.py check --once

# OTP is automatically saved to ~/.tempmail_otp/last_otp
cat ~/.tempmail_otp/last_otp
```

## Commands

### `create` - Create a temporary email account

```bash
python3 scripts/tempmail_otp.py create [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-e, --email ADDRESS` | Custom full email address |
| `-d, --domain DOMAIN` | Specific domain to use (check with `domains` command) |
| `-p, --password PASSWORD` | Account password (auto-generated if not specified) |
| `--json` | Output as JSON |

**Example:**
```bash
python3 scripts/tempmail_otp.py create --domain "marcilzo.com"
```

### `check` - Monitor inbox for OTP/links

```bash
python3 scripts/tempmail_otp.py check [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--timeout SECONDS` | Max seconds to wait (default: 300) |
| `--poll SECONDS` | Poll interval in seconds (default: 3) |
| `--sender EMAIL` | Only accept emails from this sender |
| `--subject TEXT` | Only accept emails with this in subject |
| `--pattern REGEX` | Custom regex pattern for OTP extraction |
| `--once` | Exit after first OTP found |
| `--json` | Output messages as JSON |

**Examples:**
```bash
# Wait up to 2 minutes for OTP
python3 scripts/tempmail_otp.py check --timeout 120

# Only accept emails from noreply@example.com
python3 scripts/tempmail_otp.py check --sender "noreply@example.com"

# Exit immediately after finding OTP
python3 scripts/tempmail_otp.py check --once
```

### `list` - Show account and messages

```bash
python3 scripts/tempmail_otp.py list
```

Displays the current account details and all messages in the inbox with extracted links.

### `domains` - List available domains

```bash
python3 scripts/tempmail_otp.py domains [--json]
```

Shows all available mail.tm domains with their status.

## State Management

All state is stored in a unified directory: `~/.tempmail_otp/`

| File | Purpose |
|------|---------|
| `account.json` | Account credentials and JWT token |
| `last_otp` | Most recent OTP code extracted |
| `last_link` | First validation link extracted |

Files have restricted permissions (0600) for security.

**Reset all state:**
```bash
rm -rf ~/.tempmail_otp/
```

## OTP Detection Patterns

The script automatically detects OTP codes using these patterns:
- 6-8 digit numbers (most common)
- 4 digit numbers
- `code: XXXXXX` format
- `verification: XXXXXX` format
- `otp: XXXXXX` format

For custom patterns, use the `--pattern` option with a regex containing a capture group.

## Link Extraction

Extracts all HTTP/HTTPS links from email HTML, filtering out:
- Unsubscribe links
- Tracking links
- Image files (.png, .jpg, .gif)

## Example Session

```bash
$ python3 scripts/tempmail_otp.py create
Email: a3b7c9d4@marcilzo.com
Password: --------(redacted)
Domain: marcilzo.com

Account saved to /home/user/.tempmail_otp/account.json

# Use email for signup on a website, then:

$ python3 scripts/tempmail_otp.py check --once
Monitoring: a3b7c9d4@marcilzo.com
Timeout: 300s | Poll interval: 3s
--------------------------------------------------

📧 New email from: noreply@service.com
   Subject: Your verification code

✅ OTP FOUND: 842197
OTP saved to /home/user/.tempmail_otp/last_otp
--------------------------------------------------

$ cat ~/.tempmail_otp/last_otp
842197
```

## API

This tool uses the mail.tm REST API:
- Base URL: `https://api.mail.tm`
- Authentication: JWT Bearer token
- No API key required

## Usage as a Skill

When installed as a skill in OpenClaw or Claude Code, the AI assistant can:
- Create temporary email addresses on demand
- Automatically wait for and extract OTP codes
- Parse validation links from emails

See `SKILL.md` for full skill documentation.

## License

MIT

## Notes

- Temporary emails may expire after inactivity periods
- Some services may block temporary email domains
- The script automatically handles account creation and JWT token management
- OTP patterns cover most common formats, but custom regex can be provided via `--pattern`
