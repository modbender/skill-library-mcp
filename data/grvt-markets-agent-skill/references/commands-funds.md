# Fund Management Commands

All fund commands require authentication (`grvt auth login`). Commands that move funds (transfer create, withdraw create) also require a private key for EIP-712 signing.

Deposits are made via the GRVT web interface, not the CLI. The CLI can only query deposit history.

---

## `grvt funds deposit history`

Get deposit history. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--start-time <time>` | No | Start time (unix s/ms/ns or ISO 8601) |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max results per page |
| `--cursor <cursor>` | No | Pagination cursor |
| `--all` | No | Auto-paginate all results |

```bash
grvt funds deposit history
grvt funds deposit history --limit 10
grvt funds deposit history --start-time 2025-01-01T00:00:00Z --all --output ndjson
```

---

## `grvt funds transfer create`

Transfer funds between sub-accounts within the same main account. Requires a private key for EIP-712 signing. Prompts for confirmation unless `--yes` is passed.

| Option | Required | Description |
|--------|----------|-------------|
| `--from-sub-account-id <id>` | **Yes** | Source sub-account ID |
| `--to-sub-account-id <id>` | **Yes** | Destination sub-account ID |
| `--currency <symbol>` | **Yes** | Currency symbol (e.g. `USDT`, `BTC`) |
| `--amount <amount>` | **Yes** | Amount to transfer |
| `--json <path>` | No | Read full request body from file (`@path`) or stdin (`-`) |
| `--dry-run` | No | Show signed payload without sending |

```bash
grvt funds transfer create \
  --from-sub-account-id 111 --to-sub-account-id 222 \
  --currency USDT --amount 100

# Skip confirmation for scripting
grvt funds transfer create \
  --from-sub-account-id 111 --to-sub-account-id 222 \
  --currency USDT --amount 50 --yes

# Dry-run to preview
grvt funds transfer create \
  --from-sub-account-id 111 --to-sub-account-id 222 \
  --currency USDT --amount 100 --dry-run

# From JSON file
grvt funds transfer create --json @transfer.json
```

---

## `grvt funds transfer history`

Get transfer history. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--start-time <time>` | No | Start time |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max results per page |
| `--cursor <cursor>` | No | Pagination cursor |
| `--all` | No | Auto-paginate all results |

```bash
grvt funds transfer history
grvt funds transfer history --limit 20
grvt funds transfer history --all --output ndjson
```

---

## `grvt funds withdraw create`

Withdraw funds from a sub-account to an Ethereum address. Requires a private key for EIP-712 signing. Prompts for confirmation unless `--yes` is passed.

| Option | Required | Description |
|--------|----------|-------------|
| `--to-address <address>` | **Yes** | Destination Ethereum address (`0x...`, 42 characters) |
| `--currency <symbol>` | **Yes** | Currency symbol (e.g. `USDT`) |
| `--amount <amount>` | **Yes** | Amount to withdraw |
| `--sub-account-id <id>` | No | Source sub-account ID (falls back to config) |
| `--main-account-id <id>` | No | Main account ID (falls back to current account) |
| `--json <path>` | No | Read full request body from file (`@path`) or stdin (`-`) |
| `--dry-run` | No | Show signed payload without sending |

```bash
grvt funds withdraw create \
  --to-address 0x1234567890abcdef1234567890abcdef12345678 \
  --currency USDT --amount 50

# Skip confirmation
grvt funds withdraw create \
  --to-address 0x1234...5678 --currency USDT --amount 50 --yes

# Dry-run
grvt funds withdraw create \
  --to-address 0x1234...5678 --currency USDT --amount 50 --dry-run

# Specify source sub-account
grvt funds withdraw create \
  --sub-account-id 123 --to-address 0x1234...5678 \
  --currency USDT --amount 50
```

**Validation:** `--to-address` must start with `0x` and be exactly 42 characters.

---

## `grvt funds withdraw history`

Get withdrawal history. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--start-time <time>` | No | Start time |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max results per page |
| `--cursor <cursor>` | No | Pagination cursor |
| `--all` | No | Auto-paginate all results |

```bash
grvt funds withdraw history
grvt funds withdraw history --limit 10
grvt funds withdraw history --start-time 2025-01-01T00:00:00Z --all --output ndjson
```
