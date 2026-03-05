---
name: buildertrend
description: "Complete Buildertrend automation via Browser Relay - 43 playbooks covering sales, project management, financials, scheduling, change orders, daily logs, RFIs, punch lists, invoicing, procurement. No API required."
homepage: https://github.com/elevateson/buildertrend-openclaw
metadata: { "openclaw": { "requires": { "capabilities": ["browser"] } } }
---

# Buildertrend Skill — {{company_name}}

## Overview
Buildertrend is {{company_name}}'s project management platform. **No API exists** — all automation goes through the browser via OpenClaw's Chrome Extension Relay.

> **New here?** See [Setup & Configuration](#setup--configuration) below to get started.

## How It Works
1. the user logs into Buildertrend in Chrome
2. the user clicks the OpenClaw Browser Relay toolbar icon on the Buildertrend tab (badge goes ON)
3. the agent uses `browser` tool with `profile="chrome"` to control the tab
4. Workflow: **snapshot → read → act → verify**

## Critical Rules

### Before ANY Action
1. `browser snapshot` — confirm you're on the right page
2. Check for login screen — if logged out, STOP and ask the user to re-authenticate
3. Check for loading spinners — wait until page is fully loaded
4. Identify the correct element refs before clicking

### During Actions
- **One click at a time** — snapshot after each action to verify result
- **Never rush** — add reasonable pauses between actions
- **Read before writing** — always capture current state before modifying
- **Modal awareness** — check if a modal is open before trying to interact with the page behind it

### On Errors
- Screenshot immediately
- Report what happened + what you were trying to do
- Do NOT retry blindly — ask for guidance
- Save error screenshots to `memory/bt-errors/`

## Navigation Patterns
*(To be populated during Phase 1 discovery)*

## Module Reference
See `STRATEGY.md` for complete module inventory and priority rankings.
See `buildertrend-map.json` for UI element mappings (once discovered).

## Playbooks
See `playbooks/` directory for step-by-step automation workflows.
See `playbooks/README.md` for the full index with cross-references.

### Available Playbooks (43 Total):

**Sales & Pre-Construction (6):**
| Playbook | File | Trigger |
|---|---|---|
| Lead Opportunities | `playbooks/lead-opportunities.md` | New lead, "check pipeline", lead activity |
| Convert Lead to Job | `playbooks/convert-lead-to-job.md` | Lead ready to convert, proposal accepted |
| Client Proposals | `playbooks/client-proposals.md` | "Create proposal", estimate ready, send to client |
| Run Estimates | `playbooks/run-estimates.md` | "Build estimate", new job needs pricing |
| Takeoff & Estimating | `playbooks/takeoff-estimating.md` | "Do a takeoff", upload plans, measure blueprints |
| Bid Package Management | `playbooks/bid-package-management.md` | "Send bids", bid out a trade, compare responses |

**Client & Contact Management (4):**
| Playbook | File | Trigger |
|---|---|---|
| Add Clients | `playbooks/add-clients.md` | "Add client to job", new client contact |
| Client Portal Setup | `playbooks/client-portal-setup.md` | "Set up portal", configure client access |
| Sub/Vendor Onboarding | `playbooks/sub-vendor-onboarding.md` | "Add new sub", onboard vendor, bid awarded |
| Customer Surveys & Feedback | `playbooks/surveys-feedback.md` | "Send survey", client feedback, NPS tracking |

**Project Management (9):**
| Playbook | File | Trigger |
|---|---|---|
| Create Daily Log | `playbooks/create-daily-log.md` | "Daily log for [project]", end-of-day prompt |
| Schedule Management | `playbooks/schedule-management.md` | "Add to schedule", update progress, send sub updates |
| Manage RFIs | `playbooks/manage-rfis.md` | "Create RFI", track open questions, follow up |
| To-Dos & Punch Lists | `playbooks/manage-todos-punchlist.md` | "Create to-do", "punch list", closeout tracking |
| Manage Selections | `playbooks/manage-selections.md` | "Set up selections", client finishes, allowances |
| Specifications Management | `playbooks/specifications-management.md` | "Create spec", scope documentation, link to bids |
| Document Management | `playbooks/document-management.md` | "Upload plans", file management, share docs |
| Messages & Communications | `playbooks/messaging-communications.md` | "Message [sub]", check messages, notify all subs |
| Photo & Video Management | `playbooks/photo-video-management.md` | "Upload photos", site documentation, markup, video |

**Financial (12):**
| Playbook | File | Trigger |
|---|---|---|
| Receipt → Bill | `playbooks/receipt-to-bill.md` | New receipt in Cost Inbox, the user sends receipt |
| Create Invoice | `playbooks/create-invoice.md` | "Invoice [project]", billing cycle, CO approved |
| Create Purchase Order | `playbooks/create-po.md` | "Create PO for [vendor]", bid approved, CO needs PO |
| Create Change Order | `playbooks/create-change-order.md` | "Change order for [project]", client CO request |
| Advanced Change Orders | `playbooks/manage-change-orders-advanced.md` | Complex COs, variance POs, multi-CO management |
| Job Costing Report | `playbooks/job-costing-report.md` | "How's the budget?", weekly review, pre-meeting |
| BT ↔ QBO Reconciliation | `playbooks/bt-qbo-reconciliation.md` | "Check QB sync", monthly close, mismatch detected |
| Credit Memos & Deposits | `playbooks/credit-memos-deposits.md` | "Create deposit", "apply credit", retainer management |
| Online Payments Setup | `playbooks/online-payments-setup.md` | "Set up payments", configure client/sub payments |
| Lien Waiver Tracking | `playbooks/lien-waiver-tracking.md` | "Check waivers", before payment, waiver audit |
| Retainage Management | `playbooks/retainage-management.md` | "Set up retainage", release holdback, retainage report |
| Reports & Dashboards | `playbooks/reporting-dashboards.md` | "Run a report", financial review, cash flow, KPIs |

**Labor & Time (1):**
| Playbook | File | Trigger |
|---|---|---|
| Time Clock Management | `playbooks/time-clock-management.md` | "Clock in [employee]", approve timesheets, payroll export |

**Setup & Administration (7):**
| Playbook | File | Trigger |
|---|---|---|
| New Job Setup | `playbooks/new-job-setup.md` | "New job", project goes live, lead converted |
| Cost Code Setup | `playbooks/cost-code-setup.md` | "Add cost code", check mapping, QBO sync setup |
| User & Role Management | `playbooks/user-role-management.md` | "Add user", change permissions, custom roles |
| Admin Setup & Customization | `playbooks/admin-setup-customization.md` | Company settings, branding, feature config |
| Home Depot Integration | `playbooks/home-depot-integration.md` | "Connect HD", HD receipt processing, reconciliation |
| Template Management | `playbooks/template-management.md` | "Create template", job/schedule/estimate templates |
| Financial Settings & Config | `playbooks/financial-settings-config.md` | Tax rates, invoice settings, bill approval, QBO sync config |

**Integrations (1):**
| Playbook | File | Trigger |
|---|---|---|
| Marketplace & Integrations | `playbooks/marketplace-integrations.md` | "Connect [app]", integration status, Zapier, Gusto |

**Closeout (2):**
| Playbook | File | Trigger |
|---|---|---|
| Project Closeout | `playbooks/project-closeout.md` | "Close out [project]", all work complete, final payment |
| Warranty Management | `playbooks/warranty-management.md` | "Set up warranty", new claim, check claim status |

**Mobile (1):**
| Playbook | File | Trigger |
|---|---|---|
| Mobile Workflows | `playbooks/mobile-workflows.md` | Mobile-specific BT operations, field crew actions |

### Playbook Pattern (All Workflows):
1. **Trigger** → user command, scheduled event, or external input
2. **Identify** → Which project? (inline buttons)
3. **Gather** → Collect details (guided prompts or freeform)
4. **Suggest** → Smart defaults (cost codes, vendors, amounts, tags)
5. **Review** → Present summary with Create / Edit / Cancel buttons
6. **Execute** → Browser Relay actions in Buildertrend (snapshot → act → verify)
7. **Post-action** → Log it, update Reminders, notify other agents, check QBO sync

See `playbooks/README.md` for the full index and detailed documentation.

## References
- **bt-ui-patterns.md** — Browser Relay interaction patterns for all BT forms: PO, Schedule, Change Order, Lead, combobox dropdowns, modals, grids, navigation (16 sections, 432 lines)
- **knowledge-base.md** — Complete BT module reference (2,349 lines). ⚠️ **Do NOT load the entire file per task** — it will consume significant context window. Load only the relevant section for the current workflow.
- **qbo-sync-guide.md** — QuickBooks Online integration reference
- **workflows.md** — Official BT workflow procedures
- **knowledge-base.md** — Complete BT module reference (2,349 lines). ⚠️ **Do NOT load this entire file per task** — search or load only the relevant section for the module you're working with. Loading the full file consumes significant context window.
- **qbo-sync-guide.md** — QuickBooks Online integration reference
- **workflows.md** — Official BT workflow procedures

## Session Management
- Buildertrend sessions expire — always verify login state before starting a workflow
- If session expired: notify the user, do NOT attempt to enter credentials
- the user handles all login/authentication — the agent never touches credentials

## Data Extraction
When pulling data from Buildertrend (budgets, schedules, etc.):
1. Snapshot the page
2. Parse the aria/role tree for structured data
3. Format into clean output (JSON or markdown table)
4. Store in appropriate memory file or pass to requesting agent

## Integration
- Budget data → bookkeeper agent (QBO reconciliation)
- PO data → procurement agent (procurement tracking)  
- Contact data → CRM agent (CRM enrichment)
- Schedule/CO/Daily logs → the agent (project reporting)
- Documents → Google Drive (archive)

---

## Setup & Configuration

### Prerequisites
- **OpenClaw** v2026.2.20 or later
- **OpenClaw Browser Relay** Chrome extension installed
- **Buildertrend** account (any plan with the modules you want to automate)
- **Chrome browser** — the user must be logged into BT in Chrome

### Step 1: Install the Skill
Copy the `buildertrend/` folder into your OpenClaw workspace under `SKILLS/`:
```
~/.openclaw/workspace/SKILLS/buildertrend/
```

### Step 2: Configure Placeholders
This skill uses `{{placeholders}}` throughout. Find and replace these with your company's values across all files:

| Placeholder | What It Is | Example |
|---|---|---|
| `{{company_name}}` | Your company name | Acme Construction LLC |
| `{{company_domain}}` | Your email domain | acmeconstruction.com |
| `{{company_phone}}` | Company phone number | 555-123-4567 |
| `{{company_prefix}}` | Invoice/PO prefix | ACME- |
| `{{admin_email}}` | Admin email address | admin@acmeconstruction.com |
| `{{owner_name}}` | Account owner's full name | Jane Smith |
| `{{team_member}}` | Other team members (replace per context) | John Doe |
| `{{tax_jurisdiction}}` | Your tax jurisdiction name | CA-Los Angeles |
| `{{tax_rate}}` | Combined tax rate (%) | 9.5 |
| `{{state_tax}}` | State tax portion (%) | 7.25 |
| `{{city_tax}}` | City/local tax portion (%) | 2.25 |
| `{{jurisdiction}}` | Short jurisdiction label | LA County |
| `{{project_address}}` | Example project address | 100 Main St, Suite 200 |
| `{{bookkeeper_workspace}}` | Bookkeeper agent workspace path | workspace-bookkeeper |
| `{{receipt_agent_workspace}}` | Receipt agent workspace path | workspace-receipt-agent |
| `{{procurement_agent_workspace}}` | Procurement agent workspace path | workspace-procurement |

**Quick replace** (run from the skill root):
```bash
find . -name "*.md" -exec sed -i '' 's/{{company_name}}/Your Company/g' {} +
```
Repeat for each placeholder with your values.

### Step 3: Customize Project Picker Buttons
Many playbooks include inline button tables for project selection. Replace the example projects with your actual projects:

**Before:**
```
| 🏗️ Project Alpha | `primary` | `bt_co_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_co_project_3` |
```

**After:**
```
| 🏗️ 123 Main St Office Buildout | `primary` | `bt_co_project_MAIN` |
| 🏗️ 456 Oak Ave Renovation | `primary` | `bt_co_project_OAK` |
```

### Step 4: Set Up Browser Relay
1. Install the OpenClaw Browser Relay Chrome extension
2. Log into Buildertrend in Chrome
3. Click the Browser Relay toolbar icon on the BT tab (badge turns ON)
4. The agent can now control the tab via `browser` tool with `profile="chrome"`

### Step 5: Test on a Test Project
**⚠️ Do NOT test on live projects.** Create a test job in Buildertrend first:
1. Create a job called "Test Project" in BT
2. Run a simple playbook (e.g., `create-daily-log.md`)
3. Verify the agent can snapshot, navigate, and interact correctly
4. Once confirmed, move to live projects

### Multi-Agent Setup (Optional)
> **Running a single agent?** This skill works fully with one agent. You'll see ~75 references to specialized agents (bookkeeper agent, receipt agent, procurement agent, CRM agent) across the playbooks — **ignore these.** When a playbook says "Notify bookkeeper agent," just skip that step or handle it yourself. No multi-agent setup required.

If you DO run multiple agents, configure their workspaces:
- Replace `{{bookkeeper_workspace}}` with your bookkeeper agent's workspace path
- Replace `{{receipt_agent_workspace}}` with your receipt agent's workspace path
- Replace `{{procurement_agent_workspace}}` with your procurement agent's workspace path
- Update the **Integration** section above with your agent names

### Jurisdiction Configuration
Tax rates, retainage rules, and lien waiver requirements are configured with `{{placeholders}}`. Adjust these to match your local jurisdiction:
- **Tax rate** — set `{{tax_rate}}` to your combined rate
- **Retainage** — review `playbooks/retainage-management.md` for jurisdiction-specific rules
- **Lien waivers** — review `playbooks/lien-waiver-tracking.md` for local compliance requirements
