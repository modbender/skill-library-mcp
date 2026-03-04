# Schedule Management (Agent-Assisted)

## Overview

> **UI Reference:** See `bt-ui-patterns.md` for combobox dropdown, modal, grid, and navigation patterns used in this playbook.
The agent helps the user create and manage schedule items in Buildertrend — adding tasks with dates and assignees, setting predecessor dependencies, updating progress, sending schedule updates to subs, and monitoring milestones and critical path. The schedule is the backbone of project management in BT, driving notifications, Daily Log weather, and predecessor-based auto-shifts.

## Trigger
- the user says "add [task] to the schedule for [project]"
- the user says "update schedule for [project]" or "what's the schedule look like?"
- the user says "send schedule update to subs"
- New job setup requires schedule creation
- Schedule review before client/lender meeting
- Sub asks about upcoming work dates

---

## Step 1: Identify Project
**Action:** Confirm which project

**Message to the user:**
```
📅 Schedule Management — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_sched_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_sched_project_1` |
| 🏗️ Project Beta | `primary` | `bt_sched_project_2` |
| 🏗️ Project Beta | `primary` | `bt_sched_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_sched_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_sched_project_4` |
| 🏗️ Project Eta | `primary` | `bt_sched_project_5` |
| ❌ Cancel | `danger` | `bt_sched_cancel` |

---

## Step 2: Choose Action
**Message to the user:**
```
📅 Schedule for [project] — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Add Schedule Item | `success` | `bt_sched_add` |
| ✏️ Update Progress | `primary` | `bt_sched_update` |
| 📅 Reschedule Item | `primary` | `bt_sched_reschedule` |
| 🔗 Set Dependencies | `primary` | `bt_sched_deps` |
| 📊 View Schedule Summary | `primary` | `bt_sched_view` |
| 📤 Send Update to Subs | `primary` | `bt_sched_notify` |
| 📥 Import from Template | `primary` | `bt_sched_import` |
| ❌ Cancel | `danger` | `bt_sched_cancel` |

---

## Step 3A: Add Schedule Item

### Gather Details
**Message to the user:**
```
➕ New Schedule Item — what's the task?
```

**After title received:**
```
📝 "[title]"

Fill in the details:
```

**Inline buttons for common schedule items:**
| Button | Style | callback_data |
|---|---|---|
| 🔨 Demo | `primary` | `bt_sched_quick_demo` |
| 🧱 Framing | `primary` | `bt_sched_quick_framing` |
| ⚡ Electrical Rough | `primary` | `bt_sched_quick_elec_rough` |
| 🔧 Plumbing Rough | `primary` | `bt_sched_quick_plumb_rough` |
| ❄️ HVAC Rough | `primary` | `bt_sched_quick_hvac_rough` |
| 🧯 Fire Protection | `primary` | `bt_sched_quick_fire` |
| 🧱 Drywall | `primary` | `bt_sched_quick_drywall` |
| 🎨 Paint | `primary` | `bt_sched_quick_paint` |
| 🪵 Flooring | `primary` | `bt_sched_quick_flooring` |
| 🪵 Millwork/Trim | `primary` | `bt_sched_quick_millwork` |
| 🔍 Inspection | `primary` | `bt_sched_quick_inspection` |
| 🏁 Milestone | `primary` | `bt_sched_quick_milestone` |
| ✏️ Custom Item | `primary` | `bt_sched_custom` |

### Detail Collection
**Message to the user:**
```
📅 Schedule Item Details:

📝 Title: [title]
📅 Start date: (when does this start?)
⏱️ Duration: (how many work days?)
👷 Assigned to: (which sub/team member?)
🎨 Color: (display color on calendar?)
```

**Duration quick-picks:**
| Button | Style | callback_data |
|---|---|---|
| 1 day | `primary` | `bt_sched_dur_1` |
| 3 days | `primary` | `bt_sched_dur_3` |
| 5 days (1 week) | `primary` | `bt_sched_dur_5` |
| 10 days (2 weeks) | `primary` | `bt_sched_dur_10` |
| ✏️ Custom | `primary` | `bt_sched_dur_custom` |

**Color options (match BT palette):**
| Button | Style | callback_data |
|---|---|---|
| 🔴 Red | `primary` | `bt_sched_color_red` |
| 🟡 Yellow | `primary` | `bt_sched_color_yellow` |
| 🟢 Green | `primary` | `bt_sched_color_green` |
| 🔵 Blue | `primary` | `bt_sched_color_blue` |
| ⚫ Silver (default) | `primary` | `bt_sched_color_silver` |

### Final Review
**Message to the user:**
```
📅 Schedule Item Ready:

📝 Title: [title]
🏗️ Project: [project]
📅 Start: [date]
📅 End: [calculated from start + work days]
⏱️ Duration: [N] work days
👷 Assigned to: [name(s)]
🎨 Color: [color]
🔗 Predecessor: [if set, or "None"]

Create this schedule item?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create Item | `success` | `bt_sched_create` |
| 🔗 Add Predecessor First | `primary` | `bt_sched_add_pred` |
| ✏️ Edit Details | `primary` | `bt_sched_edit` |
| ❌ Cancel | `danger` | `bt_sched_cancel` |

---

## Step 3B: Update Progress
**Action:** Update % complete on existing items

### Browser Relay Execution
1. Navigate to `/app/Schedules/0`
2. Snapshot → parse schedule items
3. Present items to the user

**Message to the user:**
```
📊 Update Progress — [project]:

Which item(s) to update?
```

**Show schedule items as buttons or list, then ask for % complete:**
```
📝 "[Schedule Item]" — currently [X]% complete.
New progress?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 25% | `primary` | `bt_sched_prog_25` |
| 50% | `primary` | `bt_sched_prog_50` |
| 75% | `primary` | `bt_sched_prog_75` |
| 100% ✅ | `success` | `bt_sched_prog_100` |
| ✏️ Custom % | `primary` | `bt_sched_prog_custom` |

**Browser Relay:** Open schedule item → adjust Progress slider/spinner → auto-save.

---

## Step 3C: Reschedule Item
**Action:** Change dates on an existing schedule item

**Message to the user:**
```
📅 Which item needs rescheduling?
```

After selecting item:
```
📅 "[Item]" — currently [start] to [end] ([N] days)

New dates?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➡️ Push 1 Day | `primary` | `bt_sched_push_1` |
| ➡️ Push 1 Week | `primary` | `bt_sched_push_5` |
| ➡️ Push 2 Weeks | `primary` | `bt_sched_push_10` |
| ✏️ Custom New Start | `primary` | `bt_sched_new_start` |
| ❌ Cancel | `danger` | `bt_sched_cancel` |

**⚠️ Important:** If schedule is Online, rescheduling triggers notifications to assigned subs and prompts for a Shift Reason. The agent should warn the user:
```
⚠️ Schedule is ONLINE — rescheduling will notify subs and record a shift reason.
Continue?
```

---

## Step 3D: Set Dependencies (Predecessors)
**Action:** Link schedule items with predecessor relationships

**Message to the user:**
```
🔗 Set Dependency — which two items?

1. Predecessor (must finish/start first): [pick item]
2. Successor (starts after): [pick item]
```

**Dependency type:**
| Button | Style | callback_data |
|---|---|---|
| FS: Finish-to-Start | `success` | `bt_sched_dep_fs` |
| SS: Start-to-Start | `primary` | `bt_sched_dep_ss` |

**Lag/Lead:**
| Button | Style | callback_data |
|---|---|---|
| No lag (0 days) | `primary` | `bt_sched_lag_0` |
| +1 day lag | `primary` | `bt_sched_lag_1` |
| +3 day lag | `primary` | `bt_sched_lag_3` |
| -1 day lead (overlap) | `primary` | `bt_sched_lead_1` |
| ✏️ Custom | `primary` | `bt_sched_lag_custom` |

**Browser Relay:** Switch to Gantt view → drag connection from predecessor to successor → set lag value.

---

## Step 3E: View Schedule Summary
**Action:** Pull current schedule and present as summary

### Browser Relay Execution
1. Navigate to `/app/Schedules/0`
2. Switch to **List view** for easy parsing
3. Snapshot → extract schedule data

**Present to the user:**
```
📅 Schedule Summary — [project]:

📊 Online/Offline: [Online ✅ / Offline ⚠️]

| # | Item | Start | End | Days | Assigned | Progress | Status |
|---|------|-------|-----|------|----------|----------|--------|
| 1 | [title] | [date] | [date] | [N] | [name] | 100% | ✅ Done |
| 2 | [title] | [date] | [date] | [N] | [name] | 50% | 🔵 In Progress |
| 3 | [title] | [date] | [date] | [N] | [name] | 0% | ⏳ Not Started |
| 4 | [title] | [date] | [date] | [N] | [name] | 30% | 🔴 Behind |

📊 Overall: [X]% complete
📅 Projected completion: [date]
⚠️ Items behind schedule: [N]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✏️ Update Progress | `primary` | `bt_sched_update` |
| ➕ Add Item | `success` | `bt_sched_add` |
| 📅 Reschedule Items | `primary` | `bt_sched_reschedule` |
| 📤 Send to Subs | `primary` | `bt_sched_notify` |
| 📊 Baseline Comparison | `primary` | `bt_sched_baseline` |
| 🔄 Refresh | `primary` | `bt_sched_refresh` |

---

## Step 3F: Send Schedule Updates to Subs
**Action:** Notify subs of their upcoming work

**Message to the user:**
```
📤 Send schedule update — who should receive it?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 All Assigned Subs | `success` | `bt_sched_notify_all` |
| 📧 Select Specific Subs | `primary` | `bt_sched_notify_select` |
| 📧 Only Next 2 Weeks | `primary` | `bt_sched_notify_2w` |
| ❌ Cancel | `danger` | `bt_sched_cancel` |

**Note:** Schedule must be **Online** to send notifications. If offline:
```
⚠️ Schedule is currently OFFLINE — subs won't receive notifications.
Put schedule online first?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🟢 Put Online & Notify | `success` | `bt_sched_online_notify` |
| ⏭️ Keep Offline | `primary` | `bt_sched_keep_offline` |

---

## Step 3G: Import from Template
**Action:** Import a schedule template for a new project

### Browser Relay Execution
1. Navigate to `/app/Schedules/0`
2. Click **More Actions** → **Import from Templates**
3. Select **Source Template** from dropdown
4. Check **Schedule** under Items to Copy
5. Set **New Start Date**
6. Click **Import**
7. Snapshot → verify schedule imported

**Report back:**
```
✅ Schedule imported from template!

📋 Template: [template name]
📅 Start date: [date]
📊 Items imported: [N]
🔗 Dependencies preserved: [Yes/No]

Review the schedule?
```

---

## Step 4: Create Item via Browser Relay
**Action:** Execute schedule item creation in BT

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/Schedules/0`
3. Snapshot → verify Schedule page loaded
4. Click **"New Schedule Item"** button
5. In the schedule item form (modal):
   - Set **Title** (text input — required)
   - Set **Display Color** (combobox)
   - Set **Assignees** (combobox — multi-select)
   - Set **Start Date** (date picker)
   - Set **Work Days** (spinner — adjusts end date automatically)
   - Set **End Date** (auto-calculated, can override)
   - Set **Progress** (slider or spinner — 0-100%)
   - Optionally set **Reminder** (combobox)
   - **Predecessors & Links tab:** Add predecessors if needed
   - **Phases & Tags tab:** Set phases and tags
   - **Notes tab:** Add notes (All Notes, Internal, Sub, Client)
   - **Files tab:** Upload supporting documents
6. Click **Save**
7. Snapshot → confirm item appears on schedule

**Report back:**
```
✅ Schedule item created!

📅 [title]
🏗️ Project: [project]
📅 [start date] → [end date] ([N] work days)
👷 Assigned to: [name(s)]
🎨 Color: [color]
📊 Progress: 0%
```

---

## Milestone Tracking
**Action:** Track key project milestones

### Common Construction Milestones
| Milestone | Typical Indicator |
|---|---|
| 📋 Permit Approved | Permits in hand |
| 🏗️ Foundation Complete | Footings/slab done |
| 🏗️ Structural Framing Complete | Frame inspection passed |
| 🔧 Rough-In Complete | MEP rough inspections passed |
| 🧱 Drywall Complete | Walls taped and finished |
| 🎨 Finishes Complete | Paint, tile, flooring done |
| 🔍 Final Inspection | TCO/CO obtained |
| 🏁 Substantial Completion | Client move-in ready |
| 📋 Punch List Complete | All items resolved |

**Mark milestones as 0-day schedule items (start = end = milestone date) with a distinctive color.**

---

## Baseline Comparison
**Action:** Compare current schedule to baseline

### Browser Relay Execution
1. Navigate to `/app/Schedules/0`
2. Click **Baseline tab**
3. Snapshot → parse baseline vs current data

**Present to the user:**
```
📊 Baseline vs Current — [project]:

| Item | Baseline End | Current End | Slip |
|------|-------------|-------------|------|
| [title] | [date] | [date] | ✅ On time |
| [title] | [date] | [date] | ⚠️ +3 days |
| [title] | [date] | [date] | 🔴 +10 days |

📊 Overall schedule slip: [+N days / On track]
```

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Schedule is locked/offline | Warn the user, offer to put online |
| Assignee not on job | Ask the user to add sub to job first |
| Predecessor creates circular dependency | BT will block — report the conflict |
| Date falls on non-work day | BT auto-adjusts to next work day — inform the user |
| Template import fails | Check template exists, try re-importing |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## URL Patterns
| Page | URL |
|---|---|
| Schedule (Calendar/List/Gantt) | `/app/Schedules/0` |
| Schedule Settings | `/app/Schedules/0/ScheduleSettings` |
| Schedule History | `/app/Schedules/0/ScheduleHistory/{jobId}` |
| Baseline tab | `/app/Schedules/0` (Baseline tab) |
| Workday Exceptions | `/app/Schedules/0` (Workday Exceptions tab) |
