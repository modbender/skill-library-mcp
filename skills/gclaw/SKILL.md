---
name: gclaw
description: Gmail inbox intelligence for OpenClaw. Reads, classifies, and digests your Gmail so the important stuff surfaces without the noise. Use when fetching new emails, running an inbox digest, classifying messages into categories (newsletter, finance, travel, work, action-required, etc.), or building downstream bots that consume email data. Provides BotContext (per-bot label isolation), EmailFetcher, EmailParser, EmailClassifier (15 categories), and EmailStore (deduplicated JSONL).
metadata:
  openclaw:
    requires:
      bins: [gog]
    env:
      - GCLAW_GMAIL_ACCOUNT
      - GOG_KEYRING_PASSWORD
---

# GClaw — Gmail Intelligence for OpenClaw

<div align="center">
<img src="assets/banner.jpg" alt="GClaw — Gmail inbox intelligence" width="100%">
</div>

Reads, classifies, and digests your Gmail so the important stuff surfaces without the noise.

**Zero LLM tokens for classification** — heuristic classifier covers 15 categories. LLM only fires when you need a summary or digest narrative.

## Setup

```bash
# Requires the gog skill (Google OAuth CLI)
export GCLAW_GMAIL_ACCOUNT="your@gmail.com"
export GOG_KEYRING_PASSWORD="your-keyring-password"

pip install -e .
```

## Quick Usage

```python
from kaimail.bot_context import BotContext
from kaimail.fetcher import EmailFetcher
from kaimail.classifier import EmailClassifier
from kaimail.store import EmailStore

# Each bot declares its own label scope
ctx = BotContext(
    bot_id="digest",
    allowed_labels=["INBOX", "CATEGORY_UPDATES"],
    max_results=50
)

fetcher = EmailFetcher(context=ctx)
emails = fetcher.fetch_new()  # deduped — never processes the same email twice

classifier = EmailClassifier()
store = EmailStore(bot_id="digest")

for email in emails:
    email.category = classifier.classify(email)
    store.save(email)
    print(f"[{email.category}] {email.subject}")
```

## Classification Categories (15)

`newsletter` · `finance` · `travel` · `work` · `action_required` · `social` ·
`shopping` · `security` · `calendar` · `health` · `legal` · `ads` · `receipt` · `personal` · `other`

All heuristic — no LLM cost.

## Architecture

```
Gmail (via gog CLI)
    └─► EmailFetcher      — fetch, cache, deduplicate
        └─► EmailParser   — extract sender, clean body, detect forwards
            └─► EmailClassifier  — 15-category heuristic classification
                └─► EmailStore  — JSONL persistence (per bot_id)
```

## BotContext — Per-Bot Isolation

Multiple bots can share one Gmail account without interfering:

```python
# Digest bot — only newsletters + inbox
digest_ctx = BotContext(bot_id="digest", allowed_labels=["Thoughts", "INBOX"])

# Travel bot — only travel senders
travel_ctx = BotContext(
    bot_id="travel",
    allowed_labels=["Travel"],
    allowed_senders=["booking.com", "airbnb.com", "kayak.com"]
)
```

## Running Tests

```bash
pip install pytest
pytest tests/
```

## Requirements

- Python 3.10+
- [gog skill](https://clawhub.com/skills/gog) installed and authenticated
- `GOG_KEYRING_PASSWORD` env var set

## License

MIT
