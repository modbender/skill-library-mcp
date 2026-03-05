# Advanced Change Order Management (Agent-Assisted)

## Overview

> **UI Reference:** See `bt-ui-patterns.md` for combobox dropdown, modal, grid, and navigation patterns used in this playbook.
Beyond basic CO creation (covered in `create-change-order.md`), this playbook handles the full lifecycle of change orders across a project — tracking all COs per project (approved, pending, declined), analyzing budget impact, handling client-initiated COs from the portal, managing multi-signature approval workflows, flowing approved COs into invoices and POs, maintaining a CO register with running totals, tracking cost variances, and generating CO summary reports. This is the operational control center for scope changes.

## Trigger
- the user says "CO status for [project]" or "change order summary"
- the user says "what's the CO total on [project]?"
- the user says "invoice the approved COs" or "create PO from CO"
- Client submits a CO request through the portal
- Heartbeat detects COs past approval deadline
- the user says "CO report" or "change order log"
- Batch: "CO summary across all projects"

---

## Step 1: Select Project & Action
**Action:** Identify project and what CO management action is needed

**Message to the user:**
```
📋 Change Order Management — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_coa_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_coa_project_1` |
| 🏗️ Project Beta | `primary` | `bt_coa_project_2` |
| 🏗️ Project Beta | `primary` | `bt_coa_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_coa_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_coa_project_4` |
| 🏗️ Project Eta | `primary` | `bt_coa_project_5` |
| 📊 All Projects (batch) | `primary` | `bt_coa_project_all` |
| ❌ Cancel | `danger` | `bt_coa_cancel` |

**On project selected:**
```
📋 CO Management for [Project] — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📊 CO Register / Summary | `primary` | `bt_coa_register` |
| 📈 Budget Impact Analysis | `primary` | `bt_coa_budget` |
| 📥 Client CO Requests | `primary` | `bt_coa_client_requests` |
| 💰 Invoice Approved COs | `primary` | `bt_coa_invoice` |
| 📦 Create PO from CO | `primary` | `bt_coa_po` |
| ⏰ Pending Approvals | `primary` | `bt_coa_pending` |
| 📊 Variance Report | `primary` | `bt_coa_variance` |
| ➕ New CO | `primary` | `bt_coa_new` |
| ❌ Cancel | `danger` | `bt_coa_cancel` |

---

## Step 2A: CO Register / Summary
**Action:** Pull all change orders for the project and present a comprehensive log

### Browser Relay — Read All COs
1. Ensure correct job selected in BT left sidebar
2. Navigate to `/app/ChangeOrders`
3. Snapshot → read the CO table
4. Extract per CO:
   - **CO ID#** (e.g., 0001, 0002)
   - **Title**
   - **Status** (Draft, Sent, Approved, Declined, Client Requested)
   - **Builder Cost** (total)
   - **Client Price** (total)
   - **Created Date**
   - **Status Change Date**
   - **Related POs** (count / linked)
   - **RFIs** (count)
   - **Files** (count)
5. Calculate running totals

**Present to the user:**
```
📋 Change Order Register — [Project Name]

| CO # | Title | Status | Builder Cost | Client Price | Date |
|------|-------|--------|-------------|-------------|------|
| 0001 | [title] | ✅ Approved | $[cost] | $[price] | [date] |
| 0002 | [title] | ⏳ Sent | $[cost] | $[price] | [date] |
| 0003 | [title] | 📝 Draft | $[cost] | $[price] | [date] |
| 0004 | [title] | ❌ Declined | $[cost] | $[price] | [date] |
| 0005 | [title] | 📥 Client Req. | $[cost] | $[price] | [date] |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Summary:
   Total COs: [count]
   ✅ Approved: [n] — Builder: $[sum] | Client: $[sum]
   ⏳ Pending: [n] — Builder: $[sum] | Client: $[sum]
   ❌ Declined: [n] — Builder: $[sum] | Client: $[sum]
   📝 Draft: [n] — Builder: $[sum] | Client: $[sum]

💰 Net Approved Impact: +$[approved_client_total]
💰 Pending Impact: +$[pending_client_total]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📈 Budget Impact | `primary` | `bt_coa_budget` |
| 🔍 View CO Details | `primary` | `bt_coa_detail` |
| 💰 Invoice Approved | `success` | `bt_coa_invoice` |
| 📦 Create POs | `primary` | `bt_coa_po` |
| ⏰ Follow Up Pending | `primary` | `bt_coa_followup` |
| ✅ Done | `success` | `bt_coa_done` |

---

## Step 2B: Budget Impact Analysis
**Action:** Show how COs affect the project budget

### Browser Relay — Read Budget with CO Impact
1. Navigate to `/app/JobCostingBudget`
2. Snapshot → read budget data
3. Extract:
   - **Original Budget** (from signed proposal)
   - **Revised Budget** (original + selections + COs)
   - **Approved CO total** (from CO register)
   - **Projected Costs**
   - **Projected Profit**

**Present to the user:**
```
📈 CO Budget Impact — [Project Name]

💰 Original Contract: $[original_client_price]
➕ Approved COs: +$[approved_co_client]
➕ Approved Selections: +$[selections_delta]
━━━━━━━━━━━━━━━━━━━━━━━
💵 Revised Contract: $[revised_client_price]

📊 Builder Side:
   Original Budget: $[original_budget]
   + CO Builder Costs: +$[approved_co_builder]
   = Revised Budget: $[revised_budget]

📈 Profit Analysis:
   Original Profit: $[original_profit] ([original_margin]%)
   CO Profit: $[co_profit] ([co_margin]%)
   Revised Profit: $[revised_profit] ([revised_margin]%)

⚠️ Pending COs (not yet in budget):
   [n] pending COs worth $[pending_total] to client
   If all approved → Revised Contract: $[projected_revised]

📊 CO as % of Original: [co_total / original × 100]%
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 View CO Register | `primary` | `bt_coa_register` |
| 📊 Full Budget Report | `primary` | `bt_coa_full_budget` |
| 💰 Invoice Difference | `primary` | `bt_coa_invoice_diff` |
| ✅ Done | `success` | `bt_coa_done` |

### Budget Impact Alert Thresholds
| Metric | Warning | Alert |
|---|---|---|
| CO total / original contract | >10% 🟡 | >25% 🔴 |
| CO margin below job margin | <5% difference 🟡 | <0% (losing money) 🔴 |
| Pending COs aging >14 days | 🟡 Warn | >30 days 🔴 Alert |

---

## Step 2C: Client-Initiated CO Requests
**Action:** Review and process COs submitted by clients through the portal

### Browser Relay — Check Client Requests
1. Navigate to `/app/ChangeOrders`
2. Filter by **Status: Client Requested**
3. Snapshot → extract pending client requests

**If requests found:**
```
📥 Client CO Requests — [Project Name]:

| # | Title | Description | Submitted | Client |
|---|-------|------------|-----------|--------|
| 1 | [title] | [desc preview] | [date] | [name] |
| 2 | [title] | [desc preview] | [date] | [name] |

⚠️ [count] pending client requests need your review.
```

**For each request, inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Accept & Price [Request 1] | `success` | `bt_coa_accept_1` |
| ✏️ Modify & Accept [1] | `primary` | `bt_coa_modify_1` |
| ❌ Decline [1] | `danger` | `bt_coa_decline_1` |
| 💬 Need More Info [1] | `primary` | `bt_coa_info_1` |
| 📋 View All Details | `primary` | `bt_coa_view_requests` |

### Accept & Price Flow:
1. Read client's request details
2. Build cost estimate (same as create-change-order Step 3)
3. Add markup → calculate client price
4. Create the CO with line items
5. Send to client for formal approval
6. Track approval status

### Decline Flow:
```
❌ Declining CO request: [Title]
Reason? (This will be visible to the client)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📐 Out of scope | `primary` | `bt_coa_decline_scope` |
| 💰 Budget constraint | `primary` | `bt_coa_decline_budget` |
| ⏳ Timing issue | `primary` | `bt_coa_decline_timing` |
| 📝 Custom reason | `primary` | `bt_coa_decline_custom` |

---

## Step 2D: Multi-Signature Approval Workflow
**Action:** Manage COs that require multiple approvers

**When to use:** Projects with multiple decision-makers (e.g., husband + wife, owner + architect, corporate board members)

**Message to the user:**
```
✍️ CO #[number] requires multiple signatures:

| Signee | Status |
|--------|--------|
| [Name 1] | ✅ Approved — [date] |
| [Name 2] | ⏳ Pending |
| [Name 3] | ⏳ Pending |

[2 of 3] signatures collected.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Resend to Pending | `primary` | `bt_coa_resend_pending` |
| ✅ Approve on Behalf | `primary` | `bt_coa_approve_behalf` |
| 💬 Remind Client | `primary` | `bt_coa_remind_client` |

### Browser Relay — Check/Update Approval Status
1. Navigate to `/app/ChangeOrders/{coId}/{jobId}/Details`
2. Scroll to **Approval Status** section
3. Read each signee's status
4. To approve on behalf: click **Approve** next to signee name → apply e-signature → **Approve**
5. Snapshot → confirm approval status

### Internal Approval:
```
✍️ Approve CO #[number] internally?
This approves on behalf of [Client Name].
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Approve (internal) | `success` | `bt_coa_approve_internal` |
| ❌ Don't approve | `danger` | `bt_coa_no_approve` |

---

## Step 2E: CO → Invoice Flow
**Action:** Bill the client for approved change orders

**Logic:**
1. If "Invoice upon client approval" was set → BT auto-created the invoice
2. If not → manually create invoice from CO

### Check Auto-Invoice Status:
```
💰 Approved COs — Invoice Status:

| CO # | Title | Client Price | Auto-Invoice | Invoice Status |
|------|-------|-------------|-------------|---------------|
| 0001 | [title] | $[price] | ✅ Yes | Sent — $[amount] |
| 0003 | [title] | $[price] | ❌ No | Not invoiced |

$[uninvoiced_total] in approved COs not yet invoiced.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💰 Invoice Uninvoiced COs | `success` | `bt_coa_invoice_create` |
| 📋 View Invoices | `primary` | `bt_coa_view_invoices` |
| ⏭️ Skip | `primary` | `bt_coa_invoice_skip` |

### Browser Relay — Create Invoice from CO
1. Navigate to `/app/OwnerInvoices`
2. Click **"+ Invoice"**
3. In invoice form:
   - Set **Title** (e.g., "CO #0003 — [CO Title]")
   - Click **"Add from"** → **"Change Orders"**
   - Select the approved CO(s) to include
   - BT auto-fills line items from CO estimate
   - Set **Due Date** and **Payment Terms**
   - Verify **Tax** ({{tax_rate}}% NY default)
4. Click **Save** (or **Send**)
5. Optionally push to QuickBooks
6. Snapshot → confirm invoice created

**Report back:**
```
✅ Invoice created from CO #[number]:

📄 Invoice #[inv_number]: $[total]
📋 From CO: [CO title]
🏗️ Project: [project]
📊 QB Status: [pushed/pending]
```

---

## Step 2F: CO → PO Flow
**Action:** Order materials or sub work for an approved change order

**Message to the user:**
```
📦 Create PO(s) for CO #[number]: [title]?

CO Line Items:
| # | Description | Cost Code | Builder Cost |
|---|-------------|-----------|-------------|
| 1 | [desc] | [code] | $[cost] |
| 2 | [desc] | [code] | $[cost] |

Which items need POs?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📦 PO for All Items | `success` | `bt_coa_po_all` |
| 📦 PO for Item [1] | `primary` | `bt_coa_po_1` |
| 📦 PO for Item [2] | `primary` | `bt_coa_po_2` |
| ⏭️ No POs needed | `primary` | `bt_coa_po_skip` |

### Browser Relay — Create PO from CO
1. Navigate to `/app/ChangeOrders/{coId}/{jobId}/Details`
2. In the CO detail, look for **"Create PO"** or **"Add to"** options
3. Alternatively, navigate to `/app/PurchaseOrders`:
   - Click **"+Purchase Order"**
   - Select **"Variance PO"** (for CO-related work)
   - BT auto-uses variance code **"72 – Customer Variance"** for client-initiated COs
   - Set **Title** referencing the CO (e.g., "PO from CO #0003 — Plumbing")
   - Set **Assignee** (sub/vendor)
   - Fill line items from CO estimate data
   - Set **Scope of Work**
   - Link to **Referenced Change Order**
4. Click **Send** (to sub) or **Save** (draft)
5. Snapshot → confirm PO created

**Report back:**
```
📦 PO created from CO #[number]:

📄 PO #[po_number]: $[amount]
👷 Assignee: [vendor/sub]
📋 Linked to: CO #[number]
🏗️ Project: [project]
📊 Type: Variance PO (Customer Variance)
```

---

## Step 2G: Variance Tracking
**Action:** Compare planned CO costs vs actual costs incurred

### Browser Relay — Read Variance Data
1. Navigate to `/app/JobCostingBudget`
2. Filter by **Related Items: Change Orders**
3. For each CO-affected cost code, compare:
   - **Revised Budget** (includes CO amounts)
   - **Committed** (POs issued for CO work)
   - **Actual** (bills received for CO work)
   - **Projected** (greatest of revised/committed/actual)

**Present to the user:**
```
📊 CO Variance Report — [Project Name]:

| CO # | Title | Budgeted | Committed | Actual | Variance |
|------|-------|----------|-----------|--------|----------|
| 0001 | [title] | $[budget] | $[committed] | $[actual] | $[delta] |
| 0003 | [title] | $[budget] | $[committed] | $[actual] | $[delta] |

Legend:
🟢 Under budget (positive variance)
🟡 On track (within 5%)
🔴 Over budget (negative variance)

Total CO Budget: $[sum_budgeted]
Total CO Actual: $[sum_actual]
Net Variance: $[net_variance] ([direction])
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔍 Drill into CO [#] | `primary` | `bt_coa_drill_1` |
| 📊 Full Budget View | `primary` | `bt_coa_full_budget` |
| ⚠️ Flag Overages | `danger` | `bt_coa_flag_overages` |
| ✅ Done | `success` | `bt_coa_done` |

---

## Step 2H: Follow Up on Pending COs
**Action:** Check for COs past deadline or stale

### Browser Relay — Check Pending
1. Navigate to `/app/ChangeOrders`
2. Filter by **Status: Sent** (awaiting approval)
3. Check each for:
   - Days since sent
   - Approval deadline (past or upcoming)
   - Client viewed (if visible)

**Present to the user:**
```
⏰ Pending COs Needing Attention — [Project]:

| CO # | Title | Client Price | Sent Date | Deadline | Days Pending |
|------|-------|-------------|-----------|----------|-------------|
| 0002 | [title] | $[price] | [date] | [deadline] | [days] |
| 0005 | [title] | $[price] | [date] | [deadline] | [days] |

⚠️ [CO #0002] is [X] days past deadline!
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Remind Client (CO #0002) | `primary` | `bt_coa_remind_0002` |
| ✅ Approve Internally | `primary` | `bt_coa_approve_0002` |
| ❌ Cancel CO | `danger` | `bt_coa_cancel_0002` |
| 📧 Remind All Pending | `primary` | `bt_coa_remind_all` |

---

## Batch Mode: CO Summary Across All Projects
When the user says "CO summary" or "change order report across projects":

### Browser Relay — Multi-Project CO Scan
1. For each active project:
   - Select job in BT sidebar
   - Navigate to `/app/ChangeOrders`
   - Snapshot → extract CO summary
2. Aggregate across projects

**Present to the user:**
```
📊 CO Summary — All Projects — [date]

| Project | Total COs | Approved | Pending | Declined | Net Approved | Net Pending |
|---------|-----------|----------|---------|----------|-------------|-------------|
| Project Alpha | [n] | [n] | [n] | [n] | $[sum] | $[sum] |
| Project Alpha | [n] | [n] | [n] | [n] | $[sum] | $[sum] |
| Project B | [n] | [n] | [n] | [n] | $[sum] | $[sum] |
| Project Beta | [n] | [n] | [n] | [n] | $[sum] | $[sum] |
| Project Delta | [n] | [n] | [n] | [n] | $[sum] | $[sum] |
| Project Gamma | [n] | [n] | [n] | [n] | $[sum] | $[sum] |
| Project Echo | [n] | [n] | [n] | [n] | $[sum] | $[sum] |
| ━━━━━━━ | ━━━ | ━━━ | ━━━ | ━━━ | ━━━━━ | ━━━━━ |
| **TOTAL** | [n] | [n] | [n] | [n] | $[sum] | $[sum] |

💰 Total Approved CO Value: $[total_approved]
⏳ Total Pending CO Value: $[total_pending]
📊 Avg CO Margin: [X]%

⚠️ Action Items:
- [Project]: [n] COs past deadline
- [Project]: CO margin below threshold
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔍 Drill into [Project] | `primary` | `bt_coa_drill_project` |
| 📊 BT CO Profit Report | `primary` | `bt_coa_bt_report` |
| ✅ Done | `success` | `bt_coa_done` |

### BT Built-in Report:
Navigate to `/Reporting/ReportDetails.aspx?reportType=21&reportFilter=133` → **Change Order Profit** report
- Shows CO client price vs builder cost per project
- Export available

---

## Change Order Status Lifecycle (Complete)

```
                  ┌─────────────┐
                  │   Draft     │
                  └──────┬──────┘
                         │ Send
                  ┌──────▼──────┐
              ┌───│    Sent     │───┐
              │   └─────────────┘   │
         Approve              Decline
              │                     │
      ┌───────▼───────┐   ┌────────▼────────┐
      │   Approved    │   │    Declined     │
      └───────┬───────┘   └────────┬────────┘
              │                     │
     ┌────────┼────────┐           │ Revise & Resend
     │        │        │           └──────► Sent
  Invoice    PO    Budget
  (auto or   (manual)  (auto)
   manual)
```

**Client-Initiated Path:**
```
Client Request → Review → Accept & Price → Send → Approve/Decline
                       → Modify & Accept → Send → Approve/Decline
                       → Decline (with reason)
```

---

## CO Impact on Budget (Detailed)

When a CO is **Approved**, BT automatically updates:

| Budget Field | Change |
|---|---|
| **Revised Budget Costs** | + CO builder cost (per cost code) |
| **Revised Client Price** | + CO client price (per cost code) |
| **Projected Costs** | Recalculates (greatest of revised/committed/actual) |
| **Projected Profit** | Recalculates (revised client − projected cost) |
| **Cost-to-Complete** | Recalculates (projected − actual) |

**Variance PO behavior:**
- POs created from COs use **Variance Code 72 — Customer Variance**
- Customer Variance amounts are NOT counted as Builder Variance
- They properly flow to **Committed Costs** under the relevant cost codes

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user, save CO data for resume |
| CO already invoiced | Cannot modify — report to the user |
| CO has linked POs | Warn before canceling: "CO has [n] linked POs" |
| Client not on project | Cannot send CO — add client first |
| No approved COs to invoice | Report: "No uninvoiced approved COs found" |
| Budget not activated | Cannot see impact — send estimate to budget first |
| Browser relay disconnected | Stop, save state, ask the user to re-enable |
| Multiple jobs have same CO # | Use project + CO # to disambiguate |
| CO declined but work already done | Flag as risk — may need builder variance |

---

## URL Quick Reference

| Page | URL |
|---|---|
| Change Orders (all) | `/app/ChangeOrders` |
| CO Detail | `/app/ChangeOrders/{coId}/{jobId}/Details` |
| CO Estimate Tab | `/app/ChangeOrders/{coId}/{jobId}/Estimate` |
| CO Client Preview | `/app/ChangeOrders/{coId}/{jobId}/ClientPreview` |
| CO Related RFI | `/app/ChangeOrders/RelatedRfi/{coId}/2/{?}/{jobId}` |
| Change Order Settings | `/app/Settings/ChangeOrderSettings` |
| Change Order Profit Report | `/Reporting/ReportDetails.aspx?reportType=21&reportFilter=133` |
| Job Costing Budget | `/app/JobCostingBudget` |
| Invoices | `/app/OwnerInvoices` |
| Purchase Orders | `/app/PurchaseOrders` |
