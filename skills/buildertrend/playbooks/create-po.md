# Create Purchase Order (Agent-Assisted)

## Overview

> **UI Reference:** See `bt-ui-patterns.md` for combobox dropdown, modal, grid, and navigation patterns used in this playbook.
When {{company_name}} needs to formally assign scope and budget to a subcontractor or vendor, the agent guides the user through creating a Purchase Order in Buildertrend — suggesting cost codes based on vendor type, filling scope of work, adding line items, linking to schedule items, and optionally releasing to the sub for signature.

## Trigger
- the user says "create PO for [vendor]" or "PO for [project]"
- procurement agent () requests a PO be created in BT after sourcing a vendor
- After a bid is approved and needs to become a PO
- Change Order approved → PO needed for the added scope

---

## Step 1: Identify Project
**Action:** Confirm which project the PO is for

**Message to the user:**
```
📦 Creating a Purchase Order — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_po_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_po_project_1` |
| 🏗️ Project Beta | `primary` | `bt_po_project_2` |
| 🏗️ Project Beta | `primary` | `bt_po_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_po_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_po_project_4` |
| 🏗️ Project Eta | `primary` | `bt_po_project_5` |
| ❌ Cancel | `danger` | `bt_po_cancel` |

---

## Step 2: Identify Vendor/Sub & Scope
**Action:** Ask who the PO is for and what work it covers

**Message to the user:**
```
📦 PO for [project] — who is this for?
(Type vendor/sub name, or pick from recent)
```

**If BT has subs on the job, show inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔨 [Sub 1 name] | `primary` | `bt_po_vendor_[id]` |
| 🔧 [Sub 2 name] | `primary` | `bt_po_vendor_[id]` |
| ➕ New Vendor | `primary` | `bt_po_vendor_new` |
| ❌ Cancel | `danger` | `bt_po_cancel` |

**On response, ask for scope:**
```
What's the scope of work?
(Quick description — e.g., "Framing for 3rd floor", "Install kitchen cabinets", "Demo bathroom")
```

---

## Step 3: Suggest Cost Codes
**Action:** Based on vendor type/name and scope, suggest cost codes

### Cost Code Suggestion Logic by Vendor Trade
| Vendor Trade / Keywords | Suggested Cost Codes |
|---|---|
| Plumber, plumbing | 07.00 Plumbing, 07.10 Fixtures, 07.20 Gas piping |
| Electrician, electrical | 08.00 Electrical, 08.10 Lighting, 08.20 Low Voltage |
| HVAC, mechanical | 09.00 HVAC, 09.10 Controls, 09.20 Ductwork |
| Framing, carpentry | 05.00 Carpentry/Framing, 05.05 Non-Structural |
| Drywall, insulation | 10.00 Insulation & Drywall, 10.10 Framing, 10.20 Insulation |
| Painter, painting | 14.00 Painting and Coating, 14.10 Interior, 14.15 Exterior |
| Flooring, tile | 15.00 Flooring & Tile, 15.10 Tile, 15.20 Wood Floor |
| Demo, demolition | 20.10 Demolition, 20.20 Abatement |
| Millwork, cabinet | 12.00 Carpentry/Millwork, 12.10 Millwork, 12.20 Cabinets |
| Glass, glazier | 11.00 Glazing, 11.10 Glass, 11.15 Mirror |
| Mason, concrete | 04.00 Excavation/Foundation, 17.00 Brick & Masonry |
| Roofer | 06.00 Roofing, 06.10 Shingles, 06.20 Membrane |
| Steel, iron | 35.00 Structural Steel, 21-20 Metal Fabrications |
| Fire protection | 25.10 Fire Protection, 25.15 Sprinklers |
| Fire alarm | 27.00 Fire Alarm, 27.10 Detection |
| Scaffold | 32.00 Scaffolding/Sheds, 32.10 Sidewalk Sheds |
| Cleaning | 19.00 Cleaning, 19.10 Final Clean |
| Countertops | 28.00 Countertops, 28.10 Fabrication |
| Windows, doors | 13.00 Windows & Doors, 13.10 Windows, 13.20 Doors |
| AV, security, camera | 26.00 Audio Visual/Security |
| Equipment rental | 39.00 Rental Equipment |
| Dumpster, waste | 02.10 Dumpster, 02.00 General Requirements |

**Message to the user:**
```
💰 Suggested cost code for [vendor]: [XX.XX] [Name]
Based on: [trade match / scope keywords]

Use this code for PO line items?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ [Suggested code] | `success` | `bt_po_code_XX.XX` |
| 🔧 [2nd suggestion] | `primary` | `bt_po_code_YY.YY` |
| 📋 Show all categories | `primary` | `bt_po_code_list` |
| ✏️ Multiple codes | `primary` | `bt_po_code_multi` |

---

## Step 4: Line Items & Amount
**Action:** Build the PO line items

**Message to the user:**
```
📝 PO Line Items for [vendor] — [project]:

How should I structure this?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💵 Single line (lump sum) | `primary` | `bt_po_lines_single` |
| 📋 Multiple lines (itemized) | `primary` | `bt_po_lines_multi` |
| 📥 Pull from Estimate | `primary` | `bt_po_lines_estimate` |
| 📥 Pull from Change Order | `primary` | `bt_po_lines_co` |

### Single Line:
```
What's the total PO amount?
```

### Multiple Lines:
```
List your line items (one per line):
Format: Description — $Amount
Example:
Rough plumbing — $8,500
Fixtures install — $3,200
Testing & inspection — $1,500
```

### Pull from Estimate:
Navigate to `/app/Estimate` → find matching cost codes → present line items with amounts from estimate → ask which to include.

### Pull from Change Order:
Navigate to `/app/ChangeOrders` → list approved COs → let the user pick → pull CO line items into PO.

---

## Step 5: Additional PO Details
**Action:** Collect deadline, schedule link, and materials flag

**Message to the user:**
```
📦 PO Details:

📅 Deadline: [suggest based on schedule if available]
🔗 Link to schedule item? [if schedule items exist]
📦 Materials only? (no labor)
📝 Scope of work notes?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📅 Set Deadline | `primary` | `bt_po_deadline` |
| 🔗 Link to Schedule | `primary` | `bt_po_schedule_link` |
| 📦 Materials Only | `primary` | `bt_po_materials_only` |
| ⏭️ Skip — Use Defaults | `success` | `bt_po_defaults` |

---

## Step 6: Final Approval
**Action:** Present complete PO summary

**Message to the user:**
```
📦 Purchase Order Ready:

🏗️ Project: [project name]
👷 Vendor: [vendor/sub name]
📋 Title: [auto-generated: "PO - [Vendor] - [Scope summary]"]
💰 Cost Code: [XX.XX] [Name]

📝 Line Items:
| # | Description | Cost Type | Amount |
|---|-------------|-----------|--------|
| 1 | [item 1]    | [type]    | $X,XXX |
| 2 | [item 2]    | [type]    | $X,XXX |

📊 Total: $[total]
📅 Deadline: [date or "None"]
🔗 Schedule: [linked item or "None"]

Create this PO?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create & Save (Draft) | `success` | `bt_po_create_draft` |
| 📤 Create & Release to Sub | `success` | `bt_po_create_release` |
| ✏️ Edit Details | `primary` | `bt_po_edit` |
| ❌ Cancel | `danger` | `bt_po_cancel` |

---

## Step 7: Create PO via Browser Relay
**Action:** Execute in Buildertrend

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/PurchaseOrders`
3. Click "Create new Purchase Order" button (+ Purchase Order) → select "Purchase Order"
4. In the PO form:
   - Set **Title** (e.g., "PO - ABC Plumbing - Rough plumbing 3rd floor")
   - Set **Assignee** (combobox) → select the vendor/sub
   - Set **Scope of Work** (rich text) → enter scope description
   - Set **Deadline** (date picker) if specified
   - Check **Materials Only** if applicable
   - **Line Items section:**
     - Click "+ Item" for each line
     - Set: Title, Cost Code (combobox), Cost Type, Unit Cost, Quantity, Unit
     - Verify Builder Cost matches expected amount
   - Optionally: **Link to Schedule Item** if requested
5. If **Draft:** Click **Save** (does NOT send to sub)
6. If **Release:** Click **Send** (releases to sub for review/signature)
7. Snapshot → confirm PO created

**Report back:**
```
✅ PO created in Buildertrend!

📦 PO #[number]: $[total]
🏗️ Project: [project]
👷 Vendor: [vendor]
📋 Status: [Draft / Released]
[If released: "📧 Sent to [vendor email] for approval"]
```

---

## Step 8: Post-Creation Actions
**Message to the user (if Draft):**
```
PO saved as Draft. What next?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Release to Sub Now | `success` | `bt_po_release` |
| 📊 Push to QuickBooks | `primary` | `bt_po_qb_push` |
| 💾 Leave as Draft | `primary` | `bt_po_leave` |

**Post-creation tasks:**
1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — track PO approval status
3. **Notify procurement agent** — PO created for vendor, amount, status
4. **Notify bookkeeper agent** — new PO in BT, may generate bills later

---

## Variance PO Flow
When creating a PO for unexpected/unplanned costs:

1. In Step 6, add option:

**Inline button:**
| Button | Style | callback_data |
|---|---|---|
| ⚠️ Create as Variance PO | `primary` | `bt_po_variance` |

2. If Variance: Check "Mark as Variance" in form
3. Select **Variance Code** (e.g., "72 – Client Change Order" for client-initiated)
4. Optionally link to **Referenced Purchase Order** or **Change Order**
5. Variance POs flow to "Committed Costs" in budget → visible in Variance column

---

## Creating PO from Change Order
Shortcut when a CO is approved and needs a PO:

1. Navigate to `/app/ChangeOrders`
2. Find the approved CO
3. Click **"Add Purchase Order"** from the CO row
4. BT pre-fills: cost codes, amounts, description from CO
5. Add vendor/sub assignment
6. Review → Save or Release

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save PO details for resume |
| Vendor not in BT | Ask the user to add vendor first (Users → Subs/Vendors → New) or use "M Misc" |
| Vendor not on this job | Ask the user to add vendor to job (Job Details → Subs/Vendors tab) |
| Cost code not found | Suggest closest match or ask the user to create in Settings → Cost Codes |
| PO amount exceeds budget | Warn: "This PO ($X) exceeds the budgeted amount ($Y) for [cost code] by $Z" |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |
| Schedule item not found | Skip schedule link, continue with PO creation |
| Duplicate PO detected | Warn: "PO already exists for [vendor] on this project — PO #[number], $[amount]" |

---

## PO Status Lifecycle

| Status | Meaning | Next Action |
|---|---|---|
| Draft | Created but not sent | Release to sub |
| Released | Sent to sub/vendor | Awaiting approval |
| Approved | Sub signed off | Can create bills against it |
| Declined | Sub rejected | Review & amend or cancel |
| Amended | Changes made post-approval | Resend for re-approval |
| Complete | All billed, work done | Mark work complete |

---

## Batch Mode
When creating multiple POs (e.g., after winning a project):

1. List all trades/subs needed
2. Ask the user: "Create POs for all subs, or pick specific ones?"
3. If all: loop through Steps 2-7 for each vendor
4. Batch the project selection (Step 1) — same project for all
5. Show running summary: "Created 4/8 POs — $125,000 committed"

---

## Cost Code Quick Reference (Common PO Trades)

| Trade | Primary Code | Secondary Codes |
|---|---|---|
| Plumber | 07.00 | 07.10, 07.20, 07.30, 07.40 |
| Electrician | 08.00 | 08.10, 08.20 |
| HVAC | 09.00 | 09.10, 09.20, 09.30 |
| Framer | 05.00 | 05.05 |
| Drywall/Insulation | 10.00 | 10.10, 10.20, 10.30, 10.31 |
| Painter | 14.00 | 14.10, 14.15, 14.25 |
| Flooring/Tile | 15.00 | 15.10, 15.20, 15.30 |
| Millwork | 12.00 | 12.10, 12.20, 12.30, 12.40 |
| Demo | 20.10 | 20.20, 20.30 |
| Mason | 17.00 | 17.10, 17.15 |
| Steel | 35.00 | 35.10, 35.20 |
| Fire Protection | 25.10 | 25.15, 25.20, 25.25 |
| Glazier | 11.00 | 11.10, 11.15 |
| Scaffold | 32.00 | 32.10, 32.20 |
