# Create & Manage Estimates (Agent-Assisted)

## Overview
the agent guides the user through building estimates in Buildertrend — creating line items with cost codes and markup, importing from templates or the cost catalog, organizing into groups/sections, calculating client pricing, managing allowances, locking/unlocking estimate versions, creating formatted proposals for clients, and feeding the estimate into the job costing budget. This is the financial foundation of every project.

## Trigger
- the user says "create estimate for [project]" or "build an estimate"
- the user says "add to estimate" or "update the estimate on [project]"
- the user says "send proposal to client" or "create a proposal"
- New job created and needs an estimate
- Lead proposal needs to be created or updated
- the user says "send estimate to budget"

---

## Step 1: Identify Project & Mode
**Action:** Determine project and whether this is a job estimate or lead proposal

**Message to the user:**
```
📊 Estimates — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_est_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_est_project_1` |
| 🏗️ Project Beta | `primary` | `bt_est_project_2` |
| 🏗️ Project Beta | `primary` | `bt_est_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_est_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_est_project_4` |
| 🏗️ Project Eta | `primary` | `bt_est_project_5` |
| 📋 Lead Proposal | `primary` | `bt_est_lead` |
| ❌ Cancel | `danger` | `bt_est_cancel` |

**If Lead Proposal selected, show leads:**
| Button | Style | callback_data |
|---|---|---|
| Project Alpha (85%) | `primary` | `bt_est_lead_1` |
| 1416 Jefferson (77%) | `primary` | `bt_est_lead_jefferson` |
| 23-29 Astoria (75%) | `primary` | `bt_est_lead_astoria` |
| 📋 Show All Leads | `primary` | `bt_est_lead_all` |

**On project selected:**
```
📊 What would you like to do?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 View Current Estimate | `primary` | `bt_est_view` |
| ➕ Add Line Items | `success` | `bt_est_add` |
| 📥 Import from Template | `primary` | `bt_est_import_template` |
| 📥 Import from Catalog | `primary` | `bt_est_import_catalog` |
| 📥 Import from Excel | `primary` | `bt_est_import_excel` |
| 📄 Create Proposal | `primary` | `bt_est_proposal` |
| 📊 Send to Budget | `primary` | `bt_est_to_budget` |
| 🔒 Lock / Unlock | `primary` | `bt_est_lock` |
| ❌ Cancel | `danger` | `bt_est_cancel` |

---

## Step 2A: View Current Estimate
**Action:** Read the estimate and present a summary

### Browser Relay — Read Estimate
1. Ensure correct job selected in BT left sidebar
2. Navigate to `/app/Estimate`
3. Snapshot → read the estimate table
4. Extract per line item:
   - **Group** (section/category)
   - **Title** (item description)
   - **Cost Code** (XX.XX)
   - **Cost Type** (Labor, Material, Sub, Equipment, Other)
   - **Quantity** and **Unit**
   - **Unit Cost** (builder cost per unit)
   - **Builder Cost** (total)
   - **Markup %** or **Margin %**
   - **Client Price** (unit price × quantity)
   - **Tax** (taxable or not)
5. Capture totals: Builder Cost, Profit, Tax, Total Price
6. Check lock status

**Present to the user:**
```
📊 Estimate for [Project Name]:
🔒 Status: [Locked / Unlocked]

| Group | Items | Builder Cost | Markup | Client Price |
|-------|-------|-------------|--------|-------------|
| [Group 1] | [n] items | $XX,XXX | [avg]% | $XX,XXX |
| [Group 2] | [n] items | $XX,XXX | [avg]% | $XX,XXX |
| [Allowances] | [n] items | $XX,XXX | [avg]% | $XX,XXX |
| — | — | — | — | — |
| **TOTAL** | [n] items | $[builder] | [avg]% | $[client] |

💰 Builder Cost: $[total_builder]
📈 Profit: $[profit] ([margin]% margin)
🏷️ Tax: $[tax]
💵 Total Client Price: $[total_price]

📋 Proposals: [count] — [latest status]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 View All Line Items | `primary` | `bt_est_view_detail` |
| ➕ Add Items | `success` | `bt_est_add` |
| ✏️ Edit Items | `primary` | `bt_est_edit` |
| 📄 Create Proposal | `primary` | `bt_est_proposal` |
| 📊 Send to Budget | `success` | `bt_est_to_budget` |
| ✅ Done | `success` | `bt_est_done` |

---

## Step 2B: Add Line Items
**Action:** Add cost items to the estimate

**Message to the user:**
```
➕ Add line items to [Project] estimate:

Give me the items in any format:
• "Framing labor — $20,000 — 15% markup"
• "Electrical sub — cost code 08.00 — $45,000"
• Or paste a list and I'll figure out the cost codes

I'll suggest cost codes and calculate client pricing.
```

**On response, parse and present:**
```
📊 New Line Items:

| # | Title | Cost Code | Cost Type | Qty | Unit Cost | Builder Cost | Markup | Client Price |
|---|-------|-----------|-----------|-----|-----------|-------------|--------|-------------|
| 1 | [title] | [XX.XX] | [type] | [qty] | $[unit] | $[builder] | [X]% | $[client] |
| 2 | [title] | [XX.XX] | [type] | [qty] | $[unit] | $[builder] | [X]% | $[client] |
| 3 | [title] | [XX.XX] | [type] | [qty] | $[unit] | $[builder] | [X]% | $[client] |

Subtotal: Builder $[sum] → Client $[sum]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Add All Items | `success` | `bt_est_add_all` |
| ✏️ Edit Item [1] | `primary` | `bt_est_edit_1` |
| ✏️ Edit Item [2] | `primary` | `bt_est_edit_2` |
| 📊 Adjust All Markup | `primary` | `bt_est_adjust_markup` |
| ➕ Add More Items | `primary` | `bt_est_add_more` |
| ❌ Cancel | `danger` | `bt_est_cancel` |

### Browser Relay — Add Line Items
1. Navigate to `/app/Estimate`
2. **Check lock status** — if locked, ask the user before unlocking:
   ```
   🔒 Estimate is locked. Unlock to add items?
   ⚠️ This was locked by [user] on [date].
   ```
3. If unlocked (or after unlock):
   - Click **"Add Item"** button
   - For each line item:
     - Set **Title** (text input)
     - Set **Cost Code** (combobox — search by number or name)
     - Set **Cost Type** (Labor / Material / Subcontractor / Equipment / Other)
     - Set **Group** (combobox — existing group or create new)
     - Set **Description** (text — internal notes)
     - Set **Unit Cost** (number input)
     - Set **Quantity** (number input)
     - Set **Unit** (text — e.g., "sf", "lf", "ea", "ls")
     - Set **Markup** (% or $ or manual)
     - Check **Taxable** if applicable
     - Optionally check **"Include Item in Catalog"** (saves for reuse)
   - Click **Save**
4. Repeat for each line item
5. Snapshot → verify all items added with correct totals

---

## Step 2C: Import from Template
**Action:** Import estimate from a job template

### Browser Relay — Template Import
1. Navigate to `/app/Estimate`
2. Click **Template Import** → **Import Job Template**
3. Select **Source Template** from dropdown
4. Check **Estimates** under items to import
5. Click **Import**
6. Review imported items — all fields are editable
7. Snapshot → confirm import

---

## Step 2D: Import from Cost Catalog
**Action:** Add pre-defined cost items from the BT catalog

### Browser Relay — Catalog Import
1. Navigate to `/app/Estimate`
2. Click **"Add from Cost Catalog"**
3. Browse or search the catalog (stores Title, Description, Unit Cost, Markup)
4. Select items with checkboxes
5. Click **"Add To Estimate"**
6. Items added with pre-filled costs — adjust quantities as needed
7. Snapshot → confirm items added

---

## Step 2E: Import from Excel
**Action:** Bulk import estimate from a spreadsheet

### Browser Relay — Excel Import
1. Navigate to `/app/Estimate`
2. Click **External Import** → **Excel**
3. **Download template** (BT provides an Excel template)
4. Have the user fill in the template (or the agent can prepare it from provided data)
5. Click **Browse Computer** → select filled Excel file
6. **Map columns** → BT asks which Excel columns map to which BT fields
7. **Map cost codes** → match Excel items to BT cost codes
8. Click **Import**
9. Review imported items — adjust as needed
10. Snapshot → confirm import

---

## Step 3: Organize the Estimate
**Action:** Group line items into logical sections

**Message to the user:**
```
📁 How should we organize this estimate?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏠 By Room / Location | `primary` | `bt_est_group_room` |
| 📋 By Cost Code Category | `primary` | `bt_est_group_costcode` |
| 📐 By Trade / Phase | `primary` | `bt_est_group_trade` |
| 📑 Custom Groups | `primary` | `bt_est_group_custom` |
| ⏭️ No Grouping | `primary` | `bt_est_group_none` |

### Grouping Options in BT:

**Custom Grouping** (room-by-room, assemblies):
1. Click **"Add Group"**
2. Set **Group Title** (e.g., "Kitchen Renovation", "Phase 1 — Demo")
3. Set **Description** (optional — appears in proposal)
4. Drag line items into groups (or use checkboxes → Move Items → select group)
5. Reorder groups and items by dragging the six-dot handle

**Cost Code Grouping** (auto-format by categories):
1. Click **Group By** → **Cost Code**
2. BT auto-organizes items by their cost code categories
3. e.g., all 07.xx items under "PLUMBING", all 08.xx under "ELECTRICAL"

**Setting from Company Settings:**
- Estimates Settings → "Group Proposal Worksheet By": Custom Grouping or Cost Code Grouping

---

## Step 4: Set Up Allowances
**Action:** Create allowance items for client-selectable elements

**Message to the user:**
```
💰 Set up allowances? (e.g., "Painting Allowance: $5,000")
Allowances let clients pick within a budget — over/under adjustments flow to the budget.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Add Allowance | `primary` | `bt_est_allowance_add` |
| ⏭️ No Allowances | `primary` | `bt_est_allowance_skip` |

### Browser Relay — Add Allowance
1. In the Estimate, add a line item with the allowance amount
2. The item will be linked to a Selection (see manage-selections playbook)
3. Set **Title** (e.g., "Painting Allowance")
4. Set **Cost Code** (matching the trade — e.g., 14.00 Painting)
5. Set **Unit Cost** = allowance amount
6. Set **Markup** as applicable
7. This creates the budget baseline — Selections will track against it

**Allowance behavior in BT:**
- Client chooses a selection option
- If option costs more than allowance → difference added to contract
- If option costs less → savings returned to contract
- All adjustments flow to **Revised Budget** automatically

---

## Step 5: Lock / Unlock Estimate
**Action:** Lock the estimate to prevent edits (recommended before sending proposals)

**Message to the user:**
```
🔒 Lock the estimate for [Project]?
• Locking prevents edits while proposals are out
• Approved Bids and Selections still update when locked
• You can unlock anytime
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔒 Lock Estimate | `success` | `bt_est_lock_confirm` |
| 🔓 Unlock Estimate | `primary` | `bt_est_unlock_confirm` |
| ⏭️ Skip | `primary` | `bt_est_lock_skip` |

### Browser Relay — Lock/Unlock
1. Navigate to `/app/Estimate`
2. Click **"Lock Estimate"** (or **"Unlock Estimate"**)
3. Snapshot → confirm lock status changed
4. Note: Lock history tracked with user + date

---

## Step 6: Create Proposal
**Action:** Generate a formatted proposal document from the estimate for client review

**Message to the user:**
```
📄 Create a proposal for [Project]?
This formats the estimate into a professional document for the client to approve.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📄 Create Proposal | `success` | `bt_est_prop_create` |
| ✏️ Customize First | `primary` | `bt_est_prop_customize` |
| ⏭️ Skip | `primary` | `bt_est_prop_skip` |

### Proposal Configuration:

**Message to the user (if customizing):**
```
📄 Proposal Settings:

What should the client see?
```

**Inline buttons (toggle):**
| Button | Style | callback_data |
|---|---|---|
| 📋 Show Line Item Titles | `primary` | `bt_est_prop_show_titles` |
| 💰 Show Item Prices | `primary` | `bt_est_prop_show_prices` |
| 📝 Show Descriptions | `primary` | `bt_est_prop_show_desc` |
| 🔢 Show Quantities | `primary` | `bt_est_prop_show_qty` |
| 📊 Show Cost Codes | `primary` | `bt_est_prop_show_codes` |
| ✍️ Require Signature | `primary` | `bt_est_prop_require_sig` |
| 📅 Set Approval Deadline | `primary` | `bt_est_prop_deadline` |
| ✅ Use Company Defaults | `success` | `bt_est_prop_defaults` |

### Browser Relay — Create Proposal
1. Navigate to `/app/Estimate`
2. Click **"+ Proposal"**
3. On the **Details tab:**
   - Set **Title** (e.g., "{{company_name}} — Proposal for [Project]")
   - Set **Required Signees** (select client contacts who must sign)
   - Set **Approval Deadline** (date picker)
   - Fill **Introductory Text** (CKEditor):
     > Dear [Client Name],
     >
     > Thank you for the opportunity to provide this proposal for [Project Address]. Below is our detailed estimate for the scope of work discussed. Please review and approve at your convenience.
   - Fill **Closing Text** (CKEditor):
     > This proposal is valid for 30 days from the date above. Upon approval, {{company_name}} will begin scheduling and procurement. If you have any questions, please don't hesitate to reach out.
     >
     > {{company_name}} | {{company_phone}} | www.{{company_domain}}
   - Add **Attachments** (drawings, specs, photos)
4. On the **Client Preview tab:**
   - Choose **Standard** or **Custom Layout**
   - If Custom: adjust Layout Options, Company/Contact Info display
   - Select which fields to show: Item Title, Cost Code, Description, Quantity, Unit Price, Total Price
   - Toggle **"Show Edit Options"** for inline adjustments
5. Preview the proposal document
6. Click **Save** (keeps as draft) or **Send** (releases to client)
7. Snapshot → confirm proposal created

### If Sending:
```
📄 Proposal ready to send!

📌 [Title]
💰 Total: $[total]
👤 Signees: [names]
📅 Deadline: [date]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Send to Client | `success` | `bt_est_prop_send` |
| 💾 Save as Draft | `primary` | `bt_est_prop_draft` |
| 📥 Export PDF | `primary` | `bt_est_prop_pdf` |

### Client Approval Flow:
- **Active clients:** Approve in Client Portal → digital signature
- **Non-active clients:** Approve via email link
- **Internal approval (on behalf):** Ellipsis → "Approve for [signee]" → signature → Approve

---

## Step 7: Send Estimate to Budget
**Action:** Activate the Job Costing Budget from the estimate

**⚠️ This is a critical step — activates financial tracking for the job.**

**Message to the user:**
```
📊 Send estimate to budget for [Project]?

This will:
• Create the Job Costing Budget baseline
• Set Original Budget = Builder Cost per cost code
• Set Original Client Price = Client Price per cost code
• Lock the estimate (if not already locked)
• Enable financial tracking (POs, Bills, Invoices track against this budget)

Estimate Summary:
💰 Total Builder Cost: $[builder]
💵 Total Client Price: $[client]
📈 Total Profit: $[profit] ([margin]%)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Send to Budget | `success` | `bt_est_budget_send` |
| 📋 Review First | `primary` | `bt_est_budget_review` |
| ❌ Not Yet | `danger` | `bt_est_budget_cancel` |

### Browser Relay — Send to Budget
1. Navigate to `/app/Estimate`
2. Click **"Send to Budget"** button
3. BT shows summary: **Total Price**, **Builder Cost**, **Profit**, **Margin**
4. Review and confirm → Click **"Send to Budget"**
5. BT locks the estimate (if not already locked)
6. Budget is now active at `/app/JobCostingBudget`
7. Snapshot → confirm budget activated

**Report back:**
```
✅ Estimate sent to budget!

📊 [Project] Budget is now ACTIVE:
💰 Original Budget: $[builder_cost]
💵 Original Client Price: $[client_price]
📈 Profit Target: $[profit] ([margin]%)

Job Costing Budget is now tracking all financial activity.
```

---

## Step 8: Export Estimate as PDF
**Action:** Generate a PDF of the estimate or proposal

### Browser Relay — Export PDF
1. Navigate to `/app/Estimate`
2. To export the proposal:
   - Go to **Proposal Dashboard** (button on estimate page)
   - Click the proposal name → opens PDF view
   - Right-click → Save As PDF, or use BT's print/download function
3. To export raw estimate:
   - Click **Export** button → select format

---

## Markup Quick Reference

### Company Standard Markups
| Category | Typical Markup | Margin Equivalent |
|---|---|---|
| General Conditions | 15–20% | 13.0–16.7% |
| Subcontractor Work | 15–20% | 13.0–16.7% |
| Material Purchases | 10–15% | 9.1–13.0% |
| Specialty / Custom Items | 10–15% | 9.1–13.0% |
| Emergency / Expedited | 25–30% | 20.0–23.1% |

### Markup vs Margin Conversion
| Markup % | Margin % | $10K Builder → Client |
|---|---|---|
| 10% | 9.1% | $11,000 |
| 15% | 13.0% | $11,500 |
| 20% | 16.7% | $12,000 |
| 25% | 20.0% | $12,500 |
| 30% | 23.1% | $13,000 |

**Formula:**
- Markup = (Client Price − Builder Cost) / Builder Cost
- Margin = (Client Price − Builder Cost) / Client Price

### BT Markup Options (per line item)
| Option | Symbol | Behavior |
|---|---|---|
| Percentage | % | Multiplier on builder cost |
| Flat dollar | $ | Fixed dollar addition to builder cost |
| Manual | — | Enter client price directly |

---

## Cost Code Suggestion Logic (for new line items)

### By Description Keywords
| Keyword | Suggested Cost Code |
|---|---|
| framing, studs, lumber | 05.00 Carpentry / Framing or 05.05 Non-Structural Framing |
| plumbing, pipe, fixtures | 07.00 Plumbing |
| electrical, wiring, outlets | 08.00 Electrical |
| HVAC, duct, AC, furnace | 09.00 HVAC |
| drywall, sheetrock, taping | 10.00 Insulation & Drywall |
| millwork, cabinets, trim | 12.00 Carpentry / Millwork |
| windows, doors | 13.00 Windows & Doors |
| painting, coating, primer | 14.00 Painting and Coating |
| flooring, tile, hardwood | 15.00 Flooring & Tile |
| demo, demolition, gutting | 20.10 Demolition |
| concrete, foundation, rebar | 04.00 Excavation Foundation |
| steel, metal, welding | 35.00 Structural Steel or 21-20 Metal Fabrications |
| roofing, membrane, flashing | 06.00 Roofing |
| cleaning, final clean | 19.00 Cleaning |
| scaffolding, hoisting | 32.00 Scaffolding / Sheds |
| countertops, stone, quartz | 28.00 Countertops |
| fire sprinkler, suppression | 25.10 Fire Protection |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user, save all line item data for resume |
| Estimate is locked | Ask the user to unlock before editing; warn about lock history |
| Cost code not found | Suggest closest match or ask the user to create new code |
| Template import fails | Fall back to manual entry or catalog import |
| Excel import column mismatch | Help the user re-map columns in the import wizard |
| Proposal send fails | Check client has email; verify they're on the job |
| Send to budget fails | Ensure estimate has items; check for zero-cost lines |
| Browser relay disconnected | Stop, save all data, ask the user to re-enable |
| CKEditor not loading | Wait 3 seconds, retry; if persistent, report |
| Markup calculations mismatch | Report discrepancy, manually verify BT totals vs expected |

---

## Multiple Proposals
BT supports multiple proposals per job — useful when iterating on scope:

1. Update the estimate with revised numbers
2. Create a new proposal (old ones stay on the Proposal Dashboard)
3. Each proposal is a snapshot of the estimate at that time
4. Can pull cost lines from previous proposals: **View Worksheet** → checkbox → **Copy to estimate**
5. All versions visible on the **Proposal Dashboard** with statuses

---

## URL Quick Reference

| Page | URL |
|---|---|
| Job Estimate | `/app/Estimate` |
| Estimate Line Item Detail | `/app/Estimate/Estimate/{jobId}/{lineItemId}/10` |
| Lead Proposals | `/app/leads/proposals` |
| Estimate Settings | `/app/Settings/EstimateSettings` |
| Cost Catalog Settings | `/app/Settings/CostCatalogSettings?viewType=1` |
| Cost Codes Settings | `/app/Settings/CostCodes` |
| Job Costing Budget | `/app/JobCostingBudget` |
