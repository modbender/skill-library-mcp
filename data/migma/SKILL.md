---
name: migma
description: Generate, send, validate, and export AI-powered emails from the terminal; manage contacts, segments, tags, domains, and webhooks with Migma CLI.
metadata:
  openclaw:
    requires:
      env:
        - MIGMA_API_KEY
      bins:
        - migma
    primaryEnv: MIGMA_API_KEY
    emoji: "\u2709"
    homepage: https://migma.ai
    install:
      - kind: node
        package: "@migma/cli"
        bins: [migma]
---

# Migma

Create and send professional, on-brand emails with AI. Your agent can design emails from a prompt, send them instantly through a managed domain, and manage an entire audience — all from the terminal.

Always pass `--json` for structured output.

## First-time setup

If the user hasn't set up yet, run these steps once:

```bash
# 1. Create an instant sending domain (no DNS needed)
migma domains managed create <companyname> --json
# → Sends from: hello@<companyname>.migma.email

# 2. Set a default project (brand)
migma projects list --json
migma projects use <projectId>
```

## Create an email

When the user asks to create, design, or generate an email:

```bash
migma generate "Welcome email for new subscribers" --wait --json
```

The `--wait` flag blocks until the AI finishes. The JSON response includes `conversationId`, `subject`, and `html`.

To save the HTML locally, add `--save ./email.html`. To include a reference image (screenshot, design mockup), add `--image <url>`.

## Send an email

When the user asks to send an email to someone:

```bash
# Send a generated email directly
migma send --to sarah@example.com --subject "Welcome!" \
  --from-conversation <conversationId> \
  --from hello@company.migma.email --from-name "Company" --json

# Or send from a local HTML file
migma send --to sarah@example.com --subject "Hello" \
  --html ./email.html \
  --from hello@company.migma.email --from-name "Company" --json

# Send to an entire segment or tag
migma send --segment <id> --subject "Big News" --html ./email.html \
  --from hello@company.migma.email --from-name "Company" --json

# Personalize with template variables
migma send --to user@example.com --subject "Hi {{name}}" --html ./email.html \
  --from hello@company.migma.email --from-name "Company" \
  --var name=Sarah --var discount=20 --json
```

`--from-conversation` auto-exports the HTML from a generated email — no separate export step.

## Validate an email

When the user wants to check an email before sending:

```bash
migma validate all --html ./email.html --json
migma validate all --conversation <conversationId> --json
```

Returns an overall score plus individual checks: compatibility (30+ email clients), broken links, spelling/grammar, and deliverability/spam score. Individual checks: `migma validate compatibility`, `links`, `spelling`, `deliverability`.

## Export to platforms

When the user wants to export to an ESP or download a file:

```bash
migma export html <conversationId> --output ./email.html
migma export klaviyo <conversationId> --json
migma export mailchimp <conversationId> --json
migma export hubspot <conversationId> --json
migma export pdf <conversationId> --json
migma export mjml <conversationId> --json
```

## Manage contacts

```bash
migma contacts add --email user@example.com --firstName John --json
migma contacts list --json
migma contacts import ./contacts.csv --json
migma contacts remove <id> --json
```

## Manage tags and segments

```bash
migma tags create --name "VIP" --json
migma tags list --json
migma segments create --name "Active Users" --description "..." --json
migma segments list --json
```

## Import a brand

When the user wants to set up a new brand from their website:

```bash
migma projects import https://yourbrand.com --wait --json
migma projects use <projectId>
```

This fetches logos, colors, fonts, and brand voice automatically.

## Error handling

On error, `--json` returns:

```json
{"error": {"message": "Not found", "code": "not_found", "statusCode": 404}}
```
