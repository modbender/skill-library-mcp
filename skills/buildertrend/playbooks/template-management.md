# Template Management — Jobs, Schedules, Estimates & Proposals

## Overview
Create, manage, and apply reusable templates in Buildertrend for jobs, schedules, estimates, and proposals. Templates standardize project setup, reduce data entry, and ensure consistency across {{company_name}}'s commercial buildout projects. Templates cover the full lifecycle from job creation through estimate and proposal delivery.

## Trigger
- "Create a template", "save this as a template"
- "Use template for new job", "apply schedule template"
- "Standard buildout setup", "template for commercial project"
- "Save this estimate as template", "proposal template"
- New job setup using standard company workflow
- Recurring project type needs standardized setup

---

## Step 1: Identify Template Type
**Action:** Determine which template to create or apply

**Message to the user:**
```
📋 Template Management — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Job Template | `primary` | `bt_tmpl_job` |
| 📅 Schedule Template | `primary` | `bt_tmpl_schedule` |
| 💰 Estimate Template | `primary` | `bt_tmpl_estimate` |
| 📄 Proposal Template | `primary` | `bt_tmpl_proposal` |
| 📋 View all templates | `primary` | `bt_tmpl_list` |

---

## Step 2: Job Templates

### What's Included in a Job Template
- Job type and contract type
- Default cost codes assigned
- Standard selections pre-loaded
- Default schedule items
- Standard estimate line items
- Document folder structure
- Default permissions and user assignments
- Custom field values

### Create Job Template
**Browser Relay Steps:**
1. Navigate to an existing job that represents the standard setup
   - OR create a new "template job" with all standard settings
2. The job's configuration becomes the template basis
3. Navigate to Jobs menu → "New Job From Template"
   - URL: `/app/leads/opportunities/QuickAction/JobFromTemplate/0/0/0/-1`
4. BT allows saving job configurations as templates

**Alternative — From Scratch:**
1. Navigate to Jobs → New Job
2. Configure all standard settings for {{company_name}} commercial buildout:
   - Type: Commercial
   - Contract Type: Fixed Price or Cost Plus
   - Cost codes: company standard 200+ codes
   - Work days: Mon-Fri (standard) or Mon-Sat
   - Default selections, estimate items, schedule items
3. Save as template

### Apply Job Template
**Browser Relay Steps:**
1. Navigate to Jobs menu → New Job
2. Select "Your Templates"
3. Choose template from list
4. All pre-configured fields populate automatically
5. Customize job-specific details:
   - Title (project name)
   - Address
   - Client contact
   - Contract price
   - Projected dates
6. Save new job

---

## Step 3: Schedule Templates

### What's Included
- Schedule items with default durations
- Dependencies (predecessors) between items
- Phases and groupings
- Standard work sequence
- Color coding

### Create Schedule Template
**Browser Relay Steps:**
1. Navigate to an existing job with a well-built schedule
2. Open Schedule (`/app/Schedules/0`)
3. Click "More Actions" menu
4. Look for "Save as Template" or "Template" option
5. Name the template (e.g., "Company Commercial Buildout — Standard")
6. Save

### Company Standard Commercial Buildout Schedule Template
| Phase | Items | Typical Duration |
|---|---|---|
| **1. Pre-Construction** | Permits, submittals, procurement | 2-4 weeks |
| **2. Demolition** | Protection, demo, debris removal | 1-3 weeks |
| **3. Rough-In — Structure** | Framing, steel, blocking | 2-4 weeks |
| **4. Rough-In — MEP** | Electrical, plumbing, HVAC, fire protection | 3-6 weeks |
| **5. Inspections (Rough)** | DOB inspections, special inspections | 1-2 weeks |
| **6. Insulation & Drywall** | Insulation, drywall hang, tape, finish | 2-4 weeks |
| **7. Finishes — Floors** | Tile, flooring, carpet | 2-3 weeks |
| **8. Finishes — Walls & Ceiling** | Paint, wall finish, ceiling tile | 2-3 weeks |
| **9. Finishes — Millwork** | Casework, trim, doors, hardware | 2-3 weeks |
| **10. MEP Trim** | Fixtures, devices, equipment | 1-2 weeks |
| **11. Specialties** | Signage, AV, security, countertops | 1-2 weeks |
| **12. Inspections (Final)** | Final DOB, TCO/CO | 1-2 weeks |
| **13. Punch List** | Walkthrough, corrections | 1-2 weeks |
| **14. Closeout** | Final cleaning, documentation, turnover | 1 week |

### Apply Schedule Template
1. Open new job's Schedule
2. Click "Apply Template" or import from template
3. Adjust dates to actual project timeline
4. Modify durations per project specifics
5. Set actual start date → all dates cascade
6. Save schedule

---

## Step 4: Estimate Templates

### What's Included
- Cost items with descriptions
- Quantities and unit costs (editable per job)
- Cost codes assigned
- Markup percentages
- Group/category structure

### Create Estimate Template (From Existing)
**Browser Relay Steps:**
1. Navigate to a job with a completed estimate
2. Open Estimate (`/app/Estimate`)
3. Click "More" or export options
4. Select "Save as Template" (or use the template function)
5. Name template (e.g., "Company Commercial Office Buildout")
6. Save

**Ref:** https://buildertrend.com/help-article/how-to-template-your-existing-estimate/

### Company Standard Estimate Template Categories
| Category | Cost Codes | Typical Items |
|---|---|---|
| General Conditions | 01.xx | Site supervision, temp facilities, permits, insurance |
| General Requirements | 02.xx | Dumpsters, safety, site protection, survey |
| Demolition | 20.xx | Selective demo, hazmat, debris removal |
| Concrete/Foundation | 04.xx | Slab, footings, rebar, formwork |
| Structural Steel | 35.xx | Steel beams, columns, connections |
| Framing | 05.xx | Metal studs, wood framing, blocking |
| Plumbing | 07.xx | Rough-in, fixtures, connections |
| Electrical | 08.xx | Rough-in, devices, panels, fixtures |
| HVAC | 09.xx | Ductwork, equipment, controls |
| Insulation & Drywall | 10.xx | Insulation, drywall, taping |
| Millwork | 12.xx | Casework, trim, custom items |
| Doors & Hardware | 13.xx | Doors, frames, hardware |
| Painting | 14.xx | Primer, paint, wall covering |
| Flooring | 15.xx | Tile, hardwood, carpet, VCT |
| Fire Protection | 25.xx | Sprinklers, alarms |
| Countertops | 28.xx | Stone, solid surface, laminate |
| Cleaning | 19.xx | Construction clean, final clean |

### Apply Estimate Template
1. Open new job's Estimate
2. Click "Apply Template"
3. Select template
4. All line items populate with default quantities/costs
5. Edit quantities and costs per actual project scope
6. Adjust markups as needed
7. Lock estimate when finalized

---

## Step 5: Proposal Templates

### What's Included
- Formatted document layout (logo, header, footer)
- Standard terms and conditions
- Scope description templates
- Exclusions list
- Payment schedule template
- Signature blocks

### Create Proposal Template
**Browser Relay Steps:**
1. Navigate to Estimate → Proposal Dashboard
2. Or navigate to Settings → Estimates (`/app/Settings/EstimateSettings`)
3. Create proposal format template
4. Set:
   - Company logo and header
   - Introduction text
   - Scope presentation format (cost code grouping or custom grouping)
   - Terms and conditions
   - Exclusions
   - Footer and signature area
5. Save as template

### Company Proposal Standard Sections
1. **Cover Page** — company logo, project name, client name, date
2. **Executive Summary** — Project overview, approach, timeline
3. **Scope of Work** — Detailed by trade/cost code
4. **Exclusions** — What's NOT included
5. **Allowances** — Client selection allowances with amounts
6. **Schedule** — Key milestones and durations
7. **Pricing** — Line items or lump sum (based on client preference)
8. **Payment Schedule** — Progress billing terms
9. **Terms & Conditions** — Standard contract terms
10. **Signature** — Acceptance block

---

## Step 6: Manage & Organize Templates

### View All Templates
**Browser Relay Steps:**
1. Job templates: Jobs → New Job → Your Templates
2. Schedule templates: Schedule → Apply Template (view list)
3. Estimate templates: Estimate → Apply Template (view list)
4. Proposal templates: Settings → Estimates

### Template Version Management
- Keep templates named with version: "Company Commercial v3"
- When updating: create new version, keep old for reference
- Archive outdated templates (rename with "ARCHIVED — " prefix)
- Document changes in template description

### Share Templates Across Team
- Templates created by any user are available company-wide
- All internal users with appropriate permissions can apply templates
- Template access follows role permissions

---

## Smart Suggestions

| Context | Suggestion |
|---|---|
| New job created from scratch | "Want to apply a template for standard setup?" |
| Estimate built for new project type | "Save this estimate as a template for future use?" |
| Schedule completed for standard buildout | "This schedule could be a template — save it?" |
| Similar project starting | "You did a similar job at [project] — use that as template?" |
| First project of a type | "After this job, we should template it for next time" |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Template not found | Check: correct template name, user has permission |
| Template applies wrong items | Template may be outdated — review and update |
| Estimate template overrides existing data | ⚠️ Apply template BEFORE entering custom data |
| Schedule template dates don't align | Adjust start date after applying — dates cascade |
| Browser relay disconnected | Stop, ask the user to re-enable extension |

---

## Batch Mode
When setting up templates for all company project types:

1. Define project types: Commercial Office, Commercial Retail, Residential Renovation, Ground-Up
2. For each type, create:
   - Job template
   - Schedule template
   - Estimate template
   - Proposal template
3. Track progress: "Created 2/4 project type template sets..."
4. Final summary: "All template sets complete for 4 project types"

---

## URL Patterns
| Page | URL |
|---|---|
| New Job from Template | `/app/leads/opportunities/QuickAction/JobFromTemplate/0/0/0/-1` |
| New Job from Scratch | `/app/JobPage/0/1?openCondensed=true` |
| Schedule | `/app/Schedules/0` |
| Schedule Settings | `/app/Schedules/0/ScheduleSettings` |
| Estimate | `/app/Estimate` |
| Estimate Settings | `/app/Settings/EstimateSettings` |
| Proposal Dashboard | Via Estimate → Proposal Dashboard |
| Jobs List | `/app/Jobs/List` |
| BT Templates Library | `https://buildertrend.com/templates/` |
