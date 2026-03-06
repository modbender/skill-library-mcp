# Project Closeout & Handover (Agent-Assisted)

## Overview
Close out a completed project in Buildertrend — verify all punch list items resolved, confirm final invoicing/payment, assemble closeout documents, set up warranty period, archive the job, and generate final reports. This is the last phase before a job transitions to Warranty or Closed status.

## Trigger
- the user says "close out [project]", "project complete", "wrap up [project]"
- Final punch list items marked complete
- Final payment received from client
- "What's left to close out [project]?"
- Certificate of Substantial Completion issued

---

## Step 1: Closeout Readiness Check
**Action:** Verify all prerequisites before closing out

### Pre-Closeout Checklist

| # | Item | Where to Verify | Status |
|---|---|---|---|
| 1 | All punch list items complete | `/app/tasks/punch-list` | ☐ |
| 2 | All to-dos complete | `/app/tasks/all` | ☐ |
| 3 | Final invoice sent | `/app/OwnerInvoices` | ☐ |
| 4 | Final payment received | `/app/OwnerInvoices` → Payments tab | ☐ |
| 5 | All bills paid | `/app/Bills` → filter: Status = Open | ☐ |
| 6 | All POs finalized | `/app/PurchaseOrders` → Work Complete | ☐ |
| 7 | Lien waivers collected | `/app/Bills` → Lien Waiver column | ☐ |
| 8 | Retainage released | Budget → retainage line items | ☐ |
| 9 | All change orders resolved | `/app/ChangeOrders` → no pending | ☐ |
| 10 | All selections approved | `/app/Selections/Default` → all approved | ☐ |
| 11 | Final daily log entered | `/app/DailyLogs` | ☐ |
| 12 | All RFIs closed | `/app/RFIs` → no open | ☐ |
| 13 | Photos documented | `/app/Photos/Standard/0` | ☐ |
| 14 | Documents complete | `/app/Documents/Standard/0` | ☐ |

**Browser Relay Execution:**
```
browser → navigate to job → /app/tasks/punch-list
browser → snapshot → verify no open punch list items

browser → navigate to /app/OwnerInvoices
browser → snapshot → verify final invoice paid

browser → navigate to /app/Bills
browser → snapshot → filter Status = Open → verify none remaining

browser → navigate to /app/PurchaseOrders
browser → snapshot → verify all POs marked Work Complete

browser → navigate to /app/ChangeOrders
browser → snapshot → verify no pending COs

browser → navigate to /app/RFIs
browser → snapshot → verify no open RFIs
```

**Message to the user:**
```
📋 Closeout Checklist for [Project]:
✅ Punch list: All [X] items complete
✅ Final invoice: Sent & paid ($[amount])
✅ Bills: All [X] paid ($[total])
✅ POs: All [X] finalized
⚠️ Lien waivers: [X] of [Y] collected
✅ Change orders: All [X] resolved
✅ Selections: All approved
✅ RFIs: All closed

[X/14] items ready. [Outstanding items listed]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Proceed to Closeout | `success` | `close_proceed` |
| ⚠️ View Outstanding Items | `primary` | `close_outstanding` |
| 📊 Generate Final Report | `primary` | `close_report` |
| ⏭️ Not Ready Yet | `danger` | `close_later` |

---

## Step 2: Final Punch List Verification
**Action:** Confirm all punch list items resolved

```
browser → navigate to https://buildertrend.net/app/tasks/punch-list
browser → snapshot → review all punch list items
browser → snapshot → verify each marked Complete
```

If items remain open, present list with assignees and due dates for the user to follow up.

---

## Step 3: Sub/Vendor Closeout
**Action:** Verify all sub/vendor obligations are complete

### Per-Sub Checklist
For each sub/vendor on the job:

| Item | Verification |
|---|---|
| All bills paid | Bills → filter by Pay To → all Paid |
| Final lien waiver signed | Lien Waiver column → signed |
| Retainage released | Budget → retainage line → paid |
| POs finalized | POs → Work Complete or closed |
| Warranty docs provided | Documents → manufacturer warranties |

```
browser → navigate to https://buildertrend.net/app/Bills
browser → snapshot → filter by each sub → verify all paid
browser → snapshot → check Lien Waiver status for each bill
```

**Message to the user:**
```
👷 Sub Closeout Status:
| Sub/Vendor | Bills Paid | Lien Waiver | Retainage | ✓ |
|---|---|---|---|---|
| [Electrician] | ✅ $45K | ✅ Signed | ✅ Released | ✅ |
| [Plumber] | ✅ $28K | ⚠️ Missing | ✅ Released | ⚠️ |
| [Painter] | ✅ $12K | ✅ Signed | N/A | ✅ |
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Request Missing Waivers | `primary` | `close_request_waivers` |
| 💰 Release Retainage | `primary` | `close_release_retainage` |
| ✅ Subs Complete | `success` | `close_subs_done` |

---

## Step 4: Final Job Costing Report
**Action:** Generate budget vs actual report

```
browser → navigate to https://buildertrend.net/app/JobCostingBudget
browser → snapshot → read Profitability Summary at top
browser → snapshot → read all cost code rows for actuals
browser → snapshot → export report if needed
```

**Report Data Points:**
| Metric | Source |
|---|---|
| Original Contract Price | Estimate → signed proposal |
| Approved Change Orders | CO total (approved) |
| Revised Contract Price | Original + COs + Selections |
| Total Actual Costs | Budget → Actual Costs column |
| Builder Variance | Budget → Builder Variance column |
| Final Profit | Revised Client Price - Projected Cost |
| Final Margin % | Profit / Revised Client Price |

**Message to the user:**
```
📊 Final Job Costing — [Project]:
| Metric | Amount |
|---|---|
| Original Contract | $[amount] |
| Change Orders | +$[amount] ([count] COs) |
| Selections/Allowances | +$[amount] |
| Revised Contract | $[total] |
| Total Costs (Actual) | $[amount] |
| Builder Variance | $[amount] |
| **Final Profit** | **$[profit]** |
| **Final Margin** | **[X]%** |
| Invoiced | $[amount] |
| Payments Received | $[amount] |
| Balance Due | $[remaining] |
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Export to Excel | `primary` | `close_export_budget` |
| 📊 Detailed Breakdown | `primary` | `close_detail_budget` |
| ✅ Report Looks Good | `success` | `close_budget_ok` |

---

## Step 5: Final Document Package
**Action:** Assemble closeout document set

### Required Closeout Documents
| Document | Description | Source |
|---|---|---|
| As-built drawings | Updated plans reflecting actual construction | Plans → upload |
| O&M manuals | Equipment operation & maintenance guides | Subs provide |
| Warranty documents | Manufacturer & sub warranties | Documents folder |
| Lien waivers (final) | All subs/vendors final waivers | Bills → Lien Waiver |
| Certificate of Occupancy | From municipality | Upload to Documents |
| Certificate of Substantial Completion | Signed by owner/architect | Upload to Documents |
| Final inspection reports | All passed inspections | Daily Logs or Documents |
| Final photos | Completion photography | Photos folder |
| Punch list completion report | All items verified complete | Tasks → Punch List |
| Final payment certification | Proof of final payment | Invoices → Payments |

### Upload to BT
```
browser → navigate to https://buildertrend.net/app/Documents/Standard/0
browser → snapshot → create "Closeout Documents" folder if needed
browser → snapshot → upload each document
browser → snapshot → verify all files uploaded
```

### Share via Client Portal
```
browser → snapshot → set document visibility to include Client
browser → snapshot → notify client of available documents
```

---

## Step 6: Final Photo Documentation
**Action:** Ensure completion photos are filed

```
browser → navigate to https://buildertrend.net/app/Photos/Standard/0
browser → snapshot → verify completion photos exist
browser → snapshot → organize into "Closeout" or "Completion" album
```

**Photo checklist:**
- ☐ Exterior (all sides)
- ☐ Interior (each room/space)
- ☐ MEP installations
- ☐ Finishes closeup
- ☐ Site restoration (landscaping, parking, etc.)

---

## Step 7: Set Up Warranty Period
**Action:** Transition job to Warranty status

```
browser → navigate to https://buildertrend.net/app/JobPage/{jobId}/1
browser → snapshot → find Status dropdown
browser → snapshot → change Status from "Open" to "Warranty"
browser → snapshot → set Actual Completion date
browser → snapshot → click "Save"
browser → snapshot → verify status updated
```

**Warranty Period:**
- Start date = Actual Completion / Substantial Completion date
- Duration: Per contract (company standard: confirm with the user, typically 1 year)
- During warranty: clients can submit claims via portal
- See `warranty-management.md` for warranty claim workflows

**Message to the user:**
```
🔧 Warranty Period Started:
• Project: [name]
• Completion date: [date]
• Warranty expires: [date]
• Client can submit claims via portal
```

---

## Step 8: Archive Job (Close)
**Action:** Close the job when warranty period complete (or immediately if no warranty)

### Close Without Warranty Period
```
browser → navigate to https://buildertrend.net/app/JobPage/{jobId}/1
browser → snapshot → change Status to "Closed"
browser → snapshot → click "Save"
```

### Close After Warranty
After warranty period expires and all claims resolved:
```
browser → navigate to https://buildertrend.net/app/JobPage/{jobId}/1
browser → snapshot → verify no open warranty claims
browser → snapshot → change Status from "Warranty" to "Closed"
browser → snapshot → click "Save"
```

**Closed jobs:**
- Remain accessible in Jobs List (filter by Closed status)
- All data preserved for historical reference
- Can be recovered if accidentally closed (Jobs List → Filter → Only Show Deleted → Restore)

---

## Step 9: Post-Closeout Actions (Company-Specific)

### Update Google Drive
- Move active project files to completed/archived section
- Ensure all documents from BT are backed up to Drive
- Folder: `Projects/[Project Name]/Other Documents/Closeout`

### Update Apple Reminders
```
remindctl complete "Company - [Project]" (all remaining items)
```
Or delete the project list if all tasks are done.

### Notify All Agents
Send internal notification:
- **Bookkeeper agent:** Job closed — final QBO reconciliation needed, no more BT-QBO syncs expected
- **Receipt agent:** No more receipts expected for this project code
- **Procurement agent:** No more procurement for this project
- **CRM agent:** Client satisfaction follow-up opportunity
- **Property agent:** If applicable — tenant handover

### Update Project Registry
Follow the project remove procedure in `AGENTS.md`:
- Update `SKILLS/project-registry.json`
- Update all agent config files
- Remove Apple Reminders list for the project

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Open bills remaining | List unpaid bills, ask the user to resolve |
| Missing lien waivers | Send waiver request to subs via BT |
| Punch list items open | List items, ask if OK to close anyway |
| Final invoice not paid | Flag balance due, hold closeout |
| QBO out of sync | Run BT-QBO reconciliation first |
| Client disputes final amount | Hold closeout, create CO or credit memo |

---

## Quick Reference: Job Status Flow

```
Pre-Sale → Open → Warranty → Closed
               ↗              ↗
(skip warranty if not applicable)
```

| Status | When to Use |
|---|---|
| Pre-Sale | Lead/estimating stage |
| Open | Active construction |
| Warranty | Complete, monitoring warranty claims |
| Closed | All obligations finished |

---

## Learning Academy Reference
- **Course:** "Project Closeout & Warranty Management (NEW)" — 6 activities
- **Course:** "Collaborating with Clients and Subs (NEW)" — 8 activities (closeout section)
- **Topics:** Walkthroughs, warranty tracking, handover documentation

---

## Company-Specific Notes
- All 6 active jobs visible in BT sidebar
- Closeout documents → Google Drive project folder → `Other Documents/Closeout`
- Final photos → Drive → `Other Documents/Completion Photos`
- Project registry update required → `SKILLS/project-registry.json`
- Coordinate with all agents on project closure
- Company naming: keep project folder in Drive even after BT close (archival)
