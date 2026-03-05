# Buildertrend Playbooks — Complete Index

Agent-assisted workflows for Buildertrend automation via Browser Relay.
All playbooks follow the same pattern: **messaging platform conversation → smart suggestions → approval → Browser Relay execution → confirmation**.

**Total: 43 Playbooks across 9 categories**

---

## Sales & Pre-Construction (6)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 1 | **Lead Opportunities** | [`lead-opportunities.md`](lead-opportunities.md) | New lead, "check pipeline", lead activity |
| 2 | **Convert Lead to Job** | [`convert-lead-to-job.md`](convert-lead-to-job.md) | Lead ready to convert, proposal accepted on lead |
| 3 | **Client Proposals** | [`client-proposals.md`](client-proposals.md) | "Create proposal", estimate ready, send to client |
| 4 | **Run Estimates** | [`run-estimates.md`](run-estimates.md) | "Build estimate", new job needs pricing |
| 5 | **Takeoff & Estimating** | [`takeoff-estimating.md`](takeoff-estimating.md) | "Do a takeoff", upload plans, measure blueprints |
| 6 | **Bid Package Management** | [`bid-package-management.md`](bid-package-management.md) | "Send bids", bid out a trade, compare responses |

## Client & Contact Management (4)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 7 | **Add Clients** | [`add-clients.md`](add-clients.md) | "Add client to job", new client contact |
| 8 | **Client Portal Setup** | [`client-portal-setup.md`](client-portal-setup.md) | "Set up portal", configure client access |
| 9 | **Sub/Vendor Onboarding** | [`sub-vendor-onboarding.md`](sub-vendor-onboarding.md) | "Add new sub", onboard vendor, bid awarded |
| 10 | **Customer Surveys & Feedback** | [`surveys-feedback.md`](surveys-feedback.md) | "Send survey", client feedback, NPS tracking |

## Project Management (9)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 11 | **Create Daily Log** | [`create-daily-log.md`](create-daily-log.md) | "Daily log for [project]", end-of-day prompt |
| 12 | **Schedule Management** | [`schedule-management.md`](schedule-management.md) | "Add to schedule", update progress, send sub updates |
| 13 | **Manage RFIs** | [`manage-rfis.md`](manage-rfis.md) | "Create RFI", track open questions, follow up |
| 14 | **To-Dos & Punch Lists** | [`manage-todos-punchlist.md`](manage-todos-punchlist.md) | "Create to-do", "punch list", closeout tracking |
| 15 | **Manage Selections** | [`manage-selections.md`](manage-selections.md) | "Set up selections", client finishes, allowances |
| 16 | **Specifications Management** | [`specifications-management.md`](specifications-management.md) | "Create spec", scope documentation, link to bids |
| 17 | **Document Management** | [`document-management.md`](document-management.md) | "Upload plans", file management, share docs |
| 18 | **Messages & Communications** | [`messaging-communications.md`](messaging-communications.md) | "Message [sub]", check messages, notify all subs |
| 19 | **Photo & Video Management** | [`photo-video-management.md`](photo-video-management.md) | "Upload photos", site documentation, markup, video |

## Financial (12)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 20 | **Receipt → Bill** | [`receipt-to-bill.md`](receipt-to-bill.md) | New receipt in Cost Inbox, the user forwards receipt |
| 21 | **Create Invoice** | [`create-invoice.md`](create-invoice.md) | "Invoice [project]", billing cycle, CO approved |
| 22 | **Create Purchase Order** | [`create-po.md`](create-po.md) | "Create PO for [vendor]", bid approved, CO needs PO |
| 23 | **Create Change Order** | [`create-change-order.md`](create-change-order.md) | "Change order for [project]", client CO request |
| 24 | **Advanced Change Orders** | [`manage-change-orders-advanced.md`](manage-change-orders-advanced.md) | Complex COs, variance POs, multi-CO management |
| 25 | **Job Costing Report** | [`job-costing-report.md`](job-costing-report.md) | "How's the budget?", weekly review, pre-meeting |
| 26 | **BT ↔ QBO Reconciliation** | [`bt-qbo-reconciliation.md`](bt-qbo-reconciliation.md) | "Check QB sync", monthly close, mismatch detected |
| 27 | **Credit Memos & Deposits** | [`credit-memos-deposits.md`](credit-memos-deposits.md) | "Create deposit", "apply credit", retainer management |
| 28 | **Online Payments Setup** | [`online-payments-setup.md`](online-payments-setup.md) | "Set up payments", configure client/sub payments |
| 29 | **Lien Waiver Tracking** | [`lien-waiver-tracking.md`](lien-waiver-tracking.md) | "Check waivers", before payment, waiver audit |
| 30 | **Retainage Management** | [`retainage-management.md`](retainage-management.md) | "Set up retainage", release holdback, retainage report |
| 31 | **Reports & Dashboards** | [`reporting-dashboards.md`](reporting-dashboards.md) | "Run a report", financial review, cash flow, KPIs |

## Labor & Time (1)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 32 | **Time Clock Management** | [`time-clock-management.md`](time-clock-management.md) | "Clock in [employee]", approve timesheets, payroll export |

## Setup & Administration (7)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 33 | **New Job Setup** | [`new-job-setup.md`](new-job-setup.md) | "New job", project goes live, lead converted |
| 34 | **Cost Code Setup** | [`cost-code-setup.md`](cost-code-setup.md) | "Add cost code", check mapping, QBO sync setup |
| 35 | **User & Role Management** | [`user-role-management.md`](user-role-management.md) | "Add user", change permissions, create custom role |
| 36 | **Admin Setup & Customization** | [`admin-setup-customization.md`](admin-setup-customization.md) | Company settings, branding, feature configuration |
| 37 | **Home Depot Integration** | [`home-depot-integration.md`](home-depot-integration.md) | "Connect HD", HD receipt processing, reconciliation |
| 38 | **Template Management** | [`template-management.md`](template-management.md) | "Create template", apply job/schedule/estimate template |
| 39 | **Financial Settings & Config** | [`financial-settings-config.md`](financial-settings-config.md) | Tax rates, invoice settings, bill approval, QBO sync config |

## Integrations (1)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 40 | **Marketplace & Integrations** | [`marketplace-integrations.md`](marketplace-integrations.md) | "Connect [app]", integration status, Zapier, Gusto |

## Closeout (2)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 41 | **Project Closeout** | [`project-closeout.md`](project-closeout.md) | "Close out [project]", all work complete, final payment |
| 42 | **Warranty Management** | [`warranty-management.md`](warranty-management.md) | "Set up warranty", new claim, check claim status |

## Mobile (1)

| # | Playbook | File | Trigger |
|---|----------|------|---------|
| 43 | **Mobile Workflows** | [`mobile-workflows.md`](mobile-workflows.md) | Mobile-specific BT operations, field crew actions |

---

## Workflow Pattern

Every playbook follows this structure:

```
1. TRIGGER      → user message, scheduled event, or external input
2. IDENTIFY     → Which project? (inline buttons)
3. GATHER       → Collect details (guided prompts or freeform)
4. SUGGEST      → Smart defaults (cost codes, vendors, amounts)
5. REVIEW       → Present summary for approval (inline buttons)
6. EXECUTE      → Browser Relay actions in Buildertrend
7. CONFIRM      → Report success/failure back to the user
8. POST-ACTION  → Log, update Reminders, notify other agents
```

---

## Playbook Cross-References

Many playbooks link to each other for complex workflows:

| Scenario | Primary Playbook | Links To |
|---|---|---|
| Lead wins → create job | lead-opportunities | → convert-lead-to-job → new-job-setup |
| New job → full setup | new-job-setup | → template-management, manage-selections, schedule-management, client-portal-setup |
| Plans received → estimate | takeoff-estimating | → run-estimates → client-proposals |
| Estimate complete → proposal | run-estimates | → client-proposals |
| Proposal accepted → budget | client-proposals | → job-costing-report |
| Bid awarded → PO | bid-package-management | → create-po |
| New sub → onboard → PO | sub-vendor-onboarding | → create-po |
| RFI requires scope change | manage-rfis | → create-change-order |
| Selection over allowance | manage-selections | → create-change-order |
| CO approved → invoice | create-change-order | → create-invoice |
| Bill created → check waiver | receipt-to-bill | → lien-waiver-tracking |
| HD receipt → bill | home-depot-integration | → receipt-to-bill |
| Daily log issue → to-do | create-daily-log | → manage-todos-punchlist |
| Site photos → daily log | photo-video-management | → create-daily-log |
| Time entries → payroll | time-clock-management | → bt-qbo-reconciliation, marketplace-integrations (Gusto) |
| PO created → retainage | create-po | → retainage-management |
| All work done → closeout | manage-todos-punchlist | → project-closeout |
| Closeout → release retainage | project-closeout | → retainage-management |
| Closeout → survey | project-closeout | → surveys-feedback |
| Project closed → warranty | project-closeout | → warranty-management |
| Warranty claim → sub | warranty-management | → messaging-communications |
| Monthly close → reconcile | job-costing-report | → bt-qbo-reconciliation |
| Financial review → reports | job-costing-report | → reporting-dashboards |
| Settings change → verify | financial-settings-config | → bt-qbo-reconciliation |
| New project type → templates | new-job-setup | → template-management |
| Connect integration | admin-setup-customization | → marketplace-integrations |

---

## Key References

- **SKILL.md** — Buildertrend skill overview and rules
- **workflows.md** — Official BT workflow procedures
- **knowledge-base.md** — Complete BT feature reference (scraped from Help Center)
- **`memory/buildertrend-phase1.md`** — URL patterns & UI mapping
- **`memory/buildertrend-phase2.md`** — Form fields, cost codes, settings

## Browser Relay Requirements

1. the user must be logged into Buildertrend in Chrome
2. OpenClaw Browser Relay extension must be active (badge ON) on the BT tab
3. the agent uses `browser` tool with `profile="chrome"`
4. Session timeout: check login state before every workflow
5. One action at a time: **snapshot → act → verify**

## Common Inline Button Styles

| Style | Use For |
|---|---|
| `primary` | Neutral options, navigation, information |
| `success` | Confirm, approve, create, proceed |
| `danger` | Cancel, reject, delete, flag problem |
