# Fava Reference

## Official Documentation

- **Fava Documentation**: https://beancount.github.io/fava/
- **Fava GitHub**: https://github.com/beancount/fava

## Overview

Fava is a web-based interface for Beancount that provides:
- Visual reports and charts
- Easy navigation of accounts and transactions
- Interactive query interface
- Document management
- Import and reconciliation tools
- Editor with syntax highlighting

## Fava Features

### Editor

The editor provides a convenient way to edit Beancount source files directly in the browser.

**Features**:
- Syntax highlighting
- Auto-completion for accounts, payees, tags
- Trailing whitespace highlighted in red
- Tab key for indentation (press Escape then Tab to exit)
- Jump to latest `insert-entry` position by default

**Configuration**:
Use `default-file` option to specify which file opens by default:
```beancount
2024-01-01 custom "fava-option" "default-file" "transactions/2024.beancount"
```

### Query Interface

Execute BQL queries like the `bean-query` command-line tool.

**Charts**: Fava displays charts for queries with exactly two columns:
- First column: date or string
- Second column: inventory

Example query that generates a chart:
```sql
SELECT
    payee,
    SUM(COST(position)) AS balance
WHERE
    account ~ 'Expenses'
GROUP BY payee, account
```

**Export Formats**:
- CSV (default)
- XLSX and ODS (install with `pip3 install fava[excel]`)

### Adding Transactions

**Quick Add**: Click `+` button or press `n` keyboard shortcut

**Features**:
- Form-based transaction entry
- Tags and links: Add in narration field separated by spaces (e.g., `narration #tag ^link`)
- Bookmark: Add `#add-transaction` to any URL to open form on load

**Insertion Position**: Configure with `insert-entry` option (see Options section)

### Up-to-Date Indicators

Visual indicators showing how current your accounts are:

**Colors**:
- **Green**: Recent activity (balance or transaction within lookback period)
- **Grey**: No activity for extended period
- **Red**: Overdue for balance assertion

**Configuration**:
```beancount
2024-01-01 custom "fava-option" "uptodate-indicator-grey-lookback-days" "60"
```

### Import System

Import transactions from external sources (CSV, OFX, etc.).

**Setup**:
1. Create import configuration file
2. Set `import-config` option pointing to config file
3. Set `import-dirs` option for directories to scan

```beancount
2024-01-01 custom "fava-option" "import-config" "importers/config.py"
2024-01-01 custom "fava-option" "import-dirs" "downloads/"
```

**Supported Entry Types**: Transaction, Balance, Note

**Special Metadata**: `__source__` displays original data (CSV row, XML fragment) in import interface. All metadata starting with underscore is stripped before saving.

### Document Management

Link and browse documents attached to your accounts.

**Linking Documents**:
```beancount
2024-01-15 document Assets:Bank:Checking "statements/2024-01-statement.pdf"
```

**Features**:
- Browse documents by account
- Search functionality
- View documents within Fava
- Upload new documents

### Budgets

Define budgets using custom directives:

```beancount
2024-01-01 custom "budget" Expenses:Coffee      "daily"      4.00 EUR
2024-01-01 custom "budget" Expenses:Books       "weekly"    20.00 EUR
2024-01-01 custom "budget" Expenses:Groceries   "monthly"   400.00 EUR
2024-01-01 custom "budget" Expenses:Electricity "quarterly"  85.00 EUR
2024-01-01 custom "budget" Expenses:Holiday     "yearly"   2500.00 EUR
```

**Frequencies**: `daily`, `weekly`, `monthly`, `quarterly`, `yearly`

**Budget Logic**:
- Budgets are valid until next budget directive for that account
- Broken down to daily budget internally
- Summed up for date ranges as needed
- Very flexible: monthly budget can be overridden by weekly budget

**Visualization**:
- Net Profit and Expenses charts show budget data
- Income Statement report shows budget vs. actual
- Changes (monthly) and Balances (monthly) reports show budget information

## Fava Options

Configure Fava behavior with custom directives:

```beancount
2024-01-01 custom "fava-option" "option-name" "value"
```

### Language

**Default**: Detected from browser

**Supported Languages**: `bg`, `ca`, `zh_CN`, `zh_TW`, `nl`, `en`, `fr`, `de`, `ja`, `fa`, `pt`, `pt_BR`, `ru`, `sk`, `es`, `sv`, `uk`

```beancount
2024-01-01 custom "fava-option" "language" "es"
```

### Locale

**Default**: Not set (or `en` if `render_commas` option is set)

Controls number formatting:
- `en_IN`: `11,11,111.33`
- `en`: `1,111,111.33`
- `de`: `1.111.111,33`

```beancount
2024-01-01 custom "fava-option" "locale" "en"
```

### Default File

Specify default file for editor:

```beancount
2024-01-01 custom "fava-option" "default-file" "transactions/2024.beancount"
; Or without argument uses the file containing this option:
2024-01-01 custom "fava-option" "default-file"
```

### Default Page

**Default**: `income_statement/`

Landing page when visiting Fava:

```beancount
2024-01-01 custom "fava-option" "default-page" "balance_sheet/"
; With filters:
2024-01-01 custom "fava-option" "default-page" "balance_sheet/?time=year-2+-+year"
```

### Fiscal Year End

**Default**: `12-31`

Last day of fiscal year in `%m-%d` format:

```beancount
2024-01-01 custom "fava-option" "fiscal-year-end" "06-30"  ; Australia/NZ
2024-01-01 custom "fava-option" "fiscal-year-end" "04-05"  ; UK
```

Enables filters: `FY2024`, `FY2024-Q3`, `fiscal_year`, `fiscal_quarter`

### Indent

**Default**: `2`

Number of spaces for indentation:

```beancount
2024-01-01 custom "fava-option" "indent" "4"
```

### Insert Entry

Specify where entries are inserted based on account patterns:

```beancount
2024-01-01 custom "fava-option" "insert-entry" "Expenses:Food"
2024-01-01 custom "fava-option" "insert-entry" "Assets:Bank"
```

**Logic**:
- Matches account of last posting in transaction
- Inserts before datewise latest matching option before entry date
- Falls back to end of default file if no match

### Auto Reload

**Default**: `false`

Automatically reload page when file changes:

```beancount
2024-01-01 custom "fava-option" "auto-reload" "true"
```

**Behavior**:
- `false`: Shows notification you can click to reload
- `true`: Reloads automatically
- Always reloads for user interactions (uploads, adding transactions)

### Unrealized

**Default**: `Unrealized`

Subaccount of Equity for unrealized gains when showing at market value:

```beancount
2024-01-01 custom "fava-option" "unrealized" "UnrealizedGains"
```

### Currency Column

**Default**: `61`

Column position for currency alignment in editor:

```beancount
2024-01-01 custom "fava-option" "currency-column" "80"
```

**Effects**:
- Aligns currencies when saving/formatting
- Shows vertical line in editor at this column

### Sidebar Show Queries

**Default**: `5`

Maximum number of saved queries to show in sidebar:

```beancount
2024-01-01 custom "fava-option" "sidebar-show-queries" "10"
; Or hide completely:
2024-01-01 custom "fava-option" "sidebar-show-queries" "0"
```

### Upcoming Events

**Default**: `7`

Days ahead to show upcoming events notification:

```beancount
2024-01-01 custom "fava-option" "upcoming-events" "14"
; Or disable:
2024-01-01 custom "fava-option" "upcoming-events" "0"
```

### Account Display Options

Control which accounts appear in trees:

```beancount
; Don't show closed accounts
2024-01-01 custom "fava-option" "show-closed-accounts" "false"

; Don't show accounts with zero transactions
2024-01-01 custom "fava-option" "show-accounts-with-zero-transactions" "false"

; Don't show accounts with zero balance
2024-01-01 custom "fava-option" "show-accounts-with-zero-balance" "false"
```

**Note**: Accounts with non-zero balance always show

### Collapse Pattern

Collapse accounts matching regex:

```beancount
; Collapse all third-level accounts
2024-01-01 custom "fava-option" "collapse-pattern" ".*:.*:.*"

; Collapse specific patterns
2024-01-01 custom "fava-option" "collapse-pattern" "Expenses:Food:.*"
```

### Use External Editor

**Default**: `false`

Use `beancount://` URL scheme instead of internal editor:

```beancount
2024-01-01 custom "fava-option" "use-external-editor" "true"
```

Requires [beancount_urlscheme](https://github.com/aumayr/beancount_urlscheme) project.

### Account Journal Include Children

**Default**: `true`

Include sub-account entries in account journal:

```beancount
2024-01-01 custom "fava-option" "account-journal-include-children" "false"
```

### Import Configuration

```beancount
2024-01-01 custom "fava-option" "import-config" "path/to/import_config.py"
2024-01-01 custom "fava-option" "import-dirs" "downloads/"
2024-01-01 custom "fava-option" "import-dirs" "bank-exports/"
```

### Invert Income/Liabilities/Equity

**Default**: `false`

Flip sign of Income, Liabilities, and Equity accounts:

```beancount
2024-01-01 custom "fava-option" "invert-income-liabilities-equity" "true"
```

**Effect**:
- Makes net profit chart show positive numbers when income > expenses
- Only affects income statement and balance sheet
- Journal and account pages unaffected

### Conversion Currencies

Specify currencies for conversion dropdown:

```beancount
2024-01-01 custom "fava-option" "conversion-currencies" "USD"
2024-01-01 custom "fava-option" "conversion-currencies" "EUR"
2024-01-01 custom "fava-option" "conversion-currencies" "GBP"
```

**Default**: All operating currencies + ISO 4217 currency codes

## Reports Available in Fava

### Balance Sheet
- Assets, Liabilities, Equity
- Net Worth calculation
- Historical date viewing
- Hierarchical account display

### Income Statement
- Income and Expenses for period
- Net income/loss
- Comparative period analysis
- Budget vs. actual when budgets defined

### Trial Balance
- All accounts with balances
- Debits and credits must balance
- Useful for reconciliation
- Exportable

### Journal
- Chronological transaction list
- Filter by account, date, tag, link
- Direct editing (if file is writable)
- Add documents and notes

### Account View
- Detailed transaction history
- Running balance
- Charts and statistics
- Quick access to related accounts

### Holdings
- Investment portfolio summary
- Current market value
- Cost basis and unrealized gains/losses
- Price history and performance

### Commodity View
- Historical prices
- Price charts
- Conversion rates
- Source links

### Documents
- Linked files organized by account
- Search functionality
- View within Fava

## Keyboard Shortcuts

- `n`: Open add transaction form
- `?`: Show keyboard shortcuts help

## Tips for Using Fava

### Hierarchical Account Structure

Design accounts for effective visualization:

**Good**:
```
Expenses:Food:Groceries
Expenses:Food:Dining:Restaurants
Expenses:Food:Dining:Coffee
Expenses:Utilities:Electricity
Expenses:Utilities:Water
```

**Benefits**:
- Collapsible in interface
- Easier to see category totals
- Better drill-down capability
- More flexible reporting

### Regular Workflow

**Monthly close**:
1. Import transactions from all accounts
2. Categorize and tag transactions
3. Add balance assertions
4. Run month-end reports
5. Compare to budget
6. Document anomalies

**Reconciliation**:
1. Download bank statement
2. Import into Fava
3. Match imported to existing
4. Add missing transactions
5. Add balance assertion
6. Verify no discrepancies

### Useful Saved Queries

Save frequently-used queries:
- Monthly expense breakdown
- Savings rate tracker
- Category budget vs. actual
- Investment performance dashboard
- Cash flow projection

### Performance Tips

For large ledgers:
- Use `collapse-pattern` to hide detail accounts
- Set `show-accounts-with-zero-balance` to false
- Limit query result sets with LIMIT clause
- Consider splitting files by year
