# Create Change Order (Agent-Assisted)

## Overview

> **UI Reference:** See `bt-ui-patterns.md` for combobox dropdown, modal, grid, and navigation patterns used in this playbook.
When the scope of a project changes — client request, unforeseen condition, or design modification — the agent guides the user through creating a Change Order in Buildertrend. The agent handles cost code assignment, markup calculation, client approval flow, and optionally creates an invoice and/or PO upon CO approval.

## Trigger
- the user says "change order for [project]" or "CO for [project]"
- the user says "the client wants to add [scope]"
- Client submits a CO Request through the BT portal
- Field crew reports unforeseen conditions requiring scope change

---

## Step 1: Identify Project & Context
**Action:** Confirm project and understand what changed

**Message to the user:**
```
📋 Creating a Change Order — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_co_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_co_project_3` |
| 🏗️ Project Beta | `primary` | `bt_co_project_2` |
| 🏗️ Project Beta | `primary` | `bt_co_project_4` |
| 🏗️ Project Epsilon | `primary` | `bt_co_project_5` |
| 🏗️ Project Gamma | `primary` | `bt_co_project_6` |
| 🏗️ Project Eta | `primary` | `bt_co_project_7` |
| ❌ Cancel | `danger` | `bt_co_cancel` |

**On response, ask about the change:**
```
What changed and who requested it?
(e.g., "Client wants to add a wet bar in the den", "Found asbestos in ceiling — need abatement")
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👤 Client Requested | `primary` | `bt_co_source_client` |
| 🏗️ Field Condition | `primary` | `bt_co_source_field` |
| 📐 Design Change | `primary` | `bt_co_source_design` |
| 📋 Other | `primary` | `bt_co_source_other` |

---

## Step 2: CO Details
**Action:** Collect title, description, and scope

**Message to the user:**
```
📋 Change Order Details:

📌 Title: [suggest based on description, e.g., "CO-04: Add wet bar — Den"]
📝 Description: [what the user described]
👤 Requested by: [source from Step 1]

Does this look right? Or edit:
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Looks good | `success` | `bt_co_details_ok` |
| ✏️ Edit title | `primary` | `bt_co_edit_title` |
| ✏️ Edit description | `primary` | `bt_co_edit_desc` |
| ❌ Cancel | `danger` | `bt_co_cancel` |

---

## Step 3: Cost Line Items
**Action:** Build the CO cost estimate — line items with cost codes, amounts, and markup

**Message to the user:**
```
💰 Change Order Pricing — how would you like to set this up?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💵 Flat Fee (single amount) | `primary` | `bt_co_price_flat` |
| 📋 Line Items (itemized) | `primary` | `bt_co_price_lines` |
| 📥 Pull from Estimate/Catalog | `primary` | `bt_co_price_catalog` |

### Flat Fee Path:
```
💵 What's the total change order amount to the client?
(This is the CLIENT price — I'll back-calculate builder cost from your markup)
```

**⚠️ Note from BT:** "Flat Fee doesn't allocate to cost codes — use Line Items for proper job costing." Show this warning:
```
⚠️ BT recommends Line Items over Flat Fee for accurate job costing.
Flat Fee won't track against specific cost codes in the budget.
Switch to Line Items?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 Switch to Line Items | `primary` | `bt_co_price_lines` |
| 💵 Keep Flat Fee | `primary` | `bt_co_price_flat_confirm` |

### Line Items Path:
```
📋 Enter line items for this CO:
(Format: Description — Cost Code — Builder Cost — Markup%)

Example:
Plumbing rough-in for wet bar — 07.00 — $2,500 — 20%
Electrical for wet bar — 08.00 — $1,800 — 20%
Millwork & cabinet — 12.00 — $4,200 — 15%
```

**Cost Code Suggestion Logic** (same as PO playbook):
Parse description keywords → suggest matching cost codes.

### After items entered, calculate and present:

**Message to the user:**
```
💰 Change Order Cost Summary:

| # | Description | Cost Code | Builder Cost | Markup | Client Price |
|---|-------------|-----------|-------------|--------|-------------|
| 1 | Plumbing rough-in | 07.00 | $2,500 | 20% | $3,000 |
| 2 | Electrical | 08.00 | $1,800 | 20% | $2,160 |
| 3 | Millwork & cabinet | 12.00 | $4,200 | 15% | $4,830 |

Subtotal Builder Cost: $8,500
Total Markup: $1,490
Subtotal Client Price: $9,990
Tax ({{tax_rate}}%): $886.61
━━━━━━━━━━━━━━━━━
Total to Client: $10,876.61
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Approve pricing | `success` | `bt_co_pricing_ok` |
| ✏️ Edit line items | `primary` | `bt_co_pricing_edit` |
| 📊 Adjust markup | `primary` | `bt_co_pricing_markup` |
| 🚫 Remove tax | `primary` | `bt_co_pricing_notax` |

---

## Step 4: Approval Settings
**Action:** Set up approvers and invoice/notification preferences

**Message to the user:**
```
📋 Approval Settings:

👤 Client approver: [auto: job's client]
📧 Invoice upon approval? (BT auto-creates invoice when CO is approved)
📅 Approval deadline: [suggest 7 days from today]
👷 Notify subs/vendors: [if applicable]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Auto-invoice on approval | `success` | `bt_co_auto_invoice` |
| ❌ No auto-invoice | `primary` | `bt_co_no_invoice` |
| 📅 Set deadline | `primary` | `bt_co_set_deadline` |
| ⏭️ Use defaults | `success` | `bt_co_defaults` |

---

## Step 5: Introduction & Closing Text
**Action:** Offer to add professional intro/closing text

**Message to the user:**
```
📝 Add intro/closing text for the client?
(This appears on the CO document the client receives)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Use standard template | `success` | `bt_co_text_standard` |
| ✏️ Custom text | `primary` | `bt_co_text_custom` |
| ⏭️ Skip — no text | `primary` | `bt_co_text_skip` |

### Standard Template:
**Introduction:**
> Dear [Client Name],
>
> The following change order reflects modifications to the original scope of work for [Project Name]. Please review the details and costs below.

**Closing:**
> Upon approval, this change order will be incorporated into the project scope and budget. Please sign below to authorize these changes. If you have any questions, contact us at {{company_phone}}.

---

## Step 6: Final Review
**Action:** Present complete CO summary

**Message to the user:**
```
📋 Change Order Ready for Review:

🏗️ Project: [project name]
📌 Title: [CO title]
🔢 CO #: [auto-assigned]
📝 Description: [description]
👤 Requested by: [source]

💰 Pricing:
| # | Item | Builder Cost | Client Price |
|---|------|-------------|-------------|
| 1 | [item 1] | $X,XXX | $X,XXX |
| 2 | [item 2] | $X,XXX | $X,XXX |

Subtotal: $[subtotal]
Tax ({{tax_rate}}%): $[tax]
Total: $[total]

📧 Auto-invoice: [Yes/No]
📅 Approval deadline: [date]
👤 Approver: [client name]

Create this CO as Draft?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create as Draft | `success` | `bt_co_create_draft` |
| 📤 Create & Send to Client | `success` | `bt_co_create_send` |
| ✏️ Edit | `primary` | `bt_co_edit` |
| ❌ Cancel | `danger` | `bt_co_cancel` |

---

## Step 7: Create Change Order via Browser Relay
**Action:** Execute in Buildertrend

**⚠️ CRITICAL:** Clicking "Create new Change Order" in BT **immediately creates a Draft CO** (auto-assigns CO # and saves a record). The agent cannot undo this — proceed only when ready.

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/ChangeOrders`
3. Click "Create new Change Order" button (+ Change Order)
4. **BT immediately creates a Draft CO and navigates to detail page**
5. On the **Details tab:**
   - Set **Required Approvers** → verify client is listed (auto-populated)
   - Set **Title**
   - Verify **ID #** (auto-assigned)
   - Set **Approval Deadline** (date picker) if specified
   - Check **"Invoice client upon approval"** if auto-invoice enabled
   - Fill **Introduction Text** (CKEditor rich text)
   - Fill **Closing Text** (CKEditor rich text)
   - Set **Internal notes** if any
   - Set **Client notes** if any
6. Switch to **Estimate tab:**
   - Select **Line Items** (not Flat Fee)
   - Click **"+ Item"** for each line item
   - For each: set Title, Cost Code (combobox), Cost Type, Unit Cost, Quantity, Markup
   - Verify Builder Cost and Client Price for each line
   - Check **Tax** column if applicable
   - Verify totals match expected values
7. Switch to **Client Preview tab:**
   - Verify the client-facing view looks correct
   - Check visible information
8. Click **Save** (keeps as Draft)
9. If sending: Click **Send** → confirm client recipients
10. Snapshot → confirm CO created

**Report back:**
```
✅ Change Order created in Buildertrend!

📋 CO #[number]: [title]
🏗️ Project: [project]
💰 Builder Cost: $[builder_cost]
💰 Client Price: $[client_price]
📋 Status: [Draft / Sent]
📧 Auto-invoice: [Yes/No]
```

---

## Step 8: Post-Creation Flow

### If Draft:
**Message to the user:**
```
CO saved as Draft. When ready:
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Send to Client Now | `success` | `bt_co_send` |
| 📎 Add attachments first | `primary` | `bt_co_attach` |
| 💾 Keep as Draft | `primary` | `bt_co_keep_draft` |

### If Sent — Monitor Approval:
- Add to Apple Reminders: "Follow up on CO #[number] — [project] — Deadline: [date]"
- On approval:
  - BT auto-creates invoice if "Invoice upon approval" was checked
  - CO costs flow to **Revised Budget** in Job Costing
  - Notify the user: "✅ CO #[number] approved by [client] — $[amount] added to project"

### Post-Creation Tasks:
1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — track CO approval status + deadline
3. **Notify bookkeeper agent** — CO created, may auto-generate invoice
4. **Create PO** — offer to create PO(s) for the new scope

**Optional follow-up:**
```
📦 Create a PO for this new scope?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create PO from this CO | `success` | `bt_co_create_po` |
| ⏭️ Not yet | `primary` | `bt_co_no_po` |

---

## Markup Calculation Reference

### Standard Markup Rates (Company Defaults)
| Trade / Category | Typical Markup |
|---|---|
| General Conditions | 15-20% |
| Subcontractor work | 15-20% |
| Material purchases | 10-15% |
| Specialty items (fixtures, appliances) | 10-15% |
| Emergency / expedited work | 25-30% |
| Design changes (client-initiated) | 15-20% |
| Unforeseen conditions | 15-20% |

### Markup vs Margin (BT uses both)
| Builder Cost | Markup % | Client Price | Margin % |
|---|---|---|---|
| $10,000 | 15% | $11,500 | 13.0% |
| $10,000 | 20% | $12,000 | 16.7% |
| $10,000 | 25% | $12,500 | 20.0% |

**Formula:**
- Markup = (Client Price − Builder Cost) / Builder Cost
- Margin = (Client Price − Builder Cost) / Client Price

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save CO details for resume |
| CO auto-created as Draft (accidental) | Note CO #, can be left as Draft or deleted by the user |
| Client not on project | Cannot set as approver — ask the user to add client first |
| Cost code not found | Suggest closest match or ask the user to create it |
| Tax rate missing | Default to {{tax_rate}}% NY or skip tax |
| Browser relay disconnected | Stop, save all details, ask the user to re-enable |
| CKEditor not loading | Wait 3 seconds, retry; if persistent, report to the user |
| Duplicate CO title | Add sequence number (e.g., "CO-04a: Add wet bar") |

---

## Change Order Status Lifecycle

| Status | Meaning | Next Action |
|---|---|---|
| Draft | Created, not sent | Review → Send to client |
| Sent | Awaiting client approval | Monitor deadline |
| Approved | Client signed off | Auto-invoice (if set), create PO |
| Declined | Client rejected | Revise and resend, or cancel |
| Client Requested | Client submitted via portal | Review → accept/modify/decline |

---

## CO Impact on Budget
When a CO is approved, BT automatically:
1. **Revised Budget** increases by CO builder cost
2. **Revised Client Price** increases by CO client price
3. If "Invoice upon approval" → Draft invoice auto-created
4. CO line items appear in **Job Costing Budget** under respective cost codes
5. **Projected Profit** recalculates

---

## Quick Reference: CO from Client Request
If client submits a CO Request through the portal:

1. CO appears on `/app/ChangeOrders` with status "Client Requested"
2. Agent reads the request details
3. Presents to the user:
```
📥 Client CO Request received:

👤 From: [client name]
📋 Title: [title]
📝 Description: [their description]

How should we handle this?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Accept & Price It | `success` | `bt_co_accept_request` |
| ✏️ Modify & Accept | `primary` | `bt_co_modify_request` |
| ❌ Decline | `danger` | `bt_co_decline_request` |
| 💬 Need more info from client | `primary` | `bt_co_request_info` |
