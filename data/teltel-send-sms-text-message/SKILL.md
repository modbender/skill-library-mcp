---
name: teltel-send-sms-text-message
description: Send SMS text messages via TelTel (teltel.io) using the REST API (api.teltel.io). Includes bulk send, delivery report, and bulk sms.
metadata: {"openclaw":{"emoji":"💬","homepage":"https://www.teltel.io/","primaryEnv":"TELTEL_API_KEY"}}
---

Use the bundled Node scripts to send SMS via the TelTel API.

## Before you use the skill (TelTel prerequisites)

1) Register at **https://www.teltel.io/**
2) Add funds / credit to your TelTel account
3) From the TelTel **SMS** section, send a **test SMS** first to confirm your sender name/phone is accepted/verified
4) In TelTel **Settings**, find your **API key**
5) Enjoy

## Configure from the OpenClaw Skills panel

### API key field (shown in the Skills UI)

This skill declares `TELTEL_API_KEY` as its **primary env var**, so the OpenClaw Skills UI can show an **API key** input for it.

Under the hood it maps to:
- `skills.entries.teltel-send-sms-text-message.apiKey` → `TELTEL_API_KEY`

### Default sender

Set a default sender name/number (used when you do **not** pass `--from`):
- `skills.entries.teltel-send-sms-text-message.env.TELTEL_SMS_FROM`

## Configure via environment variables (alternative)

- `TELTEL_API_KEY` (required)
- `TELTEL_SMS_FROM` (optional) — default sender name/number
- `TELTEL_BASE_URL` (optional) — defaults to `https://api.teltel.io/v2`

## Send a single SMS

```bash
node {baseDir}/scripts/send_sms.js \
  --to "+3712xxxxxxx" \
  --message "Hello from TelTel" \
  --from "37167881855"
```

If you omit `--from`, the script uses `TELTEL_SMS_FROM`.

Dry-run (prints URL + payload, does not send):

```bash
node {baseDir}/scripts/send_sms.js \
  --dry-run \
  --to "+37111111111" \
  --message "test" \
  --from "37167881855"
```

## Send bulk SMS

```bash
node {baseDir}/scripts/send_sms_bulk.js \
  --from "37167881855" \
  --to "+3712...,+1..." \
  --message "Hello everyone"
```

The `--to` list can be comma/newline/semicolon separated.

## API details (for reference)

- Base URL: `https://api.teltel.io/v2`
- Single SMS: `POST /sms/text`
  - JSON body: `{ "data": { "from": "...", "to": "+...", "message": "...", "callback": "https://..."? } }`
- Bulk SMS: `POST /sms/bulk/text`
  - JSON body: `{ "data": { "from": "...", "to": ["+...", "+..."], "message": "...", "callback": "https://..."? } }`

Notes:
- `to` must be in international format.
