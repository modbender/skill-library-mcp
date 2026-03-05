# SendGrid Skills - Automation Scripts

Token-efficient scripts for common SendGrid operations. Execute without loading into context.

## Available Scripts

### 📤 send-test-email.sh

Send a test email to validate SendGrid API key and configuration.

**Usage:**
```bash
./scripts/send-test-email.sh <recipient-email> [subject] [message]
```

**Examples:**
```bash
# Simple test
./scripts/send-test-email.sh test@example.com

# Custom subject and message
./scripts/send-test-email.sh test@example.com "Test Subject" "Test message body"
```

**Environment variables:**
- `SENDGRID_API_KEY` - SendGrid API key (required)
- `SENDGRID_FROM` - Sender email (default: test@example.com)

**What it does:**
- Validates API key is set
- Sends plain text email via SendGrid Mail Send API
- Reports success/failure with helpful error messages
- Handles common errors (401, 403, 429, 500)

**Limitations:**
- Plain text only (no HTML)
- For HTML emails, use `send-html-email.sh`

**Common errors:**
- **401 Unauthorized**: API key invalid or missing Mail Send permissions
- **403 Forbidden**: Sender email not verified (verify at SendGrid Console)
- **429 Too Many Requests**: Rate limit exceeded

---

### 📧 send-html-email.sh

Send HTML-formatted email via SendGrid API.

**Usage:**
```bash
./scripts/send-html-email.sh <recipient> <subject> <html-content-or-file>
```

**Examples:**
```bash
# Send HTML string
./scripts/send-html-email.sh user@example.com "Welcome" "<h1>Hello!</h1><p>Welcome to our service.</p>"

# Send HTML file
./scripts/send-html-email.sh user@example.com "Daily Report" /path/to/report.html

# With custom sender
export SENDGRID_FROM="noreply@example.com"
./scripts/send-html-email.sh user@example.com "Newsletter" newsletter.html
```

**Environment variables:**
- `SENDGRID_API_KEY` - SendGrid API key (required)
- `SENDGRID_FROM` - Sender email (default: test@example.com)

**What it does:**
- Accepts HTML string or file path
- Properly escapes special characters (quotes, newlines, etc.)
- Sends HTML email with `text/html` content type
- Uses `jq` for safe JSON construction

**Use cases:**
- Daily reports/summaries
- Newsletters
- Formatted notifications
- Rich content emails

**Benefits over send-test-email.sh:**
- Handles complex HTML with special characters
- Supports file input (easier for large templates)
- Proper JSON escaping via `jq`

---

### 📥 verify-inbound-setup.sh

Verify SendGrid Inbound Parse configuration (MX records, webhook endpoint).

**Usage:**
```bash
./scripts/verify-inbound-setup.sh <hostname> [webhook-url]
```

**Examples:**
```bash
# Check MX record only
./scripts/verify-inbound-setup.sh parse.example.com

# Check MX record and test webhook
./scripts/verify-inbound-setup.sh parse.example.com https://webhook.example.com/parse
```

**What it does:**
- Checks MX record points to `mx.sendgrid.net`
- Validates DNS propagation
- (Optional) Tests webhook endpoint accessibility
- Provides clear next steps

**Checks:**
1. MX record exists for hostname
2. MX record value is `mx.sendgrid.net`
3. (Optional) Webhook endpoint returns 2xx or 401 (auth protected)

**Note:** DNS propagation can take 24-48 hours after MX record creation.

---

### 🔧 parse-webhook-payload.js

Parse SendGrid Inbound Parse webhook payload from multipart/form-data.

**Usage:**
```bash
node scripts/parse-webhook-payload.js < payload.txt
curl https://webhook.example.com/parse | node scripts/parse-webhook-payload.js
```

**What it does:**
- Reads multipart/form-data from stdin
- Extracts email fields: from, to, cc, subject, text, html
- Parses email headers
- Extracts SMTP envelope data
- Identifies attachments
- Outputs structured JSON

**Output fields:**
```json
{
  "from": "alice@example.com",
  "to": "support@parse.example.com",
  "subject": "Help request",
  "text": "Plain text body",
  "html": "<p>HTML body</p>",
  "headers": {
    "Date": "...",
    "Message-ID": "...",
    ...
  },
  "envelope": {
    "to": ["support@parse.example.com"],
    "from": "alice@example.com"
  },
  "attachments": [
    {"field": "attachment1", "content": "..."}
  ]
}
```

**Use cases:**
- Debug webhook payloads
- Test payload parsing logic
- Extract email data for processing

---

## Benefits

### Token Efficiency
Scripts execute without loading into context - only output consumes tokens. **~90% token savings** for repetitive operations.

### Deterministic Operations
No code regeneration needed for common tasks. Same input = same output.

### Quick Testing
Validate configuration in seconds without writing code.

## Prerequisites

### send-test-email.sh
- `curl` command
- `SENDGRID_API_KEY` environment variable

### send-html-email.sh
- `curl` command
- `jq` command (for JSON escaping)
- `SENDGRID_API_KEY` environment variable

### verify-inbound-setup.sh
- `dig` or `nslookup` command
- `curl` command (for webhook testing)

### parse-webhook-payload.js
- Node.js runtime

## Integration with Skills

Scripts are referenced from relevant skills:

- **send-email** skill → `send-test-email.sh`, `send-html-email.sh`
- **sendgrid-inbound** skill → `verify-inbound-setup.sh`, `parse-webhook-payload.js`

## Error Handling

All scripts:
- Return non-zero exit codes on failure
- Provide actionable error messages
- Include help via `--help` flag

## Examples

### Complete Inbound Parse Setup Workflow

```bash
# 1. Verify MX record and webhook
./scripts/verify-inbound-setup.sh parse.example.com https://webhook.example.com/parse

# 2. Send test email to trigger webhook
echo "Test email body" | mail -s "Test" anything@parse.example.com

# 3. Parse webhook payload (from logs or capture)
curl https://webhook.example.com/parse | node scripts/parse-webhook-payload.js
```

### Send Email Workflow

```bash
# 1. Test API key
export SENDGRID_API_KEY=SG.xxxxxxxxx
export SENDGRID_FROM=support@example.com
./scripts/send-test-email.sh test@example.com

# 2. If successful, integrate into application
# (API key is valid and sender is verified)
```

## Contributing

When adding new scripts:
1. Include `--help` flag
2. Use `set -e` for bash scripts (exit on error)
3. Provide clear error messages
4. Document in this README
5. Reference from relevant SKILL.md files
