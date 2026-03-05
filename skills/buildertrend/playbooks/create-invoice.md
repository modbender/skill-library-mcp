# Create & Send Invoice (Agent-Assisted)

## Overview
When {{company_name}} needs to bill a client for work completed, the agent guides the user through creating an invoice in Buildertrend — pulling from the estimate/budget, suggesting line items or flat fee, handling progress billing (continuation sheet), applying local tax, and optionally sending to the client or pushing to QuickBooks.

## Trigger
- the user says "invoice [project]" or "bill the client for [project]"
- the user says "progress invoice" or "draw request"
- Scheduled billing cycle (monthly progress billing)
- Change Order approved with "Invoice upon client approval" checked (BT auto-creates)

---

## Step 1: Identify Project & Pull Budget Data
**Action:** Confirm which project, then navigate to Job Costing Budget to read current financials

**Message to the user:**
```
📄 Creating an invoice — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_inv_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_inv_project_1` |
| 🏗️ Project Beta | `primary` | `bt_inv_project_2` |
| 🏗️ Project Beta | `primary` | `bt_inv_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_inv_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_inv_project_4` |
| 🏗️ Project Eta | `primary` | `bt_inv_project_5` |
| ❌ Cancel | `danger` | `bt_inv_cancel` |

**On response:**

### Browser Relay — Read Budget
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/JobCostingBudget`
3. Snapshot → read the budget table
4. Extract per cost code:
   - **Revised Budget** (original + selections + COs)
   - **Actual Costs** (what's been spent)
   - **Projected Costs**
   - **Amount Invoiced** (already billed to client)
   - **Remaining to Invoice**
   - **% Invoiced**
5. Also capture:
   - **Revised Client Price** (total contract value)
   - **Total Amount Invoiced** to date
   - **Remaining Balance**

**Present to the user:**
```
📊 [Project Name] — Invoice Summary

💰 Contract: $[revised_client_price]
📤 Already Invoiced: $[total_invoiced] ([pct]%)
📥 Remaining: $[remaining]

Cost codes with uninvoiced amounts:
[table of cost codes with remaining $ to invoice]

How would you like to invoice?
```

---

## Step 2: Choose Invoice Type
**Action:** Ask the user the billing approach

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 Progress Invoice (% Complete) | `primary` | `bt_inv_type_progress` |
| 💵 Flat Fee (lump sum) | `primary` | `bt_inv_type_flat` |
| 📝 Line Items (pick & choose) | `primary` | `bt_inv_type_lines` |
| 📐 Draw Schedule | `primary` | `bt_inv_type_draw` |
| ❌ Cancel | `danger` | `bt_inv_cancel` |

---

### Path A: Progress Invoice (Continuation Sheet)
This is for bank-funded / commercial projects using Schedule of Values.

**Message to the user:**
```
📋 Progress Invoice — Enter % complete per cost code:

| # | Cost Code | Description | Scheduled Value | Prev % | Prev Billed |
|---|-----------|-------------|-----------------|--------|-------------|
| 1 | 05.05 | Non-Structural Framing | $23,000 | 50% | $11,500 |
| 2 | 01.02 | General Carpentry Labor | $5,040 | 25% | $1,260 |
| 3 | 14.00 | Painting | $5,500 | 0% | $0 |
| ... |

What % complete is each line now?
(Or say "all 75%" for uniform, or list specific: "1→80%, 2→50%, 3→25%")
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📊 All same % | `primary` | `bt_inv_progress_uniform` |
| ✏️ I'll specify each | `primary` | `bt_inv_progress_manual` |
| 📎 Use last month + 10% | `primary` | `bt_inv_progress_increment` |

**On response:** Calculate per line:
- **This Period** = (New % − Prev %) × Scheduled Value
- **Completed to Date** = New % × Scheduled Value
- **Balance to Finish** = Scheduled Value − Completed to Date

**Present calculated invoice:**
```
📋 Progress Invoice Preview:

| Cost Code | Scheduled | Prev Billed | This Period | Total Billed | Balance |
|-----------|-----------|-------------|-------------|--------------|---------|
| 05.05     | $23,000   | $11,500     | $6,900      | $18,400      | $4,600  |
| 01.02     | $5,040    | $1,260      | $1,260      | $2,520       | $2,520  |
| 14.00     | $5,500    | $0          | $1,375      | $1,375       | $4,125  |

Subtotal this period: $9,535.00
Tax ({{tax_rate}}%): $846.23
Total this period: $10,381.23
```

### Path B: Flat Fee
**Message to the user:**
```
💵 Flat fee invoice — what amount?
(Or say "remainder" to invoice the full remaining balance of $[remaining])
```

**On response:** Store amount, skip to Step 3.

### Path C: Line Items (Pick & Choose)
**Message to the user:**
```
📝 Select cost codes to include on this invoice:
```

**Inline buttons (one per uninvoiced cost code):**
| Button | Style | callback_data |
|---|---|---|
| ☐ 05.05 Framing — $4,600 remaining | `primary` | `bt_inv_line_05.05` |
| ☐ 01.02 Carpentry — $2,520 remaining | `primary` | `bt_inv_line_01.02` |
| ☐ 14.00 Painting — $4,125 remaining | `primary` | `bt_inv_line_14.00` |
| ✅ Select All | `success` | `bt_inv_line_all` |
| ➡️ Done Selecting | `success` | `bt_inv_line_done` |

For each selected line, ask amount (default = remaining).

### Path D: Draw Schedule
**Message to the user:**
```
📐 Draw Schedule — which draw number?
(BT auto-creates draft invoices from the draw schedule)
```

Show existing draws with status. the user picks one → proceed to Step 3.

---

## Step 3: Tax & Final Review
**Action:** Apply tax and present final summary

**Tax Logic:**
- Default: **{{tax_jurisdiction}} {{tax_rate}}%** ({{state_tax}}% + {{city_tax}}%)
- BT auto-applies to taxable line items when connected to QBO
- If flat fee: tax applies to entire subtotal
- If line items: tax applies to items marked "Taxable"

**Message to the user:**
```
📄 Invoice Ready for Review:

🏗️ Project: [project name]
📋 Type: [Progress/Flat/Line Items]
🔢 Invoice #: [auto-assigned]

[cost breakdown table]

Subtotal: $[subtotal]
Tax ({{tax_rate}}%): $[tax]
Total: $[total]

📅 Due: [date or payment terms]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create Invoice | `success` | `bt_inv_create` |
| ✏️ Edit Amount | `primary` | `bt_inv_edit_amount` |
| 📅 Set Due Date | `primary` | `bt_inv_set_due` |
| 🚫 No Tax | `primary` | `bt_inv_no_tax` |
| ❌ Cancel | `danger` | `bt_inv_cancel` |

---

## Step 4: Create Invoice via Browser Relay
**Action:** Execute in Buildertrend

### For Standard Invoice (Flat Fee / Line Items):
1. Navigate to `/app/OwnerInvoices`
2. Click "Create new Invoice" button (+ Invoice)
3. In the invoice form:
   - Set **Title** (e.g., "Progress Billing #3 — February 2026")
   - **Due Date:** Set payment terms or specific date
   - **Taxes:** Verify "{{tax_jurisdiction}} {{tax_rate}}%" is selected
   - **Price mode:** Select "Flat Fee" or "Line Items" as appropriate
   - If **Line Items**: Click "+ Item" for each cost code line
     - Set Title, Cost Code (combobox), Builder Cost, Markup, Client Price
     - Mark as Taxable if applicable
   - If **Flat Fee**: Enter total amount
   - Verify **Subtotal**, **Tax**, **Total Price** match expected values
4. Click **Save** (creates as Draft)
5. Snapshot → confirm invoice created

### For Progress Invoice:
1. Navigate to `/app/OwnerInvoices`
2. Click the arrow next to "+ Invoice" → select **"Progress Invoice"**
3. BT auto-pulls Schedule of Values from Estimate
4. For each line item, enter the **% complete** value
5. BT auto-calculates: This Period, Completed to Date, Balance
6. Click **Save**
7. Snapshot → confirm

---

## Step 5: Send or Save as Draft
**Message to the user:**
```
✅ Invoice created in Buildertrend!

📄 Invoice #[number]: $[total]
🏗️ Project: [project]
📋 Status: Draft

What next?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Send to Client | `success` | `bt_inv_send` |
| 📊 Push to QuickBooks | `primary` | `bt_inv_qb_push` |
| 📤 Send + Push to QB | `success` | `bt_inv_send_and_qb` |
| 💾 Keep as Draft | `primary` | `bt_inv_draft` |
| 📥 Export PDF | `primary` | `bt_inv_export` |

### If "Send to Client":
1. Click **Send** button on the invoice
2. Select client(s) to receive email notification
3. Click **Send**
4. Confirm: "Invoice sent to [client name] via email + Buildertrend portal"

### If "Push to QuickBooks":
1. Check "Invoice to QuickBooks on Send" checkbox
2. Or if already saved: open invoice → look for QB status section → click "Create Invoice"
3. Confirm QB push status

---

## Step 6: Post-Creation
After invoice is created:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`: Invoice #X created for [project], $[amount]
2. **Update Apple Reminders** — add follow-up if payment terms set
3. **Notify bookkeeper agent** — new invoice in BT, will appear in QBO if pushed
4. **Track payment** — set reminder for due date to check payment status

---

## Smart Suggestion Logic

### Invoice Amount Suggestions
| Scenario | Suggestion |
|---|---|
| First invoice on project | Full contract amount or first draw |
| Monthly billing | Progress invoice with updated %'s |
| Change Order just approved | CO amount as separate invoice line |
| Project near completion | Remaining balance (retention release) |
| Retainage held | Note retainage separately (typically 5-10%) |

### Payment Terms Suggestions
| Client Type | Default Terms |
|---|---|
| Commercial / bank-funded | Net 30 |
| Residential | Due on Receipt |
| Government | Net 45-60 |
| Repeat client (good history) | Net 30 |
| New client | Due on Receipt or Net 15 |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save invoice details for resume |
| No estimate sent to budget | Cannot pull Schedule of Values — ask the user to send estimate to budget first |
| Tax rate missing | Default to {{tax_rate}}% NY; ask the user to confirm |
| Invoice amount exceeds remaining | Warn: "This exceeds the remaining balance by $X" — allow override |
| QB push fails | Report error, suggest: check QB connection, verify job is linked |
| Client not on project | Cannot send — ask the user to add client to job first |
| Estimate locked | Normal — invoices pull from locked estimate data |

---

## Progress Invoice Quick Reference

### Continuation Sheet Columns
| Column | Meaning |
|---|---|
| Scheduled Value | Contract amount per cost code (from estimate) |
| Work Completed (Previous) | Amount billed in prior invoices |
| Work Completed (This Period) | New billing this cycle |
| Materials Stored | Materials purchased but not yet installed |
| Total Completed + Stored | Previous + This Period + Materials |
| % Complete | (Total Completed + Stored) / Scheduled Value |
| Balance to Finish | Scheduled Value − Total Completed |
| Retainage | Held amount (if applicable) |

### Tax Reference
| Rate | Components | Applies To |
|---|---|---|
| {{tax_rate}}% | {{state_tax}}% + {{city_tax}}% | Taxable line items or flat fee |
| 0% | Tax-exempt | Government projects, certain nonprofits |
| Custom | As specified | Out-of-state projects (NJ, CT rates differ) |
