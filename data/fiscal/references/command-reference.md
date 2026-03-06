# Command Reference

Every fscl command with flags and output columns.

**Entity resolution:** Commands that accept account, category, or category group IDs also accept names. The CLI resolves names to IDs using exact case-insensitive matching. Example: `fscl month set 2026-02 "Groceries" 500.00`.

## Global Options

| Flag | Description |
|---|---|
| `--data-dir <path>` | Actual data directory |
| `--budget <id>` | Active budget ID |
| `--server-url <url>` | Actual server URL |
| `--json` | JSON output |
| `--columns <cols>` | Comma-separated column filter |

### Connection and auth resolution

`server_url` is resolved in order (first wins):

1. CLI flag (`--server-url`)
2. Environment variable (`FISCAL_SERVER_URL`)
3. Config file (`~/.config/fiscal/config.json`)

Authentication uses a session token saved by `fscl login` (`config.token`). If a server is configured and no valid token is available, commands return:

```json
{ "status": "err", "message": "Not logged in. Run 'fscl login' to authenticate.", "code": "not-logged-in" }
```

### Output format

Default: human-readable tables. `--json` for machine-readable output. Agents should always use `--json`.

Amounts in output: **integer cents** (`-4599` = -$45.99). Amounts in input: **decimal notation** (`--amount -45.99`).

**Row responses** (list, query, report commands):

```json
{ "status": "ok", "entity": "accounts", "count": 2, "data": [...] }
```

**Mutation responses** (create, update, delete — always JSON regardless of `--json` flag):

```json
{ "status": "ok", "entity": "account", "action": "create", "id": "a1b2c3" }
```

**Errors:**

```json
{ "status": "err", "message": "No budget selected." }
```

Validation errors include an `errors` array with `path` and `message` per item.

| Field | Description |
|---|---|
| `status` | `ok` or `err` |
| `entity` | Entity context (e.g. `transactions`, `import`) |
| `count` | Row count or error count |
| `data` | Array of rows |
| `action` | Mutation action (`create`, `update`, `delete`, etc.) |
| `message` | Human-readable summary or error message |
| `errors` | Detail array for parse/validation failures |

## init

`fscl init [--non-interactive --mode <local|remote>]`

| Flag | Description |
|---|---|
| `--non-interactive` | Disable prompts |
| `--mode <mode>` | `local`, `remote` |
| `--budget-name <name>` | Budget name (local) |
| `--password <pw>` | Server password (remote) |
| `--sync-id <id>` | Remote sync ID (remote) |

Modes: `local` (disk-only), `remote` (pull from server). Use `budgets push` to upload a local budget. On success, prints `fscl status` output.

When `init` is launched through `npx fscl init`, interactive mode asks whether to install fscl globally (`npm install -g fscl`) so the `fscl` command is available afterward.

Interactive `fscl init` also asks whether to install the Fiscal agent skill by running `npx skills add fiscal-sh/fscl`.

## status

`fscl status [--compact]`

Shows: budget name/ID, server connectivity, entity counts, uncategorized count, transaction date range.

## sync

`fscl sync`

Write commands auto-sync when a server is configured. Use for explicit manual sync.

## login

`fscl login [server-url] [--password <pw>]`

Authenticates with the Actual server and stores `serverURL` + `token` in config. If `--password` is omitted in a TTY, fscl prompts securely.

Server URL resolution:
1. Positional arg (`[server-url]`)
2. `FISCAL_SERVER_URL`
3. Config `serverURL`

## logout

`fscl logout`

Clears stored `serverURL` and `token`.

## budgets

| Command | Description |
|---|---|
| `budgets list` | Columns: `id`, `name`, `group_id`, `cloud_file_id`, `state` (one row per logical budget; `state` is `local`, `linked`, or `remote`) |
| `budgets create [name]` | Create a new budget (interactive if name omitted) |
| `budgets use <id>` | Set active budget |
| `budgets delete <id>` | Delete local budget copy (`--yes` required) |
| `budgets pull <syncId>` | Download remote budget, set active |
| `budgets push` | Upload local budget to server |

`budgets create` options:

| Flag | Description |
|---|---|
| `--non-interactive` | Run without prompts |
| `--mode <mode>` | `local`, `remote` |
| `--budget-name <name>` | Budget name (alternative to positional arg) |
| `--password <pw>` | Server password for `remote` mode |
| `--sync-id <id>` | Remote sync ID for `remote` |

Remote operations require a valid login token (`fscl login`).

## accounts

| Command | Key Flags |
|---|---|
| `accounts list` | |
| `accounts find <names...>` | Case-insensitive substring, OR-matched |
| `accounts create <name>` | `--offbudget`, `--balance <decimal>` |
| `accounts create-batch <json>` | Array of `{name, offbudget?, balance?}` |
| `accounts update <id>` | `--name`, `--offbudget` / `--no-offbudget` |
| `accounts close <id>` | `--transfer-to <acctId>`, `--transfer-category <catId>` |
| `accounts reopen <id>` | |
| `accounts delete <id>` | `--yes` (required) |
| `accounts balance <id>` | `--cutoff <YYYY-MM-DD>` |

Output columns: `id`, `name`, `offbudget`, `closed`, `balance_current`

## transactions

| Command | Key Flags |
|---|---|
| `transactions list <acctId>` | `--start`, `--end` (both required) |
| `transactions uncategorized` | `--account <id>`, `--start`, `--end` |
| `transactions add <acctId>` | `--date`, `--amount` (required); `--payee`, `--category`, `--notes`, `--cleared` |
| `transactions delete <id>` | `--yes` (required) |
| `transactions import <acctId> <file>` | See [Import](#importing-transactions) below |

Output columns: `id`, `date`, `account`, `account_name`, `amount`, `payee`, `payee_name`, `category`, `category_name`, `notes`, `cleared`, `reconciled`, `transfer_id`, `imported_id`

### categorize draft/apply

`fscl transactions categorize draft [--account <id>] [--start] [--end] [--limit <n>]`
`fscl transactions categorize apply [--dry-run]`

Draft shape: `[{ id, category, _meta: { date, amount, payeeName, accountName, notes } }]`

Fill in `category` with category IDs. Apply output: `id`, `category`, `result`.

### edit draft/apply

`fscl transactions edit draft --account|--category|--start|--end [--limit <n>]` (at least one filter required)
`fscl transactions edit apply [--dry-run]`

Draft shape: `[{ id, date, amount, payee, category, notes, cleared, account, _meta }]`

Amounts are decimal strings. Apply output: `id`, `fields`, `result`.

## Importing transactions

Supported formats: CSV/TSV, OFX/QFX, QIF, CAMT XML. Auto-detected from file extension.

### General flags

| Flag | Description |
|---|---|
| `--report` | Print compact import summary |
| `--dry-run` | Preview without committing |
| `--show-rows` | Print individual imported rows |
| `--no-reconcile` | Skip rule processing and deduplication |
| `--no-clear` | Don't auto-set `cleared=true` |
| `--no-import-notes` | Skip memo/notes field |
| `--date-format <fmt>` | Override date parsing format |
| `--multiplier <n>` | Multiply amounts (use `0.01` if values are in cents) |
| `--flip-amount` | Negate all amounts |

Supported date formats: `yyyy mm dd`, `yy mm dd`, `mm dd yyyy`, `mm dd yy`, `dd mm yyyy`, `dd mm yy`.

`--dry-run` requires reconcile mode (default). Cannot combine with `--no-reconcile`.

### OFX/QFX flags

| Flag | Description |
|---|---|
| `--fallback-payee-to-memo` | Use memo as payee when payee is missing |

### CSV flags

| Flag | Description |
|---|---|
| `--no-csv-header` | CSV has no header row |
| `--csv-delimiter <char>` | Delimiter character (default: `,`) |
| `--csv-skip-start <n>` | Skip N lines at start |
| `--csv-skip-end <n>` | Skip N lines at end |
| `--csv-date-col <name\|index>` | Date column |
| `--csv-amount-col <name\|index>` | Signed amount column |
| `--csv-payee-col <name\|index>` | Payee column |
| `--csv-notes-col <name\|index>` | Notes column |
| `--csv-category-col <name\|index>` | Category column |
| `--csv-inflow-col <name\|index>` | Inflow column (alternative to single amount) |
| `--csv-outflow-col <name\|index>` | Outflow column (alternative to single amount) |
| `--csv-inout-col <name\|index>` | In/out marker column |
| `--csv-out-value <value>` | Value treated as outflow in `--csv-inout-col` |

### CSV amount modes

Three ways to handle amounts:

1. **Single signed column:** `--csv-amount-col "Amount"`
2. **Separate inflow/outflow:** `--csv-inflow-col "Credit" --csv-outflow-col "Debit"`
3. **Amount with in/out marker:** `--csv-amount-col "Amount" --csv-inout-col "Type" --csv-out-value "DR"`

### Import pipeline

Parse → Normalize (date format, multiplier, flip) → Reconcile (rules + dedup, skip with `--no-reconcile`) → Commit (skip with `--dry-run`)

## month

| Command | Key Flags |
|---|---|
| `month list` | |
| `month show <month>` | |
| `month status` | `--month <YYYY-MM>`, `--compare <n>`, `--only <over\|under\|on>` |
| `month set <month> <catId> <amount>` | Amount as decimal string |
| `month copy <source> <target>` | Copy all budget amounts between months |
| `month set-carryover <month> <catId> <true\|false>` | Toggle rollover overspending |
| `month cleanup <month>` | End-of-month cleanup |

`month show` columns: `month`, `group_id`, `group_name`, `category_id`, `category_name`, `budgeted`, `spent`, `balance`. Metadata: `toBudget`.

`month status` columns: above + `remaining`, `percent_used`, `over_under`, `status`, `compare_months`, `prev_spent_avg`, `trend_delta`.

### month draft/apply

`fscl month draft <month>`
`fscl month apply <month> [--dry-run]`

Draft shape: `[{ categoryId, group, name, amount }]`. Only `categoryId` and `amount` (decimal string) are used on apply.

### month templates

| Command | Key Flags |
|---|---|
| `month templates check` | Validate templates |
| `month templates draft` | Generate editable template definitions |
| `month templates apply` | `--dry-run` |
| `month templates run <month>` | `--category <id>` for single category |

## categories

| Command | Key Flags |
|---|---|
| `categories list` | |
| `categories find <names...>` | Case-insensitive substring, OR-matched |
| `categories create <name>` | `--group <groupId>` (required), `--income` |
| `categories draft` | Writes editable category-group/category tree to draft file |
| `categories apply` | `--dry-run`; creates/renames/moves from draft |
| `categories update <id>` | `--name` |
| `categories delete <id>` | `--yes` (required), `--transfer-to <catId>` |
| `categories create-group <name>` | `--income` |
| `categories update-group <id>` | `--name` |
| `categories delete-group <id>` | `--yes` (required), `--transfer-to <catId>` |

List columns: `kind`, `id`, `group_id`, `name`, `is_income`, `hidden`
Find columns: `kind`, `id`, `name`, `group_id`, `group_name`, `is_income`, `hidden`

### categories draft/apply

`fscl categories draft`
`fscl categories apply [--dry-run]`

Draft shape: `[{ id?, name, categories: [{ id?, name }] }]`

Top-level entries are category groups. The `categories` array contains category entities. Categories do not nest inside other categories.

- `id` present + changed `name` -> rename
- category `id` moved under a different group -> reassign
- missing `id` -> create
- rows removed from draft are ignored (no deletion)

## payees

| Command | Key Flags |
|---|---|
| `payees list` | |
| `payees find <names...>` | Case-insensitive substring, OR-matched |
| `payees stats` | `--since <date>`, `--min-count <n>`, `--extended` |
| `payees create <name>` | |
| `payees update <id>` | `--name` |
| `payees delete <id>` | `--yes` (required) |
| `payees merge <targetId> <mergeIds...>` | Reassigns all transactions to target |

Output columns: `id`, `name`, `transfer_acct`

## rules

| Command | Key Flags |
|---|---|
| `rules list` | |
| `rules validate <json>` | Validate without creating |
| `rules preview <json>` | Show matching transactions |
| `rules run` | `--rule <id>`, `--dry-run`, `--and-commit` |
| `rules create <json>` | `--run` (apply retroactively) |
| `rules create-batch <json>` | All validated before any created |
| `rules draft` | Generate editable draft |
| `rules apply` | `--dry-run` |
| `rules update <jsonWithId>` | Full rule object with `id` required |
| `rules delete <id>` | `--yes` (required) |

List columns: `id`, `stage`, `conditions_op`, `conditions`, `actions`
Run columns: `id`, `date`, `account`, `account_name`, `amount`, `payee_before`, `payee_before_name`, `payee_after`, `payee_after_name`, `notes`, `category_before`, `category_before_name`, `category_after`, `category_after_name`, `matched_rule`

See [rules.md](rules.md) for JSON schema, stages, conditions, and actions.

## schedules

| Command | Key Flags |
|---|---|
| `schedules list` | |
| `schedules find <names...>` | Case-insensitive name search |
| `schedules upcoming` | `--days <n>` (default: 7) |
| `schedules missed` | `--days <n>` (default: 30) |
| `schedules summary` | Monthly/annual cost rollup |
| `schedules history <id>` | `--limit <n>` (default: 12) |
| `schedules review <id> <json>` | `{decision, note?, cadenceMonths?}` |
| `schedules reviews` | `--due` (only unreviewed/due) |
| `schedules create <json>` | |
| `schedules update <id> <json>` | |
| `schedules delete <id>` | `--yes` (required) |

List columns: `id`, `name`, `posts_transaction`, `next_date`, `amount`, `amount_op`, `account`, `account_name`, `payee`, `payee_name`, `date`
Upcoming adds: `days_until`. Missed adds: `days_overdue`.
Summary columns: `id`, `name`, `payee_name`, `account_name`, `amount`, `frequency`, `interval`, `monthly_amount`, `annual_amount`, `next_date`. Metadata: `total_monthly`, `total_annual`.
Reviews columns: `schedule_id`, `name`, `payee_name`, `amount`, `decision`, `reviewed_at`, `next_review_at`, `cadence_months`, `note`, `days_until_review`

## tags

| Command | Key Flags |
|---|---|
| `tags list` | |
| `tags find <names...>` | Case-insensitive name search |
| `tags create <name>` | `--color <hex>`, `--description <text>` |
| `tags update <id>` | `--name`, `--color`, `--description` |
| `tags delete <id>` | `--yes` (required) |

## query

Run custom [ActualQL](https://actualbudget.org/docs/api/actual-ql/) queries.

```bash
fscl query --module <path>       # Run a query module
fscl query --inline <expr>       # Run an inline expression
```

Use exactly one of `--module` or `--inline`. Module can export `default (q) => query` or a named `query`.

## Draft/apply workflow

Six commands support draft/apply: **categories**, **categorize**, **edit**, **rules**, **month**, **templates**.

1. `<command> draft [filters]` — generates JSON at `<dataDir>/<budgetId>/drafts/`
2. Edit the JSON file
3. `<command> apply --dry-run` — preview changes
4. `<command> apply` — commit (deletes draft on success)

Never hand-create a draft file by path. Generate it with `<command> draft`, then edit that generated file.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Failure (validation errors, partial import failures, etc.) |
