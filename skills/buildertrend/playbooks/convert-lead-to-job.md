# Convert Lead to Job (Agent-Assisted)

## Overview
When a lead reaches "Won" or is qualified to proceed, the agent guides the user through converting the lead into a full Buildertrend job — pre-filling from lead data, walking through complete job setup (title, type, contract, PMs, dates, estimate, schedule, cost codes, client account), and then triggering {{company_name}}'s project-registry.json checklist (Google Drive folders, Apple Reminders list, agent configs). This ensures zero data loss between sales and production.

## Trigger
- the user says "convert [lead] to a job" or "start a job from [lead]"
- Lead status changed to "Won/Sold" (from lead-opportunities playbook)
- Proposal approved by client on a lead
- the user says "we got [project] — set it up"

---

## Step 1: Select the Lead to Convert
**Action:** Identify which lead to convert

**Message to the user:**
```
🏗️ Convert Lead to Job — which lead?
```

### Browser Relay — Read Leads
1. Navigate to `https://buildertrend.net/app/leads/opportunities`
2. Snapshot → extract leads with confidence >60% or status = Won
3. Present qualified leads

**Inline buttons (sorted by confidence, highest first):**
| Button | Style | callback_data |
|---|---|---|
| ✅ Project Alpha (85%) | `success` | `bt_conv_lead_1` |
| 🟢 1416 Jefferson (77%) | `primary` | `bt_conv_lead_jefferson` |
| 🟢 23-29 Astoria Blvd (75%) | `primary` | `bt_conv_lead_astoria` |
| 🟡 474 Irving Ave (61%) | `primary` | `bt_conv_lead_irving` |
| 📋 Show All Leads | `primary` | `bt_conv_lead_all` |
| ❌ Cancel | `danger` | `bt_conv_cancel` |

**On selection:**

### Browser Relay — Read Lead Detail
1. Navigate to `/app/leads/opportunities/Lead/{leadId}`
2. Snapshot → extract ALL lead data:
   - Contact info (name, email, phone, company, address)
   - Project address / title
   - Revenue estimate
   - Notes (all notes)
   - Files attached
   - Proposal status & amounts
   - Activities history
3. Store everything for pre-fill

---

## Step 2: Pre-Fill & Review Job Details
**Action:** Present job details pre-filled from lead data, with suggestions

**Message to the user:**
```
📋 New Job from Lead: [Lead Title]

Pre-filled from lead data:
┌─────────────────────────────────────┐
│ 📌 Title: [lead title or address]
│ 🏗️ Type: [suggest from project type]
│ 📜 Contract Type: [suggest]
│ 💰 Contract Price: $[from revenue est.]
│ 📅 Work Days: Mon–Fri (default)
│ 📍 Address: [from lead/contact]
│ 📮 Zip: [from lead]
│
│ 👥 Project Managers:
│    • {{owner_name}}
│    • [{{team_member}} if was salesperson]
│
│ 👤 Client: [contact name]
│    📧 [email]
│    📱 [phone]
│
│ 📅 Projected Start: [if available]
│ 📅 Projected Completion: [if available]
│
│ 📝 Notes: [lead notes — first 200 chars]
│ 📎 Files: [count] files will carry over
│ 📋 Proposal: [status — approved/pending]
└─────────────────────────────────────┘

Review and confirm:
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Looks Good — Create Job | `success` | `bt_conv_create` |
| ✏️ Edit Title | `primary` | `bt_conv_edit_title` |
| ✏️ Edit Contract Type | `primary` | `bt_conv_edit_contract` |
| ✏️ Edit Price | `primary` | `bt_conv_edit_price` |
| ✏️ Edit PMs | `primary` | `bt_conv_edit_pms` |
| ✏️ Edit Dates | `primary` | `bt_conv_edit_dates` |
| 📝 Edit Notes | `primary` | `bt_conv_edit_notes` |
| ❌ Cancel | `danger` | `bt_conv_cancel` |

---

### Contract Type Selection (if editing)
**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💰 Fixed Price | `primary` | `bt_conv_contract_fixed` |
| 📖 Open Book | `primary` | `bt_conv_contract_open` |

### Job Type Selection (if editing)
**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ New Construction | `primary` | `bt_conv_type_new` |
| 🔨 Renovation | `primary` | `bt_conv_type_reno` |
| 🏢 Commercial Fit-Out | `primary` | `bt_conv_type_fitout` |
| 🏠 Residential Remodel | `primary` | `bt_conv_type_remodel` |
| 📋 Other | `primary` | `bt_conv_type_other` |

---

## Step 3: Create Job in Buildertrend
**Action:** Execute the job creation via Browser Relay

### Browser Relay — Create Job from Lead
1. Navigate to lead detail `/app/leads/opportunities/Lead/{leadId}`
2. Click **"+ New Job"** dropdown
3. Select **"From Scratch"** (or **"Your Templates"** if a template applies)
4. BT will pre-populate fields from the lead automatically
5. **⚠️ BT copies all information, files, and legacy proposals to the Job**

### If creating From Scratch:
1. On the new job page (`/app/JobPage/0/1?openCondensed=true`):
   - Verify **Title** (required) — set from lead
   - Set **Type** (required) — from project type
   - Set **Contract Type** (required) — Fixed Price or Open Book
   - Set **Work Days** (required) — default Mon–Fri
   - Verify **Address** and **Zip Code** (required)
   - Set **Contract Price** — from revenue estimate
   - Set **Project Managers** — the user + {{team_member}} (if applicable)
   - Set **Projected Start** and **Projected Completion** dates
   - Set **Status** — "Pre-Sale" or "Open"
   - Add **Notes for internal users** — paste lead notes
   - Add **Notes for subs/vendors** — if any
2. Click **Save**
3. Snapshot → confirm job created, capture **Job ID**

### If creating From Template:
1. BT opens template selection page
2. Select appropriate template from **Source Template** dropdown
3. Use **checkboxes** to select items to import:
   - ☐ Estimate
   - ☐ Schedule
   - ☐ Selections
   - ☐ To-Dos
   - ☐ Subs/Vendors
4. Review/modify **Project Managers, Subs/Vendors, Workdays**
5. Click **Save**
6. Snapshot → confirm job created, capture **Job ID**

**Report back:**
```
✅ Job created in Buildertrend!

🏗️ [Job Title]
🔢 Job ID: [id]
📜 Type: [job type] | Contract: [Fixed/Open]
💰 Price: $[contract price]
👥 PMs: [names]
📅 Start: [date] → Completion: [date]
📎 [X] files carried over from lead
📋 Proposal: [carried over / N/A]
```

---

## Step 4: Job Setup Checklist
**Action:** Walk through remaining setup items

**Message to the user:**
```
📋 Job [Title] created! Let's finish setup:

☐ Estimate — import from lead proposal or create new
☐ Schedule — import template or build from scratch
☐ Cost Codes — confirm applicable codes
☐ Client Account — create login & send portal invite
☐ Subs/Vendors — assign to job
☐ Budget — send estimate to budget

Which would you like to tackle first?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📊 Set Up Estimate | `primary` | `bt_conv_estimate` |
| 📅 Import Schedule | `primary` | `bt_conv_schedule` |
| 💰 Set Up Cost Codes | `primary` | `bt_conv_costcodes` |
| 👤 Create Client Account | `primary` | `bt_conv_client` |
| 👷 Assign Subs | `primary` | `bt_conv_subs` |
| ✅ Do All (Guided) | `success` | `bt_conv_all` |
| ⏭️ Skip — I'll do this later | `primary` | `bt_conv_skip_setup` |

---

### Step 4A: Set Up Estimate
**Action:** Import estimate from lead proposal or create new

**If lead had an approved proposal:**
```
📊 Lead had a proposal with [X] line items totaling $[amount].
Import into job estimate?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📥 Import from Lead Proposal | `success` | `bt_conv_est_import` |
| 📋 Import from Template | `primary` | `bt_conv_est_template` |
| ➕ Create New Estimate | `primary` | `bt_conv_est_new` |
| ⏭️ Skip | `primary` | `bt_conv_est_skip` |

### Browser Relay — Import Estimate
1. Ensure new job is selected in left sidebar
2. Navigate to `/app/Estimate`
3. If importing from lead: Click **Template Import** → select source
4. If from catalog: Click **Add from Cost Catalog** → select items → **Add To Estimate**
5. Review imported line items — verify cost codes, markup, totals
6. Click **Lock Estimate** when finalized
7. Click **Send to Budget** → review totals → **Send to Budget**
8. Snapshot → confirm budget activated

---

### Step 4B: Import Schedule
**Action:** Import a schedule template or create baseline

### Browser Relay — Import Schedule
1. Navigate to `/app/Schedules/0`
2. Click **More Actions** → **Import from Templates**
3. Select **Source Template**
4. Check **Schedule** under items to import
5. Set **New Start Date** (from projected start)
6. Click **Import**
7. Review imported schedule items
8. Optionally: Set the **Baseline** (Baseline tab → Set Baseline)
9. Keep schedule **Offline** until ready to publish
10. Snapshot → confirm schedule imported

---

### Step 4C: Set Up Cost Codes
**Action:** Review/assign cost codes relevant to this project

```
💰 Which cost categories apply to this project?
({{company_name}} has 43 categories with 200+ codes — I'll pre-select common ones)
```

**Common pre-selections based on project type:**

#### Renovation:
01-General Conditions, 02-General Requirements, 05-Carpentry, 07-Plumbing, 08-Electrical, 09-HVAC, 10-Insulation & Drywall, 12-Millwork, 13-Windows & Doors, 14-Painting, 15-Flooring, 19-Cleaning, 20-Demolition

#### New Construction:
All of the above plus: 03-Superstructure, 04-Excavation/Foundation, 06-Roofing, 17-Brick & Masonry, 18-Exterior Works, 35-Structural Steel

#### Commercial Fit-Out:
01-General Conditions, 02-General Requirements, 05-Carpentry, 08-Electrical, 09-HVAC, 10-Insulation & Drywall, 12-Millwork, 14-Painting, 15-Flooring, 22-Ceilings, 25-Fire Protection, 27-Fire Alarm, 32-Scaffolding

---

### Step 4D: Create Client Account & Send Portal Invite
**Action:** Add client to job and send Buildertrend portal invitation

### Browser Relay — Add & Invite Client
1. Navigate to `/app/JobPage/{jobId}/2?accessedFromContact=true` (Clients tab)
2. Click **"+ Existing Contact"** (contact carried from lead) or **"+ New Contact"**
3. Verify contact info: name, email, phone, company, address
4. Click **Save**
5. BT prompts: "Would you like to invite this client?"
6. **Before inviting, set permissions:**
   - Review access levels (Schedule, Daily Logs, Change Orders, Invoices, Selections, Files)
   - Set **notification preferences** (email, text, push)
7. Click **Send Invite**
8. Snapshot → confirm invite sent (status: **Pending**)

**Report back:**
```
✅ Client portal invite sent!

👤 [Client Name] — [email]
📋 Status: Pending (awaiting signup)
🔒 Permissions: [summary of what they can see]
```

---

### Step 4E: Assign Subs/Vendors
**Action:** Add known subs/vendors to the job

```
👷 Assign subs/vendors to [Job Title]?
(They'll get access to relevant schedule items, POs, etc.)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👷 Add Subs Now | `primary` | `bt_conv_subs_add` |
| ⏭️ Skip — will assign later | `primary` | `bt_conv_subs_skip` |

### Browser Relay — Assign Subs
1. Navigate to Job Info → **Subs/Vendors** tab
2. Click **"+ Sub/Vendor"**
3. Search and add from existing BT contacts
4. Run **Permission Wizard** for each — set feature access
5. Optionally invite (or hold until schedule is published)

---

## Step 5: Mark Lead as Won
**Action:** Update the lead status in the pipeline

### Browser Relay — Update Lead
1. Navigate to `/app/leads/opportunities/Lead/{leadId}`
2. Set **Lead Status** → **Sold**
3. Set **Sold Date** → today
4. Set **Related Job** → link to newly created job
5. Click **Save**
6. Snapshot → confirm lead updated

```
✅ Lead [Title] marked as WON and linked to Job [Job Title]
```

---

## Step 6: Trigger Company Project Registry Checklist
**Action:** Run {{company_name}}'s internal project setup workflow from `project-registry.json`

**⚠️ This is company-specific, not Buildertrend. This runs AFTER BT job creation.**

**Message to the user:**
```
🏗️ BT job is live! Now running company project setup:

☐ Google Drive — create project folder + subfolders
☐ Apple Reminders — create company project list
☐ Update project-registry.json
☐ Update agent TOOLS.md — Active Projects table
☐ Update agent MEMORY.md — Active Projects
☐ Update receipt agent config — receipt routing
☐ Update receipt agent known-projects.json
☐ Update bookkeeper agent QBO config
☐ Update procurement agent known-projects.json
☐ Notify all agents of new project

Proceed with full setup?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Run Full Setup | `success` | `bt_conv_registry_full` |
| 📋 Just BT — I'll handle the rest | `primary` | `bt_conv_registry_skip` |
| ✏️ Set Project Code First | `primary` | `bt_conv_registry_code` |

**If "Set Project Code First":**
```
What project code for this job?
(Short code for filing: e.g., PROJ1, PROJ2, PROJ3)
```

### Registry Setup Execution
Follow **every step** in `SKILLS/project-registry.json` → `update_checklist`:

1. **Google Drive** — create folder under `Projects/` with standard subfolders:
   - Invoices
   - Expenses / Receipts - Pending Review / Receipts - Matched
   - Estimating
   - Procurement - Orders
   - Other Documents

2. **project-registry.json** — add new project entry with:
   - Title, code, BT job ID, Drive folder ID, contract type, PMs, dates

3. **agent TOOLS.md** — add to Active Projects table

4. **agent MEMORY.md** — add to Active Projects section

5. **receipt agent rcpt/config.json** — add receipt routing for project code

6. **receipt agent rcpt/known-projects.json** — add project matching patterns

7. **bookkeeper agent quickBooks transactions/config.json** — add QBO mapping

8. **procurement agent purchasing-manager/known-projects.json** — add procurement matching

9. **{{bookkeeper_workspace}}/TOOLS.md** — update project folder table

10. **{{receipt_agent_workspace}}/TOOLS.md** — update project folders + receipt buttons

11. **{{receipt_agent_workspace}}/MEMORY.md** — update active projects list

12. **{{procurement_agent_workspace}}/TOOLS.md** — update active projects table

13. **Apple Reminders** — create `Company - [Project Name]` list

14. **Notify agents** — message bookkeeper agent, receipt agent, procurement agent about new project

**Report back:**
```
✅ Full project setup complete!

🏗️ [Job Title] ([Code])
📁 Drive folder: created ✅
📋 Reminders list: created ✅
🔧 All agent configs: updated ✅
📣 Agents notified: bookkeeper agent, receipt agent, procurement agent ✅
```

---

## Step 7: Post-Conversion Summary
**Action:** Final status report

```
🎉 Lead → Job Conversion Complete!

📊 From Lead:
   📌 [Lead Title] → Status: WON ✅
   💰 Revenue: $[amount]
   📅 Age: [X] days in pipeline

🏗️ To Job:
   📌 [Job Title]
   🔢 BT Job ID: [id]
   📜 Contract: [type] | $[price]
   👥 PMs: [names]
   👤 Client: [name] — Portal invite [sent/pending]

Setup Completed:
   ✅ Estimate: [imported/created/skipped]
   ✅ Schedule: [imported/created/skipped]
   ✅ Cost Codes: [configured/skipped]
   ✅ Budget: [activated/skipped]
   ✅ Client Portal: [invited/skipped]
   ✅ Drive Folder: [created/skipped]
   ✅ Agent Configs: [updated/skipped]
```

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user, save all collected data for resume |
| Lead has no contact info | Cannot create client — ask the user for contact details |
| Lead already linked to a job | Warn: "This lead is already linked to Job [X]." — ask to proceed or cancel |
| Template import fails | Fall back to "From Scratch" — manually enter fields |
| Contact email missing | Cannot send portal invite — ask the user for email |
| Job creation fails | Screenshot, report error, ask the user for guidance |
| Browser relay disconnected | Stop, save state, ask the user to re-enable |
| Estimate locked on source | Cannot import — ask the user to unlock source estimate first |
| Drive API fails | Skip Drive step, add to Reminders for manual follow-up |

---

## Job Setup Quick Reference

### Required Fields for Job Creation
| Field | Source | Fallback |
|---|---|---|
| Title | Lead title | Ask the user |
| Type | Lead project type | Ask the user |
| Contract Type | From proposal/discussion | Ask the user |
| Work Days | Mon–Fri default | Confirm with the user |
| Zip Code | Lead/contact address | Ask the user |

### Job Status Flow
| Status | When |
|---|---|
| Pre-Sale | Lead converted, estimate being built |
| Open | Contract signed, work starting |
| Warranty | Construction complete, warranty period |
| Closed | All work and warranty complete |

### Post-Conversion Checklist
| Item | Where | Agent |
|---|---|---|
| Estimate → Budget | BT | the agent |
| Schedule → Online | BT | the agent |
| Client → Invite | BT | the agent |
| QBO → Link job | BT Accounting | bookkeeper agent |
| Drive → Folders | Google Drive | the agent |
| Reminders → List | Apple Reminders | the agent |
| Configs → Update | Agent workspace files | the agent |
