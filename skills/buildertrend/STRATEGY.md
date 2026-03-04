# Buildertrend Automation Strategy — {{company_name}}

## The Problem
Buildertrend has **no public API**. No developer keys. No OAuth. No REST endpoints.
But it's our project management backbone — we need to automate it.

## The Solution: Browser Automation via Chrome Extension Relay

OpenClaw has a **Browser Relay** — a Chrome extension that lets us control an attached browser tab via the `browser` tool. We log into Buildertrend like a human, attach the tab, and automate from there.

No scraping. No reverse engineering. We're clicking buttons and reading screens — same as a human would, just faster and smarter.

---

## Phase 0: STUDY — Know Buildertrend Inside-Out

Before touching the browser, learn every corner of the platform from official and community sources.

### Learning Sources
1. **Official Help Center** — every help article, every FAQ (see knowledge-base.md for full list)
2. **Official YouTube tutorials** — Complete Tutorial series (PM, Daily Logs, Scheduling, Specs, Templates)
3. **Official Blog** — best practices, cost codes guide, scheduling guide, budget guide, workflow tips
4. **Product Updates** — monthly changelogs (2025 updates documented in knowledge-base.md)
5. **Reddit r/Construction + r/ConstructionManagers** — real user tips, complaints, workarounds
6. **Resource Hub** — downloadable guides and expert-backed strategies
7. **Webinars / Podcasts** — "The Building Code" podcast, BT webinar series

### Key Knowledge Areas
- **Cost code structure** — how to set up for commercial GC (not just residential)
- **Budget flow** — Estimate → Proposal → Budget → POs/Bills → Actuals → Variance tracking
- **QBO integration** — 2-way sync, what pushes where, matching workflows
- **Schedule management** — phases, dependencies, baseline, mobile updates
- **Sub portal** — how subs interact with POs, bids, RFIs, daily logs
- **Daily log best practices** — legal protection, photo documentation, detail level
- **Change order workflow** — client variance vs builder variance, approval chain
- **Lien waiver tracking** — compliance requirements for your jurisdiction

### Deliverable: `knowledge-base.md`
Comprehensive reference doc covering every module, best practices, community insights, and company-specific configuration notes. **DONE — see knowledge-base.md**

---

## Phase 1: LEARN — Map the Entire Platform (Browser Discovery)

With knowledge-base study complete, map the actual live UI for automation.

### Discovery Tasks
1. **Log into Buildertrend** via browser, attach tab with Chrome Relay
2. **Snapshot every major page** — capture the DOM structure, aria labels, button refs
3. **Document the navigation tree:**
   - Top nav → sidebar → sub-pages → modals
   - URL patterns (are they SPA routes? hash-based? query params?)
4. **Map every module** and its UI elements:

#### Buildertrend Modules (complete inventory)

**PRE-SALE / SALES**
| Module | What It Does | {{company_name}} Priority |
|---|---|---|
| Lead Management / CRM | Track prospects, lead sources, pipeline stages | Medium |
| Email Marketing | Campaigns, templates, drip sequences | Low |
| Proposals / Estimates | Build proposals, line items, send to clients | HIGH |
| Bid Requests | Send bid packages to subs, collect responses | HIGH |

**PROJECT MANAGEMENT**
| Module | What It Does | {{company_name}} Priority |
|---|---|---|
| Schedule / Gantt | Tasks, dependencies, milestones, baseline tracking | HIGH |
| To-Do's | Task assignments, checklists, completion tracking | HIGH |
| Daily Logs | Field reports — weather, labor, equipment, notes, photos | HIGH |
| Change Orders | Client variances, builder variances, approval workflow | HIGH |
| Selections | Client selection tracking (finishes, materials, fixtures) | Medium |
| Warranty | Post-completion warranty tracking | Low |
| Time Clock | Labor time tracking, clock in/out | Medium |
| RFIs | Request for Information — questions to architect/engineer | HIGH |
| Submittals | Shop drawings, product data, samples for approval | HIGH |
| Punch List | Deficiency tracking, completion sign-off | HIGH |
| Photos / Videos | Job photos organized by date, category, location | Medium |
| Documents / Files | Plans, specs, contracts, permits — file storage | HIGH |
| Messages | Internal messaging, owner communication | Medium |

**FINANCIAL MANAGEMENT**
| Module | What It Does | {{company_name}} Priority |
|---|---|---|
| Budget | Project budget vs actuals, cost codes | HIGH |
| Estimates / Bids | Detailed cost estimates with line items | HIGH |
| Purchase Orders | POs to vendors/subs, approval workflow | HIGH |
| Bills | Incoming invoices from subs/vendors | HIGH |
| Invoicing | Progress billing to clients (AIA-style) | HIGH |
| Lien Waivers | Conditional/unconditional waivers, tracking | HIGH |
| Owner Draws | Draw requests, bank integration | Medium |
| Financial Reporting | P&L by job, cash flow, cost analysis | HIGH |

**CUSTOMER MANAGEMENT**
| Module | What It Does | {{company_name}} Priority |
|---|---|---|
| Customer Portal | Client-facing view — schedule, selections, invoices | Medium |
| Surveys | Client satisfaction tracking | Low |

### Deliverable: `buildertrend-map.json`
```json
{
  "modules": {
    "schedule": {
      "nav_path": "Project → Schedule",
      "url_pattern": "/project/{id}/schedule",
      "key_elements": {
        "add_task_btn": "aria-ref or selector",
        "task_list": "...",
        "gantt_view": "...",
        "calendar_view": "..."
      },
      "actions": ["create_task", "edit_task", "set_dependency", "update_status"],
      "data_fields": ["task_name", "start_date", "end_date", "assignee", "status", "notes"]
    }
  }
}
```

---

## Phase 2: BUILD — Automation Playbooks

Once we've mapped the UI, build reusable **playbooks** — step-by-step browser actions for common workflows.

### Priority Playbooks (what we automate first)

#### 1. Daily Log Entry
**Trigger:** The agent/field crew provides daily report info
**Actions:**
- Navigate to project → Daily Logs → New Entry
- Fill: date, weather, temperature, crew count
- Add: work performed notes, issues/delays
- Attach: photos if provided
- Submit

#### 2. Change Order Creation
**Trigger:** the user approves a scope change
**Actions:**
- Navigate to project → Change Orders → New
- Fill: description, line items, amounts
- Attach: backup documentation
- Route for approval

#### 3. Schedule Update
**Trigger:** Task completion or delay reported
**Actions:**
- Navigate to project → Schedule
- Find task by name
- Update: status, actual dates, % complete
- Add notes if provided

#### 4. Budget Review / Pull
**Trigger:** Weekly or on-demand
**Actions:**
- Navigate to project → Budget
- Snapshot the budget summary
- Extract: budgeted vs actual vs committed vs projected
- Report back with variance flags

#### 5. RFI Submission
**Trigger:** Field question needs architect response
**Actions:**
- Navigate to project → RFIs → New
- Fill: subject, question, drawings reference
- Assign to: architect/engineer
- Set priority and due date

#### 6. Purchase Order Creation
**Trigger:** Approved material order
**Actions:**
- Navigate to project → Purchase Orders → New
- Fill: vendor, line items, amounts, cost codes
- Route for approval

#### 7. Invoice / Pay App Pull
**Trigger:** Monthly billing cycle
**Actions:**
- Navigate to project → Invoicing
- Pull current SOV status
- Extract: completed to date, stored materials, retention
- Generate pay app data

#### 8. Punch List Management
**Trigger:** Punch walk or deficiency report
**Actions:**
- Navigate to project → Punch List
- Create items with location, description, assignee
- Attach photos
- Track completion status

---

## Phase 3: INTEGRATE — Connect to {{company_name}} Ecosystem

### Data Flow
```
Buildertrend (browser) ←→ the agent (automation)
                              ↓
                    ┌─────────┼─────────┐
                    ↓         ↓         ↓
                 procurement agent      bookkeeper agent     CRM agent
              (PO data)   (invoices) (contacts)
```

### Integration Points
- **Budget data → bookkeeper agent** for QBO reconciliation
- **PO data → procurement agent** for procurement tracking
- **Contact data → CRM agent** for CRM enrichment
- **Schedule data → the agent** for project status reporting
- **Change orders → the agent** for scope tracking + the user approval
- **Daily logs → Google Drive** for backup/archive

---

## Phase 4: HARDEN — Reliability & Error Handling

### Challenges We'll Face
1. **Session timeouts** — Buildertrend will log us out. Need re-auth flow.
2. **Dynamic UI** — SPA frameworks change DOM on navigation. Need robust selectors.
3. **Loading states** — Wait for spinners/loaders before acting.
4. **Modal dialogs** — Buildertrend loves modals. Need to handle open/close.
5. **Rate concerns** — Don't click too fast. Add human-like delays.
6. **Error recovery** — If a click fails, screenshot → report → don't keep clicking blindly.

### Reliability Rules
- **Always snapshot before acting** — verify we're on the right page
- **Never assume navigation succeeded** — check URL or page title
- **Screenshot on error** — save evidence for debugging
- **One action at a time** — no parallel browser operations
- **Session check before every playbook** — verify we're still logged in

---

## Technical Approach

### Browser Relay (OpenClaw built-in)
```
1. the user logs into Buildertrend in Chrome
2. Clicks OpenClaw Browser Relay toolbar icon on the BT tab
3. the agent can now control that tab via `browser` tool
4. Snapshot → read state → act → verify
```

### Skill Structure
```
SKILLS/buildertrend/
├── SKILL.md              # Operating manual
├── STRATEGY.md           # This document
├── buildertrend-map.json # UI element map (Phase 1 output)
├── playbooks/
│   ├── daily-log.md      # Step-by-step: create daily log
│   ├── change-order.md   # Step-by-step: create change order
│   ├── schedule-update.md
│   ├── budget-pull.md
│   ├── rfi-submit.md
│   ├── po-create.md
│   ├── invoice-pull.md
│   └── punch-list.md
└── selectors/
    └── element-refs.json # Stable selectors per module
```

---

## Rollout Plan

| Phase | What | Timeline | Who |
|---|---|---|---|
| 1 - LEARN | Map all modules, document UI elements | Week 1 | the agent + the user (browser relay) |
| 2 - BUILD | Priority playbooks (daily logs, COs, budget) | Week 2-3 | the agent |
| 3 - INTEGRATE | Connect to bookkeeper agent/procurement agent/CRM agent data flows | Week 3-4 | the agent |
| 4 - HARDEN | Error handling, session management, reliability | Ongoing | the agent |

---

## Prerequisites

Before we start Phase 1:
1. ✅ OpenClaw Browser Relay extension installed in Chrome
2. ⬜ the user logs into Buildertrend and attaches the tab
3. ⬜ Confirm {{company_name}}'s Buildertrend plan/tier (affects available modules)
4. ⬜ List active projects in Buildertrend to map against company project registry

---

*This is a living document. Updated as we learn more about BT's UI structure.*
