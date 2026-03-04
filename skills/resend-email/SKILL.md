---
name: resend-email
description: Send emails via Resend API from any verified domain. Use when sending emails, notifications, or automated messages. Supports HTML and plain text. Default voice is warm bureaucratic (configurable).
---

# Resend Email

Send emails from any Resend-verified domain using the Resend API.

## Quick Start

```bash
# Send simple email
bash skills/resend-email/scripts/send.sh \
  --to "recipient@example.com" \
  --subject "Subject Line" \
  --body "Email body text"

# With custom from address
bash skills/resend-email/scripts/send.sh \
  --to "recipient@example.com" \
  --from "you@yourdomain.com" \
  --subject "Subject" \
  --body "Body"
```

## Direct API Call

```bash
curl -X POST 'https://api.resend.com/emails' \
  -H "Authorization: Bearer $(cat ~/.config/resend/credentials.json | jq -r .api_key)" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "noreply@yourdomain.com",
    "to": ["recipient@example.com"],
    "subject": "Subject",
    "text": "Plain text body"
  }'
```

## Configuration

- **Credentials:** `~/.config/resend/credentials.json`
- **Domain:** any Resend-verified domain (configured in your Resend account)
- **Default from:** set in `credentials.json` (e.g., `noreply@yourdomain.com`)

## Receiving (Webhook + Clawdbot)

Use this when you want Resend inbound emails to trigger Clawdbot automatically.

### 1) Enable Clawdbot hooks

```json5
{
  hooks: {
    enabled: true,
    token: "<shared-secret>",
    path: "/hooks",
    transformsDir: "~/.clawdbot/hooks",
    mappings: [
      {
        id: "resend",
        match: { path: "resend" }, // relative to /hooks (no leading slash)
        action: "agent",
        deliver: true,
        channel: "telegram",
        transform: { module: "resend-inbound.js", export: "transform" }
      }
    ]
  }
}
```

**Important:** `match.path` is **relative** to `/hooks` (e.g., `/hooks/resend` → `resend`).

### 2) Expose the webhook (Tailscale Funnel)

If your gateway is local-only, expose it via Funnel:

```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale funnel --bg 18789
```

**MagicDNS + HTTPS certs must be enabled** in your tailnet for TLS to work.

### 3) Configure Resend webhook

In Resend → Webhooks:

- **URL:** `https://<your-tailnet-host>.ts.net/hooks/resend?token=<shared-secret>`
- **Event:** `email.received`

Resend cannot set custom headers, so use `?token=`.

### 4) Fetch full email content

Resend webhooks do **not** include body text. Use the receiving API:

```
GET https://api.resend.com/emails/receiving/:id
```

(See `resend-inbound.js` for an example transform that fetches the body.)

## Email Voice: The Bureaucrat

See `references/voice-bureaucrat.md` for the default email tone.

**Key traits:**
- Warm, patient, endlessly polite
- Passive voice ("it is recommended that…")
- Official jargon ("compliance framework", "pursuant to section 14(b)")
- Everything framed as "best practices"
- Bullet points start with "Please note that…"
- Ends with "We appreciate your cooperation"

**Tone:** DMV supervisor who smiles while denying your form × LinkedIn thought-leader who genuinely believes bureaucracy is beautiful.

When drafting emails, apply this voice unless instructed otherwise.

## HTML Emails

```bash
curl -X POST 'https://api.resend.com/emails' \
  -H "Authorization: Bearer $RESEND_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "noreply@yourdomain.com",
    "to": ["recipient@example.com"],
    "subject": "Subject",
    "html": "<h1>Hello</h1><p>HTML content</p>"
  }'
```

## Notes

- `send.sh` preserves line breaks in `--body` (no literal `\n` output).
- Use `--html` for rich formatting; default is plain text.

## Common Patterns

**Transactional notification:**
```bash
# Order confirmation, welcome email, etc.
bash skills/resend-email/scripts/send.sh \
  --to "customer@example.com" \
  --subject "Your Request Has Been Processed" \
  --body "$(cat <<'EOF'
Dear Valued Individual,

Please note that your recent submission has been received and processed in accordance with standard operating procedures.

It should be understood that all requests are handled in the order received, pursuant to our established compliance framework.

We appreciate your cooperation in maintaining an orderly process.

Warm regards,
Clawd
Agent Services Division
EOF
)"
```

**Reply to inquiry:**
Apply bureaucrat voice. Be helpful while maintaining the veneer of official procedure.
