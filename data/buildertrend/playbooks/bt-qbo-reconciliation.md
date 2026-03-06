# BT ↔ QBO Reconciliation (Agent-Assisted)

## Overview

> **UI Reference:** See `bt-ui-patterns.md` for combobox dropdown, modal, grid, and navigation patterns used in this playbook.
The agent checks the sync status between Buildertrend and QuickBooks Online for bills and invoices, identifies discrepancies (synced, pending, failed, not sent), cross-references with QBO data when possible, and reports problems with fix suggestions. This is a read-only audit workflow — no data modifications.

## Trigger
- the user says "check QB sync" or "reconcile BT and QBO"
- bookkeeper agent (QBO agent) flags a mismatch between BT and QBO records
- Monthly close process — verify all bills/invoices are in sync
- Before filing taxes or running financial reports
- After a batch of bills/invoices were created

---

## Step 1: Choose Scope
**Action:** Ask what to reconcile

**Message to the user:**
```
🔄 BT ↔ QBO Sync Check — what should I audit?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🧾 Bills (AP) | `primary` | `bt_qbo_bills` |
| 📄 Invoices (AR) | `primary` | `bt_qbo_invoices` |
| 🔄 Both Bills + Invoices | `success` | `bt_qbo_both` |
| 🏗️ Specific Project Only | `primary` | `bt_qbo_project` |
| ❌ Cancel | `danger` | `bt_qbo_cancel` |

If "Specific Project" → show project buttons (same as other playbooks) → filter results to that job only.

---

## Step 2: Extract Bills Sync Status
**Action:** Navigate to Bills page and read the QuickBooks Status column

### Browser Relay Execution — Bills
1. Navigate to `/app/Bills`
2. If project-specific: apply job filter in left sidebar
3. Snapshot → read the table
4. For each bill, extract:

| Field | Column |
|---|---|
| Job | Job column |
| Bill # | Bill # column |
| Title | Bill Title column |
| Vendor | Pay To column |
| Amount | Bill Amount column |
| Bill Status | Bill Status column (Open / Paid) |
| **QuickBooks Status** | QuickBooks Status column |
| Date | Invoice Date column |
| Date Paid | Date Paid column |

5. If the table has many rows, page through or adjust filters:
   - Filter by "Sent To Accounting" = No → shows unsynced bills
   - Filter by date range if needed

### QB Status Values to Check:
| BT QB Status | Meaning | Flag |
|---|---|---|
| ✅ Synced / Sent | Bill exists in QBO | OK |
| ⏳ Pending | Push in progress | Monitor |
| ❌ Failed | Push attempted but failed | 🔴 ACTION |
| 🚫 Not Sent | Never pushed to QBO | ⚠️ REVIEW |
| — (blank/none) | No QB action taken | ⚠️ REVIEW |

---

## Step 3: Extract Invoices Sync Status
**Action:** Navigate to Invoices page and read the QuickBooks invoice column

### Browser Relay Execution — Invoices
1. Navigate to `/app/OwnerInvoices`
2. If project-specific: apply job filter
3. Snapshot → read the table
4. For each invoice, extract:

| Field | Column |
|---|---|
| Job | Job column |
| Invoice # | Invoice ID column |
| Title | Title column |
| Status | Status column (Draft / Sent / Paid) |
| Amount | Total price column |
| Tax | Total tax column |
| Balance Due | Balance due column |
| **QuickBooks Invoice** | QuickBooks invoice column |
| Due Date | Due column |
| Date Paid | Date paid column |

### QB Status Values to Check:
| BT QB Status | Meaning | Flag |
|---|---|---|
| ✅ Invoiced in QB | Invoice exists in QBO | OK |
| 🚫 Not Invoiced in QB | Never pushed | ⚠️ REVIEW |
| ❌ Error | Push failed | 🔴 ACTION |
| Draft (BT status) | Not yet sent to client | ℹ️ Expected to be unsynced |

---

## Step 4: Compile Discrepancy Report
**Action:** Categorize all items by sync status and build report

### Report Format:

**Message to the user:**
```
🔄 BT ↔ QBO SYNC REPORT
📅 As of [date]
🏗️ Scope: [All Projects / Specific Project]

━━━ BILLS (Accounts Payable) ━━━

✅ Synced: [count] bills ($[total])
⏳ Pending: [count] bills ($[total])
🔴 Failed: [count] bills ($[total])
⚠️ Not Sent: [count] bills ($[total])

━━━ INVOICES (Accounts Receivable) ━━━

✅ Synced: [count] invoices ($[total])
⚠️ Not Synced: [count] invoices ($[total])
🔴 Failed: [count] invoices ($[total])
📝 Draft (not expected to sync): [count] invoices ($[total])
```

### If discrepancies found, list them:

```
━━━ 🔴 ITEMS NEEDING ATTENTION ━━━

FAILED BILLS:
| # | Bill | Vendor | Amount | Job | Error |
|---|------|--------|--------|-----|-------|
| 1 | B-0023 | ABC Plumbing | $4,250 | Project Alpha | QB validation error |
| 2 | B-0031 | Home Depot | $892 | Project A | Vendor not linked |

NOT SENT (should be):
| # | Bill | Vendor | Amount | Job | Age |
|---|------|--------|--------|-----|-----|
| 3 | B-0045 | XYZ Electric | $3,100 | Project B | 15 days old |
| 4 | B-0052 | Misc | $1,200 | W27 | 8 days old |

INVOICES NOT SYNCED:
| # | Invoice | Amount | Job | Status | Age |
|---|---------|--------|-----|--------|-----|
| 5 | INV-0012 | $15,000 | Project A | Sent | 22 days |
| 6 | INV-0018 | $8,500 | Project A | Sent | 10 days |
```

---

## Step 5: Fix Suggestions
**Action:** For each discrepancy, suggest a fix

**Message to the user:**
```
🔧 RECOMMENDED FIXES:

1. 🔴 B-0023 (ABC Plumbing, $4,250)
   Fix: Open bill → check cost codes match QB Products & Services → re-push
   
2. 🔴 B-0031 (Home Depot, $892)
   Fix: Link vendor "Home Depot" to QBO Vendor → then re-push bill
   
3. ⚠️ B-0045 (XYZ Electric, $3,100) — 15 days unsynced
   Fix: Open bill → check "Send to QuickBooks" → Save
   
4. ⚠️ B-0052 (Misc, $1,200) — 8 days unsynced  
   Fix: Assign proper vendor (not Misc) → then push to QB
   
5. ⚠️ INV-0012 ($15,000) — sent 22 days ago, not in QB
   Fix: Open invoice → QB Status section → click "Create Invoice"
   
6. ⚠️ INV-0018 ($8,500) — sent 10 days ago, not in QB
   Fix: Open invoice → QB Status section → click "Create Invoice"
```

### Common Fix Patterns:
| Problem | Root Cause | Fix |
|---|---|---|
| Vendor not linked | BT vendor has no QBO match | Link: vendor card → Accounting tab → Link sub |
| Cost code not mapped | BT cost code not mapped to QB P&S | Map: Settings → Cost Codes → Import → QuickBooks |
| Job not linked | BT job not linked to QB Customer/Project | Link: Job Details → Accounting tab → Link job |
| Bill validation error | Missing required field for QB | Open bill, fill missing field, re-push |
| Invoice not pushed | Forgot to check "Send to QB" | Open invoice → push manually |
| Payment mismatch | Paid in one system, not the other | Check bank feed matching in QBO |
| Duplicate entry | Pushed twice, or manually entered in QB | Delete duplicate in QBO, keep BT-pushed version |

---

## Step 6: Action Buttons
**Action:** Offer to fix issues or take next steps

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔧 Fix bill [#1 — worst] | `primary` | `bt_qbo_fix_1` |
| 🔧 Fix all failed bills | `success` | `bt_qbo_fix_all_bills` |
| 📤 Push all unsynced invoices | `success` | `bt_qbo_push_invoices` |
| 📋 Send report to bookkeeper agent | `primary` | `bt_qbo_notify_agent` |
| 💾 Save report to Drive | `primary` | `bt_qbo_save_drive` |
| 🔄 Re-check (refresh) | `primary` | `bt_qbo_refresh` |
| 👍 All clear, thanks | `success` | `bt_qbo_done` |

### If "Fix bill":
1. Navigate to `/app/Bills/Bill/{billId}/{jobId}`
2. Identify the specific issue (missing vendor link, cost code, etc.)
3. If fixable: apply the fix via relay
4. If not fixable by agent: report specific instructions for the user

### If "Push all unsynced invoices":
1. Navigate to `/app/OwnerInvoices`
2. For each unsynced sent invoice:
   - Open invoice → find QB status section
   - Click "Create Invoice" to push to QB
3. Report results: "Pushed 3/3 invoices to QB — verify in QBO"

### If "Notify bookkeeper agent":
- Send the discrepancy report to bookkeeper agent for QBO-side investigation
- bookkeeper agent can check QBO for matching transactions, bank feed status

---

## Step 7: Cross-Reference with QBO (Advanced)
**If bookkeeper agent has QBO access**, request cross-reference:

**Agent-to-Agent Request:**
```
@bookkeeper agent — BT sync check found [count] discrepancies. Please verify in QBO:

Bills to check:
- B-0023: ABC Plumbing $4,250 (should exist as bill)
- B-0031: Home Depot $892 (vendor may not be linked)

Invoices to check:
- INV-0012: $15,000 for Project Alpha (should be in AR)
- INV-0018: $8,500 for W98 (should be in AR)

Do these exist in QBO? If so, are they matched to bank transactions?
```

**bookkeeper agent responds with QBO-side data → the agent consolidates into final report.**

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| QB Status column not visible | May need to add column to view; instruct the user: Bills → manage columns → add QuickBooks Status |
| Too many bills to parse | Filter by date range (last 30/60/90 days) |
| Browser relay disconnected | Stop, ask the user to re-enable |
| QB not connected | Report: "QuickBooks is not connected — check Settings → Accounting" |
| Permission denied on Accounting Settings | Note: "AA role can't access Accounting Settings — the user may need to log in as Admin" |

---

## Sync Status Quick Reference

### What Should Be Synced
| Item | When to Push to QB |
|---|---|
| Bill | Always — when created or saved (default setting) |
| Invoice | When sent to client (check "Invoice to QuickBooks on Send") |
| Time Clock | On approval (if auto-push enabled) |
| Deposit Payment | After payment received |
| Credit Memo | On release (check "Send to QuickBooks on Release") |

### What Comes Back from QB
| Item | Direction | Trigger |
|---|---|---|
| Bill Payment | QB → BT | Marked paid in QBO → auto-updates BT |
| Invoice Payment | QB → BT | Payment received in QBO → auto-updates BT |
| QB Expenses | QB → BT | Bills/Checks/CC in QBO → appear in BT budget |
| Estimates | QB → BT | Manual import only |

### Reconciliation Checklist
- [ ] All bills pushed to QB (check "Sent To Accounting" filter)
- [ ] All sent invoices pushed to QB (check QB invoice column)
- [ ] Bill payments match between BT and QB
- [ ] Invoice payments match between BT and QB
- [ ] No duplicate entries in either system
- [ ] Bank feed matches in QBO are complete
- [ ] QB expenses showing in BT budget (if enabled)

---

## Batch Reconciliation Schedule

| Frequency | What to Check |
|---|---|
| Daily | New bills/invoices created today → verify auto-push |
| Weekly | All bills from past 7 days → verify sync |
| Monthly | Full audit — all unpaid bills, all open invoices |
| Quarterly | Deep reconciliation with bookkeeper agent — match every $ |
