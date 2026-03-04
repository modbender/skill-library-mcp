```
 ____  _____ _   _ ____   ____ ____  ___ ____    ____  _  _____ _     _     ____  
/ ___|| ____| \ | |  _ \ / ___|  _ \|_ _|  _ \  / ___|| |/ /_ _| |   | |   / ___| 
\___ \|  _| |  \| | | | | |  _| |_) || || | | | \___ \| ' / | || |   | |   \___ \ 
 ___) | |___| |\  | |_| | |_| |  _ < | || |_| |  ___) | . \ | || |___| |___ ___) |
|____/|_____|_| \_|____/ \____|_| \_\___|____/  |____/|_|\_\___|_____|_____|____/ 
```

# SendGrid Skills

AI agent skills for SendGrid email platform integration. Send transactional emails and receive inbound emails programmatically using the [SendGrid](https://sendgrid.com) v3 Web API.

## Available Skills

### 📤 [`send-email`](./send-email)
Send transactional emails and notifications via SendGrid's Mail Send API. Supports:
- Simple text/HTML emails
- Attachments
- CC/BCC recipients
- Dynamic templates with personalization
- Reply-to addresses

**Common use cases:** Welcome emails, password resets, receipts, notifications, automated alerts

### 📥 [`sendgrid-inbound`](./sendgrid-inbound)
Receive and parse inbound emails via SendGrid's Inbound Parse Webhook. Covers:
- MX record setup and DNS configuration
- Webhook endpoint implementation
- Multipart payload parsing
- Attachment handling
- Security best practices (auth, allowlisting, rate limiting)

**Common use cases:** Email-to-app workflows, support ticket creation from email, auto-reply systems, email parsing

## Installation

### Via ClawHub (recommended)
```bash
clawhub install sendgrid-skills
```

### Manual Installation
```bash
git clone https://github.com/vince-winkintel/sendgrid-skills.git
```

## Quick Start

### Sending Email

**1. Set API key:**
```bash
export SENDGRID_API_KEY=SG.xxxxxxxxx
```

**2. Example prompts for AI agent:**
- "Send a welcome email to vince@example.com"
- "Send a password reset email with a dynamic template"
- "Send a receipt email with PDF attachment"

**3. Direct usage (Node.js):**
```typescript
import sgMail from '@sendgrid/mail';

sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

await sgMail.send({
  from: 'support@example.com',
  to: 'user@example.com',
  subject: 'Welcome!',
  text: 'Welcome to our service',
  html: '<p>Welcome to our service</p>',
});
```

### Receiving Email

**1. Configure MX record:**
```
Type: MX
Host: parse.example.com
Priority: 10
Value: mx.sendgrid.net
```

**2. Configure Inbound Parse** in SendGrid Console with webhook URL

**3. Example prompts for AI agent:**
- "Set up an inbound email parser for support@parse.example.com"
- "Parse incoming email attachments and store in S3"
- "Create a webhook handler for email-to-ticket conversion"

## Supported Languages

- **Node.js / TypeScript** (recommended, `@sendgrid/mail`)
- Python (`sendgrid` package)
- Go (`sendgrid-go`)
- PHP (`sendgrid-php`)
- Ruby (`sendgrid-ruby`)
- Java (`sendgrid-java`)
- C# / .NET (`SendGrid`)
- cURL (direct API calls)

## Prerequisites

- SendGrid account ([sign up free](https://signup.sendgrid.com))
- Verified sender identity or authenticated domain
- API key with Mail Send permissions

**Get your API key:** <https://app.sendgrid.com/settings/api_keys>

## Features

✅ **Comprehensive workflows** - Step-by-step guides for common tasks  
✅ **Decision trees** - "Plain send vs Dynamic Templates", "How to secure webhooks"  
✅ **Troubleshooting** - Self-service problem solving for common issues  
✅ **Multi-language support** - Examples for 8+ programming languages  
✅ **Security best practices** - Webhook authentication, rate limiting, input validation  

## Documentation

- [SendGrid Official Docs](https://docs.sendgrid.com)
- [Mail Send API Reference](https://docs.sendgrid.com/api-reference/mail-send/mail-send)
- [Inbound Parse Webhook](https://docs.sendgrid.com/for-developers/parsing-email/setting-up-the-inbound-parse-webhook)

## Examples

See skill-specific documentation:
- [`send-email/references/single-email-examples.md`](./send-email/references/single-email-examples.md)
- [`sendgrid-inbound/references/webhook-examples.md`](./sendgrid-inbound/references/webhook-examples.md)

## License

MIT
