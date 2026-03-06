# Account Commands

All account commands require authentication (`grvt auth login`).

---

## `grvt account funding`

Get the funding (main) account summary. Shows balances in the main account before allocation to sub-accounts.

No options required (beyond global options).

```bash
grvt account funding
grvt account funding --output json --pretty
```

---

## `grvt account summary`

Get the summary for a specific sub-account, including balances, margin usage, unrealized P&L, and positions.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |

```bash
grvt account summary
grvt account summary --sub-account-id 123456
grvt account summary --output json --pretty
```

---

## `grvt account aggregated`

Get an aggregated summary across all sub-accounts. Useful for a high-level portfolio view.

No options required (beyond global options).

```bash
grvt account aggregated
grvt account aggregated --output json --pretty
```

---

## `grvt account history`

Get hourly snapshots of sub-account state over time. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--start-time <time>` | No | Start time (unix s/ms/ns or ISO 8601) |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max results per page |
| `--cursor <cursor>` | No | Pagination cursor |
| `--all` | No | Auto-paginate all results |

```bash
grvt account history
grvt account history --start-time 2025-01-01T00:00:00Z --limit 24
grvt account history --start-time 2025-01-01T00:00:00Z --end-time 2025-01-02T00:00:00Z --all --output ndjson
grvt account history --all --output json --pretty
```
