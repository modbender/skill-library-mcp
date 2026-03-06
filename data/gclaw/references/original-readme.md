# kai-mail

Reusable Python email infrastructure library for Kai AI assistant.

## Overview

kai-mail provides a clean abstraction layer for fetching, parsing, classifying, and storing emails from Gmail. It's designed to power multiple downstream bots (email digest, travel bot, prescription reminders, etc.) while enforcing access control through `BotContext`.

## Architecture

```
kai-mail/
├── src/kaimail/
│   ├── __init__.py
│   ├── client.py        # GogGmailClient — thin wrapper around gog CLI
│   ├── models.py        # Pydantic models: Email, Thread, ParsedEmail, etc.
│   ├── fetcher.py       # EmailFetcher — fetch, deduplicate, cache
│   ├── parser.py        # EmailParser — extract sender, clean body, detect forwards
│   ├── classifier.py    # EmailClassifier — heuristic classification (no LLM)
│   ├── store.py         # EmailStore — JSONL persistence + deduplication
│   └── bot_context.py   # BotContext — per-bot access control
├── tests/
│   ├── fixtures/        # Real email fixtures (JSONL)
│   └── test_*.py        # Unit and oracle tests
└── memory/email-store/  # Runtime storage (created on first use)
```

## Key Design Principles

### 1. Bot Isolation via BotContext

Each consumer bot gets its own `BotContext` that restricts what emails it can access:

```python
from kaimail import BotContext, EmailFetcher

# Digest bot can only see "Thoughts" label
digest_ctx = BotContext(
    bot_id="digest",
    allowed_labels=["Thoughts"],
    max_results=100,
)

# Travel bot can only see travel-related emails
travel_ctx = BotContext(
    bot_id="travel",
    allowed_labels=["Travel"],
    allowed_senders=["booking.com", "expedia.com"],
    max_results=50,
)
```

The fetcher enforces these constraints — a travel bot literally cannot fetch emails from the "Thoughts" label.

### 2. Parse Once, Store Structured

Raw emails are fetched → parsed → classified → stored as structured JSONL. Downstream bots read from the store, minimizing gog CLI calls:

```python
# Fetch new emails (makes gog calls, stores results)
emails = fetcher.fetch(labels=["Thoughts"], newer_than_days=7)

# Read from store (no gog calls)
stored = fetcher.get_stored(category="newsletter", limit=50)
```

### 3. Deduplication

`EmailStore` tracks seen message IDs in `memory/email-store/seen.json`. The fetcher never re-processes the same email:

```python
# Only fetch emails we haven't seen
new_emails = fetcher.get_new_since_last_fetch()
```

### 4. No LLM in the Library

Classification uses rules and heuristics only. Categories:
- `newsletter` — Substack, Stratechery, mailchimp, etc.
- `travel` — Booking.com, flight confirmations, restaurant reservations
- `notification` — GitHub, system alerts
- `receipt` — Apple invoices, order confirmations
- `promotional` — Marketing emails
- `personal` — Default fallback

LLM summarization happens in consuming bots, not here.

## Quick Start

### Installation

```bash
cd kai-mail
pip install -e ".[dev]"
```

### Environment

```bash
export GOG_KEYRING_PASSWORD=kai-gog-keyring
```

### Basic Usage

```python
from kaimail import BotContext, EmailFetcher

# Create context for your bot
ctx = BotContext(
    bot_id="my-bot",
    allowed_labels=["INBOX"],
    max_results=25,
)

# Create fetcher (uses default store location)
fetcher = EmailFetcher.create(
    context=ctx,
    account="hyatt.yonatan@gmail.com",
)

# Fetch recent emails
emails = fetcher.fetch(newer_than_days=7)

for email in emails:
    print(f"{email.category}: {email.subject}")
    print(f"  From: {email.sender_name} <{email.sender_email}>")
    print(f"  Preview: {email.body_preview[:100]}...")
```

### Reading from Store

```python
# Get previously fetched newsletters
newsletters = fetcher.get_stored(category="newsletter", limit=20)

# Export for downstream processing
store = fetcher.store
data = store.export_for_bot(category="newsletter", limit=50)
```

## Adding a New Consumer Bot

1. **Define a BotContext** with appropriate restrictions:

```python
health_ctx = BotContext(
    bot_id="health",
    allowed_labels=["Health", "Prescriptions"],
    allowed_senders=["pharmacy.com", "doctor.com"],
    max_results=30,
)
```

2. **Create an EmailFetcher** with your context:

```python
fetcher = EmailFetcher.create(context=health_ctx)
```

3. **Fetch and process emails**:

```python
# Get new emails since last check
new_emails = fetcher.get_new_since_last_fetch()

# Filter by category if needed
receipts = [e for e in new_emails if e.category == "receipt"]
```

4. **Use the store for incremental processing**:

```python
# Bots should primarily read from store
# Only call fetch() periodically to update the store
```

## Classification Heuristics

The classifier uses domain patterns, sender patterns, subject patterns, and Gmail labels:

| Category | Detection Signals |
|----------|-------------------|
| Newsletter | substack.com, stratechery.com, mailchimp, "Thoughts" label, "This Week in" subjects |
| Travel | booking.com, airline domains, "reservation", "confirmation", "Travel" label |
| Notification | github.com, noreply@, notifications@, "GitHub" label |
| Receipt | apple.com, "invoice", "receipt", "order confirmation" |
| Promotional | CATEGORY_PROMOTIONS label, "% off", "sale", "deal" |
| Personal | Default fallback |

## Testing

```bash
# Run all tests
pytest

# Run oracle (ground truth) tests
pytest -m oracle

# With coverage
pytest --cov=kaimail

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```

## Email Categories

```python
from kaimail import EmailCategory

EmailCategory.NEWSLETTER    # Substacks, digests, thought leadership
EmailCategory.TRAVEL        # Flights, hotels, restaurant reservations
EmailCategory.NOTIFICATION  # System alerts, GitHub, service notifications
EmailCategory.RECEIPT       # Invoices, order confirmations
EmailCategory.PROMOTIONAL   # Marketing, sales emails
EmailCategory.PERSONAL      # Default/unclassified
```

## API Reference

### BotContext

```python
BotContext(
    bot_id: str,                    # Unique identifier
    allowed_labels: list[str],      # Gmail labels this bot can access
    allowed_senders: list[str],     # Domain/address allowlist
    max_results: int = 50,          # Hard cap on fetch results
    readonly: bool = True,          # Bots never modify emails
)
```

### EmailFetcher

```python
fetcher.fetch(
    labels: list[str] = None,       # Labels to search
    senders: list[str] = None,      # Senders to filter
    newer_than_days: int = None,    # Age filter
    is_unread: bool = False,        # Only unread
    max_results: int = 50,          # Results limit
    skip_seen: bool = True,         # Skip already-processed
) -> list[ParsedEmail]

fetcher.get_stored(
    category: str = None,           # Filter by category
    limit: int = 100,               # Max results
) -> list[ParsedEmail]

fetcher.get_new_since_last_fetch() -> list[ParsedEmail]
```

### ParsedEmail

```python
ParsedEmail(
    id: str,
    thread_id: str,
    date: datetime,
    sender_email: str,
    sender_name: str,
    sender_domain: str,
    subject: str,
    subject_clean: str,             # Without Re:, Fwd:
    body_text: str,                 # Cleaned content
    body_preview: str,              # First ~200 chars
    labels: list[str],
    category: EmailCategory,
    is_forwarded: bool,
    is_reply: bool,
    has_attachments: bool,
)
```

## License

Internal use only — part of Kai AI assistant infrastructure.
