# CRM Intel Module 🐾

**Berman-style 2-stage filtering + contact scoring** for OEE's Personal CRM.

## Architecture

```
Contact → Stage 1 (Hard Filters) → Stage 2 (AI / Haiku) → Scoring → Decision
```

### Stage 1 — Hard Filters (instant, no API cost)
- Own emails/domains
- Generic inboxes (`info@`, `team@`, `noreply@`, etc.)
- Marketing domains (`tx.`, `cx.`, `mail.`, `email.` prefixes)
- Known skip domains (GitHub notifications, Stripe, etc.)
- Previously rejected contacts

### Stage 2 — AI Classification (Claude Haiku)
- Rejects automated senders, newsletters, cold outreach
- Approves real people with genuine 2-way interaction
- Requires `ANTHROPIC_API_KEY` env var

### Scoring (0–150+)

| Signal | Points |
|---|---|
| Base | 50 |
| Per exchange (max 4) | +5 each |
| Per meeting (max 5) | +3 each |
| Preferred title | +15 |
| Small meetings (≤3 ppl) | +10 |
| Last interaction ≤7d | +10 |
| Last interaction ≤30d | +5 |
| In both email + calendar | +25 |
| Recognizable role | +10 |
| Known company | +5 |

## Usage

```python
from crm_filter import CRMFilter

crm = CRMFilter("learning.json")

# Single contact
result = crm.evaluate_contact({
    "email": "jane@startup.com",
    "name": "Jane Smith",
    "title": "CEO",
    "exchange_count": 4,
    "meeting_count": 2,
    "meeting_avg_attendees": 2,
    "last_interaction": "2026-02-10T12:00:00",
    "in_email": True,
    "in_calendar": True,
    "has_role": True,
    "known_company": True,
    "has_replies": True,
    "subjects": ["Catch up", "Partnership idea"],
})

# Batch
results = crm.evaluate_batch(contacts_list)
print(crm.summary(results))
crm.save_config()  # persist rejected contacts
```

### CLI

```bash
# Quick stage-1 check
python crm_filter.py --email noreply@github.com

# Batch from JSON file
python crm_filter.py --input contacts.json

# Demo mode
python crm_filter.py
```

## Configuration — `learning.json`

Edit to customize filtering behavior:

- **`own_emails`** / **`own_domains`** — your addresses (always filtered)
- **`skip_domains`** — notification/marketing domains
- **`prefer_titles`** — titles that get +15 score boost
- **`skip_keywords`** — subject-line signals for AI rejection
- **`min_exchanges`** — minimum exchanges for consideration
- **`max_days_between`** — contacts go STALE after this many days
- **`rejected_contacts`** — auto-populated, persisted across runs

## Dependencies

- `anthropic` Python SDK (for Stage 2 AI classification)
- `ANTHROPIC_API_KEY` environment variable

```bash
pip install anthropic
```

---
*🐾*
