# Buildertrend UI Patterns — Browser Relay Reference

**Purpose:** Step-by-step interaction patterns for BT's custom UI components.
Playbooks describe *what* to do. This file describes *how to click it*.

**Last verified:** March 2, 2026 on buildertrend.net

---

## 0. Sidebar Job Switching (UPDATED)

The sidebar has a **search textbox** at the top. This DOES work for switching jobs:

1. Find the sidebar search `textbox` (usually first textbox on page)
2. `kind: "type"` the job name (e.g., "Test Project")
3. Sidebar filters to matching jobs
4. Use JS evaluate to click the job name (class: `ItemRowJobName`)

```javascript
() => {
  const items = document.querySelectorAll('*');
  for (const el of items) {
    if (el.textContent.trim() === 'JOB_NAME' && el.offsetHeight > 0 && el.offsetWidth > 0 && el.children.length === 0) {
      el.click();
      return 'clicked: ' + el.tagName + ' ' + el.className;
    }
  }
  return 'not found';
}
```

**Clear search:** Click `button "close-circle"` next to the search box to reset.

Direct URL navigation is still the most reliable method, but sidebar search works as a fallback when you don't have the job ID.

---

## 1. Job IDs & Direct Navigation

BT uses numeric job IDs in URLs. Always use direct URL navigation instead of trying to click the sidebar job picker.

### Known Job IDs
| Job | ID | Direct URL |
|---|---|---|
| Project Alpha | {{job_id_1}} | `/app/JobPage/{{job_id_1}}/1` |
| Test Project | {{job_id_2}} | `/app/JobPage/{{job_id_2}}/1` |
| 1375 Broadway - Partitions | (check Jobs List) | — |
| 188 East 70th St - APT Reno | (check Jobs List) | — |
| Project Theta | (check Jobs List) | — |
| Project Theta - Client Office | (check Jobs List) | — |
| Pouillart Residence | (check Jobs List) | — |
| Test Project 2 | (check Jobs List) | — |

### URL Patterns
| Page | URL Pattern |
|---|---|
| Job Info | `/app/JobPage/{jobId}/1` |
| New PO (for a job) | `/app/PurchaseOrders/PurchaseOrder/0/{jobId}` |
| Edit PO | `/app/PurchaseOrders/PurchaseOrder/{poId}/{jobId}` |
| PO List | `/app/PurchaseOrders` (shows selected job's POs) |
| Schedule | `/app/Schedules/0` |
| Daily Logs | `/app/DailyLogs` |
| Change Orders | `/app/ChangeOrders` |
| Jobs List | `/app/Jobs/List` |
| Reports | `/app/Reporting` |
| Leads | `/app/leads/opportunities` |

### Sidebar Job Picker — AVOID
The left sidebar job list uses custom React components that don't respond reliably to `click` events via Browser Relay. **Always use direct URL navigation** instead.

---

## 2. Custom Combobox (Type-Ahead Dropdown)

BT uses custom comboboxes for: Cost Codes, Assigned To (vendor), Cost Type, Variance Codes, and most dropdown selectors. These are NOT native `<select>` elements.

### The Golden Pattern (works for ALL BT comboboxes)

```
Step 1: CLICK the combobox ref → opens and focuses it
Step 2: TYPE the search text (kind: "type") → filters the dropdown
Step 3: SNAPSHOT → see the filtered dropdown options
Step 4: EVALUATE JS → click the matching option by text content
Step 5: SNAPSHOT → verify the selection stuck
```

### JavaScript to Select a Dropdown Option

```javascript
// Replace 'SEARCH_TEXT' with the option text to match (partial OK)
() => {
  const options = document.querySelectorAll('[role="option"], li[class*="option"], div[class*="option"]');
  for (const opt of options) {
    if (opt.textContent.includes('SEARCH_TEXT')) {
      opt.click();
      return 'clicked: ' + opt.textContent.trim();
    }
  }
  return 'not found, options: ' + options.length;
}
```

### Cost Code Dropdown — Step by Step

**Element:** `combobox "Cost code *"` (one per line item in PO form)

**Dropdown structure when opened:**
- **"Budgeted cost codes"** group — codes already in the job's estimate (shown first)
- **"Other cost codes"** group — all remaining codes from Settings

**Example — selecting "08.00 - Electrical":**

1. `act: click` on the `combobox "Cost code *"` ref
2. `act: type` → ref: same combobox, text: `"08"` (use code number, not name)
3. `snapshot` → confirm dropdown shows filtered options including "08.00 - Electrical"
4. `act: evaluate` → JS to click option containing `'08.00'`
5. `snapshot` → confirm combobox now shows "08.00 - Electrical", dropdown closed

**What NOT to do:**
- ❌ `kind: "select"` — not a native select
- ❌ Click `option` refs from snapshot — stale after React re-render
- ❌ Type full name "Electrical" — code number is more precise
- ❌ Skip the type step — full list too long, may not render all

**Filter tips:**
- Type code number (e.g., `"08"`, `"15.10"`) for precise matching
- Partial name works too (e.g., `"Electr"`)
- Dropdown auto-filters as you type

### Assigned To (Vendor/Sub) Dropdown

**Element:** `combobox "Assigned to"` (top of PO form)

Same golden pattern:
1. Click combobox → 2. Type vendor name (e.g., `"Nead"`, `"Penguin"`) → 3. Snapshot → 4. JS evaluate click → 5. Verify

**Default:** "Unassigned"

### Cost Type Dropdown

**Element:** `combobox "Cost type"` (per line item)

Options: None, Materials, Labor, Subcontract, Equipment, Other

Same pattern, but few options so can sometimes click option ref directly.

---

## 3. PO Form Layout (Dialog)

PO creation opens as a **modal dialog** over the main page. Navigate to:
`/app/PurchaseOrders/PurchaseOrder/0/{jobId}`

### Form Sections (top to bottom)

| Section | Key Fields |
|---|---|
| **General Info** | PO # (auto), `textbox "Title"`, `combobox "Assigned to"`, `checkbox "Materials Only"` |
| **Completion** | `radio "Choose date"` (default) / `radio "Link to Schedule"`, date textbox |
| **Scope of Work** | Rich Text Editor (CKEditor iframe) |
| **Specs** | Available after first save |
| **Attachments** | `button "Add"`, `button "Create new doc"` |
| **Variance** | `checkbox "Mark as a Variance PO"` |
| **Cost (Line Items)** | Grid — see Section 4 |
| **Bills/Lien Waivers** | `button "Bill Remaining"`, `button "New Bill"` |
| **Related Bids** | Read-only if bids exist |
| **Internal Notes** | `textbox "Internal Notes"` |

### Footer Buttons
| Button | State | Action |
|---|---|---|
| **Save** | Disabled until required fields filled | Saves as Draft |
| **Related actions** | Always enabled | Dropdown menu |
| **Send** | Disabled until saved | Releases to vendor |

---

## 4. Line Item Grid

### Adding Lines
Click `button "plus-circle Item"` to add a new row.

### Fields Per Row
| Field | Element | Default | Required |
|---|---|---|---|
| Title | `textbox "Title"` | empty | No |
| Cost code | `combobox "Cost code *"` | empty | **Yes** |
| Cost type | `combobox "Cost type"` | None | No |
| Unit cost | `textbox "Unit cost"` | "0" | No |
| Quantity | `spinbutton` (+/- buttons) | "1" | No |
| Unit | `textbox "Unit"` | empty | No |
| Builder Cost | Read-only | $0.00 (auto-calc) | — |

**Expanded row** (below each line item):
| Field | Element |
|---|---|
| Description | `textbox "Description"` |
| Internal notes | `textbox "Internal notes"` |

### Delete Line
Trash icon button at far right of each row.

---

## 5. Rich Text Editor (CKEditor)

Used for: Scope of Work, email body, some notes fields.

### Interaction
1. Click the `application "Rich Text Editor"` or its `iframe` child
2. `kind: "type"` to enter text
3. Toolbar buttons available: Bold, Italic, Underline, Strikethrough, Font, Size, Colors, Alignment

### Default Content (PO Scope)
New POs may have a pre-populated signature block.

---

## 6. Date Fields

**Completion Date** is a textbox. Type the date directly in `MM/DD/YYYY` format.

Alternative: Select `radio "Link to Schedule"` to pull date from a schedule item.

---

## 7. Dialog/Modal Handling

### Rules
- Check for open dialogs before interacting with the main page
- Dialog has `button "Close"` (X icon) in the header
- Dialogs block the page behind them
- Multiple dialogs can stack

### Closing a Dialog (fallback JS)
```javascript
() => {
  const btn = document.querySelector('dialog button[aria-label="Close"], button:has(img[alt="Close"])');
  if (btn) { btn.click(); return 'closed'; }
  return 'not found';
}
```

---

## 8. Navigation Menu Map

| Menu | Sub-items |
|---|---|
| **Sales** | Lead Opportunities, Lead Activities, Lead Proposals, Lead Activity Calendar, Lead Map |
| **Jobs** | Summary, Job Info, Job Price Summary, Jobs List, Jobs Map, New Job From Scratch/Template |
| **Project Management** | Schedule, Daily Logs, Tasks, Change Orders, Selections, Warranties, Time Clock, Plans and Specs, Client Updates |
| **Files** | Documents, Photos, Videos |
| **Messaging** | (may need job context) |
| **Financial** | (may need job context or permissions) |
| **Reports** | `/app/Reporting` |

### Setup Menu (top-right avatar "AA")
Company Settings, Integrations, Additional Services, Logout

---

## 9. Job Info Tabs

Page: `/app/JobPage/{jobId}/1`

| Tab | Content |
|---|---|
| Job details | Title, address, contract type, schedule dates, notes |
| Clients | Client contacts on this job |
| Internal users | {{company_name}} team assigned |
| Subs/vendors | Subcontractors & vendors |
| Advanced settings | Permissions, custom fields |
| Builder's Risk Insurance | Insurance details |

---

## 10. Grid/Table Patterns

### Sorting
Column headers with `caret-up`/`caret-down` buttons. Click to sort.

### Filtering
Right-side panel with filter comboboxes. Apply → `button "Apply filter"`. Reset → `button "Clear all"`.

### Views
Bottom-left `combobox "Standard View"` for saved views.

### Pagination
Bottom-right shows "1-X of Y items".

---

## 11. Common Pitfalls

| Problem | Solution |
|---|---|
| **Refs go stale after actions** | Always re-snapshot before next interaction |
| **Wrong dialog opens** | Some job card icons open message compose, not PO form. Check snapshot. |
| **Save button disabled** | Fill all required fields (Cost code * on every line item) |
| **Session timeout** | If login page appears, STOP. Ask the user to re-login. |
| **Click timeout on ref** | Use JS `evaluate` to find and click by text content |
| **Sidebar job picker unreliable** | Use direct URL navigation with job ID |
| **Cost code not found in dropdown** | Type more specific text, or check if code exists in Settings → Cost Codes |

---

## 12. Test Projects

**Always use test projects for experimenting — never production jobs.**

| Project | Job ID | Notes |
|---|---|---|
| Test Project | {{job_id_2}} | PM: {{owner_name}} |
| Test Project 2 | (get from Jobs List) | — |

Delete any test POs after testing.

---

## 13. Schedule Item Form

Opens as dialog from `button "New Schedule Item"` on Schedule page.

### Fields
| Field | Element | Type | Notes |
|---|---|---|---|
| Title * | `textbox "Title *"` | Text | Required |
| Display Color | `combobox "Display Color"` | Combobox | Default: "Forest" |
| Assignees | `combobox "Assignees"` | Combobox | Type-ahead, same golden pattern |
| Start Date * | `textbox "Start Date *"` | Date | Defaults to today |
| Work Days * | `spinbutton` (+/- buttons) | Number | Default: 1 |
| End Date * | `textbox "End Date *"` | Date | Auto-calculated |
| Hourly | `switch "Hourly"` | Toggle | |
| Progress | `slider` + `spinbutton` | 0-100% | |
| Reminder | `combobox "Reminder"` | Combobox | Default: "None" |

### Tabs (bottom of form)
| Tab | Contains |
|---|---|
| **Predecessors & Links** | Predecessor combobox (schedule items), Type combobox (FS/SS/FF/SF), Lag days |
| **Phases & Tags** | `combobox "Phase"` (with Add/Edit), `combobox "Tags"` (with Add/Edit) |
| **Viewing** | Visibility settings |
| **Notes** | Notes field |
| **Files** | File attachments |

### Predecessor Dropdown
Same combobox pattern — type schedule item name to filter, JS evaluate to select.

---

## 14. Change Order Form

Opens as a full page (not dialog) from `button "Create new Change Order"`.

### Fields
| Field | Element | Type | Notes |
|---|---|---|---|
| Required Approvers | `combobox "Required Approvers"` | Combobox | Client picker |
| Title | `textbox "Title"` | Text | |
| ID# | `textbox "ID#"` | Text | Auto-assign placeholder |
| Approval Deadline | `textbox "Approval Deadline"` | Date | |
| Invoice upon approval | `checkbox` | Checkbox | |
| Introduction Text | Rich Text Editor (editor1) | CKEditor | |
| Closing Text | Rich Text Editor (editor2) | CKEditor | |
| Subs/Vendors | `combobox` | Combobox | Sub/vendor assignment |
| Internal notes | `textbox` | Text | |
| Sub/Vendor notes | `textbox` | Text | |
| Client notes | `textbox` | Text | |

### Action Buttons (top bar)
| Button | Action |
|---|---|
| **Details** | Current tab |
| **Estimate** | Estimating worksheet (line items with cost codes) |
| **Client preview** | How client sees it |
| **Decline** | Reject CO |
| **Approve** | Approve CO |
| **Add to** | Add to invoice/PO |
| **Save** | Save draft |
| **Send** | Send to client |

### Estimate Tab
The Estimate tab has the same **cost code combobox** and **line item grid** as the PO form. Use the same golden pattern from Section 2.

---

## 15. Lead Opportunities

Page: `/app/leads/opportunities`

### Views Available
- List view (default)
- Activity view
- Activity calendar
- Activity templates
- Lead proposals
- Proposal templates
- Map

### Lead List Columns
Title, Created Date, Client Contact, Lead Status, Age, Confidence

### Creating a Lead
Button: `+ Lead Opportunity` (top right)

### Lead Fields (when opened)
Leads have their own form with:
- Contact info (name, email, phone)
- Address
- Lead status
- Confidence slider
- Source
- Assigned salesperson (combobox)
- Activities/follow-ups
- Proposals
- Notes

All comboboxes in the lead form follow the same golden pattern.

---

## 16. Universal Rules (All Forms)

1. **Every BT combobox** uses the same pattern: Click → Type → Snapshot → JS Evaluate → Verify
2. **Every BT dialog** has a Close button in the header
3. **Every BT grid** has sortable columns, filter panel, and pagination
4. **Rich Text Editors** are always CKEditor iframes
5. **Date fields** accept direct typing in MM/DD/YYYY format
6. **Required fields** are marked with * — form won't save without them
7. **Always re-snapshot** after every action — React re-renders invalidate refs
8. **Session timeout** = stop immediately, ask the user to re-login
