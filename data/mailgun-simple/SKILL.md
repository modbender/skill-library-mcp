---
name: mailgun-simple
description: Send outbound emails via the Mailgun API. Uses MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_REGION, and MAILGUN_FROM.
metadata: {"openclaw": {"requires": {"bins": ["node"], "env": ["MAILGUN_API_KEY", "MAILGUN_DOMAIN", "MAILGUN_REGION", "MAILGUN_FROM"]}, "primaryEnv": "MAILGUN_API_KEY", "install": [{"id": "npm-deps", "kind": "node", "package": "mailgun.js@12.7.0 form-data@4.0.1", "label": "Install Mailgun SDK dependencies"}]}}
---

# Mailgun Simple

Send outbound emails using the official Mailgun JS SDK.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `MAILGUN_API_KEY` | **Yes** | — | Your private Mailgun API key. |
| `MAILGUN_DOMAIN` | **Yes** | `aicommander.dev` | Your verified sending domain. |
| `MAILGUN_REGION` | **Yes** | `EU` | API region: `EU` or `US`. |
| `MAILGUN_FROM` | No | `Postmaster <postmaster@{domain}>` | Default sender address. |

## Setup

```bash
npm install mailgun.js@12.7.0 form-data@4.0.1
```

## Tools

### Send Email
```bash
MAILGUN_API_KEY=xxx MAILGUN_DOMAIN=example.com MAILGUN_REGION=EU node scripts/send_email.js <to> <subject> <text> [from]
```
