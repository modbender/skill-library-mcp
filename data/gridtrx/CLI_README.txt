GridTRX CLI Reference
=====================

GridTRX CLI is the command-line interface for the GridTRX accounting engine.
It calls models.py directly. Zero dependencies beyond Python 3.7+ standard
library.

Usage
-----
  python cli.py                           # Interactive mode — pick a client
  python cli.py /path/to/books.db         # Open specific books interactively
  python cli.py /path/to/books.db tb      # One-shot: run command and exit

One-shot mode is designed for AI agents: run a single command, get plain-text
output on stdout, exit. Chain with && for multi-step workflows.

When GRIDTRX_WORKSPACE is set, the CLI enforces workspace boundaries — paths
outside the workspace are rejected.


Commands
--------

SESSION
  new <folder> ["Name"] [MM-DD]     Create new books with full chart of accounts.
                                    MM-DD sets the fiscal year end (default 12-31).
                                    Creates books.db with ~60 posting accounts,
                                    5 reports (BS, IS, AJE, TRX, RE.OFS),
                                    60+ import rules, and 4 tax codes.
  open <path>                       Open an existing books.db file.
  close                             Close the current books.
  info                              Show company name, fiscal year, lock date,
                                    and database statistics.
  library [path]                    List client books in a directory.
  quit / exit                       Exit the CLI.


CHART OF ACCOUNTS
  accounts [posting|total]          List all accounts. Filter by type.
  account <name>                    Show details for a single account.
  find <query>                      Search accounts by name or description.
  addaccount <name> <D|C> ["desc"]  Add a new posting account.
                                    D = debit-normal, C = credit-normal.
  editaccount <name> [desc] [num]   Edit an account's description or number.


TRANSACTIONS
  post <date> <desc> <amt> <dr> <cr>
      Post a simple 2-line transaction.
      Example: post 2025-01-15 "Office supplies" 84.00 EX.OFFICE BANK.CHQ
      This debits EX.OFFICE 84.00 and credits BANK.CHQ 84.00.

  postx <date> <desc>
      Post a multi-line (compound) transaction interactively.
      Enter lines as: <account> <amount>
      Positive = debit, negative = credit.
      Type 'done' to commit. Sum of all lines must be zero.

  edit <txn_id>                     Show transaction details by ID.
  delete <txn_id>                   Delete a transaction. Respects lock date.
  search <query>                    Search transactions by description or reference.


BANK IMPORT
  importcsv <file> <account>        Import a bank CSV file.
                                    Applies import rules to auto-categorize.
                                    Unmatched rows go to EX.SUSP (Suspense).
                                    Skips duplicate transactions automatically.

  importofx <file> <account>        Import a bank OFX or QBO file.
                                    Same rule-matching as importcsv.

  Import output shows: posted, skipped (duplicates), to_suspense.


IMPORT RULES
  rules                             List all import rules with ID, keyword,
                                    account, tax code, and priority.
  addrule <keyword> <account> [tax] [priority]
      Add an import rule.
      Example: addrule SHOPIFY REV.SVC G5 10
      Keyword matching is case-insensitive. Highest priority wins
      when multiple rules match.

  editrule <id> [keyword] [account] [tax] [priority]
      Edit an existing import rule.

  delrule <id>                      Delete an import rule by ID.


REPORTS
  tb [date]                         Trial balance — all accounts, Dr/Cr columns.
                                    Optional as-of date. Debits must equal credits.
  report <name> [from] [to]         Run a named report.
                                    Reports: BS, IS, AJE, TRX, RE.OFS
                                    BS = Balance Sheet
                                    IS = Income Statement
                                    AJE = Adjusting Journal Entries
                                    TRX = Transaction Detail
                                    RE.OFS = Retained Earnings Rollforward
  reports                           List all available reports.
  editreport <name> <description>   Edit a report's description.
  balance <acct> [from] [to]        Single account balance for a period.
  ledger <acct> [from] [to]         Account ledger with running balance.
                                    Shows every transaction line with date,
                                    reference, description, Dr/Cr, and balance.


EXPORT
  exportcsv <report> [file] [from] [to]
      Export a report to CSV file.
      Example: exportcsv IS income.csv 2025-01-01 2025-12-31

  exporttb [file] [date]
      Export trial balance to CSV file.
      Example: exporttb trial_balance.csv 2025-12-31


RECONCILIATION
  reconcile <acct>                  Show reconciliation summary for a bank account.


TAX
  taxcodes                          List all tax codes.
                                    G5 = GST 5%, H13 = HST 13%,
                                    H15 = HST 15%, E = Exempt.


PERIOD CONTROLS
  lock [date]                       Show or set the lock date.
                                    Prevents posting, editing, or deleting
                                    transactions on or before the lock date.
  ye <date>                         Year-end rollover.
                                    Posts closing entries to Retained Earnings,
                                    sets the lock date to the year-end date.
                                    This is one-way — cannot be undone.


Display Format
--------------
   1,500.00       $1,500 debit
  (1,500.00)      $1,500 credit
      ---         zero

Positive = debit. Parentheses = credit. No sign-flipping.


Account Naming Convention
-------------------------
ALWAYS use GridTRX account names. Never use numeric account codes.
If source data has numeric codes (1010, 5800, etc.), ignore the codes
and map by description. If no match exists, create using EX. or REV.
prefix convention. Always run 'accounts' or 'find' first before creating.

  BANK.xxx    Bank accounts (debit-normal) — BANK.CDN, BANK.US, BANK.CHQ
  AR.xxx      Accounts receivable (debit-normal)
  AP.xxx      Accounts payable (credit-normal)
  REV.xxx     Revenue (credit-normal) — REV, REV.SVC, REV.FOREIGN
  EX.xxx      Expenses (debit-normal) — EX.PHONE, EX.OFFICE, EX.VEHICLE
  GST.xxx     Tax accounts — GST.IN, GST.OUT, GST.CLR
  SHL.xxx     Shareholder loans (credit-normal) — SHL.DANA
  RE.xxx      Retained earnings (credit-normal)
  EX.SUSP     Suspense — uncategorized transactions land here


Standard Workflow
-----------------
  1. Create books:     new ~/clients/acme "Acme Corp"
  2. Import bank data: importcsv ~/data/bank.csv BANK.CHQ
  3. Review suspense:  ledger EX.SUSP
  4. Add rules:        addrule <keyword> <account> [tax] [priority]
  5. Delete suspense:  delete <txn_id>
  6. Re-import:        importcsv ~/data/bank.csv BANK.CHQ
  7. Verify:           tb
  8. Run reports:      report BS && report IS


Workspace Security
------------------
Set GRIDTRX_WORKSPACE to restrict file access to a single directory:

  export GRIDTRX_WORKSPACE=~/clients

Both the MCP server and CLI enforce this boundary. Paths outside the
workspace are rejected at runtime.
