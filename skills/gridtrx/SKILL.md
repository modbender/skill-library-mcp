---
name: gridtrx
description: Double-entry, full-cycle accounting suite built for AI agents. Converts bank CSVs, OFX, and QBO files into balanced, auditable books — balance sheet, income statement, general ledger, trial balance. All data stays in a single local SQLite file.
homepage: https://github.com/gridtrx/gridtrx
requires_tools:
  - exec
  - read
  - write
metadata:
  clawdbot:
    requires:
      env:
        - GRIDTRX_WORKSPACE
      bins:
        - python3
    primaryEnv: GRIDTRX_WORKSPACE
    files:
      - "*.py"
---

# Skill: GridTRX Accounting

## Demo

**[Watch the demo: Full accounting cycle in 15 minutes](https://youtu.be/9mmHbgEB3PQ)**

## What it does

Use this skill when the user asks you to "do the books," "categorize expenses," "import bank transactions," "run a balance sheet," or any bookkeeping task. GridTRX is a full-cycle double-entry accounting engine. You prompt in plain English, and the agent completes the books correctly. Every transaction balances. Every amount is deterministic. All data is local — no cloud services, no external APIs.

GridTRX produces a full set of auditable books: balance sheet, income statement, general ledger, trial balance, adjusting journal entries, retained earnings rollforward. Reports are exportable to CSV and PDF for any time period.

## Architecture

GridTRX has three interfaces to the same engine (`models.py` → `books.db`):

1. **MCP Server (preferred for agents)** — Structured JSON tools. 20 tools (12 read, 8 write) wrapping `models.py` directly. No text parsing, typed parameters, deterministic output.
2. **CLI (fallback for agents, power users)** — One-shot shell commands via `python cli.py`. Zero dependencies beyond Python 3.7+ standard library. Any terminal-based agent can drive it via subprocess.
3. **Browser UI (for humans)** — Flask web interface at `localhost:5000` via `python run.py`. Ledger browsing, report viewer with drill-down, comparative reports up to 13 columns, bank import with rule preview, reconciliation marking, dark mode.

All three hit the same `models.py` data layer. Nothing is out of sync. Use MCP when available. Fall back to CLI otherwise. The browser UI is for human review.

### Prerequisites

Install dependencies before first use (one-time setup):

```bash
pip install -r requirements.txt
```

Or install individually: `pip install mcp` (MCP server), `pip install flask` (browser UI). The CLI has no dependencies beyond the Python 3.7+ standard library.

**No packages are installed at runtime.** All dependencies must be pre-installed.

### MCP Setup

Add to the agent's MCP config with `GRIDTRX_WORKSPACE` set to the user's client folder:
```json
{
  "command": "python",
  "args": ["/path/to/mcp_server.py"],
  "env": {"GRIDTRX_WORKSPACE": "/path/to/clients"}
}
```

`GRIDTRX_WORKSPACE` is mandatory — the MCP server will refuse to start without it. Any `db_path` outside the workspace is rejected at runtime. Every MCP tool takes `db_path` as its first parameter, which must resolve to a `books.db` file inside the workspace.

### CLI Usage

```
GRIDTRX_WORKSPACE=/path/to/clients python cli.py /path/to/clients/acme/books.db <command>
```

Runs one command, prints plain text to stdout, exits. When `GRIDTRX_WORKSPACE` is set, the CLI enforces the same workspace boundary as the MCP server — paths outside the workspace are rejected.

## Inputs needed

- The absolute path to the client's books (`books.db` file or its parent folder).
- The absolute path to the bank file (`.csv`, `.ofx`, or `.qbo`).
- The bank account name to post against (typically `BANK.CHQ` for chequing).

## Core concepts

- **Double-entry:** Every transaction is a balanced zero-sum entry. Debits = Credits. Always.
- **Sign convention:** Positive = Debit. Parentheses `(1,500.00)` = Credit. `—` = Zero.
- **Amounts:** Stored as integer cents internally. Displayed as dollars with two decimals.
- **Account names:** Case-insensitive, UPPER by convention. Common prefixes: `BANK.` `EX.` `REV.` `AR.` `AP.` `GST.` `RE.` `SHL.` — When importing a trial balance or creating accounts, ALWAYS use GridTRX naming. Never use numeric account codes. If the source data has numeric codes (1010, 5800, etc.), ignore the codes and map by description to the nearest GridTRX account name. If no match exists, create the account using the `EX.` or `REV.` prefix convention. Always call `list_accounts` first before creating anything.
- **EX.SUSP (Suspense):** Where unrecognized transactions land. This is the triage queue. Tell the AI what the suspense items are and it will clear them. Or clear them yourself through the GUI.
- **Import rules:** Keyword → account mappings. Case-insensitive match, highest priority wins. Optional tax code splits the amount into net + tax automatically.
- **Lock date:** Prevents changes to closed periods. Check before importing historical data.
- **Architecture:** Each client is one SQLite file. Copy it, back it up, email it. One data layer (`models.py`) — CLI, MCP server, and browser UI all call the same functions.

## Workflow

### Step 1: Initialize (if no books exist)

**MCP:** No direct tool — use exec to run CLI.
**CLI:** `python cli.py` then `new /path/to/folder "Company Name"`

This creates `books.db` with a full chart of accounts (~60 posting accounts), five reports (BS, IS, AJE, TRX, RE.OFS), 60+ import rules, and four tax codes. **Always use starter books as the base** — they include the critical perpetual retained earnings chain (IS → NI → RE.CLOSE → RE on BS, plus RE.OFS/RE.OPEN for year-end). Never build reports from scratch without this chain. The fiscal year ceiling (`fy_end_date`) is automatically set to the current fiscal year end.

After setup, run `validate` to confirm the report chain is intact:
**CLI:** `python cli.py /path/to/books.db validate`

### Step 2: Import bank data

**MCP (preferred):**
- CSV: `import_csv(db_path, csv_path, "BANK.CHQ")`
- OFX/QBO: `import_ofx(db_path, ofx_path, "BANK.CHQ")`

**CLI fallback:**
- CSV: `python cli.py /path/to/books.db importcsv /path/to/file.csv BANK.CHQ`
- OFX: `python cli.py /path/to/books.db importofx /path/to/file.qbo BANK.CHQ`

The import applies all rules automatically. Check the result summary: `posted`, `skipped`, `to_suspense`.

**CaseWare AJE import:**
- MCP: `import_aje(db_path, file_path, "25AJE")`
- CLI: `python cli.py /path/to/books.db importaje /path/to/aje_export.iif 25AJE`
- Supports QuickBooks IIF and Venice/MYOB text formats. Maps CsW account descriptions to Grid account codes.

### Step 3: Audit suspense

**MCP:** `get_ledger(db_path, "EX.SUSP")`
**CLI:** `python cli.py /path/to/books.db ledger EX.SUSP`

Every entry here is an unrecognized transaction. Note the description and transaction ID for each.

### Step 4: Resolve suspense with the user

Present each suspense item to the user. Ask: *"What category is this?"*

Do NOT guess. If the description is ambiguous (e.g., "AMAZON", "BEST BUY", "TRANSFER"), ask the user for business context before categorizing.

Once the user answers, add a rule so future imports are automatic:

**MCP:** `add_rule(db_path, "AMAZON", "EX.OFFICE", "G5", 0)`
**CLI:** `python cli.py /path/to/books.db addrule AMAZON EX.OFFICE G5 0`

Tax code is optional. Common codes: `G5` (GST 5%), `H13` (HST 13%), `H15` (HST 15%), `E` (exempt).

### Step 5: Clear the bad suspense entries and re-import

Delete each suspense transaction, then re-import so the new rules apply:

**MCP:** `delete_transaction(db_path, txn_id)` for each, then `import_csv(...)` or `import_ofx(...)` again.
**CLI:** `python cli.py /path/to/books.db delete <txn_id>` for each, then re-run the import command.

Repeat Steps 3-5 until suspense is empty.

### Step 6: Verify and report

**MCP:**
- `trial_balance(db_path)` — debits must equal credits
- `generate_report(db_path, "BS")` — Balance Sheet
- `generate_report(db_path, "IS")` — Income Statement

**CLI:**
- `python cli.py /path/to/books.db tb`
- `python cli.py /path/to/books.db report BS`
- `python cli.py /path/to/books.db report IS`

### Step 7: Year-end rollforward

When the fiscal year is complete:

**MCP:** `rollforward(db_path, "2025-12-31")`
**CLI:** `python cli.py /path/to/books.db rollforward 2025-12-31`

This reads RE.CLOSE from the IS, posts Dr RE.OFS / Cr RE.OPEN, sets the lock date, and advances the FY ceiling to the next year. Then repeat from Step 2 for the next fiscal year. Rows beyond the ceiling are automatically skipped during import.

## Recovery: Undoing a bad import

If the user uploaded the wrong file or you imported against the wrong account:

1. **Find the bad transactions:** `search_transactions(db_path, "some description")` or via CLI `search <keyword>`.
2. **Delete them one by one:** `delete_transaction(db_path, txn_id)` or CLI `delete <txn_id>`.
3. **Verify the trial balance** still balances after cleanup.
4. **Re-import** the correct file.

There is no bulk undo. Deletions are individual and respect the lock date — you cannot delete transactions in a locked period.

## MCP tools reference (20 tools)

### Read tools
| Tool | Purpose |
|------|---------|
| `list_accounts(db_path, query?)` | List/search chart of accounts |
| `get_balance(db_path, account_name, date_from?, date_to?)` | Single account balance |
| `get_ledger(db_path, account_name, date_from?, date_to?)` | Account ledger with running balance |
| `trial_balance(db_path, as_of_date?)` | Trial balance — all accounts, Dr/Cr columns |
| `generate_report(db_path, report_name, date_from?, date_to?)` | Run a report (BS, IS, AJE, etc.) |
| `get_transaction(db_path, txn_id)` | Single transaction with all journal lines |
| `search_transactions(db_path, query, limit?)` | Search by description/reference |
| `list_reports(db_path)` | List available reports |
| `list_rules(db_path)` | List import rules |
| `get_info(db_path)` | Company name, fiscal year, lock date |

### Write tools
| Tool | Purpose |
|------|---------|
| `post_transaction(db_path, date, description, amount, debit_account, credit_account)` | Post a simple 2-line entry |
| `delete_transaction(db_path, txn_id)` | Delete a transaction (respects lock date) |
| `add_account(db_path, name, normal_balance, description?)` | Add a posting account |
| `add_rule(db_path, keyword, account_name, tax_code?, priority?)` | Add an import rule |
| `delete_rule(db_path, rule_id)` | Delete an import rule |
| `import_csv(db_path, csv_path, bank_account)` | Import bank CSV |
| `import_ofx(db_path, ofx_path, bank_account)` | Import bank OFX/QBO |
| `import_aje(db_path, file_path, ref_prefix)` | Import CaseWare AJE export (IIF or Venice) |
| `rollforward(db_path, ye_date)` | Year-end rollforward (posts RE closing, sets lock, advances ceiling) |
| `year_end(db_path, ye_date)` | Alias for rollforward |
| `set_lock_date(db_path, lock_date?)` | Show or set the lock date |
| `set_ceiling(db_path, date?)` | Show or set the fiscal year ceiling |
| `bulk_report_layout(db_path, report_name, items, after_account?, mode?)` | Batch-place items on a report (accounts, totals, labels, separators) |

## Guardrails

- **NEVER GUESS CATEGORIES.** If a transaction description is ambiguous, let it go to `EX.SUSP` and ask the user. Do not assume "AMAZON" is office supplies — it could be inventory, personal, or cost of sales.
- **NEVER MODIFY books.db DIRECTLY.** All writes go through `cli.py` commands or MCP tools. Never use file tools to read or write the SQLite database.
- **STAY IN THE WORKSPACE.** Only operate on `books.db` files within the user's GridTRX workspace. Both the MCP server and CLI enforce this when `GRIDTRX_WORKSPACE` is set — the MCP server will not start without it, and both interfaces reject any path outside the workspace.
- **NO OUTBOUND NETWORK REQUESTS.** GridTRX processes data locally. It does not phone home, call APIs, or transmit data. Do not attempt to "verify" transactions against external services.
- **RESPECT THE POSTING WINDOW.** Before importing, check the lock date and FY ceiling with `get_info()`. You cannot post on or before the lock date, or after the FY ceiling. Run `rollforward` to advance to the next fiscal year.
- **PRESERVE RAW OUTPUT.** When presenting financial data to the user, use the exact numbers from GridTRX. Do not round, reformat, or flip signs. Positive = Debit. Parentheses = Credit.
- **TRIAL BALANCE MUST BALANCE.** After any operation, if the trial balance shows unequal debits and credits, something is wrong. Stop and investigate before proceeding.
- **LIMIT EXEC SCOPE.** When using exec, only run `python cli.py` commands against books within the workspace. Do not run arbitrary shell commands, install packages, start background processes, or execute scripts other than `cli.py`. The MCP server is the preferred interface — use CLI only when MCP is unavailable.
