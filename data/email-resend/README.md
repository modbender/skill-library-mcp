# Email Resend Skill

Send and receive emails using the Resend API.

## License: Apache-2.0

See LICENSE file for full text.

## Features

- **Send emails** directly via Resend API
- **Receive notifications** via cron job (every 15 minutes)
- **Reply with proper threading** (Gmail-compatible)
- **Download attachments** from inbound emails
- **Custody chain tracking** - full lineage from email to notification to actions

## Quick Setup

```bash
# Required environment variables
export RESEND_API_KEY="re_123456789"
export DEFAULT_FROM_EMAIL="you@example.com"
export DEFAULT_FROM_NAME="Your Name"
```

## Usage

### Send an Email
```bash
python3 skills/email-resend/scripts/outbound.py \
  --to "recipient@example.com" \
  --subject "Hello" \
  --body "Message text"
```

### Reply to Email (Use This!)
```bash
# Step 1: Start draft
python3 skills/email-resend/scripts/draft-reply.py start <email_id>

# Step 2: Set content
python3 skills/email-resend/scripts/draft-reply.py content "Your reply"

# Step 3: Send
python3 skills/email-resend/scripts/draft-reply.py send
```

### Check Inbound Emails
```bash
python3 skills/email-resend/scripts/inbound.py
```

### Download Attachments
```bash
python3 skills/email-resend/scripts/download_attachment.py <email_id> --output-dir ./attachments
```

## Cron Setup (Email Notifications)

```bash
openclaw cron add \
  --name "email-resend-inbound" \
  --schedule "cron */15 * * * *" \
  --message "Follow instructions in skills/email-resend/cron-prompts/email-inbound.md exactly." \
  --session isolated \
  --announce \
  --channel telegram \
  --to "-1003748898773:topic:334"
```

See SKILL.md for complete documentation.
