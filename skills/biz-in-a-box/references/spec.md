# biz-in-a-box Protocol Spec (v0.3)

## Required Entry Fields

Every journal entry MUST include:
- `id` — globally unique string (ULID recommended)
- `time` — ISO-8601 UTC event timestamp

## Optional Common Fields

- `recorded_at` — ISO-8601 UTC write timestamp
- `labels` — string[]
- `description` — string
- `attachments` — array
- `created_by` — actor id
- `prev_hash` — 64-char lowercase hex SHA-256
- `hash` — 64-char lowercase hex SHA-256

## Financial Entry Fields

If `labels` contains `financial`, entry MUST include:
- `debits`: `[{ account: string, amount: number }]`
- `credits`: `[{ account: string, amount: number }]`
- Constraint: `sum(debits.amount) == sum(credits.amount)`

## System Labels

| Label | Requirement |
|-------|------------|
| `financial` | triggers double-entry validation |
| `correction` | requires `supersedes: <entry_id>` |
| `transfer` | requires `from` and `to` fields |
| `historical` | required when entry is >7 days backdated |
| `imported` | alternative to `historical` for bulk imports |
| `opening-balance` | use for initial balances when starting mid-year |

## Hashing

- Algorithm: SHA-256, full 64 hex chars
- Genesis `prev_hash`: `0000000000000000000000000000000000000000000000000000000000000000`
- Hash input: canonical JSON of entry excluding `hash` field
- Canonicalization: sort object keys lexicographically at all levels, preserve array order

## Validation Rules

1. Required fields present (`id`, `time`)
2. Financial entries are balanced (`sum debits == sum credits`)
3. `correction` entries have `supersedes`
4. `transfer` entries have `from` and `to`
5. Hash chain is continuous and correct
6. Entries with `recorded_at - time > 7 days` have `historical` or `imported` label

## Backward Compatibility

- New fields may be added without breaking old readers
- Existing field semantics cannot be redefined in base protocol
- Vertical forks may add labels/fields but must keep base rules valid
