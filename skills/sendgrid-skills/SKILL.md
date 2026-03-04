---
name: sendgrid
description: SendGrid email platform integration for sending and receiving emails. Routes to sub-skills for outbound transactional emails (send-email) and receiving via Inbound Parse Webhook (sendgrid-inbound). Use when user mentions SendGrid, transactional email, email API, inbound email parsing, or email webhooks. Triggers on SendGrid, send email, receive email, email webhook, Inbound Parse, transactional email.
requirements:
  env:
    - SENDGRID_API_KEY
  env_optional:
    - SENDGRID_FROM
  binaries:
    - curl
    - jq
    - node
  binaries_optional:
    - dig
    - nslookup
metadata:
  openclaw:
    requires:
      env:
        - SENDGRID_API_KEY
      bins:
        - curl
        - jq
        - node
    notes: |
      Scripts operate on user-provided file paths (send-html-email.sh) and network endpoints (verify-inbound-setup.sh). Review scripts before executing. Use a SendGrid API key scoped to Mail Send only.
---

# SendGrid

## Overview

SendGrid is an email platform for developers. This skill routes to feature-specific sub-skills.

## Sub-Skills

| Feature | Skill | Use When |
|---------|-------|----------|
| **Sending emails** | `send-email` | Transactional emails, notifications, simple sends, dynamic templates |
| **Receiving emails** | `sendgrid-inbound` | Inbound Parse Webhook, MX record setup, parsing incoming email |

## Common Setup

### API Key

Store in environment variable:
```bash
export SENDGRID_API_KEY=SG.xxxxxxxxx
```

### SDK Installation

See `send-email` skill for installation instructions across supported languages.

## When to use SendGrid vs other services

```
What's your use case?
├─ Transactional emails (receipts, notifications, password resets)
│  └─ SendGrid (send-email) ✅
├─ Marketing campaigns / bulk email
│  └─ Consider SendGrid Marketing Campaigns (outside this skill)
├─ Receiving emails programmatically
│  └─ SendGrid Inbound Parse (sendgrid-inbound) ✅
└─ Simple SMTP relay
   └─ SendGrid SMTP (outside this skill)
```

## Resources

- [SendGrid Documentation](https://docs.sendgrid.com)
- [SendGrid Node SDK](https://github.com/sendgrid/sendgrid-nodejs)
- [Email API v3 Reference](https://docs.sendgrid.com/api-reference/mail-send/mail-send)
