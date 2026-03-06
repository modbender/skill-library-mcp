# Beancount Syntax Reference

## Official Documentation Links

- **Beancount Documentation**: https://beancount.github.io/docs/index.html
- **Beancount GitHub**: https://github.com/beancount/beancount
- **Official Syntax Cheat Sheet**: http://furius.ca/beancount/doc/cheatsheet
- **Complete Syntax Documentation**: http://furius.ca/beancount/doc/syntax
- **Beancount Options Reference**: http://furius.ca/beancount/doc/options

## Core Concepts

**Double-Entry Accounting**: Every transaction affects at least two accounts. Total debits must equal total credits.

**Building Blocks**:
1. **Commodities** - Currencies and tradeable items (USD, EUR, AAPL)
2. **Accounts** - Named containers for commodities
3. **Directives** - Dated entries that build your ledger

## Commodities

**Format**: All in CAPS

**Examples**:
- Currencies: `USD`, `EUR`, `CAD`, `GBP`, `JPY`
- Stocks: `GOOG`, `AAPL`, `MSFT`
- Custom: `RBF1005`, `HOME_MAYST`, `AIRMILES`, `HOURS`

**Rules**:
- Must be all uppercase
- Can include letters, numbers, underscores, hyphens
- No spaces allowed
- Represent any tradeable commodity

## Accounts

Accounts are colon-separated capitalized words forming a hierarchy.

### Five Root Account Types

| Name | Sign | Contains | Examples |
|------|------|----------|----------|
| `Assets` | + | Cash, Bank accounts, Investments | `Assets:Checking`, `Assets:Investments:Stocks` |
| `Liabilities` | - | Credit cards, Loans | `Liabilities:CreditCard`, `Liabilities:Mortgage` |
| `Income` | - | Salary, Interest | `Income:Salary:BigCorp`, `Income:Interest` |
| `Expenses` | + | All expense categories | `Expenses:Food:Groceries`, `Expenses:Rent` |
| `Equity` | - | Opening balances, Earnings | `Equity:Opening-Balances` |

**Sign Convention**:
- `+` accounts increase with debits (positive postings)
- `-` accounts increase with credits (negative postings)

### Account Naming Rules

**Format**: `RootType:Level2:Level3:...`

**Examples**:
```
Assets:Cash
Assets:Bank:Checking
Assets:Bank:Savings:Emergency
Expenses:Food:Groceries
Expenses:Food:Dining:Restaurants
Income:Salary:Employer
Liabilities:CreditCard:Visa
```

**Best Practices**:
- Use descriptive names
- Create hierarchies for better reporting
- Consistent naming conventions
- Separate words with hyphens or CamelCase
- Plan structure before starting

### Custom Root Account Names

Change root account names with options (must be at beginning of file):

```beancount
option "name_assets"      "Vermoegen"
option "name_liabilities" "Verbindlichkeiten"
option "name_income"      "Einkommen"
option "name_expenses"    "Ausgaben"
option "name_equity"      "Eigenkapital"
```

## Directives

**General Format**: `YYYY-MM-DD <directive> <arguments...>`

Date format is always `YYYY-MM-DD`. Directives are processed by date, not by order in file.

### Open and Close Accounts

#### Open Directive

Declares that an account exists:

```beancount
2024-01-01 open Expenses:Restaurant
```

With currency constraints:

```beancount
2024-01-01 open Assets:Checking USD,EUR
2024-01-01 open Assets:Investments USD,AAPL,GOOG
```

#### Close Directive

Closes an account (no postings allowed after this date):

```beancount
2024-12-31 close Assets:OldBank:Checking
```

### Commodity Directive

**Optional** - Use to attach metadata to currencies:

```beancount
1998-07-22 commodity AAPL
  name: "Apple Computer Inc."
  precision: 3

2020-01-01 commodity EUR
  name: "Euro"
  precision: 2
```

**Metadata**:
- `name`: Displayed as tooltip in Fava
- `precision`: Number of decimal digits to display (overrides auto-inferred precision)

### Price Directive

Fill the historical price database:

```beancount
2024-04-30 price AAPL 125.15 USD
2024-05-30 price AAPL 130.28 USD
2024-05-30 price EUR 1.18 USD
```

**Uses**:
- Track market prices over time
- Enable currency/commodity conversions
- Calculate unrealized gains
- Show portfolio market value

### Note Directive

Add notes to accounts:

```beancount
2024-03-20 note Assets:Checking "Called to ask about rebate"
2024-06-15 note Assets:Investments:Brokerage "Opened account for retirement savings"
```

**Best Practice**: Use for important account-related information.

### Document Directive

Link external files to accounts:

```beancount
2024-03-20 document Assets:Checking "/path/to/statement.pdf"
2024-12-31 document Expenses:Taxes "/path/to/tax-documents/2024-w2.pdf"
```

**Fava Integration**: Documents appear in Fava's document viewer.

### Transaction Directive

The core directive for recording financial transactions.

#### Basic Transaction

```beancount
2024-05-30 * "Some narration about this transaction"
  Liabilities:CreditCard  -101.23 USD
  Expenses:Restaurant      101.23 USD
```

#### Transaction with Payee

```beancount
2024-05-30 * "Cable Co" "Phone Bill"
  Expenses:Home:Phone    87.45 USD
  Assets:Checking       -87.45 USD
```

#### Transaction with Tags and Links

```beancount
2024-05-30 ! "Cable Co" "Phone Bill" #bills #monthly ^invoice-2024-05
  id: "TW378743437"
  Expenses:Home:Phone    87.45 USD
  Assets:Checking               ; Amount auto-calculated
```

**Transaction Flags**:
- `*` = Cleared/completed transaction
- `!` = Pending/uncleared transaction

**String Order**:
- One string: Narration
- Two strings: Payee, then Narration

**Tags**: `#tag-name` (can have multiple)
**Links**: `^link-name` (can have multiple)

**Metadata**: Key-value pairs indented after transaction date line

#### Complete Transaction Example

```beancount
2024-05-30 * "Restaurant XYZ" "Dinner with clients" #business #meal ^trip-chicago
  receipt: "receipt-2024-05-30.pdf"
  Expenses:Food:Restaurant:Business   185.50 USD
  Liabilities:CreditCard:Amex       -185.50 USD
```

### Postings

Postings are indented lines within transactions.

#### Basic Posting Format

```beancount
  Account:Name   Amount COMMODITY
```

#### Posting Examples

```beancount
2024-05-30 * "Example transaction with various postings"
  ; Simple posting
  Account:Name    123.45 USD
  
  ; Posting with cost (buying stocks)
  Account:Name       10 AAPL {502.12 USD}
  
  ; Posting with price (currency conversion)
  Account:Name  1000.00 USD @ 0.85 EUR
  
  ; Posting with cost AND price
  Account:Name       10 AAPL {502.12 USD} @ 520.00 USD
  
  ; Posting with cost date (track purchase date)
  Account:Name       10 AAPL {502.12 USD, 2024-05-12}
  
  ; Posting with flag
  ! Account:Name   123.45 USD
  
  ; Posting with inline comment
  Account:Name    123.45 USD  ; This is a comment
```

**Important Rules**:
- At most ONE posting can omit the amount (auto-calculated)
- All amounts must balance (sum to zero)
- Indentation matters (typically 2 or 4 spaces)

#### Posting with Metadata

```beancount
2024-05-30 * "Grocery Store" "Weekly groceries"
  trip: "Spain-2024"
  Expenses:Food:Groceries    125.50 USD
    category: "essential"
    tax-deductible: FALSE
  Assets:Bank:Checking      -125.50 USD
```

#### Cost vs Price

**Cost** (`{}`): Acquisition price (what you paid)
```beancount
Assets:Investments   10 AAPL {150.00 USD}  ; Bought at $150 each
Assets:Bank         -1500.00 USD
```

**Price** (`@`): Conversion rate (for reporting)
```beancount
Assets:Cash:EUR     100.00 EUR @ 1.18 USD  ; €100 worth $118
Assets:Cash:USD    -118.00 USD
```

**Both** (for securities with gain/loss tracking):
```beancount
Assets:Investments  -10 AAPL {150.00 USD} @ 175.00 USD  ; Sold at $175, bought at $150
Assets:Bank         1750.00 USD
Income:Capital-Gains  -250.00 USD  ; Gain calculated automatically
```

### Balance Assertions

Verify account balance at specific date:

```beancount
2024-05-31 balance Assets:Checking 1500.00 USD
```

**If balance doesn't match**: Beancount reports an error with difference amount.

**Best Practice**: Add balance assertions after every bank statement for reconciliation.

**Multiple Currencies**:
```beancount
2024-05-31 balance Assets:Checking 1500.00 USD
2024-05-31 balance Assets:Checking  500.00 EUR
```

**Commodity Holdings**:
```beancount
2024-05-31 balance Assets:Investments:Brokerage 100 AAPL
```

### Pad Directive

Automatically insert missing transaction to balance accounts:

```beancount
2024-01-01 open Assets:Checking
2024-01-01 open Equity:Opening-Balances

2024-01-01 pad Assets:Checking Equity:Opening-Balances
2024-01-02 balance Assets:Checking 1000.00 USD
```

**Effect**: Creates automatic transaction on 2024-01-01:
```beancount
2024-01-01 * "Padding for Assets:Checking"
  Assets:Checking            1000.00 USD
  Equity:Opening-Balances   -1000.00 USD
```

**Use Case**: Setting opening balances when starting to track accounts.

### Event Directive

Track life events for filtering/reporting:

```beancount
2024-01-01 event "location" "New York, USA"
2024-03-15 event "employer" "BigCorp Inc."
2024-06-01 event "address" "123 Main Street, Apt 4B"
```

**Use Cases**:
- Track location changes (for tax purposes)
- Document employment changes
- Record address history
- Any custom life event tracking

### Query Directive

Save named queries in the ledger:

```beancount
2024-01-01 query "monthly-expenses" "
  SELECT
    year, month, account,
    sum(position) AS total
  WHERE
    account ~ 'Expenses:'
  GROUP BY year, month, account
  ORDER BY year, month, total DESC
"
```

**Fava Integration**: Saved queries appear in sidebar for quick access.

### Custom Directive

User-defined directives for plugins or custom processing:

```beancount
2024-01-01 custom "budget" Expenses:Food 500.00 USD

2024-01-01 custom "fava-option" "default-file" "main.beancount"
```

**Common Uses**:
- Budget directives (Fava budgets)
- Fava options
- Plugin configuration
- Custom metadata

### Options

Configure ledger behavior (place at beginning of file):

```beancount
option "title" "My Personal Finances"
option "operating_currency" "USD"
option "operating_currency" "EUR"
```

**Common Options**:

- `title`: Ledger title
- `operating_currency`: Main currencies (can specify multiple)
- `account_previous_balances`: "Equity:Opening-Balances"
- `account_previous_earnings`: "Equity:Earnings:Previous"
- `account_previous_conversions`: "Equity:Conversions:Previous"
- `account_current_earnings`: "Income:Current"
- `account_current_conversions`: "Equity:Conversions:Current"
- `account_rounding`: "Equity:Rounding"

**Full Reference**: http://furius.ca/beancount/doc/options

### Plugin Directive

Enable Beancount plugins:

```beancount
plugin "beancount.plugins.auto_accounts"
plugin "beancount.plugins.check_commodity"
plugin "fava_dashboards"
```

**Common Plugins**:
- `auto_accounts`: Auto-open accounts when first used
- `check_commodity`: Verify commodity declarations
- `implicit_prices`: Infer prices from transactions

### Include Directive

Split ledger across multiple files:

```beancount
include "accounts.beancount"
include "2024/january.beancount"
include "2024/february.beancount"
```

**Best Practice**: Organize by year, month, or category for maintainability.

### pushtag and poptag

Apply tags to a range of entries:

```beancount
pushtag #trip-to-peru

2024-06-01 * "Flight to Lima"
  Expenses:Travel:Flights   450.00 USD
  Liabilities:CreditCard   -450.00 USD

2024-06-15 * "Hotel in Cusco"
  Expenses:Travel:Lodging   300.00 USD
  Liabilities:CreditCard   -300.00 USD

poptag #trip-to-peru
```

**Effect**: All entries between `pushtag` and `poptag` get `#trip-to-peru` tag.

**Nesting**: Can be nested for multiple tags.

### Comments

```beancount
; This is a comment (semicolon)

* This is also ignored (any non-directive line)

2024-01-01 * "Transaction"  ; Inline comment
  Assets:Checking  100 USD  ; Another inline comment
```

**Comments can appear**:
- On their own lines (starting with `;`)
- After directives (after `;`)
- Any line not starting with valid date/directive is ignored

## Common Transaction Patterns

### Simple Expense

```beancount
2024-01-15 * "Grocery Store" "Weekly groceries"
  Expenses:Food:Groceries    125.50 USD
  Assets:Bank:Checking      -125.50 USD
```

### Income (Salary with Deductions)

```beancount
2024-01-31 * "BigCorp" "January salary"
  Income:Salary:BigCorp     -3500.00 USD
  Expenses:Taxes:Income        525.00 USD
  Expenses:Taxes:Social        210.00 USD
  Expenses:Benefits:Health     150.00 USD
  Assets:Bank:Checking        2615.00 USD
```

### Credit Card Purchase and Payment

```beancount
; Purchase
2024-01-15 * "Amazon" "Office supplies"
  Expenses:Office:Supplies      89.99 USD
  Liabilities:CreditCard:Visa  -89.99 USD

; Payment
2024-02-01 * "Credit card payment"
  Liabilities:CreditCard:Visa  500.00 USD
  Assets:Bank:Checking        -500.00 USD
```

### Investment Purchase

```beancount
2024-01-15 * "Buy AAPL shares"
  Assets:Investments:Brokerage    10 AAPL {175.50 USD}
  Assets:Bank:Checking         -1755.00 USD
```

### Investment Sale

```beancount
2024-06-15 * "Sell AAPL shares"
  Assets:Investments:Brokerage   -10 AAPL {175.50 USD} @ 185.00 USD
  Assets:Bank:Checking          1850.00 USD
  Income:Capital-Gains           -95.00 USD  ; Gain auto-calculated
```

### Currency Exchange

```beancount
2024-01-15 * "Exchange USD to EUR"
  Assets:Cash:EUR     100.00 EUR @ 1.18 USD
  Assets:Cash:USD    -118.00 USD
```

### Split Transaction

```beancount
2024-01-15 * "Costco" "Monthly shopping"
  Expenses:Food:Groceries        120.00 USD
  Expenses:Household              45.00 USD
  Expenses:Personal:Clothing      35.00 USD
  Assets:Bank:Checking          -200.00 USD
```

### Transfer Between Accounts

```beancount
2024-01-15 * "Transfer to savings"
  Assets:Bank:Savings     500.00 USD
  Assets:Bank:Checking   -500.00 USD
```

### Dividend Income

```beancount
2024-03-15 * "AAPL" "Quarterly dividend"
  Assets:Investments:Brokerage    23.50 USD
  Income:Dividends:AAPL          -23.50 USD
```

### Loan Payment (Principal + Interest)

```beancount
2024-01-01 * "Mortgage payment"
  Liabilities:Mortgage:Principal   800.00 USD
  Expenses:Interest:Mortgage       450.00 USD
  Assets:Bank:Checking          -1250.00 USD
```

### Reimbursable Expense

```beancount
2024-01-15 * "Conference hotel" "Reimbursable" #business
  Assets:Receivables:Employer   350.00 USD
  Liabilities:CreditCard       -350.00 USD

; When reimbursed
2024-02-01 * "Employer" "Expense reimbursement"
  Assets:Bank:Checking          350.00 USD
  Assets:Receivables:Employer  -350.00 USD
```

### Bill Splitting

```beancount
2024-01-15 * "Restaurant" "Dinner with Alice - split bill"
  Expenses:Food:Restaurant       60.00 USD
  Assets:Receivables:Alice       30.00 USD
  Assets:Cash                   -90.00 USD

; When Alice pays back
2024-01-20 * "Alice" "Payback for dinner"
  Assets:Cash                    30.00 USD
  Assets:Receivables:Alice      -30.00 USD
```

## Best Practices

### File Organization

**Option 1 - Single File**:
```
finances.beancount
```

**Option 2 - By Year**:
```
main.beancount
accounts.beancount
2023.beancount
2024.beancount
```

**Option 3 - By Month**:
```
main.beancount
accounts.beancount
2024/
  2024-01.beancount
  2024-02.beancount
  ...
```

**Option 4 - By Account**:
```
main.beancount
accounts/
  checking.beancount
  savings.beancount
  credit-cards.beancount
  investments.beancount
```

### Transaction Entry Tips

1. **Always include payee and narration** for searchability
2. **Use tags for cross-cutting categories** (#business, #vacation, #tax-deductible)
3. **Link related transactions** (^invoice-123)
4. **Add balance assertions regularly** (at least monthly)
5. **Attach documents for important transactions**
6. **Use consistent account naming**
7. **Add metadata for special tracking needs**

### Account Structure Tips

1. **Plan hierarchy before starting**
2. **Keep depth reasonable** (3-4 levels usually sufficient)
3. **Use parallel structures** (e.g., all food under Expenses:Food:)
4. **Be consistent with naming conventions**
5. **Document account purposes** (with notes or comments)

### Date Management

1. **Use transaction date, not entry date**
2. **Be consistent with pending vs. cleared**
3. **Post transactions promptly** (reduces backlog)
4. **Use pending flag (!) for uncleared items**
5. **Reconcile regularly with balance assertions**

## Validation and Errors

Run `bean-check` to validate your ledger:

```bash
bean-check finances.beancount
```

**Common Errors**:
- Transaction doesn't balance
- Account not opened before use
- Balance assertion failure
- Invalid syntax
- Duplicate commodity declarations

**Error Messages Include**:
- File and line number
- Error type and description
- Suggested fixes (where applicable)

## Advanced Features

### Price Interpolation

Beancount interpolates prices between known prices:

```beancount
2024-01-01 price AAPL 150.00 USD
2024-01-31 price AAPL 160.00 USD

; Prices for dates in between are interpolated
```

### Automatic Price Inference

Prices can be inferred from transactions:

```beancount
2024-01-15 * "Buy AAPL"
  Assets:Investments    10 AAPL {155.00 USD}
  Assets:Checking    -1550.00 USD

; Beancount infers: 2024-01-15 price AAPL 155.00 USD
```

Enable with:
```beancount
plugin "beancount.plugins.implicit_prices"
```

### Lot Selection

When selling, Beancount uses FIFO (first-in, first-out) by default.

Specify lot:
```beancount
; Sell specific lot
Assets:Investments  -10 AAPL {150.00 USD, 2024-01-01}  @ 175.00 USD
```

### Precision and Rounding

Beancount auto-detects precision from your entries.

Override with commodity metadata:
```beancount
2020-01-01 commodity BTC
  precision: 8
```

Rounding differences go to:
```beancount
option "account_rounding" "Equity:Rounding"
```

## Integration with Fava

Most Beancount features integrate seamlessly with Fava:
- All directives displayed appropriately
- Balance assertions highlighted
- Documents viewable inline
- Saved queries accessible in sidebar
- Tags/links filterable
- Metadata displayed in detail views

See `fava_features.md` for complete Fava reference.
