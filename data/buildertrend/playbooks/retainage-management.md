# Retainage / Holdback Tracking

## Overview
Track retainage (holdback) amounts withheld from subcontractor payments and client invoices. Buildertrend does NOT have a native retainage field — this playbook uses the official BT-recommended workaround: split POs into two bills (work amount + retainage hold) with custom fields for filtering.

## Trigger
- "Set up retainage for [sub/PO]", "hold back 10%"
- "Release retainage for [sub/project]", "final payment"
- "Retainage report", "what's held back?"
- "How much retainage on [project]?"
- Project closeout requiring retainage release

---

## Step 1: Set Up Retainage on a New PO
**Action:** Create PO with retainage structure (two-bill method)

### Gather Info
**Message to the user:**
```
🔒 Setting up retainage for a PO. Need:
• Project
• Sub/Vendor
• Total PO amount
• Retainage % (default 10%)
```

**Inline buttons for retainage %:**
| Button | Style | callback_data |
|---|---|---|
| 5% | `primary` | `bt_retainage_5` |
| 10% ⭐ | `success` | `bt_retainage_10` |
| 15% | `primary` | `bt_retainage_15` |
| Custom % | `primary` | `bt_retainage_custom` |

### Calculate Split
- **Total PO:** $[amount]
- **Bill 1 (Work):** $[amount × (100% - retainage%)]
- **Bill 2 (Retainage Hold):** $[amount × retainage%]

**Example:** $50,000 PO at 10% retainage:
- Bill 1: $45,000 (payable on completion)
- Bill 2: $5,000 (held until release)

### Browser Relay Execution — Create PO
1. Navigate to `https://buildertrend.net/app/PurchaseOrders`
2. Click "Create new Purchase Order"
3. Fill PO details:
   - Title: "[Sub Name] — [Trade] (Retainage: [X]%)"
   - Pay to: [Selected sub/vendor]
   - Add line items per scope
   - Total = full contract amount
4. Save PO
5. Snapshot → confirm PO created

### Browser Relay Execution — Create Bill 1 (Work Amount)
1. Navigate to Bills from PO or `/app/Bills`
2. Click "Create new Bill"
3. Fill bill details:
   - Title: "[Sub Name] — Work Payment (90%)" 
   - Link to PO: select the PO just created
   - Amount: $[total × (1 - retainage%)]
   - Cost code: same as PO
4. Save Bill 1

### Browser Relay Execution — Create Bill 2 (Retainage Hold)
1. Click "Create new Bill" again
2. Fill bill details:
   - Title: "[Sub Name] — RETAINAGE HOLD ([X]%)"
   - Link to PO: same PO
   - Amount: $[total × retainage%]
   - Cost code: same as PO
   - Status: Open (DO NOT mark ready for payment)
3. Save Bill 2

**Confirm to the user:**
```
🔒 Retainage set up:
• PO: [title] — $[total]
• Bill 1 (Work): $[work_amount] — ready for payment
• Bill 2 (Retainage): $[hold_amount] — held until release
• Project: [project name]
• Sub: [sub name]
```

---

## Step 2: Track Retainage on Progress Bills
**Action:** For ongoing work with multiple progress payments, create bills at (100% - retainage) of each draw

### For Progress Billing (Multiple Draws)
When a sub submits a progress bill for $10,000 at 10% retainage:
- Create bill for $9,000 (mark Ready for Payment)
- Create retainage bill for $1,000 (keep Open/Hold)
- Add note: "Retainage from Draw #[X]"

### Naming Convention
```
[Sub Name] — Draw #[X] Work Payment (90%)
[Sub Name] — Draw #[X] RETAINAGE HOLD (10%)
```

---

## Step 3: Retainage on Client Invoices
**Action:** Withhold retainage from client draws/invoices

**Note:** BT's invoice retainage fields must be edited via exported Excel/Sheets/Numbers document.

### Browser Relay Steps
1. Navigate to `/app/OwnerInvoices`
2. Create or open invoice
3. For retainage withholding:
   - Calculate: Invoice amount × retainage %
   - Option A: Reduce invoice line items by retainage %
   - Option B: Add negative line item "Retainage Withheld (-[X]%)"
   - Option C: Export to Excel, edit retainage fields, re-import
4. Note retainage in invoice description
5. Save/Send

---

## Step 4: View Retainage Status (Report)
**Action:** Pull retainage report across all subs and jobs

### Browser Relay Steps
1. Navigate to `/app/Bills`
2. Use filter: search "RETAINAGE" in title
3. Filter by Bill Status: "Open" (unreleased retainage)
4. Snapshot → extract data

### Present Summary
```
🔒 Retainage Summary — [Date]

| Project | Sub/Vendor | Retainage Held | Status |
|---------|-----------|---------------|--------|
| [job 1] | [sub 1]   | $[amount]     | Held   |
| [job 1] | [sub 2]   | $[amount]     | Held   |
| [job 2] | [sub 3]   | $[amount]     | Held   |

💰 Total retainage held: $[total]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔓 Release retainage (select sub) | `success` | `bt_retainage_release` |
| 📊 Export retainage report | `primary` | `bt_retainage_export` |
| ✅ Done | `primary` | `bt_retainage_done` |

---

## Step 5: Release Retainage
**Action:** Release held retainage at project completion or milestone

### Pre-Release Checklist
**Message to the user:**
```
🔓 Ready to release retainage for [sub] on [project]?

Pre-release checklist:
☐ All work complete and accepted
☐ Final punch list items resolved
☐ Final lien waiver received
☐ No outstanding claims or disputes
☐ Warranty documentation provided
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ All clear — release retainage | `success` | `bt_retainage_confirm_release` |
| 📋 Need lien waiver first | `primary` | `bt_retainage_need_waiver` |
| ❌ Not ready yet | `danger` | `bt_retainage_hold` |

### Browser Relay Execution
1. Navigate to `/app/Bills`
2. Find the retainage hold bill (search "RETAINAGE HOLD [sub name]")
3. Click to open bill
4. Update title: "[Sub Name] — RETAINAGE RELEASED"
5. Mark as "Ready for Payment"
6. If lien waiver required: go to Lien Waiver tab → verify waiver received
7. Save bill
8. Snapshot → confirm status change

**Confirm to the user:**
```
✅ Retainage released!
• Sub: [sub name]
• Project: [project]
• Amount: $[amount]
• Bill status: Ready for Payment
• Lien waiver: [received/pending]
```

---

## Step 6: QBO Sync for Retainage
**Action:** Ensure retainage bills sync properly to QuickBooks

### Recommended QBO Setup
- **Retainage Held (liability):** Create QBO account "Retainage Payable" 
- **When retainage bill is created:** Bill posts to Retainage Payable account
- **When retainage is released:** Payment clears Retainage Payable

### Sync Steps
1. Push retainage hold bills to QBO (they'll appear as open bills)
2. Do NOT pay retainage bills in QBO until released in BT
3. When released: mark paid in BT → syncs payment to QBO
4. Verify in QBO: Retainage Payable account should net to zero per completed job

---

## Jurisdiction-Specific Retainage Rules

### Commercial Projects (Company Standard)
| Rule | Details |
|---|---|
| Standard retainage | 10% of each progress payment |
| Reduction trigger | Typically reduced to 5% at 50% completion |
| Final release | After punch list completion + final inspection |
| Lien waiver required | Final unconditional lien waiver before release |
| Time limit | Release within 30 days of final acceptance (check local requirements) |
| Interest | Some contracts require interest on held retainage |

### Pre-Release Documentation
1. ✅ Certificate of Substantial Completion
2. ✅ Final unconditional lien waiver from sub
3. ✅ All punch list items resolved
4. ✅ As-built drawings submitted (if applicable)
5. ✅ Warranty documentation
6. ✅ Final inspection sign-off

---

## Smart Suggestions

| Context | Suggestion |
|---|---|
| New PO created for sub > $10K | "Want to set up 10% retainage on this PO?" |
| Project reaching substantial completion | "Ready to review retainage for release?" |
| Lien waiver received for sub | "Lien waiver received — release retainage?" |
| Monthly financial review | Include retainage summary in report |
| Sub asks about held funds | Pull retainage balance for that sub |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| PO already has bills beyond split | Manual adjustment needed — report to the user |
| Retainage bill accidentally paid | Flag immediately — may need QBO reversal |
| Custom field not set up | Guide through creating "Retainage" custom field on Bills |
| Lien waiver missing | Block release, redirect to lien-waiver-tracking playbook |
| Browser relay disconnected | Stop, ask the user to re-enable extension |

---

## Batch Mode
When setting up retainage for multiple subs on a new project:

1. List all POs that need retainage
2. Confirm standard retainage % (or per-sub override)
3. Create PO + two-bill structure for each
4. Show progress: "Set up retainage 3/8 subs..."
5. Final summary: total retainage held across all subs

---

## URL Patterns
| Page | URL |
|---|---|
| Purchase Orders | `/app/PurchaseOrders` |
| Bills | `/app/Bills` |
| Bill Detail | `/app/Bills/Bill/{billId}/{jobId}` |
| Invoices | `/app/OwnerInvoices` |
| Invoice Detail | `/app/OwnerInvoices/OwnerInvoice/{invoiceId}/{jobId}/false` |
| Lien Waivers (on Bill) | Bill detail → Lien Waiver tab |
