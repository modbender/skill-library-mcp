# Full New Job Setup (Agent-Assisted)

## Overview
the agent guides the user through the complete setup of a new job in Buildertrend — from creating the job record with basic info, through assigning PMs, importing estimates/schedules from templates, configuring cost codes, setting up client and sub access, creating folders, and linking to QuickBooks. This also triggers parallel tasks: creating matching Google Drive folders, Apple Reminders lists, and updating all agent configs per `project-registry.json`.

## Trigger
- the user says "set up new job in BT" or "new project: [name]"
- Lead converted to job in BT → needs full setup
- Signed contract → project goes live
- Follows the `SKILLS/project-registry.json` → `update_checklist`

---

## Step 1: Basic Job Information
**Action:** Collect essential job details

**Message to the user:**
```
🆕 New Job Setup — let's get started!

I need the basics:
• Job title (e.g., "Project Alpha" or "Project Alpha - {{project_address}}")
• Address (street, city, state, zip)
• Project type
• Contract type
```

### Project Type Selection
**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Commercial Renovation | `primary` | `bt_newjob_type_comreno` |
| 🏠 Residential Renovation | `primary` | `bt_newjob_type_resreno` |
| 🏗️ New Construction | `primary` | `bt_newjob_type_newcon` |
| 🏢 Commercial Fit-Out | `primary` | `bt_newjob_type_fitout` |
| 🏠 Residential New Build | `primary` | `bt_newjob_type_resnew` |
| ✏️ Other | `primary` | `bt_newjob_type_other` |

### Contract Type Selection
**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💰 Fixed Price | `primary` | `bt_newjob_contract_fixed` |
| 📊 Open Book (Cost Plus) | `primary` | `bt_newjob_contract_open` |

### Additional Details
**Message to the user:**
```
📝 Additional details:

• Contract price: $[amount]
• Projected start date:
• Projected completion date:
• Work days: (default Mon-Fri)
• Project code for {{company_name}}: (e.g., PROJ1, PROJ2, PROJ3)
```

---

## Step 2: Job Creation Method
**Action:** Create from scratch or template

**Message to the user:**
```
📋 Create job from scratch or use a template?

Templates can import: Estimate, Schedule, Selections, To-Dos, Cost Codes
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🆕 From Scratch | `primary` | `bt_newjob_scratch` |
| 📋 From Template | `primary` | `bt_newjob_template` |

---

## Step 3: Create Job via Browser Relay

### Browser Relay Execution — From Scratch
1. Navigate to `/app/JobPage/0/1?openCondensed=true`
2. Snapshot → verify New Job form loaded
3. Fill required fields:
   - **Title** (required) → job name
   - **Type** (required) → select from dropdown
   - **Contract Type** (required) → Fixed Price or Open Book
   - **Work Days** (required) → set work week (default Mon-Fri)
   - **Address** → street, city, state, **zip code** (required)
4. Fill optional fields:
   - **Contract price** → if known
   - **Projected start / completion dates**
   - **Project managers** → select from dropdown
   - **Prefix** → for financial/RFI numbering
   - **Status** → "Open" (default) or "Pre-Sale"
   - **Schedule color** → assign unique color
   - **Notes for internal users** → any setup notes
5. Click **Save**
6. Snapshot → confirm job created, capture `{jobId}` from URL

### Browser Relay Execution — From Template
1. Navigate to `/app/leads/opportunities/QuickAction/JobFromTemplate/0/0/0/-1`
2. Fill **New Job Information** fields (same as above)
3. Select **Source Template** from dropdown
4. Check items to import:
   - ☑️ Estimate
   - ☑️ Schedule
   - ☑️ Selections
   - ☑️ To-Dos
5. Review Project Managers, Subs/Vendors, Workdays
6. Click **Save**
7. Snapshot → confirm job created with imported items

**Report back:**
```
✅ Job created in Buildertrend!

🏗️ [Job Title]
📍 [Address]
📋 Type: [type]
💰 Contract: [Fixed Price / Open Book]
📅 Start: [date]
📅 Completion: [date]
🆔 Job ID: [jobId]
```

---

## Step 4: Assign Project Managers
**Action:** Set PMs on the job

**Message to the user:**
```
👤 Assign Project Managers:
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👤 {{owner_name}} | `primary` | `bt_newjob_pm_kris` |
| 👤 {{team_member}} | `primary` | `bt_newjob_pm_niko` |
| 👤 {{team_member}} | `primary` | `bt_newjob_pm_arion` |
| 👥 the user + {{team_member}} | `success` | `bt_newjob_pm_user_team` |
| ✅ Done | `success` | `bt_newjob_pm_done` |

**Browser Relay:** Job Info page → Project Managers dropdown → select → Save.

---

## Step 5: Set Up Cost Codes
**Action:** Ensure cost codes are available for the job

**Message to the user:**
```
💰 Cost Codes — using the company-wide cost codes or need custom ones for this job?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Use Standard (200+ codes) | `success` | `bt_newjob_codes_standard` |
| 📋 Import from Template | `primary` | `bt_newjob_codes_template` |
| ✏️ Customize for This Job | `primary` | `bt_newjob_codes_custom` |

**Note:** BT uses company-wide cost codes by default. All 200+ codes from `buildertrend-phase2.md` are available on every new job.

---

## Step 6: Estimate Setup
**Action:** Build or import the estimate

**Message to the user:**
```
📊 Estimate — how do you want to build it?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 Import from Template | `primary` | `bt_newjob_est_template` |
| 📥 Import from Excel | `primary` | `bt_newjob_est_excel` |
| 🆕 Build from Scratch | `primary` | `bt_newjob_est_scratch` |
| 📂 Import from QuickBooks | `primary` | `bt_newjob_est_qbo` |
| ⏭️ Skip — Do Later | `primary` | `bt_newjob_est_skip` |

If importing from Excel: Download BT template → the user fills → upload → map columns → map cost codes → import.

---

## Step 7: Schedule Setup
**Action:** Build or import the schedule

**Message to the user:**
```
📅 Schedule — how do you want to build it?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 Import from Template | `primary` | `bt_newjob_sched_template` |
| 🆕 Build from Scratch | `primary` | `bt_newjob_sched_scratch` |
| ⏭️ Skip — Do Later | `primary` | `bt_newjob_sched_skip` |

### Import from Template
1. Navigate to `/app/Schedules/0`
2. Click **More Actions** → **Import from Templates**
3. Select template → check Schedule → set start date → Import
4. Review imported items → adjust dates if needed
5. Set schedule **Offline** (don't notify subs yet)

---

## Step 8: Configure Permissions (Sub/Client Access)
**Action:** Set up who can see what

**Message to the user:**
```
🔐 Permissions — do you want to configure sub/client access now?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👷 Add Subs to Job | `primary` | `bt_newjob_add_subs` |
| 👤 Add Client to Job | `primary` | `bt_newjob_add_client` |
| 🔐 Use Default Permissions | `success` | `bt_newjob_perms_default` |
| ⏭️ Skip — Do Later | `primary` | `bt_newjob_perms_skip` |

### Add Client
1. Navigate to Job Details → Clients tab
2. Click "+ New Contact" or "+ Existing Contact"
3. Fill contact info → Save
4. Review permissions → Send Invite (or defer)

### Add Subs
1. Navigate to Job Details → Subs/Vendors tab
2. Add subs from existing contacts
3. Run Permission Wizard for each sub
4. Optionally invite active subs

---

## Step 9: Create BT File Folders
**Action:** Set up the job's folder structure in BT

### Browser Relay Execution
1. Navigate to `/app/Documents/Standard/0` (ensure new job is selected)
2. Create standard folders:
   - Contracts
   - Submittals
   - Insurance (COIs)
   - Permits & Filings
   - Shop Drawings
   - Correspondence
   - Meeting Minutes
   - Reports & Inspections
   - Close-Out
3. Snapshot → verify folders created

---

## Step 10: Set Up Selections (if applicable)
**Action:** Create selection categories for the job

**Message to the user:**
```
🎨 Does this job need selection categories? (client finishes/materials)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Yes — Set Up Selections | `primary` | `bt_newjob_selections_yes` |
| ⏭️ No — Skip | `primary` | `bt_newjob_selections_skip` |

If yes: Follow `manage-selections.md` playbook for batch template creation.

---

## Step 11: Link to QuickBooks
**Action:** Connect the BT job to QBO customer/project

**Message to the user:**
```
📊 QuickBooks — link this job to QBO?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔗 Link to Existing QBO Customer | `primary` | `bt_newjob_qbo_existing` |
| ➕ Create New QBO Customer | `primary` | `bt_newjob_qbo_new` |
| ⏭️ Skip QBO Link | `primary` | `bt_newjob_qbo_skip` |

### Browser Relay Execution
1. Navigate to Job Details → Accounting tab
2. Click **"Link job"**
3. Select corresponding QBO Customer/Job from dropdown
4. Click Save
5. Snapshot → confirm QB link

---

## Step 12: Parallel Tasks (Company Infrastructure)
**Action:** Update all company systems per `project-registry.json` checklist

**Message to the user:**
```
🔧 Setting up company infrastructure for [project]:

☐ Google Drive folders
☐ Apple Reminders list
☐ Project Registry (project-registry.json)
☐ Agent configs (the agent, receipt agent, bookkeeper agent, procurement agent)

Running parallel setup...
```

### Checklist (from project-registry.json `update_checklist`):
| # | Task | Agent/System | Status |
|---|------|-------------|--------|
| 1 | Google Drive — create folder + subfolders | the agent/gog | ☐ |
| 2 | `SKILLS/project-registry.json` — add project | the agent | ☐ |
| 3 | the agent `TOOLS.md` — update Active Projects table | the agent | ☐ |
| 4 | the agent `MEMORY.md` — update Active Projects section | the agent | ☐ |
| 5 | `SKILLS/rcpt/config.json` — add receipt routing | the agent | ☐ |
| 6 | `SKILLS/rcpt/known-projects.json` — add project matching | the agent | ☐ |
| 7 | `SKILLS/quickBooks transactions/config.json` — add QBO mapping | the agent | ☐ |
| 8 | `SKILLS/purchasing-manager/known-projects.json` — add procurement | the agent | ☐ |
| 9 | `{{bookkeeper_workspace}}/TOOLS.md` — update project folder table | the agent | ☐ |
| 10 | `{{receipt_agent_workspace}}/TOOLS.md` — update project folders + receipt buttons | the agent | ☐ |
| 11 | `{{receipt_agent_workspace}}/MEMORY.md` — update active projects list | the agent | ☐ |
| 12 | `{{procurement_agent_workspace}}/TOOLS.md` — update active projects table | the agent | ☐ |
| 13 | Apple Reminders — create company project list | the agent | ☐ |
| 14 | Notify all agents of new project | the agent | ☐ |

**After each step, report progress:**
```
✅ [N]/14 parallel tasks complete:
✅ Google Drive folders created
✅ Project Registry updated
✅ Agent configs updated
⏳ Agent configs in progress...
```

---

## Step 13: Final Summary
**Message to the user:**
```
🎉 New Job Setup Complete!

🏗️ [Job Title]
📍 [Address]
🆔 BT Job ID: [jobId]
📋 Type: [type] | Contract: [contract type]
📅 [start] → [end]
👤 PMs: [names]

✅ BT Setup:
  ✅ Job created
  ✅ Cost codes: [standard/custom]
  ✅ Estimate: [imported/skipped]
  ✅ Schedule: [imported/skipped]
  ✅ Folders: Created
  ✅ Client: [added/skipped]
  ✅ Subs: [N added/skipped]
  ✅ QBO: [linked/skipped]

✅ Company Infrastructure:
  ✅ Google Drive: [folder link]
  ✅ Reminders: Company - [project]
  ✅ All agent configs updated
  ✅ Project Registry updated

Ready to roll! 🚧
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📊 View in BT | `primary` | `bt_newjob_view` |
| 📅 Set Up Schedule Now | `primary` | `bt_newjob_schedule` |
| 📨 Send Bids Now | `primary` | `bt_newjob_bids` |
| ✅ Done | `success` | `bt_newjob_done` |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Job title already exists | Warn: "A job with this name already exists — use a different title?" |
| Template not found | List available templates for selection |
| QBO customer not found | Create new customer in QBO first (via bookkeeper agent) |
| Google Drive folder creation fails | Retry, or create manually |
| Agent config file missing | Log error, continue with other steps |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |
| Zip code invalid | Required for weather data — ask for correction |

---

## Quick Setup Checklist (Copyable)
```
New Job: [Name]
☐ BT: Job created (ID: _____)
☐ BT: PMs assigned
☐ BT: Cost codes set
☐ BT: Estimate imported/created
☐ BT: Schedule imported/created
☐ BT: File folders created
☐ BT: Client added + invited
☐ BT: Subs added + permissions set
☐ BT: QBO linked
☐ BT: Selections set up (if applicable)
☐ Company: Drive folders created
☐ Company: Reminders list created
☐ Company: Project registry updated
☐ Company: All agent configs updated
```

---

## URL Patterns
| Page | URL |
|---|---|
| New Job (From Scratch) | `/app/JobPage/0/1?openCondensed=true` |
| New Job (From Template) | `/app/leads/opportunities/QuickAction/JobFromTemplate/0/0/0/-1` |
| Job Info | `/app/JobPage/{jobId}/1` |
| Job Clients Tab | `/app/JobPage/{jobId}/2?accessedFromContact=true` |
| Job Settings | `/app/Settings/JobSettings` |
| Company Settings | `/app/Settings` |
