---
name: send-email
description: Send transactional emails and notifications via SendGrid v3 Mail Send API. Supports simple emails, HTML/text content, attachments, CC/BCC, dynamic templates, and personalization. Use when sending welcome emails, password resets, receipts, notifications, or any programmatic email. Triggers on send email, transactional email, SendGrid send, email notification, welcome email, password reset email, email template, dynamic template.
---

# Send Email with SendGrid

## Overview

SendGrid provides a single **Mail Send** endpoint for sending email via the v3 API. The Node SDK (`@sendgrid/mail`) is the recommended integration for JavaScript/TypeScript.

**Use this skill when:**
- Sending transactional emails (welcome, password reset, receipts)
- Sending simple notifications
- You need basic text/HTML emails with optional attachments
- Using dynamic templates for personalized content

## Quick Start

### Test Your Configuration First
```bash
# Validate API key and send test email
../scripts/send-test-email.sh recipient@example.com
```

**Then integrate:**

1. **Detect project language** (package.json, requirements.txt, go.mod, etc.)
2. **Install SDK** (preferred) or use cURL - See [references/installation.md](references/installation.md)
3. **Prepare message** with `from`, `to`, `subject`, and `text` or `html`
4. **Send and handle errors** (retry on 429/5xx)

## Required Parameters

| Parameter | Type | Description |
|----------|------|-------------|
| `from` | string | Sender email (must be verified) |
| `to` | string or string[] | Recipient email(s) |
| `subject` | string | Email subject |
| `text` or `html` | string | Email body content |

## Optional Parameters

| Parameter | Type | Description |
|----------|------|-------------|
| `cc` | string or string[] | CC recipients |
| `bcc` | string or string[] | BCC recipients |
| `reply_to` | string | Reply-to address |
| `attachments` | array | Base64-encoded attachments |
| `template_id` | string | Dynamic template ID (if using templates) |
| `dynamic_template_data` | object | Template data (if using templates) |

## Minimal Example (Node.js)

```ts
import sgMail from '@sendgrid/mail';

sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

await sgMail.send({
  from: 'Support <support@winkintel.com>',
  to: 'vince@winkintel.com',
  subject: 'Hello from SendGrid',
  text: 'This is a test email.',
  html: '<p>This is a test email.</p>',
});
```

## Templates (Dynamic Templates)

If using SendGrid Dynamic Templates, supply `template_id` and `dynamic_template_data` instead of `html`/`text`.

```ts
await sgMail.send({
  from: 'Support <support@winkintel.com>',
  to: 'vince@winkintel.com',
  templateId: 'd-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
  dynamicTemplateData: { first_name: 'Vince' },
});
```

## Decision: Plain Send vs Dynamic Templates?

```
How complex is your email?
├─ Simple, one-off message
│  └─ Plain send (html/text) ✅
├─ Reusable design with variables
│  └─ Dynamic Template ✅
└─ Personalized at scale
   └─ Dynamic Template with merge tags ✅
```

**Use plain send when:**
- Quick, simple messages
- Content changes every time
- No design reusability needed

**Use dynamic templates when:**
- Consistent design across emails
- Variable substitution (names, dates, etc.)
- Non-technical teams manage email content
- A/B testing email designs

## Troubleshooting

**"401 Unauthorized":**
- API key invalid or missing
- Check `SENDGRID_API_KEY` environment variable
- Verify key has mail send permissions

**"403 Forbidden":**
- Sender email not verified
- Go to SendGrid Console → Settings → Sender Authentication
- Verify single sender or authenticate domain

**"429 Too Many Requests":**
- Rate limit exceeded
- Implement exponential backoff (retry after 1s, 2s, 4s...)
- Consider upgrading SendGrid plan

**"500/503 Service Errors":**
- SendGrid temporary service issue
- Retry with exponential backoff
- Check SendGrid status page

**Emails not arriving:**
- Check recipient spam folder
- Verify sender domain authentication (SPF/DKIM)
- Use both `text` and `html` for better deliverability
- Avoid spam trigger words in subject/body

## Best Practices (Short)

- Always set **both** `text` and `html` when possible (deliverability + accessibility).
- Retry **only** on 429 or 5xx errors with exponential backoff.
- Use verified senders; unverified domains will fail.
- Avoid fake addresses at real providers; test with addresses you control.

For deeper details, see:
- [references/best-practices.md](references/best-practices.md)
- [references/single-email-examples.md](references/single-email-examples.md)

## Automation Scripts

**Quick testing:**
- `scripts/send-test-email.sh` - Send plain text test email (API key validation)
- `scripts/send-html-email.sh` - Send HTML email (newsletters, reports, formatted content)

See [scripts/README.md](../scripts/README.md) for usage examples.

## Related Skills

**Receiving email responses:**
- See `sendgrid-inbound` for handling incoming emails via Inbound Parse Webhook
- Common use case: Auto-reply systems, support ticket creation from email
