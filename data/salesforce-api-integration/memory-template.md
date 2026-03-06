# Memory Template — Salesforce API

Create `~/salesforce-api-integration/memory.md` with this structure:

```markdown
# Salesforce Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- What you know about their Salesforce org -->
<!-- Org type: production or sandbox -->
<!-- Main objects they work with (Account, Contact, custom objects) -->
<!-- Common operations they request -->

## Objects
<!-- Key objects they've mentioned or queried -->
<!-- Standard: Account, Contact, Opportunity, Lead, Case -->
<!-- Custom: ObjectName__c (note the __c suffix) -->

## Queries
<!-- SOQL patterns they use frequently -->
<!-- Save queries that work well for them -->

## Notes
<!-- Internal observations -->
<!-- Field names they use frequently -->
<!-- Any API version preferences -->

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

- **No config keys visible** — use natural language, not "default_limit: 100"
- **Learn from behavior** — if they always query Accounts first, remember that
- **Track objects loosely** — note what they use but don't maintain full schema
- Update `last` on each use
