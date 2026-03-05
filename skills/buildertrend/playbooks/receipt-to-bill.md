# Receipt → Bill Workflow (Agent-Assisted)

## Overview

> **UI Reference:** See `bt-ui-patterns.md` for combobox dropdown, modal, grid, and navigation patterns used in this playbook.
When an agent (receipt agent or the agent) sees a new receipt in Buildertrend's Cost Inbox, this workflow guides it through assigning the receipt to a project, suggesting a cost code, getting approval, and creating the bill.

## Trigger
- Agent detects new receipt(s) in Cost Inbox (`/app/Receipts`) with status "New"
- OR receipt agent uploads a receipt to BT Cost Inbox
- OR the user forwards a receipt and says "add to Buildertrend"

---

## Step 1: Read the Receipt
**Action:** Navigate to `/app/Receipts` → click the receipt → extract details

**Extract:**
| Field | Source |
|---|---|
| Vendor name | OCR / title |
| Amount | OCR / amount column |
| Date | Purchase date |
| Line items | OCR detail (if available) |
| Current status | Status column |
| Current job assignment | Job column (may be blank) |
| Current cost code | Cost code column (may be blank) |

**Present to the user:**
```
🧾 New receipt detected in BT Cost Inbox:
• Vendor: [vendor]
• Amount: $[amount]
• Date: [date]
• Items: [line items summary if available]
• Currently assigned: [job if any, or "Unassigned"]
```

---

## Step 2: Ask for Project Assignment
**Action:** Present project options with inline buttons

**Logic:**
1. Check vendor name against known project vendors (from project-registry.json)
2. Check if receipt was uploaded with a job already assigned
3. If match found → suggest it as default
4. Always show all active projects as options

**Message to the user:**
```
Which project does this belong to?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_project_1` |
| 🏗️ Project Beta | `primary` | `bt_project_2` |
| 🏗️ Project Beta | `primary` | `bt_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_project_4` |
| 🏗️ Project Eta | `primary` | `bt_project_5` |
| 📁 Admin (indirect) | `primary` | `bt_project_ADMIN` |
| ⏭️ Skip | `danger` | `bt_project_skip` |

If vendor/items suggest a likely project, add ⭐ to that button and list it first.

**On response:** Store selected project, proceed to Step 3.

---

## Step 3: Suggest Cost Code
**Action:** Based on vendor name, line items, and amount — suggest the most likely cost code(s)

**Cost Code Suggestion Logic:**

### By Vendor Name Pattern
| Vendor Pattern | Suggested Cost Code |
|---|---|
| Home Depot, Lowe's, lumber yards | 41.10 Materials - General |
| Electrical supply, electrical sub | 08.00 Electrical |
| Plumbing supply | 07.00 Plumbing |
| Paint store, Benjamin Moore, Sherwin | 14.00 Painting and Coating |
| Hardware store | 01.00 General Conditions |
| Flooring, tile supply | 15.00 Flooring & Tile |
| Glass, mirror | 11.00 Glazing |
| HVAC supply | 09.00 HVAC |
| Concrete, masonry | 17.00 Brick & Masonry |
| Steel, metal fab | 21-20 Metal Fabrications |
| Dumpster, waste | 02.00 General Requirements |
| Scaffold, shed rental | 32.00 Scaffolding / Sheds |
| Equipment rental | 39.00 Rental Equipment |
| Cleaning service | 19.00 Cleaning |
| Demo contractor | 20.10 Demolition |
| Insurance | 00-01 Insurance (NON-BILLABLE) |
| Auto/vehicle | 00.09 Auto Expenses (NON-BILLABLE) |
| Office supplies, tech | 00.06 Technology / 00.08 General Admin (NON-BILLABLE) |
| Restaurant, food, catering | 01.00 General Conditions |

### By Line Item Keywords
| Keyword | Suggested Cost Code |
|---|---|
| lumber, wood, plywood, 2x4 | 05.00 Carpentry / Framing |
| wire, conduit, outlet, switch | 08.00 Electrical |
| pipe, fitting, valve | 07.00 Plumbing |
| drywall, joint compound, tape | 10.00 Insulation & Drywall |
| paint, primer, roller, brush | 14.00 Painting and Coating |
| tile, grout, thinset | 15.00 Flooring & Tile |
| door, hardware, lockset | 13.00 Windows & Doors |
| window, glass | 11.00 Glazing / 13.00 Windows & Doors |
| concrete, rebar, form | 04.00 Excavation Foundation |
| insulation | 10.00 Insulation & Drywall |
| cabinet, trim, molding | 12.00 Carpentry / Millwork |
| countertop | 28.00 Countertops |
| fire extinguisher, sprinkler | 25.10 Fire Protection |
| camera, alarm, security | 26.00 Audio Visual / Security |
| ceiling tile, grid | 22.10 Ceilings |

**Message to the user:**
```
💰 Suggested cost code: [XX.XX] [Name]
Based on: [reason — vendor match / line item match]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ [Suggested code + name] | `success` | `bt_costcode_XX.XX` |
| 🔧 [2nd suggestion if applicable] | `primary` | `bt_costcode_YY.YY` |
| 📋 Show all categories | `primary` | `bt_costcode_list` |
| ⏭️ Skip cost code | `danger` | `bt_costcode_skip` |

**If "Show all categories" selected:** Show the 43 BILLABLE categories as pages (10 per message) with buttons.

**On response:** Store selected cost code, proceed to Step 4.

---

## Step 4: Final Approval — Create Bill
**Action:** Present complete bill summary for approval

**Message to the user:**
```
📋 Ready to create bill in Buildertrend:

🧾 Receipt: [vendor] — $[amount]
📅 Date: [date]
🏗️ Project: [project name]
💰 Cost Code: [XX.XX] [code name]
📝 Items: [line items if available]

Create this bill?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create Bill | `success` | `bt_bill_create` |
| ✏️ Edit Details | `primary` | `bt_bill_edit` |
| ❌ Cancel | `danger` | `bt_bill_cancel` |

**On "Create Bill":**

### Browser Relay Execution
1. Navigate to `/app/Receipts`
2. Click the receipt row
3. Click "Create Bill" button
4. In bill form:
   - Verify/set **Job** to selected project
   - Verify/set **Cost Code** on line items to selected code
   - Verify **vendor/amount/date** match receipt
   - Set status: **Draft** (safe — the user can finalize)
5. Click **Save**
6. Snapshot → confirm bill was created
7. Report back:

```
✅ Bill created in Buildertrend!
• Bill #: [number]
• Job: [project]
• Vendor: [vendor]  
• Amount: $[amount]
• Cost Code: [XX.XX]
• Status: Draft
• QBO sync: [pending/synced]
```

**On "Edit Details":** Ask which field to change → loop back to relevant step.

**On "Cancel":** Acknowledge and stop.

---

## Step 5: Post-Creation (Automatic)
After bill is created:

1. **Update Apple Reminders** — mark receipt as processed if tracked
2. **Log to daily memory** — `memory/YYYY-MM-DD.md`
3. **Notify bookkeeper agent** (if agent-to-agent is enabled) — new bill in BT, may appear in QBO
4. **Check QBO sync status** — if QBO is connected in BT, verify the bill pushed

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save state for resume |
| Receipt already has a bill | Report to the user: "This receipt already has a linked bill: [bill #]" |
| Cost code not found in BT | Suggest closest match or ask the user to create it |
| OCR misread amount | Flag discrepancy: "OCR says $X but receipt shows $Y" |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## Batch Mode
When multiple receipts are in the Cost Inbox:

1. List all "New" receipts with vendor + amount
2. Ask the user: "Process all, or pick specific ones?"
3. If all: loop through Steps 1-4 for each, **but batch the project question** if same vendor
4. Show running total: "Processed 3/7 receipts — $1,234.56 total"

---

## Cost Code Quick Reference (Top 20 Most Used)

| Code | Name | Common Vendors |
|---|---|---|
| 01.00 | General Conditions | Misc, food, general |
| 02.00 | General Requirements | Dumpsters, permits, safety |
| 05.00 | Carpentry / Framing | Lumber yards |
| 07.00 | Plumbing | Plumbing supply |
| 08.00 | Electrical | Electrical supply, Naed |
| 09.00 | HVAC | HVAC supply |
| 10.00 | Insulation & Drywall | Drywall supply |
| 12.00 | Carpentry / Millwork | Millwork shops |
| 13.00 | Windows & Doors | Door/window vendors |
| 14.00 | Painting and Coating | Paint stores |
| 15.00 | Flooring & Tile | Tile/flooring supply |
| 20.10 | Demolition | Demo contractors |
| 28.00 | Countertops | Countertop vendors |
| 32.00 | Scaffolding / Sheds | Scaffold rental |
| 39.00 | Rental Equipment | Equipment rental |
| 41.10 | Materials - General | Home Depot, Lowe's |
| 00-01 | Insurance (NON-BILL) | Insurance companies |
| 00.08 | General Admin (NON-BILL) | Office, tech, misc |
| 00.09 | Auto Expenses (NON-BILL) | Gas, vehicle |
| 00.07 | Material Purchases (NON-BILL) | Non-project materials |
