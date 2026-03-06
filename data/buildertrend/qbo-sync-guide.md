# Buildertrend ↔ QuickBooks Online Sync Guide
> Comprehensive deep dive on BT ↔ QBO integration
> Field mapping, sync rules, what pushes where, and best practices
> Created: February 19, 2026

---

## Table of Contents
1. [Integration Overview](#1-integration-overview)
2. [Data Flow Summary](#2-data-flow-summary)
3. [Initial Setup & Connection](#3-initial-setup--connection)
4. [Entity Linking (Required First)](#4-entity-linking)
5. [Pushing Bills to QBO](#5-pushing-bills-to-qbo)
6. [Pushing Invoices to QBO](#6-pushing-invoices-to-qbo)
7. [Pushing Deposit Payments to QBO](#7-pushing-deposit-payments-to-qbo)
8. [Pushing Credit Memos to QBO](#8-pushing-credit-memos-to-qbo)
9. [Pushing Time Clock to QBO](#9-pushing-time-clock-to-qbo)
10. [Receiving Estimates from QBO](#10-receiving-estimates-from-qbo)
11. [Syncing Invoice Payments](#11-syncing-invoice-payments)
12. [Syncing Bill Payments](#12-syncing-bill-payments)
13. [Syncing QB Expenses to Budget](#13-syncing-qb-expenses-to-budget)
14. [Bank Feed Matching](#14-bank-feed-matching)
15. [Online Payments Reconciliation](#15-online-payments-reconciliation)
16. [Tax Integration (US)](#16-tax-integration-us)
17. [International Tax Handling](#17-international-tax-handling)
18. [Payroll Integration](#18-payroll-integration)
19. [Default Accounting Settings](#19-default-accounting-settings)
20. [Troubleshooting & Best Practices](#20-troubleshooting--best-practices)

---

## 1. Integration Overview

Buildertrend's integration with QuickBooks Online enables seamless transfer of financial data in BOTH directions, eliminating duplicate entry and reducing errors. The integration supports:

**From BT → QBO:**
- Jobs → Customers / Sub Customers / Projects
- Subs/Vendors → Vendors
- Bills
- Invoices (including Progress Invoices)
- Deposit Payments
- Credit Memos
- Time Clock entries

**From QBO → BT:**
- Estimates (import)
- Bill Payments (auto-sync)
- Invoice Payments (auto-sync)
- Expenses → Budget Actuals (configurable)

---

## 2. Data Flow Summary

| BT Entity | QBO Entity | Direction | Trigger |
|---|---|---|---|
| Job + Client | Customer / Sub Customer / Project | BT → QBO | Manual link or auto on creation |
| Sub/Vendor | Vendor | BT → QBO | Manual link or auto on creation |
| Bill | Bill | BT → QBO | Checkbox on save or manual push |
| Invoice | Invoice | BT → QBO | Checkbox on send or manual push |
| Progress Invoice | Invoice | BT → QBO | Checkbox on send or manual push |
| Deposit Payment | Payment (Undeposited Funds) | BT → QBO | Manual push after payment |
| Credit Memo | Credit Memo | BT → QBO | Checkbox on release or manual push |
| Time Clock Shift | Time Activity / Weekly Timesheet | BT → QBO | Auto on approval or manual push |
| QBO Estimate | BT Estimate | QBO → BT | Manual import via wizard |
| QBO Invoice Payment | BT Invoice status | QBO → BT | Auto-sync |
| QBO Bill Payment | BT Bill status | QBO → BT | Auto-sync |
| QBO Expense | BT Budget Actuals | QBO → BT | Auto if enabled; manual sync available |

---

## 3. Initial Setup & Connection

### Steps:
1. **Company Settings → Accounting → Get started with QuickBooks**
2. Review benefits → **Begin Setup**
3. Authorize connection to your QBO company
4. Configure **Default Accounting Settings** (see Section 19)

### Key Settings to Configure:
- Job linking preferences
- Invoice options (flat fee item, AR account, auto-push)
- Bill/PO options (AP account, auto-link subs, auto-push)
- Budget options (include QBO costs, Cash vs Accrual)
- Time Clock options (auto-push on approval)
- Tax options

---

## 4. Entity Linking

### ⚠️ CRITICAL: Link entities BEFORE pushing financial data

### Cost Codes → QBO Products & Services
1. Company Settings → **Cost Codes** → **Import → QuickBooks**
2. Use multi-select to choose QBO Items
3. For each: **Create New Cost Code** or **Select Existing BT Cost Code**
4. Auto-suggestion: exact name matches auto-populate
5. All financial data routes through these mappings

### Jobs → QBO Customers/Projects
1. Job Details → **Accounting tab** → **Link job**
2. Select QBO Customer, Sub Customer, or Project from dropdown
3. Or enable auto-link during job creation in settings
4. ⚠️ Client must be added to job for Customer record creation

**Customer Fields Mapped:**
| BT Field | QBO Field |
|---|---|
| Client Name | Display Name |
| Company | Company |
| Phone | Phone |
| Email | Email |
| Address | Billing Address |
| Job Address | Shipping Address |

### Subs/Vendors → QBO Vendors
1. Sub/Vendor card → **Accounting tab** → **Link sub**
2. Select QBO Vendor from dropdown
3. Or enable auto-link during creation in settings

**Vendor Fields Mapped:**
| BT Field | QBO Field |
|---|---|
| Company Name | Display Name |
| Contact Name | Name |
| Phone | Phone |
| Email | Email |
| Address | Address |

---

## 5. Pushing Bills to QBO

### Method 1: Auto-Push on Save
1. Create Bill in BT
2. Check **Send to QuickBooks** in QB section
3. **Save** → Bill immediately pushes to QBO

### Method 2: Manual Push Later
1. Create and save Bill WITHOUT checking Send to QuickBooks
2. Later: Select bill from Bills dashboard → **Send to QuickBooks**

### Default Setting
- Company Settings → Accounting → "Default Send to QuickBooks" for new bills

### Editing Bills Already in QBO
- Enable: "Allow bill edits to sync with QuickBooks" in Accounting settings
- Changes in BT → auto-sync to QBO on save
- ⚠️ If QBO bill has newer changes, BT will NOT overwrite
- ⚠️ Fully paid bills cannot be edited unless payment removed in QBO

### Bill Field Mapping:
| BT Bill Field | QBO Bill Field |
|---|---|
| Pay To (Sub/Vendor) | Vendor |
| Bill # | Ref No. |
| Date Billed | Bill Date |
| Due Date | Due Date |
| Payment Terms | Terms |
| Line Item Cost Code | Product/Service (via linked code) |
| Line Item Amount | Amount |
| Line Item Description | Description |
| Line Item Quantity | Qty |
| Line Item Rate | Rate |

### PO Suffix Feature
If enabled (Company Settings → Bills → "Add PO suffix to bill number"):
- Bills pushed to QBO include PO number suffix
- Helps identify which BT Purchase Order the bill relates to
- Streamlines reconciliation across platforms

---

## 6. Pushing Invoices to QBO

### Method 1: Auto-Push on Send
1. Create Invoice in BT
2. Check **Invoice to QuickBooks on Send**
3. **Send** to client → Invoice pushes to QBO

### Method 2: Manual Push Later
1. Create, save, and send invoice WITHOUT checking QB option
2. Later: open sent invoice → **Create Invoice** from QB Status section

### Default Setting
- Company Settings → Accounting → "Default Invoice to QuickBooks on Send"

### Invoice Field Mapping:
| BT Invoice Field | QBO Invoice Field |
|---|---|
| Client (linked Customer) | Customer |
| Invoice # | Invoice No. |
| Due Date | Due Date |
| Payment Terms | Terms |
| Line Item Cost Code | Product/Service (via linked code) |
| Line Item Amount | Amount |
| Line Item Description | Description |
| Line Item Quantity | Qty |
| Tax Rate | Tax Rate |

### Adding QBO Costs to BT Invoice
1. Open Invoice → **Add From** → **QuickBooks Costs**
2. Select applicable QBO costs with checkboxes → **Apply**
3. Once invoiced, cost removed from future invoice options (prevents double-invoicing)

### Progress Invoices
- Same push logic as standard invoices
- Line items pulled from Estimate Schedule of Values

---

## 7. Pushing Deposit Payments to QBO

### Prerequisites:
- Deposit must be **PAID** first (BT Payments or offline payment)

### Steps:
1. Create deposit in BT → request payment from client
2. Once paid → open deposit → **Send to QuickBooks**
3. Payment goes to **Undeposited Funds** account in QBO
4. In QBO: **Create Bank Deposit** → match to bank transaction

### ⚠️ CRITICAL: Turn OFF auto-apply credits in QBO
This ensures deposits can be properly applied in BT.

### Workflow for Applying Deposits to Invoices:
1. Send deposit payment to QBO (goes to Undeposited Funds)
2. Match deposit to bank payment (create Bank Deposit)
3. Create and send BT invoice(s) to QBO (don't send to client yet)
4. Apply BT deposit to applicable invoice(s)
5. Send updated invoice(s) to client
6. QBO invoices auto-paid using the deposit payment

### For Liability Posting (Advanced):
- Create Journal Entry: debit Unapplied Cash Income → credit Client Deposit Account
- 🛑 **Only under guidance of qualified accountant** (tax implications)
- After applying deposit: second Journal Entry to reverse

---

## 8. Pushing Credit Memos to QBO

### Jobs WITH Active Client:
1. Create credit memo in BT
2. Check **Send to QuickBooks on Release**
3. Send to client → pushes to QBO
4. Or push later: open → **Create Credit Memo** from QB Status

### Jobs WITHOUT Active Client:
1. Create and save credit memo
2. Open → ellipsis → **Save to Accounting**

### Default Setting:
- "Default Send to QuickBooks on Release" in Accounting settings

### Credit Memo Fields Synced:
- ID#, Unit Amount, Quantity, Cost Code (→ linked accounting code), Description, Amount

### Key Notes:
- Applied Credit Memos lower amount owed (NOT Job Running Total)
- Only internal users can apply memos to invoices
- Credits applied in QBO create "Applied Payment" in BT (not a BT Credit Memo)

---

## 9. Pushing Time Clock to QBO

### Auto-Push (Recommended):
1. Enable: Accounting Settings → "Create a new QuickBooks time activity from a Time Clock shift when approved"
2. Approve time entries → auto-push to QBO

### Manual Push:
1. Approve time entry
2. Open shift → **Send to QuickBooks** from QB Status section

### Mass Actions:
- Multi-select shifts → Approve → Send to QuickBooks (bulk)
- Fastest for payroll processing

### Time Clock Field Mapping:
| BT Time Clock Field | QBO Field |
|---|---|
| Internal User (linked Employee) | Employee |
| Job (linked Customer) | Customer/Job |
| Cost Code (linked P&S) | Service |
| Clock In/Out Date | Date |
| Hours | Duration/Hours |
| Notes | Description |

### Important Notes:
- Pushes to **Time Entry** or **Weekly Timesheets** based on QBO version/payroll subscription
- ⚠️ **Overtime hours NOT automatically sent** — must be manually adjusted in QBO
- Default hourly rate assumed when Payroll Items not mapped
- Multiple Payroll Items (overtime, etc.) require manual Weekly Timesheet edits

---

## 10. Receiving Estimates from QBO

### Import Steps:
1. Job → Financials → Estimate
2. Click **External Import** → **QuickBooks**
3. Select QBO estimate from dropdown → **Next**
4. Map QBO estimate fields to BT cost line fields
5. Map QBO Products & Services to BT Cost Codes
6. Confirm → **Next** → import complete

---

## 11. Syncing Invoice Payments

### How It Works:
- Payment applied to invoice in QBO → corresponding BT invoice marked as **Paid**
- Automatic sync (no manual action required)
- Details visible in Payment History and QB Status section

### Timeline:
- QBO: Near real-time sync
- QBD: Updates on next Web Connector run

---

## 12. Syncing Bill Payments

### How It Works:
- Payment made to bill in QBO → corresponding BT bill marked as **Paid**
- Automatic sync (no manual action required)
- QBO payments update automatically
- QBD payments update on next Web Connector run

---

## 13. Syncing QB Expenses to Budget

### Purpose:
Pull expenses created in QBO into BT's Job Costing Budget to reflect true actuals.

### Enabling:
**Company-wide (all new jobs):**
- Company Settings → Accounting → "Include costs entered in QuickBooks in the budget by default when linking jobs to QuickBooks"

**Per-job basis:**
- Job Details → Advanced Settings → "Include costs entered in QuickBooks in the budget"

### What Pulls In:
| QBO Expense Type | Pulls to BT as |
|---|---|
| Bill | QBO Cost |
| Expense | QBO Cost |
| Check | QBO Cost |
| Vendor Credit | QBO Cost |
| Credit Card Credit | QBO Cost |

### Fields Mapped:
| QBO Field | BT Field |
|---|---|
| Vendor | Pay To |
| Date | Date |
| Amount | Amount |
| Product/Service | Cost Code (via linked code) |
| Description | Description |
| Expense Type | Expense Type label |

### Manual Sync:
If expense hasn't appeared within 5 minutes, trigger manual sync from Job Costing Budget.

### Viewing QBO Expenses:
- Appear in **Actual Costs** column of Job Costing Budget
- Click on expense for detailed info
- 💡 Can add QBO costs to BT invoices (Add From → QuickBooks Costs)

---

## 14. Bank Feed Matching

### Purpose:
Match BT-originated bills/invoices to bank transactions in QBO, preventing duplicates and ensuring budget accuracy.

### Steps for Bills:
1. Create Bill in BT → Push to QBO
2. In QBO → **Bank transactions**
3. QBO suggests match for unpaid bill (same amount)
4. Click **Match** → creates Bill Payment
5. Both BT and QBO bills marked as Paid

### If No Auto-Match:
1. Navigate to bank transaction
2. Click **Match**
3. In "Find other matches" popup → use filters to locate bill
4. Select correct bill → Match

### Same Process for Invoices:
Substitute "Bill" with "Invoice" in steps above.

### 💡 Pro Tip:
Bank Feed matching is commonly used with **Cost Inbox** workflow:
1. Scan receipt into BT Cost Inbox
2. Create Bill from receipt
3. Push Bill to QBO
4. Match in QBO bank feed

---

## 15. Online Payments Reconciliation

### Setup:
1. Job Details → Client tab → QB integration settings
2. Set **Deposit Online Payments** dropdown (account destination)
3. Set **Expense Account for Online Transaction Fees** dropdown

### Reconciling via Undeposited Funds:
1. Payment + Journal Entry (processing fee) → Undeposited Funds
2. QBO → Banking → **Make Deposits**
3. Check payment AND journal entry (match reference numbers)
4. Verify date and checking account → **Save and Close**
5. QBO suggests match → click **Match** → resolved

### Reconciling via Checking Account:
1. Direct Deposit Online Payments to checking account
2. Navigate to bank transaction in QBO
3. Verify suggested match → **Match**
4. Note: BT auto-creates deposit slip within **2 business days**

---

## 16. Tax Integration (US)

### QBO Setup:
1. QBO → Taxes → Sales Tax → **Use Automated Sales Tax**
2. Walk through agency/filing frequency setup

### BT Setup:
1. Company Settings → %Taxes → **Enable Tax**
2. ⚠️ Do NOT add tax rates manually — import from QBO

### Importing Tax Rate:
1. Job Details → Options tab → Default Tax Rate → **Import rate from Accounting**
2. Ensure BT job Zip Code matches QBO customer shipping address
3. If already linked: Job Details → Accounting → **Update Job in QuickBooks**
4. Imported rate available for future jobs

### How Taxes Flow:
1. Create Invoice in BT with tax rate
2. Push to QBO
3. Taxes assigned to appropriate agency liability report

### Variable Rates (by Product/Service):
1. Send invoice to QBO with default tax rate
2. Edit invoice in QBO → QBO updates tax per P&S code
3. Next BT sync → BT invoice updated to match

---

## 17. International Tax Handling

### Sales Tax (International):
- Set rates by Country/Province
- Group tax rates for combined sales/purchase codes
- Apply tax rate to each Product/Service code in QBO
- Choose **Inclusive** or **Exclusive** in BT Accounting Settings

**Inclusive:** Tax deducted from total, applied to liability
**Exclusive:** QBO adds tax on top

### Purchase Tax:
- Same pattern: rate per P&S code + Inclusive/Exclusive choice
- **Tax Inclusive:** Include in budget as COGS
- **Tax Exclusive:** QBO adds tax; budget shows COGS only

### PST as Cost of Goods Sold (Canadian):
- Create custom GST purchase tax rate:
  - 7% PST provinces: **4.6729%** adjusted GST rate
  - 6% PST provinces: **4.717%** adjusted GST rate
- Apply custom rate to P&S codes requiring PST
- BT bills: separate PST line item OR combined with material cost

---

## 18. Payroll Integration

### What Syncs:
- Employee data, Cost Code (P&S), Dates/times, Project/Job details

### What Does NOT Sync:
- QBO Payroll Items (pay types)
- These must be set up and assigned per employee in QBO

### Setup in QBO:
1. Payroll → Employees → **Edit payroll items**
2. Create Pay types (New Payroll Item)
3. Assign Pay Rate per employee (default hourly, custom types)

### Workflow:
1. Approve shifts in BT → push to QBO
2. Time entries appear on Weekly Timesheet
3. Payroll Item field blank (assumes default hourly rate)
4. Manually assign Payroll Items for overtime, etc.

---

## 19. Default Accounting Settings

Access: Company Settings → Accounting

### Job Linking Options:
| Setting | Description |
|---|---|
| Link jobs during creation | Auto-generates QBO Customer/Job |
| Preferred item type | Customer or Job structure |

### Invoice Options:
| Setting | Description |
|---|---|
| Flat fee item | QBO Item for non-itemized totals |
| Accounts receivable | QBO AR account for unpaid invoices |
| Auto-create on send | Push invoice on release |
| Auto-create credit memo | Push credit memo on release |

### Bill/PO Options:
| Setting | Description |
|---|---|
| Accounts payable | QBO AP account for bills |
| Auto-link subs/vendors | Create QBO vendor on creation |
| Allow bill sync | Enable bill push to QBO |
| Default send to QB | Auto-check Send to QB on bills |
| Default mark as billable | For Open Book (no BT Invoice) |

### Budget Options:
| Setting | Description |
|---|---|
| Include QBO costs by default | Auto-pull expenses on job link |
| Cash vs Accrual | Determines Actual Costs calculation |

### Time Clock Options:
| Setting | Description |
|---|---|
| Auto-push on approval | Create QBO time activity when approved |

### Tax Options:
| Setting | Description |
|---|---|
| Inclusive/Exclusive | How taxes display on invoices |
| Show client tax from QBO | Display QBO-applied taxes in BT |

---

## 20. Troubleshooting & Best Practices

### Best Practices:
1. **Link ALL entities BEFORE pushing financial data** — Cost Codes, Jobs, Vendors, Internal Users
2. **Use consistent naming** between BT and QBO for easy matching
3. **Enable auto-push defaults** to reduce forgotten syncs
4. **Match in bank feed** instead of creating new expenses (avoids duplicates)
5. **Turn OFF auto-apply credits** in QBO when using deposits
6. **Don't create expenses AND bills** for the same transaction (double-count)
7. **Use Cost Inbox → Bill → Push to QBO → Bank Feed Match** for field receipts
8. **Check QB Expenses are enabled** per job if actuals aren't showing in budget
9. **Review PO suffix on bills** for easy cross-reference
10. **Test with one bill/invoice first** before bulk-pushing

### Common Issues:

| Issue | Cause | Solution |
|---|---|---|
| Bill won't push | Cost Code not linked to QBO P&S | Link cost code in Company Settings |
| Invoice won't push | Job not linked to QBO Customer | Link job in Job Details → Accounting |
| QBO expense not in budget | "Include QBO costs" not enabled | Enable in Job Details → Advanced Settings |
| Tax rate wrong | Zip code mismatch | Match BT job zip to QBO customer shipping address |
| Bill edits not syncing | Setting not enabled | Enable "Allow bill edits to sync" in Accounting |
| Fully paid bill can't edit | QBO restriction | Remove payment in QBO first |
| Deposit not applying | Auto-apply credits ON in QBO | Turn OFF auto-apply credits in QBO |
| Time entries missing | Not approved | Approve shifts first, then push |
| Overtime not in QBO | BT doesn't push overtime | Manually enter overtime in QBO |
| Duplicate costs in budget | Both BT bill + QBO expense exist | Use one or the other; void duplicate |

### ⚠️ Warning: Journal Entries
- Journal Entries for reclassifying income/expenses are **advanced accounting practices**
- Always consult with a qualified accountant before creating
- May have tax implications
- Only needed for deposit liability posting or PST tracking scenarios

---

*End of QBO Sync Guide*
