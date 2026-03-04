# Manage Selections — Client Finishes & Materials (Agent-Assisted)

## Overview
When {{company_name}} needs to present material/finish options to a client (e.g., flooring, countertops, fixtures, lighting), the agent guides the user through creating Selection categories in Buildertrend, adding choices with pricing and images, setting allowance amounts, and sending to the client for review and approval via the Client Portal. If approved choices exceed the allowance, the agent can initiate a Change Order.

## Trigger
- the user says "set up selections for [project]" or "add flooring options"
- Project reaches selections phase on the schedule
- Client asks about finish choices via portal
- Design coordinator prepares selection packages

---

## Step 1: Identify Project
**Action:** Confirm which project the selections are for

**Message to the user:**
```
🎨 Setting up Selections — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_sel_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_sel_project_1` |
| 🏗️ Project Beta | `primary` | `bt_sel_project_2` |
| 🏗️ Project Beta | `primary` | `bt_sel_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_sel_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_sel_project_4` |
| 🏗️ Project Eta | `primary` | `bt_sel_project_5` |
| ❌ Cancel | `danger` | `bt_sel_cancel` |

---

## Step 2: Choose Action
**Action:** Determine what the user wants to do with selections

**Message to the user:**
```
🎨 Selections for [project] — what would you like to do?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Create New Selection | `success` | `bt_sel_action_new` |
| 📋 View All Selections | `primary` | `bt_sel_action_list` |
| 📊 Allowance Summary | `primary` | `bt_sel_action_summary` |
| 📤 Send to Client | `primary` | `bt_sel_action_send` |
| ❌ Cancel | `danger` | `bt_sel_cancel` |

---

## Step 3: Create New Selection
**Action:** Gather selection details

### 3A: Category & Location
**Message to the user:**
```
🎨 New Selection — pick a category:
```

**Inline buttons (common categories):**
| Button | Style | callback_data |
|---|---|---|
| 🪵 Flooring | `primary` | `bt_sel_cat_flooring` |
| 🪨 Countertops | `primary` | `bt_sel_cat_countertops` |
| 🚿 Plumbing Fixtures | `primary` | `bt_sel_cat_plumbing_fixtures` |
| 💡 Lighting | `primary` | `bt_sel_cat_lighting` |
| 🚪 Doors & Hardware | `primary` | `bt_sel_cat_doors` |
| 🧱 Tile | `primary` | `bt_sel_cat_tile` |
| 🎨 Paint Colors | `primary` | `bt_sel_cat_paint` |
| 🍳 Appliances | `primary` | `bt_sel_cat_appliances` |
| 🪟 Window Treatments | `primary` | `bt_sel_cat_window_treatments` |
| 🪵 Cabinetry | `primary` | `bt_sel_cat_cabinetry` |
| ✏️ Custom Category | `primary` | `bt_sel_cat_custom` |

**Then ask location:**
```
📍 Where in the project? (e.g., Kitchen, Master Bath, Living Room, All Floors)
```

### 3B: Selection Details
**Message to the user:**
```
📝 Selection details for [Category] — [Location]:

• Title: [suggested: "[Category] — [Location]"]
• Require client selection? (client must pick before proceeding)
• Allowance amount? (budget for this selection)
• Deadline? (date or link to schedule item)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Use Suggested Title | `success` | `bt_sel_title_default` |
| ✏️ Custom Title | `primary` | `bt_sel_title_custom` |
| 💵 Set Allowance | `primary` | `bt_sel_allowance` |
| 📅 Set Deadline | `primary` | `bt_sel_deadline` |
| ⏭️ No Allowance / No Deadline | `primary` | `bt_sel_skip_details` |

### Allowance Suggestion Logic
| Category | Typical Allowance Range (per SF or unit) | Suggested Code |
|---|---|---|
| Flooring | $8–$25/SF | 15.00 Flooring & Tile |
| Countertops | $50–$150/SF | 28.00 Countertops |
| Plumbing Fixtures | $2,000–$15,000 lump | 07.10 Plumbing Fixtures |
| Lighting | $3,000–$20,000 lump | 08.10 Lighting Fixtures |
| Doors & Hardware | $500–$2,000/unit | 13.00 Windows & Doors |
| Tile | $10–$30/SF | 15.10 Tile |
| Paint Colors | $2–$5/SF | 14.00 Painting and Coating |
| Appliances | $5,000–$30,000 lump | 16.00 Appliances |
| Cabinetry | $200–$800/LF | 12.20 Cabinets |
| Window Treatments | $500–$2,000/window | 33.00 Window Treatments |

---

## Step 4: Add Choices
**Action:** Add product options for the client to choose from

**Message to the user:**
```
🎨 Add choices for [Selection Title]:

Send me the options — for each choice I need:
• Choice name (e.g., "Calacatta Gold Marble")
• Price (flat or per unit)
• Product link (optional)
• Photo/image (optional)
• Vendor (optional)

You can send one at a time or list them all.
```

**After each choice:**
```
✅ Choice added: [Name] — $[price]

What next?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Add Another Choice | `primary` | `bt_sel_choice_add` |
| 📤 Send to Client Now | `success` | `bt_sel_send` |
| 💰 Request Price from Sub | `primary` | `bt_sel_choice_sub_price` |
| 💾 Save as Draft | `primary` | `bt_sel_save_draft` |

### Sub/Vendor Price Request
If pricing isn't known:
1. Ask which vendor/sub should price this choice
2. In BT, use "Request From Sub/Vendor" pricing option
3. Sub receives notification in their portal
4. Track Outstanding Pricing Requests

---

## Step 5: Review & Send to Client
**Action:** Present complete selection summary for approval

**Message to the user:**
```
🎨 Selection Ready to Send:

📋 Title: [Selection Title]
🏗️ Project: [project name]
📍 Location: [location]
📂 Category: [category]
💵 Allowance: $[amount]
📅 Deadline: [date or "None"]

🔢 Choices:
| # | Choice | Price | Within Allowance? |
|---|--------|-------|--------------------|
| 1 | [Name] | $X,XXX | ✅ Under by $XXX |
| 2 | [Name] | $X,XXX | ⚠️ Over by $XXX |
| 3 | [Name] | $X,XXX | ✅ Under by $XXX |

Send to client for review?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Send to Client | `success` | `bt_sel_send_confirm` |
| ✏️ Edit Selection | `primary` | `bt_sel_edit` |
| ➕ Add More Choices | `primary` | `bt_sel_choice_add` |
| ❌ Cancel | `danger` | `bt_sel_cancel` |

---

## Step 6: Create Selection via Browser Relay
**Action:** Execute in Buildertrend

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/Selections/Default`
3. Snapshot → verify Selections page loaded
4. Click **"New Selection"** button
5. In the selection form:
   - Set **Title** (text input)
   - Set **Category** (combobox) → select or create new
   - Set **Location** (combobox) → select or create new
   - Set **Deadline** (date picker or link to schedule)
   - Check **"Require client to make a selection"** if specified
   - Set **Allowance** amount if specified
   - Set **Single vs Shared** allowance
   - Add **Public Instructions** (client-facing notes)
   - Add **Internal Notes** (team-only)
   - Add **Attachments** if any
6. Click **Save**
7. Snapshot → confirm selection created

### Adding Choices
8. Open the saved selection
9. Click **"Create New Choice"**
10. For each choice:
    - Set **Choice Title**
    - Set **Product Link** (URL)
    - Set **Include in Budget** checkbox
    - Add **Attachments** (photos/images)
    - Set **Price Details**: Flat Fee, Line Items, or Request From Sub
    - If Line Items: add cost code, cost type, unit cost, quantity
    - Add **Product Description**
    - Click **Save**
11. Repeat for all choices
12. Snapshot → verify all choices added

### Sending to Client
13. Click **"Send"** button on the selection
14. Snapshot → confirm sent status
15. Report back:

```
✅ Selection sent to client!

🎨 [Selection Title]
🏗️ Project: [project]
📍 Location: [location]
💵 Allowance: $[amount]
🔢 Choices: [count] options
📧 Client notified via portal
📊 Status: Pending client approval
```

---

## Step 7: Track Approval & Handle Over-Allowance

### Monitor Approval
Navigate to `/app/Selections/Default` → check status column

**When client approves:**
```
✅ Selection Approved!

🎨 [Selection Title]
👤 Client chose: [Choice Name] — $[price]
💵 Allowance: $[allowance]
```

**If within allowance:**
```
✅ Within allowance — under by $[difference]
No further action needed.
```

**If over allowance:**
```
⚠️ Over allowance by $[difference]

This overage needs to be captured as a Change Order.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📝 Create Change Order for Overage | `success` | `bt_sel_co_create` |
| 📊 View Budget Impact | `primary` | `bt_sel_budget_view` |
| ⏭️ Note It, Handle Later | `primary` | `bt_sel_co_defer` |

### Auto-Create Change Order for Overage
1. Follow `create-change-order.md` playbook
2. Pre-fill: Title = "Selection Overage — [Category] — [Location]"
3. Amount = approved choice price − allowance amount
4. Cost code = matching selection cost code
5. Link to selection as Related Item

---

## Step 8: Post-Action
After selection is created/approved:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — track selection deadline and approval status
3. **Check budget impact** — approved selections flow to Revised Budget
4. **Notify relevant agents:**
   - bookkeeper agent — selection approved, may affect invoicing
   - procurement agent — if selection requires procurement (PO creation)

---

## View All Selections (List Mode)
**Action:** Pull selections summary from BT

### Browser Relay Execution
1. Navigate to `/app/Selections/Default`
2. Snapshot → parse selection table
3. Extract: Title, Description, Client Price, Approved Price, Status

**Present to the user:**
```
📊 Selections Summary — [project]:

| # | Selection | Allowance | Approved | Status | Over/Under |
|---|-----------|-----------|----------|--------|------------|
| 1 | [Title]   | $X,XXX    | $X,XXX   | ✅ Approved | -$XXX |
| 2 | [Title]   | $X,XXX    | —        | ⏳ Pending | — |
| 3 | [Title]   | $X,XXX    | $X,XXX   | ✅ Approved | +$XXX ⚠️ |

💵 Total Allowance: $XX,XXX
✅ Total Approved: $XX,XXX
📊 Net Over/Under: $[+/-]XXX
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Create New Selection | `success` | `bt_sel_action_new` |
| 📤 Send Pending to Client | `primary` | `bt_sel_send_pending` |
| 📝 Create CO for Overages | `primary` | `bt_sel_co_overages` |
| 🔄 Refresh | `primary` | `bt_sel_refresh` |

---

## Batch Mode: Template Selections
When setting up selections for a new project from a template:

1. Ask: "Use selection template or build from scratch?"
2. If template: Navigate to existing job with selections → copy template
3. Present template categories with default allowances
4. Let the user adjust allowances per project budget
5. Create all selections in batch
6. Summary: "Created [N] selection categories — total allowance: $[amount]"

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save selection details for resume |
| Category doesn't exist | Create new category in the form (BT allows custom categories) |
| Location doesn't exist | Create new location in the form (BT allows custom locations) |
| Client not active on portal | Warn: "Client isn't active on BT portal — selection can't be sent. Invite client first?" |
| Product link broken | Flag and ask for updated URL |
| Image upload fails | Save without image, attach manually later |
| Over-allowance CO declined | Log it, keep selection approved, note budget impact |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## Selection Cost Code Quick Reference

| Category | Primary Cost Code | Notes |
|---|---|---|
| Flooring | 15.00 Flooring & Tile | Includes hardwood, vinyl, carpet |
| Tile | 15.10 Tile | Bathroom, kitchen, accent walls |
| Countertops | 28.00 Countertops | Stone, quartz, laminate |
| Plumbing Fixtures | 07.10 Fixtures | Faucets, sinks, tubs, toilets |
| Lighting | 08.10 Lighting Fixtures | Includes decorative + recessed |
| Appliances | 16.00 Appliances | Kitchen + laundry |
| Cabinetry | 12.20 Cabinets | Kitchen, bath, built-ins |
| Paint | 14.00 Painting and Coating | Interior + exterior |
| Doors & Hardware | 13.20 Doors | Interior + exterior |
| Window Treatments | 33.00 Window Treatments | Blinds, shades, curtains |
| Wall Finishes | 23.05 Wallpaper | Wallpaper, stone veneer, panels |
