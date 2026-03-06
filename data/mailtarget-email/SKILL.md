---
name: mailtarget-email
description: Send transactional and marketing emails via Mailtarget API. Manage sending domains, templates, API keys, and sub-accounts. Use when the agent needs to send emails, manage email templates, configure sending domains, or handle any email infrastructure task through Mailtarget (mailtarget.co). Supports HTML emails, attachments, click/open tracking, template-based sending with substitution data, CC/BCC, reply-to, and custom headers.
---

# Mailtarget Email

Send emails and manage email infrastructure via the [Mailtarget](https://mailtarget.co) API.

## Setup

Set the `MAILTARGET_API_KEY` environment variable with your Mailtarget API key.

Get your API key from the [Mailtarget dashboard](https://app.mailtarget.co) → Settings → API Keys.

## Sending Email

Use `curl` or any HTTP client. All requests go to `https://transmission.mailtarget.co/v1` with `Authorization: Bearer $MAILTARGET_API_KEY`.

### Simple send

```bash
curl -X POST https://transmission.mailtarget.co/v1/layang/transmissions \
  -H "Authorization: Bearer $MAILTARGET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": [{"email": "recipient@example.com", "name": "Recipient"}],
    "from": {"email": "noreply@yourdomain.com", "name": "Your App"},
    "subject": "Hello from Mailtarget",
    "bodyHtml": "<h1>Hello!</h1><p>This is a test email.</p>",
    "bodyText": "Hello! This is a test email."
  }'
```

A successful response returns `{"message": "Transmission received", "transmissionId": "..."}`.

### Template-based send

Use `templateId` with `substitutionData` instead of bodyHtml/bodyText:

```json
{
  "to": [{"email": "user@example.com", "name": "User"}],
  "from": {"email": "noreply@yourdomain.com", "name": "Your App"},
  "subject": "Welcome, {{name}}!",
  "templateId": "welcome-template",
  "substitutionData": {"name": "User", "company": "Acme"}
}
```

### Tracking options

Control click and open tracking per transmission:

```json
{
  "optionsAttributes": {
    "clickTracking": true,
    "openTracking": true,
    "transactional": true
  }
}
```

Set `transactional: true` for transactional emails (password resets, receipts) to bypass unsubscribe preferences.

### Attachments

Include base64-encoded attachments:

```json
{
  "attachments": [{
    "filename": "report.pdf",
    "mimeType": "application/pdf",
    "value": "<base64-encoded-content>"
  }]
}
```

## Managing Templates

- List: `GET /template?page=1&size=10&search=keyword`
- Create: `POST /template` with `{"id": "slug", "name": "Display Name", "html": "<html>..."}`

## Managing Sending Domains

- List: `GET /domain/sending`
- Create: `POST /domain/sending` with `{"domain": "example.com"}`
- Verify: `PUT /domain/sending/{id}/verify-txt`
- Check SPF: `GET /domain/sending/{id}/spf-suggestion`

## Autonomous Domain Setup (with cloudflare-dns skill)

When paired with the `cloudflare-dns` skill, the agent can set up a sending domain end-to-end with zero manual DNS editing:

1. Create sending domain: `POST /domain/sending` with `{"domain": "example.com"}`
2. Read required DNS records from the response: `spfHostname`, `spfValue`, `dkimHostname`, `dkimValue`, `cnameHostname`, `cnameValue`
3. Add SPF TXT record in Cloudflare using `spfHostname` and `spfValue`
4. Add DKIM TXT record in Cloudflare using `dkimHostname` and `dkimValue`
5. Add CNAME record in Cloudflare using `cnameHostname` and `cnameValue` (set `proxied: false`)
6. Verify domain: `PUT /domain/sending/{id}/verify-txt`
7. Confirm status via `GET /domain/sending/{id}` — check `spfVerified`, `dkimVerified`, `cnameVerified`

Install the companion skill: `clawhub install cloudflare-dns`

## Getting Started

New to Mailtarget + OpenClaw? See [references/getting-started.md](references/getting-started.md) for a 5-minute setup guide.

## Full API Reference

See [references/api.md](references/api.md) for complete endpoint documentation including API key management, sub-accounts, and permissions.
