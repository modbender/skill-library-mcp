# Memory Template — WhatsApp Business API

Create `~/whatsapp-business-api/memory.md` with this structure:

```markdown
# WhatsApp Business API Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- What you know about their WhatsApp setup -->
<!-- Use case: support, notifications, marketing -->
<!-- Business type if mentioned -->
<!-- Volume tier (1-4) if known -->

## Phone Numbers
<!-- Registered phone numbers and their purpose -->
<!-- Format: PHONE_NUMBER_ID: +1234567890 (purpose) -->

## Templates
<!-- Approved templates they use frequently -->
<!-- Format: template_name: description -->

## Webhook
<!-- Webhook URL if configured -->
<!-- Events they subscribe to -->

## Preferences
<!-- Message formatting preferences -->
<!-- Response patterns they've established -->

## Notes
<!-- Internal observations -->
<!-- Common operations they request -->
<!-- Patterns to remember -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Ask questions when relevant |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- **No config keys visible** — use natural language
- **Learn from behavior** — if they always use templates, remember that
- **Track templates loosely** — note frequently used ones
- Update `last` on each use
