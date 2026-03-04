# Creating & Formatting Client Proposals (Agent-Assisted)

## Overview
Create professional client proposals in Buildertrend from estimates — format with cover page, scope of work, line items, terms, and digital signature. Manage proposal iterations, track client responses, and convert accepted proposals into active jobs with funded budgets. The pipeline flows: **Estimate → Proposal → Client Approval → Send to Budget → Active Job**.

## Trigger
- the user says "create proposal for [project]", "send proposal to [client]"
- Estimate is complete and ready for client presentation
- Client requests updated proposal (revision v2, v3, etc.)
- "Check proposal status", "did [client] sign?"
- Accepted proposal → create job or activate budget

---

## Step 1: Navigate to Estimate / Proposal Dashboard
**Action:** Open the Estimate page for the job

```
browser → navigate to https://buildertrend.net/app/Estimate
(ensure correct job selected in sidebar)
browser → snapshot → verify Estimate page loaded with line items
```

**URL:** `/app/Estimate`
**Key toolbar actions:** +Proposal, Proposal Dashboard, Lock/Unlock Estimate, Launch Takeoff, Add Items, Export

### Proposal Dashboard
```
browser → snapshot → click "Proposal dashboard" button
browser → snapshot → view all proposal versions and statuses
```

---

## Step 2: Prepare the Estimate
**Action:** Ensure estimate is complete before creating proposal

### Pre-Proposal Checklist
| # | Item | Verification |
|---|---|---|
| 1 | All line items entered | Review estimate rows |
| 2 | Cost codes assigned | Every item has a cost code |
| 3 | Markup/margin set | Builder Cost → Client Price with markup |
| 4 | Tax configured | Job Details → Advanced Settings → Tax Rate |
| 5 | Taxable items marked | Checkboxes on taxable line items |
| 6 | Groups organized | Custom or Cost Code grouping applied |
| 7 | Descriptions complete | Client-facing descriptions filled in |

### Estimate Grouping Options
| Mode | Description | Use When |
|---|---|---|
| Custom Grouping | Room-by-room, assemblies, custom sections | Client wants organized by area/phase |
| Cost Code Grouping | Auto-grouped by cost category | Standard trade-based presentation |
| List View | Flat list of all items | Simple/small projects |

### Lock the Estimate
Before sending a proposal, lock the estimate to prevent accidental edits:
```
browser → snapshot → click "Lock Estimate" in toolbar
browser → snapshot → verify lock icon appears
```
**Note:** Approved Bids and Selections still update a locked estimate. Unlock anytime for changes.

---

## Step 3: Create a Proposal
**Action:** Click +Proposal → configure details

```
browser → snapshot → click "+Proposal" button
browser → snapshot → verify proposal creation form opens
```

### Details Tab
| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| Collect Signatures | Toggle | No | On | Require digital signatures |
| Required Signees | User selector | Yes (if signatures on) | Job's client(s) | Select who must sign |
| Title | Text input | No | "Proposal" | Proposal name |
| Approval Deadline | Date picker | No | — | When client must respond |
| Introductory Text | Rich text (CKEditor) | No | Company default | Cover letter / intro |
| Closing Text | Rich text (CKEditor) | No | Company default | Terms, conditions, fine print |
| Attachments | File upload | No | — | Drawings, specs, photos |

```
browser → snapshot → set Title (e.g., "[Project] — Proposal v1")
browser → snapshot → set Required Signees to client(s)
browser → snapshot → set Approval Deadline
browser → snapshot → compose Introductory Text (or use company default)
browser → snapshot → compose Closing Text (terms & conditions)
browser → snapshot → attach drawings, spec sheets, photos
```

**Default Text Settings:** Company Settings → Estimates → Job Proposal Format Settings:
- Header, Content, Show Contact Name & Phone, Show Address
- Default Introductory Text, Title, Closing Text, Release Text
- Estimate Disclaimer (custom message before approval)
- **Settings URL:** `/app/Settings/EstimateSettings`

---

## Step 4: Format the Proposal (Client Preview)
**Action:** Configure what the client sees

```
browser → snapshot → click "Client Preview" tab
browser → snapshot → configure layout and display options
```

### Layout Options
| Option | Description |
|---|---|
| Standard Layout | BT default format |
| Custom Layout | Fully configurable sections |

### Display Fields (toggle on/off per proposal)
| Field | Show? | Notes |
|---|---|---|
| Item Title | ✅ Usually on | Line item names |
| Cost Code | Optional | Hide from clients unless open book |
| Description | ✅ Usually on | Detailed scope text |
| Quantity | Optional | Show for itemized proposals |
| Unit | Optional | EA, SF, LF, etc. |
| Unit Price | Optional | Per-unit client price |
| Total Price | ✅ Usually on | Line item total |
| Group Subtotals | Optional | Subtotal per section |
| Tax | Optional | Tax line items |

### Pricing Display Options
| Style | When to Use |
|---|---|
| **Lump Sum** | Hide all line items — show only total | Simple, small projects |
| **Itemized** | Show every line item with quantities and prices | Transparent/open book |
| **Grouped** | Show sections with subtotals, hide detail | Standard commercial |

```
browser → snapshot → select Layout (Standard or Custom)
browser → snapshot → toggle display fields for client visibility
browser → snapshot → preview the proposal as client sees it
browser → snapshot → adjust formatting until satisfied
```

### Company Information Display
| Option | Description |
|---|---|
| Company Logo | Shows on header |
| Contact Name & Phone | Builder's contact info |
| Address | Company address |
| Custom fields | Company Settings → Company Information |

---

## Step 5: Add Sections (Inclusions, Exclusions, Alternates)
**Action:** Structure the proposal with clear scope boundaries

### Using Custom Grouping
```
browser → snapshot → switch to estimate (if needed)
browser → snapshot → click "Add Group" to create sections:
```

**Recommended Sections:**
| Section | Purpose |
|---|---|
| Scope of Work | Main included items |
| Inclusions | Explicitly included items |
| Exclusions | Items NOT included (critical for scope clarity) |
| Alternates / Add-Ons | Optional upgrades client can add |
| Allowances | Budget amounts for client selections |
| General Conditions | OH&P, supervision, temp facilities |
| Terms & Conditions | Payment terms, timeline, warranty |

```
browser → snapshot → create "Inclusions" group → add relevant items
browser → snapshot → create "Exclusions" group → add exclusion text items
browser → snapshot → create "Alternates" group → add optional items
```

**Note:** Use line items with $0 builder cost for text-only inclusions/exclusions, or use the Description field for scope narratives.

---

## Step 6: Send Proposal to Client
**Action:** Release proposal for client review and signature

```
browser → snapshot → verify Client Preview looks correct
browser → snapshot → click "Send" button
browser → snapshot → select clients to receive notification
browser → snapshot → confirm Send
browser → snapshot → verify proposal status changes to "Sent"
```

**Delivery methods:**
- **Active clients:** Proposal appears in Client Portal + email notification
- **Inactive clients:** Email with approval link
- **Print option:** For physical signature collection

**Message to the user:**
```
📄 Proposal sent to [client]:
• Title: [proposal title]
• Total: $[client price]
• Builder Cost: $[builder cost]
• Profit: $[profit] ([margin]%)
• Tax: $[tax amount]
• Deadline: [approval deadline]
• Sent via: [portal + email / email only]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👁️ Preview as Client | `primary` | `prop_preview` |
| 📊 View Proposal Dashboard | `primary` | `prop_dashboard` |
| 📧 Resend to Client | `primary` | `prop_resend` |

---

## Step 7: Track Proposal Status
**Action:** Monitor client response

```
browser → snapshot → click "Proposal dashboard"
browser → snapshot → read proposal statuses
```

### Status Definitions
| Status | Meaning |
|---|---|
| Draft | Created but not sent |
| Sent | Delivered to client |
| Viewed | Client opened the proposal |
| Approved | Client signed and accepted |
| Declined | Client rejected |

**Message to the user (Status Check):**
```
📄 Proposal Status — [Project]:
| Version | Title | Sent | Status | Client Price |
|---|---|---|---|---|
| v1 | Original Proposal | Jan 15 | Declined | $150,000 |
| v2 | Revised Scope | Jan 22 | Viewed | $138,000 |
| v3 | Final Offer | Feb 1 | Approved ✅ | $142,500 |
```

---

## Step 8: Client Approval Process
**Action:** Client reviews, approves, and signs

### Client Approval Flow
1. Client receives email notification
2. Opens proposal in Client Portal (or via email link)
3. Reviews scope, pricing, terms
4. Clicks "Approve"
5. Provides digital signature
6. Optional: adds comments
7. Status → Approved
8. Builder receives notification

### Internal Approval (on behalf of client)
If client approves verbally or by physical signature:
```
browser → snapshot → open proposal from Proposal Dashboard
browser → snapshot → click "..." menu → "Approve for [client]"
browser → snapshot → apply e-signature
browser → snapshot → click "Approve"
browser → snapshot → verify status = Approved
```

---

## Step 9: Revision Management (v1, v2, v3...)
**Action:** Create revised proposals when scope changes

### Create a New Proposal Version
```
browser → snapshot → modify estimate (unlock if needed)
browser → snapshot → update line items, pricing, scope
browser → snapshot → click "+Proposal" (creates new version)
browser → snapshot → update Title to reflect version (e.g., "Revised Proposal v2")
browser → snapshot → update Introductory Text explaining changes
browser → snapshot → send new proposal
```

### Pull from Previous Proposals
```
browser → snapshot → open Proposal Dashboard
browser → snapshot → click previous proposal → "View Worksheet"
browser → snapshot → select line items to carry forward
browser → snapshot → click "Copy to estimate"
browser → snapshot → modify as needed for new version
```

**All versions preserved in Proposal Dashboard** for audit trail.

---

## Step 10: Accepted Proposal → Active Job
**Action:** Convert approved proposal into active budget

### Send to Budget
```
browser → snapshot → navigate to Estimate
browser → snapshot → click "Send to Budget"
browser → snapshot → review summary:
  - Total Client Price: $[amount]
  - Total Builder Cost: $[amount]
  - Total Profit: $[amount]
  - Profit Margin: [X]%
browser → snapshot → click "Send to Budget"
browser → snapshot → verify Job Costing Budget activated
```

**After sending to budget:**
- Estimate auto-locks
- Original Budget populated in Job Costing Budget
- Job is financially active
- Can now create invoices, POs, bills against the budget

### Lead → Proposal → Job Flow
If the proposal was on a Lead (not yet a Job):
1. Proposal approved on Lead
2. Convert Lead to Job: Lead detail → "+ New Job"
3. All info, files, proposal data carry over
4. Job created with budget from proposal

See `convert-lead-to-job.md` for detailed lead conversion workflow.

---

## Step 11: Proposal Templates
**Action:** Create reusable proposal templates for common project types

### Save as Template
```
browser → snapshot → navigate to Job Info
browser → snapshot → click "Copy to Template" (from 3-dot menu at bottom)
browser → snapshot → this copies estimate, schedule, selections, etc.
browser → snapshot → access template from Templates menu
```

### Template Ideas for {{company_name}}
| Template | Contents |
|---|---|
| Commercial Fit-Out | All 43 cost categories, standard markup |
| Residential Renovation | Subset of categories, typical residential scope |
| Small Projects (< $50K) | Simplified cost codes, lump sum format |
| Emergency/Quick Turn | Abbreviated scope, T&M pricing |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Estimate empty | Must add line items before creating proposal |
| Estimate not locked | Lock before sending (prevents mid-send edits) |
| Client not on job | Add client first (see add-clients.md) |
| Client not invited to portal | Proposal sent via email only — invite for full access |
| Proposal already sent | Cannot edit sent proposal — create new version |
| Tax rate not set | Job Details → Advanced Settings → set tax rate |
| Markup missing | Check Cost Type defaults or per-line markup |
| Send button grayed out | Check required fields (signees, etc.) |

---

## Quick Reference: Estimate → Proposal Fields

| Estimate Field | Shown in Proposal? | Notes |
|---|---|---|
| Item Title | Configurable | Toggle in Client Preview |
| Description | Configurable | Important for scope clarity |
| Cost Code | Usually hidden | Internal reference |
| Cost Type | Hidden | Internal only |
| Builder Cost | **Hidden** | Never show to client |
| Markup | **Hidden** | Never show to client |
| Client Price | Shown | What client pays |
| Tax | Configurable | Shows if tax enabled |
| Internal Notes | **Hidden** | Team-only notes |
| Groups | Shown as sections | Organize proposal layout |

---

## Learning Academy Reference
- **Course:** "Creating & Formatting Client Proposals (NEW)" — 7 activities
- **Course:** "Creating and Managing Estimates (NEW)" — 6 activities
- **Course:** "Feature: Estimate" — 5 activities, 40 min
- **Topics:** Proposal formatting, client experience, approval workflow

---

## Company-Specific Notes
- **Estimate URL:** `/app/Estimate` (job-scoped)
- **Proposal Format Settings:** `/app/Settings/EstimateSettings`
- **QBO Connected:** Proposals → Budget → Bills sync to QuickBooks Online Plus
- **Tax Rate:** {{tax_jurisdiction}} {{tax_rate}}% (auto-applied to taxable items)
- **Test Project:** "Test Project 2" has existing estimate — locked by the user
- **Common proposal format:** Grouped by trade with subtotals, lump-sum alternates
- Accepted proposals create the budget that all financial features reference
