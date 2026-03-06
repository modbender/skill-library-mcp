# GridTRX

**Built specifically for agent use as a double-entry, full-cycle accounting suite and reporting framework. You prompt in plain english -> agent completes the books correctly.**

GridTRX is a bookkeeping system primarily built for AI agents first, and human accountants second. Feed it a bank statement or an Excel file, and the system produces a full set of auditable books: balance sheet, income statement, general ledger, trial balance. No subscriptions, no cloud, full privacy and security. Full GUI for humans, and CLI for agents.

## Built by a CPA

GridTRX was built by a cross-border tax CPA practitioner who does dual-citizen and international tax returns for a living. Not a developer who read an accounting textbook. A real accountant who got tired of watching the industry bolt chatbots onto QuickBooks and call it AI. The chart of accounts, the import rules, the report structures, and the suspense workflow all comes from doing real client work, not from a product spec.

## What You Get

**Financial Statements**
- Balance Sheet with opening balances, closing balances, $ change, % change
- Income Statement with period comparisons, up to 13 comparative columns
- General Ledger with running balances and cross-account references
- Trial Balance — always ties, debits equal credits
- Adjusting Journal Entry report
- Retained Earnings rollforward and YE close
- Sales tax reporting
- All reports exportable to CSV and PDF. For any time period. Just ask your agent for the report, and GridTRX can produce it.

**Full Accounting Cycle**
- Import bank data from CSV, OFX, and QBO files with auto-categorization
- customizable import rules match vendors to accounts automatically
- Unrecognized transactions land in Suspense (EX.SUSP) for human review and clearing. Tell the AI what the suspense items are and it will clear them. Or clear them yourself through the GUI.
- Year-end close with retained earnings rollover
- editable lock date enforcement for closed periods.
- Reconciliation tracking
- Sales tax code support (GST, HST with automatic net + tax splitting)

**Architecture**
- Each client is one SQLite file. Copy it, back it up, email it.
- Amounts stored as integers (cents). No floating-point rounding.
- Every transaction balances. Sum of all lines = 0. Always.
- One data layer (`models.py`) — CLI, MCP server, and browser UI all call the same functions.

## How It Works

An AI agent operates GridTRX on behalf of a human. The human never touches the software.

```
Human: "Here's my bank statement. Can you do my books?"
  ↓
Agent: Creates books → Imports bank data → Applies rules
  ↓
Agent: "I couldn't categorize 3 transactions. What's the Amazon charge for?"
  ↓
Human: "Office supplies."
  ↓
Agent: Adds rule → Deletes old entry → Re-imports → Trial balance ties
  ↓
Agent: "Books are done. Here's your balance sheet and income statement."
```

No clicking. No menus. No login. Just a conversation.

## Three Interfaces, One Engine

**MCP Server (preferred for agents)** — Structured JSON tools for AI agents. 19 tools (12 read, 7 write) wrapping `models.py` directly. No text parsing, typed parameters, deterministic output.

**CLI (fallback for agents, power users)** — One-shot shell commands. Zero dependencies beyond Python 3.7+. Any terminal-based agent can drive it via subprocess. Humans can use it too.

**Browser UI (for humans)** — Flask web interface at `localhost:5000`. Ledger browsing, report viewer with drill-down, comparative reports up to 13 columns, bank import with rule preview, reconciliation marking, dark mode. Same database, same data.

All three hit the same `models.py` data layer. Nothing is out of sync. MCP and CLI enforce a workspace boundary when `GRIDTRX_WORKSPACE` is set.

## Quick Start

### MCP Server (for Claude Desktop / Claude Code)

```bash
pip install mcp
```

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gridtrx": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "env": {"GRIDTRX_WORKSPACE": "/path/to/clients"}
    }
  }
}
```

Set `GRIDTRX_WORKSPACE` to restrict database access to a specific directory. The MCP server rejects any path outside the workspace.

### CLI

```bash
# Create new books
python cli.py
Grid> new ~/clients/acme "Acme Corp"

# Post a transaction
Grid/Acme Corp> post 2025-01-15 "Office supplies" 84.00 EX.OFFICE BANK.CHQ

# Import a bank statement
Grid/Acme Corp> importcsv ~/downloads/jan2025.csv BANK.CHQ

# Import OFX/QBO from your bank
Grid/Acme Corp> importofx ~/downloads/jan2025.qbo BANK.CHQ

# Trial balance
Grid/Acme Corp> tb

# Balance sheet
Grid/Acme Corp> report BS

# Income statement for a period
Grid/Acme Corp> report IS 2025-01-01 2025-12-31
```

One-shot mode for agents:

```bash
python cli.py ~/clients/acme tb
python cli.py ~/clients/acme report BS
python cli.py ~/clients/acme importcsv ~/downloads/jan2025.csv BANK.CHQ
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `new <folder> ["Name"] [MM-DD]` | Create new books with full chart of accounts |
| `open <path>` | Open existing books |
| `post <date> <desc> <amt> <dr> <cr>` | Post a 2-line transaction |
| `postx <date> <desc>` | Post a multi-line (compound) transaction |
| `tb [date]` | Trial balance |
| `report <name> [from] [to]` | Run a report (BS, IS, AJE, TRX, RE.OFS) |
| `ledger <acct> [from] [to]` | Account ledger with running balance |
| `balance <acct> [from] [to]` | Single account balance |
| `importcsv <file> <acct>` | Import bank CSV with auto-categorization |
| `importofx <file> <acct>` | Import bank OFX/QBO with auto-categorization |
| `accounts [posting\|total]` | List chart of accounts |
| `find <query>` | Search accounts by name/description |
| `search <query>` | Search transactions by description/reference |
| `rules` | List import rules |
| `addrule <kw> <acct> [tax] [pri]` | Add an import rule |
| `ye <date>` | Year-end rollover |
| `lock [date]` | Show or set lock date |
| `exportcsv <report> [file]` | Export report to CSV |
| `exporttb [file] [date]` | Export trial balance to CSV |
| `reconcile <acct>` | Reconciliation summary |
| `taxcodes` | List tax codes |

Full CLI reference: [CLI_README.txt](CLI_README.txt)

## MCP Tools

### Read Tools
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

### Write Tools
| Tool | Purpose |
|------|---------|
| `post_transaction(db_path, date, description, amount, debit_account, credit_account)` | Post a simple 2-line entry |
| `delete_transaction(db_path, txn_id)` | Delete a transaction (respects lock date) |
| `add_account(db_path, name, normal_balance, description?)` | Add a posting account |
| `add_rule(db_path, keyword, account_name, tax_code?, priority?)` | Add an import rule |
| `delete_rule(db_path, rule_id)` | Delete an import rule |
| `import_csv(db_path, csv_path, bank_account)` | Import bank CSV |
| `import_ofx(db_path, ofx_path, bank_account)` | Import bank OFX/QBO |
| `year_end(db_path, ye_date)` | Year-end rollover |
| `set_lock_date(db_path, lock_date?)` | Show or set the lock date |

## Display Format

```
 1,500.00      ← $1,500 debit
(1,500.00)     ← $1,500 credit
    —          ← zero
```

Positive = debit. Parentheses = credit. No sign-flipping. What you see is what's stored.

## Account Naming

GridTRX uses descriptive account names, not numeric codes. When importing a trial balance or creating accounts, always use GridTRX naming conventions. If source data has numeric codes (1010, 5800, etc.), ignore them and map by description.

| Prefix | Type | Examples |
|--------|------|----------|
| `BANK.xxx` | Bank accounts | `BANK.CDN`, `BANK.US`, `BANK.CHQ` |
| `REV.xxx` | Revenue | `REV`, `REV.SVC`, `REV.FOREIGN` |
| `EX.xxx` | Expenses | `EX.PHONE`, `EX.OFFICE`, `EX.VEHICLE`, `EX.WAGES` |
| `GST.xxx` | Tax accounts | `GST.IN`, `GST.OUT`, `GST.CLR` |
| `AR.xxx` | Accounts receivable | `AR` |
| `AP.xxx` | Accounts payable | `AP`, `AP.CC` |
| `SHL.xxx` | Shareholder loans | `SHL.DANA` |
| `RE.xxx` | Retained earnings | `RE`, `RE.OPEN`, `RE.CLOSE` |

If no existing account matches, create one using the `EX.` or `REV.` prefix convention.

## Browser UI

For visual work, start the web interface:

```bash
python run.py
```

Opens at `http://localhost:5000`. Same database, same data.

- Account ledgers with inline editing
- Report viewer with drill-down
- Multi-column comparative reports (up to 13 columns)
- Bank CSV import with rule matching preview
- Print-ready report output
- Reconciliation marking
- Dark mode

## OpenClaw Skill

GridTRX is available as an [OpenClaw skill on ClawHub](https://clawhub.ai). Any OpenClaw agent can install it and immediately handle bookkeeping tasks.

See [SKILL.md](SKILL.md) for the full skill definition.

## Requirements

**CLI only:** Python 3.7+ (standard library only — no pip install needed)

**MCP Server:** Python 3.7+ and `pip install mcp`

**Browser UI:** Python 3.7+ and Flask (`pip install flask`, or just run `run.py` and it installs automatically)

## License

AGPLv3 — see [LICENSE](LICENSE)
