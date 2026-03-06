---
name: pidgesms
description: Send and read SMS text messages via an Android phone using pidge. Use when asked to send a text, check texts, read SMS inbox, or reply to a text message.
homepage: https://github.com/typhonius/pidge
metadata:
  {
    "openclaw":
      {
        "emoji": "📱",
        "requires": { "bins": ["pidge"] },
        "install": "go install github.com/typhonius/pidge@latest",
      },
  }
---

# pidgesms — SMS via pidge

Send and read SMS messages via pidge, a CLI for [Android SMS Gateway](https://github.com/capcom6/android-sms-gateway). The gateway runs on an Android device and pidge connects to it automatically.

pidge reads its config from `~/.config/pidge/config.toml` — no env vars needed.

## Send SMS

```bash
pidge send "+1XXXXXXXXXX" "Your message here"
```

- Phone numbers must be E.164 format (e.g. `+15551234567`)
- Response includes `id` and `state` (Pending → Processed → Sent → Delivered)

## Check delivery status

```bash
pidge status <message-id>
```

## Read SMS (inbox)

```bash
pidge inbox
pidge inbox --unread
pidge inbox --json
```

## Mark message as processed / unprocessed

```bash
pidge ack <id>      # mark as processed
pidge unack <id>    # mark as unprocessed
```

## Health check

```bash
pidge health
```

## Safety rules

- Messages are sent to real phone numbers. Always confirm the recipient and content before sending.
- NEVER send SMS to unknown numbers without explicit owner approval.
- NEVER send bulk or repeated messages.
- NEVER send sensitive information (passwords, API keys, tokens, etc.) via SMS.
- NEVER include the full content of private SMS messages in group chat responses.
- When showing credentials, prefer a summary — only reveal full message content if directly requested in a private context.
