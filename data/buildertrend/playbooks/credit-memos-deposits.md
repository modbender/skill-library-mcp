# Credit Memos & Deposits Management
> Deposit creation, payment tracking, credit memo workflow, applying to invoices

## Trigger
- the user says "create a deposit", "apply credit", "collect retainer"
- Client overpayment needs to be credited
- Deposit collected and needs to be recorded in BT

## Error Handling
| Issue | Resolution |
|---|---|
| Deposit not showing on invoice | Check deposit status — must be "Received" to apply |
| Credit memo amount exceeds invoice | Reduce credit amount or split across invoices |
| Cannot apply deposit | Verify deposit is on the correct job |
| QBO sync mismatch on credit | Check QBO sync settings, may need manual reconciliation |
| BT session expired | Stop, notify the user to re-login |

---

## Overview
Buildertrend's advanced invoicing features include:
- **Deposits** — Collect upfront client payments, apply to future invoices
- **Credit Memos** — Issue monetary credits back to clients

Both ensure the job running total accurately reflects all payments and adjustments.

---

## DEPOSITS

### Creating a Deposit
1. Select a **Job**
2. Navigate to **Invoices** (Financial dropdown)
3. Select **Deposits** tab
4. Click **+ Deposit**
5. Fill out deposit information:
   - Title / Description
   - Attachments (optional)
   - Amount: **Flat Fee** or **% of contract price**
6. Choose action:
   - **Save & Close** — Keep internal (don't send to client yet)
   - **Send deposit request** — Email to client immediately

### Tracking Deposit Status
View all deposit statuses from the **Deposits dashboard** within the Invoices section.

### Paying Deposits

#### With Buildertrend Payments
Client pays directly through Client Portal:
1. Client navigates to **Invoices** (Financial header)
2. Clicks **Deposit** tab
3. Selects the deposit
4. Clicks **Pay**

#### Without Buildertrend Payments
Record payment manually:
1. Open the deposit
2. Select **Record Offline Payment**
3. Enter payment details

### Applying Deposits to Invoices

**Method 1: From the Deposit**
1. Go to **Deposits dashboard**
2. Select **Apply to Invoice** next to paid deposit
3. In the Apply to existing Invoice modal:
   - Select an existing invoice
   - Specify dollar amount to apply

**Method 2: From the Invoice**
1. Go to **Invoice dashboard**
2. Open an existing invoice
3. Select **Apply deposit**
4. Specify dollar amount to apply

> When total deposit amount is applied, status changes to **Applied**.

### Converting Lead Proposal Payment to Deposit
When a Legacy Proposal on a Lead has a BT Payments payment:
1. Go to **Create a Job > Copy Lead Info to New Job** modal
2. Select the Proposal containing a payment
3. Choose **Copy Proposal Payment to Job**
4. Select **Copy to deposit**

---

## CREDIT MEMOS

### When to Use Credit Memos
- Issue a monetary credit back to the client
- Applicable within Owner Invoices only
- **Does NOT reduce Revised Client Price** (use negative Change Order for that)

**Example Scenario:**
- Builder's mistake extended project duration
- Builder gives client $500 off next invoice
- Builder creates $500 Credit Memo → applies to invoice
- Credit counts toward client's payments on record

### Creating a Credit Memo
1. Select a **Job**
2. Navigate to **Invoices** (Financial dropdown)
3. Select **Credit Memos** tab
4. Click **+ Credit Memo**
5. Enter information:
   - **Title** and **Description**
   - **ID#** (auto-assigns, or enter custom)
6. Choose cost format:
   - **Flat Fee** — Single amount, no Cost Codes
   - **Line Items** — Multiple items broken out by Cost Codes

### Applying Credit Memo to Invoice

> Credit Memos can be applied to **only one invoice at a time**. If the Credit Memo exceeds the Invoice amount, the remaining balance can be applied to another Invoice until $0.

**Method 1: From the Credit Memo**
1. Open the Credit Memo
2. Select **Apply Invoice**
3. Choose invoice and confirm

**Method 2: From an Invoice**
1. Open the Invoice
2. Select **Record payment** (from Pay dropdown)
3. Payment Method: **Credit Memo**
4. Choose the credit memo
5. Select **Record Payment**

**Method 3: From Accounting Platform (QBO/Xero)**
- If Credit Memo was pushed to QuickBooks/Xero, apply it there
- The invoice it's applied to must also have been pushed from BT
- Once applied in QBO/Xero, status updates to Applied in BT

### Where Applied Credit Memos Appear
- Payment History dropdown on the Invoice
- Price Breakdown on Invoices, Payments, Credit Memos, and Deposits dashboard
- Payments and Credit Memos tabs within Invoices
- Jobs Price Summary
- Jobs List (add Applied Credit Memos column to view)

---

## Company Workflow Recommendations

### Deposit Best Practices
1. **Always use deposits for projects over $50K** — Protects cash flow
2. **Standard deposit:** 10-20% of contract price
3. **Send deposit request immediately** after contract signing
4. **Apply deposits systematically** to first invoices

### Credit Memo Best Practices
1. **Document the reason** in Description field
2. **Use Line Items** format for credit memos over $500 (better cost code tracking)
3. **Apply promptly** to avoid confusion on client statements
4. **If QBO integrated:** Push Credit Memo to QBO and apply there for clean books

### Key Distinction: Credit Memo vs. Negative Change Order
| Scenario | Use Credit Memo | Use Negative Change Order |
|----------|----------------|--------------------------|
| One-time courtesy credit | ✅ | ❌ |
| Reduce contract price | ❌ | ✅ |
| Fix billing error | ✅ | ❌ |
| Scope reduction | ❌ | ✅ |
| Offset against specific invoice | ✅ | ❌ |
