# Home Depot Pro Xtra Integration (Agent-Assisted)

## Overview
Buildertrend integrates with Home Depot's Pro Xtra loyalty program to automatically import purchase receipts, map them to jobs and cost codes, and streamline bill creation. This eliminates manual receipt entry for HD purchases and provides real-time material cost tracking across projects.

## Trigger
- the user says "connect Home Depot", "check HD receipts", "map HD purchase to [project]"
- New HD receipt appears in BT Cost Inbox (auto-imported)
- Monthly reconciliation of HD purchases across jobs
- Receipt from local HD store needs processing
- Receipt agent detects HD receipt that should route to BT

---

## Step 1: Connect HD Pro Xtra Account
**Action:** Link Home Depot Pro Xtra account to Buildertrend

### Settings URL
```
browser → navigate to https://buildertrend.net/app/Settings/TheHomeDepotSettings
browser → snapshot → verify Home Depot integration settings page
```

### Connection Steps
```
browser → snapshot → click "Connect" or "Link Account" button
⚠️ HAND OFF TO USER — the user enters HD Pro Xtra account credentials directly (agent does not handle credentials)
browser → snapshot → authorize Buildertrend to access purchase data
browser → snapshot → verify connection status shows "Connected"
```

**Message to the user:**
```
🏠 Home Depot Pro Xtra Integration:
• Status: [Connected / Not Connected]
• Account: [HD Pro Xtra account identifier]
• Auto-import: [Enabled / Disabled]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Looks Good | `success` | `hd_confirm` |
| 🔧 Configure Settings | `primary` | `hd_settings` |
| 🔌 Connect Account | `primary` | `hd_connect` |

---

## Step 2: Automatic Receipt Import
**Action:** HD purchases auto-import into BT Cost Inbox

### How It Works
1. Employee makes purchase at Home Depot using Pro Xtra account
2. HD sends purchase data to Buildertrend
3. Receipt appears in Cost Inbox (`/app/Receipts`) with:
   - Vendor: Home Depot
   - Date: Purchase date
   - Amount: Total
   - Line items: Individual items purchased (from HD SKU data)
   - Status: New

### Viewing Imported Receipts
```
browser → navigate to https://buildertrend.net/app/Receipts
browser → snapshot → filter by Sub/Vendor → "Home Depot"
browser → snapshot → review imported receipts
```

**Known HD receipts in BT (from Phase 1 mapping):**
| Receipt | Amount | Date | Status |
|---|---|---|---|
| HD receipt #XXXX-XX-XXXX | $XXX.XX | [date] | New |
| HD receipt #XXXX-XX-XXXX | $XXX.XX | [date] | New |
| HD receipt #XXXX-XX-XXXX | $XXX.XX | [date] | New |
| Bill from HD material | $XXX.XX | [date] | Linked to Bill |

---

## Step 3: Map HD Purchases to Jobs
**Action:** Assign imported HD receipts to the correct project

```
browser → snapshot → click on HD receipt in Cost Inbox
browser → snapshot → review line items and amount
browser → snapshot → select Job from dropdown
browser → snapshot → save assignment
```

**Smart Suggestion Logic:**
| Purchase Pattern | Suggested Job |
|---|---|
| Receipt date matches active job schedule | That job |
| Employee assigned to one job | That job |
| Previous HD purchases mapped to a job | Same job |
| Items match job scope (e.g., plumbing for plumbing phase) | Matching job |

**Message to the user:**
```
🧾 HD Receipt — $[amount] ([date]):
Items: [line items summary]

Which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `hd_job_1` |
| 🏗️ Project Alpha | `primary` | `hd_job_1` |
| 🏗️ Project Beta | `primary` | `hd_job_2` |
| 🏗️ Project Beta | `primary` | `hd_job_2` |
| 🏗️ Project Epsilon | `primary` | `hd_job_3` |
| 🏗️ Project Gamma | `primary` | `hd_job_4` |
| 🏗️ Project Eta | `primary` | `hd_job_5` |
| 📁 Admin (indirect) | `primary` | `hd_job_ADMIN` |

---

## Step 4: Assign Cost Codes to HD Items
**Action:** Map HD line items to appropriate cost codes

### HD Item → Cost Code Mapping
| HD Item Category | Suggested Cost Code | {{company_name}} Code |
|---|---|---|
| Lumber, plywood, studs | Carpentry / Framing | 05.00 – 05.05 |
| Electrical wire, outlets, switches | Electrical | 08.00 – 08.20 |
| Pipe, fittings, valves | Plumbing | 07.00 – 07.40 |
| Paint, primer, rollers | Painting and Coating | 14.00 – 14.25 |
| Drywall, joint compound | Insulation & Drywall | 10.00 – 10.31 |
| Tile, grout, thinset | Flooring & Tile | 15.00 – 15.30 |
| Doors, hardware, locksets | Windows & Doors | 13.00 – 13.35 |
| Concrete mix, rebar | Excavation Foundation | 04.00 – 04.40 |
| Cleaning supplies | Cleaning | 19.00 – 19.10 |
| Safety equipment | General Requirements | 02.00 – 02.45 |
| Tools (general) | General Conditions | 01.00 – 01.50 |
| Misc materials | Materials - General | 41.10 |

```
browser → snapshot → open HD receipt
browser → snapshot → review auto-suggested cost code (or "Buildertrend Flat Rate")
browser → snapshot → change cost code to correct company code
browser → snapshot → save
```

---

## Step 5: Create Bill from HD Receipt
**Action:** Convert HD receipt to a bill in BT

### From Cost Inbox
```
browser → snapshot → open HD receipt in Cost Inbox
browser → snapshot → click "Create Bill" button
browser → snapshot → verify bill form pre-fills with HD data:
  - Title: HD receipt number
  - Pay To: Home Depot
  - Amount: Receipt total
  - Line items: From HD data
  - Cost Code: Assigned code (or Flat Rate if unassigned)
browser → snapshot → verify/update Job assignment
browser → snapshot → verify/update Cost Code
browser → snapshot → click "Save"
browser → snapshot → verify bill created
```

### Auto-Fill from File (OCR)
If HD receipt is a scan/photo:
```
browser → snapshot → in Bill creation, click "Auto-fill from file"
browser → snapshot → upload HD receipt image (.pdf, .jpg, .png)
browser → snapshot → OCR extracts vendor, date, amount, line items
browser → snapshot → review/correct OCR results
browser → snapshot → save bill
```

**Message to the user:**
```
✅ Bill created from HD receipt:
• Bill #: [number]
• Vendor: Home Depot
• Amount: $[amount]
• Job: [project]
• Cost Code: [XX.XX] [name]
• Date: [purchase date]
• QB Sync: [pending/auto]
```

---

## Step 6: Reconcile HD Receipts with BT Bills
**Action:** Monthly reconciliation of HD purchases

### Reconciliation Checklist
```
browser → navigate to https://buildertrend.net/app/Receipts
browser → snapshot → filter: Sub/Vendor = Home Depot, Status = New
browser → snapshot → count unprocessed HD receipts
```

**For each unprocessed receipt:**
1. Open receipt → verify amount matches HD statement
2. Assign to correct job
3. Assign proper cost code
4. Create bill
5. Mark receipt as processed

### Cross-Reference with HD Pro Xtra Statement
- Compare BT Cost Inbox receipts vs HD Pro Xtra monthly statement
- Flag any missing receipts (HD purchase not in BT)
- Flag any duplicate receipts

**Message to the user:**
```
📊 HD Pro Xtra Reconciliation — [Month]:
• Receipts imported: [X]
• Bills created: [Y]
• Unprocessed: [Z]
• Total HD spend: $[amount]
• By project:
  - [Project A]: $[amount] ([count] receipts)
  - [Project B]: $[amount] ([count] receipts)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ All Reconciled | `success` | `hd_reconciled` |
| 🧾 Process Remaining | `primary` | `hd_process_remaining` |
| 📋 Export Report | `primary` | `hd_export` |

---

## Step 7: Purchase Tracking by Job
**Action:** View all HD purchases grouped by project

```
browser → navigate to https://buildertrend.net/app/Bills
browser → snapshot → filter: Pay To = Home Depot
browser → snapshot → group/sort by Job
browser → snapshot → read totals per project
```

**Alternative:** From Job Costing Budget per job:
```
browser → navigate to https://buildertrend.net/app/JobCostingBudget
browser → snapshot → filter by Related Items → Bills
browser → snapshot → look for Home Depot bills per cost code
```

---

## Batch Mode: Process Multiple HD Receipts
When multiple HD receipts are waiting:

1. Navigate to Cost Inbox → filter by Home Depot + Status: New
2. List all pending receipts with amounts
3. Ask the user: "Process all to same project, or assign individually?"
4. If same project: batch-assign job + cost codes
5. Create bills for each receipt
6. Report running total

**Message to the user:**
```
🧾 [X] HD receipts pending in Cost Inbox:
1. #XXXX-XX-XXXX — $XXX.XX (Jan 25)
2. #XXXX-XX-XXXX — $XXX.XX (Jan 23)
3. #XXXX-XX-XXXX — $XXX.XX ([date])
Total: $465.11

Process all to same project or assign individually?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ All → [Suggested Project] | `success` | `hd_batch_project` |
| 📋 Assign Individually | `primary` | `hd_individual` |
| ⏭️ Later | `danger` | `hd_later` |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| HD account not connected | Navigate to Settings → Home Depot → Connect |
| Receipt not auto-importing | Check HD Pro Xtra account link, manual upload fallback |
| OCR misread HD receipt | Flag discrepancy, manually correct |
| Duplicate receipt imported | Compare amounts/dates, delete duplicate |
| Cost code "Buildertrend Flat Rate" | Replace with proper company cost code before QB sync |
| HD return/credit | Process as negative bill or credit memo |

---

## Lowe's PRO Integration
BT also supports Lowe's PRO integration:
**Settings URL:** `/app/Settings/LowesSettings`
- Similar workflow: Link account → auto-import → map to jobs → create bills
- Use when purchasing from Lowe's instead of HD

---

## Company-Specific Notes
- **Primary HD Store:** Configure your local store ID and address
- **HD Settings URL:** `/app/Settings/TheHomeDepotSettings`
- **Lowe's Settings URL:** `/app/Settings/LowesSettings`
- **Receipt naming standard:** `YYYY-MM-DD_HomeDepot_$Amount_ProjectCode.ext`
- **HD receipt flow:** HD purchase → BT Cost Inbox → assign job/code → create bill → QB sync
- Receipt agent may also process HD receipts via the receipt skill — coordinate to avoid duplicates
- HD Pro pricing available through Apify/SerpApi for comparison (see TOOLS.md)

## Learning Academy Reference
- **Course:** "Home Depot Pro Xtra" — 6 activities, 25 min
- **Topics:** Account linking, receipt import, job mapping, reconciliation
