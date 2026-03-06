---
name: webhook-promo-scheduler
description: Schedule and send promo/alert messages to a Discord webhook URL with an anti-spam ledger.
---

## webhook-promo-scheduler

Schedule and send promo/alert messages to a Discord webhook URL with an anti-spam ledger.

### What it does
- Posts to a Discord webhook (JSON payload with `content`)
- Maintains a JSONL ledger to enforce **max 1 successful post per day per channel**
- Provides a rotation mode that cycles through a message list
- Supports `--dry-run` so you can validate cadence/ledger without sending anything

### Positioning (best angle)
- Ship updates without becoming a spammer (or leaking a webhook): strict cadence + audit trail.

### Files
- `scripts/post_webhook.py` : Discord webhook POST helper (stdlib only)
- `scripts/ledger.py` : JSONL ledger helpers (stdlib only)
- `scripts/promo_scheduler.py` : CLI tool (stdlib only)

### Ledger
- Default: `~/.openclaw/webhook-promo-ledger.jsonl`
- Override: `--ledger-path /path/to/ledger.jsonl`
- JSONL fields (per line): `date`, `channel`, `status`, `hash`

### Safety
- The CLI **refuses to print** the webhook URL.
- Logs redact any webhook URL if it would appear.
- Recommended: keep the webhook in a private channel, rotate it if leaked, and use `--dry-run` before enabling live sends.

### FAQ (security)
**Q: This exposes a Discord webhook — is that dangerous?**
A: Treat it like a password. This tool won’t print it, supports secret injection, and has `--dry-run` + a ledger so you can validate behavior before turning on live posting. If you want zero direct exposure, put a relay (Cloudflare Worker / Supabase Edge Function) in front and keep the real webhook private.

### Usage

One-shot post:

```bash
python3 {baseDir}/scripts/promo_scheduler.py post \
  --webhook-url <URL> \
  --channel openclaw-discord \
  --message "Hello from OpenClaw!"
```

Draft rotation:

```bash
python3 {baseDir}/scripts/promo_scheduler.py rotate \
  --webhook-url <URL> \
  --channel openclaw-discord \
  --messages-file messages.txt
```

`messages.txt` format:
- One message per non-empty line
- Lines starting with `#` are ignored
