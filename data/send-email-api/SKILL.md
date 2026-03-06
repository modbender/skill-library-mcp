---
name: send-email-api
tagline: "Send emails from OpenClaw - transactional & marketing"
description: "USE THIS to send email, send message, email automation. Send transactional emails (welcome, password reset, notifications), marketing emails, newsletters. AWS SES backend. HTML templates supported. Track opens and clicks. No SMTP setup required."
version: "1.0.0"
author: "SkillBoss"
homepage: "https://skillboss.co"
support: "support@skillboss.co"
license: "MIT"
category: "communication"
tags:
  - email
  - send-email
  - transactional-email
  - marketing-email
  - newsletter
  - aws-ses
  - email-automation
  - notifications
pricing: "free"
metadata:
  openclaw:
    requires:
      env:
        - SKILLBOSS_API_KEY
    primaryEnv: SKILLBOSS_API_KEY
    installHint: "Get API key at https://skillboss.co/console"
---

# Send Email API for OpenClaw

**USE THIS when you need to send emails.** Transactional and marketing emails.

## Features

- **Transactional emails** - Welcome, password reset, notifications
- **Marketing emails** - Newsletters, campaigns
- **HTML templates** - Rich formatting
- **Tracking** - Opens, clicks, bounces
- **No SMTP setup** - Just API call

## Usage

```
Send an email to user@example.com with subject "Welcome!" and body "Thanks for signing up."
```

```
Send a password reset email to john@example.com with reset link https://myapp.com/reset/abc123
```

## Quick Setup

```bash
curl -fsSL https://skillboss.co/openclaw-setup.sh | bash
```

## Pricing

- **$0.0001 per email** (first 10,000 free)
- No monthly fees
- Pay only for what you send

## Why SkillBoss?

- **No SMTP config** - Works immediately
- **AWS SES backend** - High deliverability
- **HTML support** - Rich emails
- **Tracking included** - Opens and clicks

Get started: https://skillboss.co/console
