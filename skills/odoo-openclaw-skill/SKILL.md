---
name: odoo
description: "Query Odoo data including salesperson performance, customer analytics, orders, invoices, CRM, accounting, VAT, inventory, and AR/AP. Generates WhatsApp cards, PDFs, Excel. Use when user explicitly mentions Odoo or asks for Odoo data."
---

# Odoo Financial Intelligence

**Read-only, Evidence-First, Ledger-Based Reports**

## Quick Reference: Common Odoo Models

| Model | What It Contains | Use For |
|-------|------------------|---------|
| `res.users` | Users/Salespeople | Find salesperson by name, get user_id |
| `sale.order` | Sales Orders | Revenue by salesperson, order counts, status |
| `account.move` | Invoices/Journal Entries | Invoice tracking, payments, P&L data |
| `res.partner` | Contacts/Customers | Customer info, top customers by revenue |
| `product.product` | Products | Product sales, inventory |
| `account.account` | Chart of Accounts | Financial reporting, balance sheet |
| `account.move.line` | Journal Lines | Detailed ledger entries |

## Security & Credentials

### Required Environment Variables

This skill requires Odoo connection credentials stored in `assets/autonomous-cfo/.env`:

| Variable | Description | Secret |
|----------|-------------|--------|
| `ODOO_URL` | Odoo instance URL (e.g., `https://your-odoo.com`) | No |
| `ODOO_DB` | Odoo database name | No |
| `ODOO_USER` | Odoo username/email | No |
| `ODOO_PASSWORD` | Odoo password or API key | **Yes** |

**Setup:**
```bash
cd skills/odoo/assets/autonomous-cfo
cp .env.example .env
# Edit .env with your actual credentials
nano .env
```

### Model Invocation Policy

**Model invocation is DISABLED** per `skill.json` policy. This skill handles sensitive financial data and external Odoo connections — it must be explicitly invoked by the user.

**Data Handling:** All queries are read-only. No data is modified or exfiltrated.

### Data Handling

- **Read-only:** All mutating methods (`create`, `write`, `unlink`, etc.) are blocked at the client level
- **No exfiltration:** Reports are generated locally in `assets/autonomous-cfo/output/`
- **Network endpoints:** Only connects to the Odoo URL specified in `.env`
- **Output formats:** PDF, Excel, and WhatsApp image cards (local files only)

### Installation

The skill requires a Python virtual environment with specific packages:

```bash
cd skills/odoo/assets/autonomous-cfo
./install.sh
```

Or manually:
```bash
cd skills/odoo/assets/autonomous-cfo
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

**Dependencies:** `requests`, `matplotlib`, `pillow`, `fpdf2`, `openpyxl`

## Critical Rules

1. **NEVER assume** - Always ask clarifying questions before generating reports
2. **Multi-company check** - If multiple companies exist, ASK which one to use
3. **Ledger-based** - Use Chart of Accounts and journal entries (account.move.line), not just invoice summaries
4. **Verify periods** - Confirm date ranges with user before running
5. **No silent defaults** - Every assumption must be confirmed

## Before Any Report, Ask:

1. "Which company should I use?" (if multiple exist)
2. "What period? (from/to dates)"
3. "Which accounts or account types to include?"
4. "Any specific breakdown needed?" (by account, by partner, by journal, etc.)
5. "Output format preference?" (PDF, WhatsApp cards, or both)

## Entrypoint

Uses the venv with fpdf2, matplotlib, pillow for proper PDF/chart generation:

```bash
./skills/odoo/assets/autonomous-cfo/venv/bin/python ./skills/odoo/assets/autonomous-cfo/src/tools/cfo_cli.py <command>
```

Or from the skill directory:
```bash
cd skills/odoo/assets/autonomous-cfo && ./venv/bin/python src/tools/cfo_cli.py <command>
```

## Chart of Accounts Based Reporting

Reports should be built from:
- `account.account` - Chart of Accounts structure (code, name, type, internal_group)
- `account.move.line` - Journal entry lines (debit, credit, account_id, date)
- `account.journal` - Source journals (type: sale, purchase, cash, bank, general)

### Account Internal Groups
- **ASSET** - Assets (current, non-current, cash, receivables)
- **LIABILITY** - Liabilities (payables, taxes, accrued)
- **EQUITY** - Owner's equity
- **INCOME** - Revenue accounts
- **EXPENSE** - Cost and expense accounts
- **OFF_BALANCE** - Off-balance sheet accounts

### Common Account Types
- `asset_cash` - Bank and cash accounts
- `asset_receivable` - Accounts receivable
- `asset_current` - Current assets
- `liability_payable` - Accounts payable
- `income` - Revenue
- `expense` - Expenses

### Special Equity Types (Odoo-Specific)
- `equity` - Standard equity accounts (share capital, retained earnings)
- `equity_unaffected` - **Suspense account** for undistributed profits/losses (e.g., 999999)

**CRITICAL for Balance Sheet:**
Odoo's `equity_unaffected` is a SUSPENSE account. Do NOT use its ledger balance directly.

**Correct Equity Calculation:**
1. **Equity Proper** (type: `equity`) - Use ledger balance (credit - debit)
2. **Retained Earnings** (prior years) - Ledger balance from `equity_unaffected`
3. **Current Year Earnings** - Compute real-time: Income - Expenses

```
Total Equity = Equity Proper + Retained Earnings + Current Year Earnings
```

Where Current Year Earnings = Σ(income credit-debit) - Σ(expense debit-credit)

**Why this matters:** Odoo computes Current Year Earnings in real-time on the Balance Sheet. Using only the `equity_unaffected` ledger balance will cause the balance sheet to NOT balance.

## Automatic Reporting Standard Detection

The skill automatically detects the company's accounting standard based on country/jurisdiction and formats reports accordingly.

**Supported Standards:**
| Standard | Jurisdiction | Notes |
|----------|--------------|-------|
| IFRS | International | Default for most countries |
| US GAAP | United States | SEC registrants |
| Ind-AS | India | Indian GAAP converged with IFRS |
| UK GAAP | United Kingdom | FRS 102 |
| SOCPA | Saudi Arabia | IFRS adopted |
| EU IFRS | European Union | IAS Regulation |
| CAS | China | Chinese Accounting Standards |
| JGAAP | Japan | Japanese GAAP |
| ASPE | Canada | Private enterprises |
| AASB | Australia | Australian standards |

**Detection Logic:**
1. Query company's country from `res.company`
2. Map country code to reporting standard
3. Apply standard-specific formatting:
   - Number format (1,234.56 vs 1.234,56)
   - Negative display ((123) vs -123)
   - Date format (DD/MM/YYYY vs MM/DD/YYYY)
   - Statement titles (Balance Sheet vs Statement of Financial Position)
   - Cash flow method (indirect vs direct)

**Override:**
```python
# Force a specific standard
reporter.generate(..., standard="US_GAAP")
```

## Commands

### Sales & CRM Queries

```bash
# Salesperson performance - use direct RPC for flexibility
./venv/bin/python -c "
from src.visualizers.whatsapp_cards import WhatsAppCardGenerator
# Query sale.order by user_id, aggregate by month/status
# Generate cards with generate_kpi_card() and generate_comparison_card()
"

# Example RPC query for salesperson:
# - sale.order (user_id, amount_total, state, date_order)
# - account.move (invoice_user_id, amount_total, payment_state)
# - res.users (salesperson info)
# - res.partner (customer info)
```

### Pre-built Reports

```bash
# Financial Health - cash flow, liquidity, burn rate, runway
cfo_cli.py health --from YYYY-MM-DD --to YYYY-MM-DD --company-id ID

# Revenue Analytics - MoM trends, top customers
cfo_cli.py revenue --from YYYY-MM-DD --to YYYY-MM-DD --company-id ID

# AR/AP Aging - overdue buckets
cfo_cli.py aging --as-of YYYY-MM-DD --company-id ID

# Expense Breakdown - by vendor/category
cfo_cli.py expenses --from YYYY-MM-DD --to YYYY-MM-DD --company-id ID

# Executive Summary - one-page CFO snapshot
cfo_cli.py executive --from YYYY-MM-DD --to YYYY-MM-DD --company-id ID
```

### Direct RPC Queries (Advanced)

For sales/CRM data not covered by pre-built commands, use direct RPC:

```python
# Query sales orders by salesperson
orders = jsonrpc('sale.order', 'search_read',
    [[('user_id', '=', SALESPERSON_ID)]],
    {'fields': ['name', 'partner_id', 'amount_total', 'state', 'date_order']})

# Query invoices by salesperson
invoices = jsonrpc('account.move', 'search_read',
    [[('invoice_user_id', '=', SALESPERSON_ID), ('move_type', '=', 'out_invoice')]],
    {'fields': ['name', 'partner_id', 'amount_total', 'payment_state']})

# Find salesperson by name
users = jsonrpc('res.users', 'search_read',
    [[('name', 'ilike', 'name_here')]],
    {'fields': ['id', 'name', 'login']})
```

### Ad-hoc Reports

```bash
# Custom comparison
cfo_cli.py adhoc --from YYYY-MM-DD --to YYYY-MM-DD --metric-a "revenue" --metric-b "expenses"

# Examples:
cfo_cli.py adhoc --metric-a "cash in" --metric-b "cash out"
cfo_cli.py adhoc --metric-a "direct expenses" --metric-b "indirect expenses"
```

### Output Formats

```bash
--output whatsapp   # Dark theme 1080x1080 PNG cards
--output pdf        # Light theme A4 PDF
--output excel      # Excel workbook (.xlsx)
--output both       # PDF + WhatsApp cards
--output all        # PDF + Excel + WhatsApp cards
```

## Automatic Visualizations

**Reports always include appropriate visualizations by default:**

| Report | Auto-Included Charts |
|--------|---------------------|
| Financial Health | Cash position, burn rate trend, runway |
| Revenue | MoM trend, top customers, growth KPI |
| AR/AP Aging | Aging buckets pie, overdue highlights |
| Expenses | Category breakdown, trend, top vendors |
| Executive | All KPI cards, summary charts |
| Balance Sheet | Asset/liability composition |
| P&L | Revenue vs expense, margin trend |
| Cash Flow | Operating breakdown, cash trend |

**Rule:** If visualization makes the report clearer, include it automatically. Never ask "do you want charts?" — just add them.

## Interactive Param Collection

If required params are missing, the skill will ask:

1. **Company:** "Which company?" (list available options)
2. **Period:** "What period? (e.g., 'last month', 'Q4 2024', custom dates)"
3. **Accounts:** "Which accounts or groups?" (e.g., 'all income', 'bank accounts only')
4. **Breakdown:** "Group by? (Month, Customer, Category, Account)"
5. **Output:** "Output format? (WhatsApp cards, PDF, Both)"

## How to Use in Chat

Just ask naturally:

**Sales & CRM:**
- "How is [name] salesperson performance?"
- "Show me top customers for [salesperson]"
- "Compare sales team performance"
- "Which salesperson has the most orders?"

**Financial Reports:**
- "Give me a financial health report for last quarter"
- "Show revenue vs expenses for the past 6 months"
- "What's my AR aging?"
- "Generate an executive summary for this month"
- "Show me profit & loss statement based on chart of accounts"

**General Queries:**
- "How many orders did we get this month?"
- "Who are the top 10 customers?"
- "Show invoice status for [customer name]"

The skill will:
1. Check for multiple companies and ask which one
2. Parse your request
3. Ask for any missing info
4. Fetch data from Odoo using ledger entries or direct RPC
5. Generate charts + WhatsApp cards
6. Deliver via WhatsApp cards and/or PDF

## Hard Rules

1. Odoo RPC output is source of truth
2. Strict read-only (no create/write/unlink)
3. No proactive actions unless requested
4. Every number includes methodology note
5. Always verify with user before assuming
6. **Always include visualizations** - If a report benefits from charts/graphs, include them automatically without asking. Reports should be visually complete.

## Diagnostics

```bash
python3 ./skills/odoo/assets/autonomous-cfo/src/tools/cfo_cli.py doctor
```

## Report Themes

- **WhatsApp Cards:** "Midnight Ledger" — Navy-black (#0a0e1a), copper glow (#cd7f32)
- **PDF Reports:** Clean white, copper accents, professional layout
