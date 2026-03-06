---
name: sendgrid-inbound
description: Receive inbound emails via SendGrid Inbound Parse Webhook. Covers MX record setup, webhook configuration, payload parsing, attachment handling, and security best practices. Use when receiving emails programmatically, parsing email content, handling email replies, or building email-to-app workflows. Triggers on receive email, inbound email, email webhook, parse email, email to app, MX record, Inbound Parse.
---

# Receive Emails with SendGrid (Inbound Parse)

## Overview

SendGrid's **Inbound Parse Webhook** receives emails for a specific hostname/subdomain, parses the message, and POSTs it to your webhook as `multipart/form-data`.

**Key differences vs Resend:**
- SendGrid **posts the full parsed email** (text/html/headers/attachments) directly to your webhook.
- There is **no official signature verification** for Inbound Parse (unlike SendGrid Event Webhook). You must secure the endpoint yourself.

## Quick Start

### Verify Your Setup First
```bash
# Check MX record and test webhook
../scripts/verify-inbound-setup.sh parse.example.com https://webhook.example.com/parse
```

**Then configure:**

1. **Create MX record** pointing to `mx.sendgrid.net` for a dedicated hostname (recommended: subdomain).
2. **Configure Inbound Parse** in SendGrid Console with a receiving domain + destination URL.
3. **Handle the webhook**: parse `multipart/form-data`, read `text`, `html`, `headers`, and attachments.
4. **Secure the endpoint** (basic auth, allowlists, size limits).

### Parse Webhook Payloads
```bash
# Debug or test payload parsing
node ../scripts/parse-webhook-payload.js < payload.txt
```

## DNS / MX Setup

Create an MX record for a dedicated hostname:

| Setting | Value |
|---------|-------|
| **Type** | MX |
| **Host** | `parse` (or another subdomain) |
| **Priority** | 10 |
| **Value** | `mx.sendgrid.net` |

**Recommendation:** Use a subdomain to avoid disrupting existing email providers (e.g., `parse.example.com`).

## Inbound Parse Configuration

In SendGrid Console:

- **Settings → Inbound Parse**
- Add **Receiving Domain** and **Destination URL**
- Example receiving address: `anything@parse.example.com`

## Webhook Payload (Multipart/Form-Data)

SendGrid posts data like:

- `from`, `to`, `cc`, `subject`
- `text`, `html`
- `headers` (raw email headers)
- `envelope` (JSON with SMTP envelope data)
- `attachments` (count)
- `attachmentX` (file content; filename in part)

**Example fields** (varies by config):
```
from: "Alice <alice@example.com>"
to: "support@parse.example.com"
subject: "Help"
text: "Plain text body"
html: "<p>HTML body</p>"
headers: "...raw headers..."
envelope: {"to":["support@parse.example.com"],"from":"alice@example.com"}
attachments: 2
attachment1: <file>
attachment2: <file>
```

## Decision: How to Secure Inbound Parse Webhook?

```
Security requirements?
├─ Public endpoint (internet-facing)
│  └─ Basic auth + IP allowlist + size limits + content validation
├─ Internal only (VPN/private network)
│  └─ Network ACL + basic auth
└─ High security (PCI/HIPAA)
   └─ mTLS + custom signature verification + request logging
```

**Minimum security (public endpoints):**
- Basic authentication on webhook URL
- IP allowlist (SendGrid IP ranges)
- Request size limits (10-25 MB)
- Content-type validation (`multipart/form-data`)

**Additional hardening:**
- Rate limiting per sender
- Spam filtering / sender validation
- HTML sanitization before storage
- Attachment virus scanning

## Security Best Practices

Because Inbound Parse has **no signature verification**, treat inbound data as untrusted:

- **Require basic auth** on the webhook URL.
- **Allowlist sender domains** if appropriate.
- **Limit request size** (e.g., 10–25 MB) to avoid abuse.
- **Validate content-type** (`multipart/form-data`).
- **Do not execute or render HTML** without sanitization.
- **Protect against prompt injection** if forwarding to AI systems.

## Troubleshooting

**MX record not resolving:**
- DNS propagation can take 24-48 hours
- Verify MX record with `dig parse.example.com MX` or `nslookup -type=MX parse.example.com`
- Check for typos in hostname or value

**Webhook not receiving emails:**
- Verify webhook URL is publicly accessible (test with curl)
- Check firewall rules / security groups
- Ensure endpoint returns 200 OK response
- Check SendGrid Inbound Parse logs in console

**Payload parsing errors:**
- Verify you're handling `multipart/form-data` correctly
- Use a multipart parser library (e.g., `multer` for Node.js)
- Log raw request body for debugging

**Attachments too large:**
- Configure web server size limits (nginx: `client_max_body_size`)
- Application size limits (Express: `limit` in body-parser)
- SendGrid default max is 30 MB per email

**Unauthorized webhook access:**
- Add basic authentication to webhook URL
- Allowlist SendGrid IP ranges (see SendGrid docs)
- Use HTTPS only
- Monitor for suspicious activity

## Examples

See:
- [references/webhook-examples.md](references/webhook-examples.md)
- [references/best-practices.md](references/best-practices.md)

## Related Skills

**Sending automated responses:**
- See `send-email` for sending replies or auto-responses
- Common use case: Support ticket auto-replies, confirmation emails
