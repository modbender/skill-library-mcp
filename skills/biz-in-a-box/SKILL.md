---
name: biz-in-a-box
description: Agent-native business ledger using the biz-in-a-box protocol. Use when: (1) setting up a new business entity ledger (LLC, rental unit, sole trader, DAO, trust, etc.), (2) recording financial transactions as double-entry journal entries, (3) querying a biz-in-a-box journal for P&L, cash flow, burn rate, balances, or audit trails, (4) forking the repo for a new vertical (pm-in-a-box, dental-in-a-box, etc.), (5) validating a journal.ndjson file for hash chain integrity or double-entry balance. One repo = one entity. Works with any entity type on earth.
---

# biz-in-a-box Skill

Agent-native operating system for any business entity. An append-only, hash-chained journal (`journal.ndjson`) + a chart of accounts (`accounts.yaml`) + entity metadata (`entity.yaml`). Agents can derive any financial report from it in one context window.

- **Protocol spec:** See [references/spec.md](references/spec.md)
- **Chart of accounts:** See [references/accounts.md](references/accounts.md)
- **Vertical examples:** See [references/verticals.md](references/verticals.md)

## Quickstart

### 1. Fork or clone the repo

**GitHub:** https://github.com/taylorhou/biz-in-a-box
**Website:** https://biz-in-a-box.org

```bash
git clone https://github.com/taylorhou/biz-in-a-box my-entity
cd my-entity
```

Edit `entity.yaml` with the entity's `id`, `name`, and `type`. Edit `accounts.yaml` to match the entity's chart of accounts.

### 2. Record a transaction

Append a JSON line to `journal.ndjson`. Every entry needs `id` (ULID recommended) and `time` (ISO-8601 UTC). Financial entries also need balanced `debits`/`credits`.

**Example — record a $1,200 rent payment:**

```json
{"id":"01HXYZ...","time":"2026-02-26T14:00:00Z","labels":["financial"],"description":"February rent","debits":[{"account":"5200-rent","amount":1200}],"credits":[{"account":"1010-bank-checking","amount":1200}]}
```

### 3. Validate

```bash
node validate.js
```

Checks: required fields, double-entry balance, hash chain continuity, `correction` has `supersedes`, `transfer` has `from`/`to`.

### 4. Query / report

Read `journal.ndjson` line by line. Filter by `labels`, `time` range, or accounts to derive:
- **P&L:** sum revenue (4xxx) vs expenses (5xxx) over a period
- **Balance sheet:** sum assets (1xxx), liabilities (2xxx), equity (3xxx) at a point in time
- **Cash flow:** filter `1010-bank-checking` debits and credits
- **Burn rate:** sum expenses (5xxx) over trailing 30/90 days

## Key Rules

- `sum(debits.amount)` must equal `sum(credits.amount)` for financial entries
- Use `correction` label + `supersedes: <id>` to amend entries — never edit in place
- Genesis `prev_hash`: 64 zeros; subsequent entries chain via SHA-256
- Entries > 7 days backdated require `historical` or `imported` label

## File Set

| File | Purpose |
|------|---------|
| `journal.ndjson` | Append-only event log (one JSON per line) |
| `entity.yaml` | Entity metadata (id, name, type, jurisdiction, etc.) |
| `accounts.yaml` | Chart of accounts (assets/liabilities/equity/revenue/expenses) |
| `labels.yaml` | Label definitions |
| `access.yaml` | Access control |
| `validate.js` | Validation script |
| `snapshots/` | Optional periodic balance snapshots |
| `verticals/` | Vertical-specific extensions |
