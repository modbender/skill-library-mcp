# Manage To-Dos & Punch Lists (Agent-Assisted)

## Overview
The agent helps the user create, assign, and track To-Dos and Punch Lists in Buildertrend. To-Dos are individual tasks with assignees and deadlines. Punch Lists are batch to-dos created during project closeout — each item a deficiency or incomplete work item that must be resolved before final completion. The agent tracks completion, follows up on overdue items, and generates status reports.

## Trigger
- the user says "create to-do for [project]" or "add task for [sub]"
- the user says "punch list for [project]" or "start closeout list"
- End of project phase — punchlist walkthrough
- Daily log reveals items needing follow-up
- Site inspection generates action items
- the user asks "what's outstanding on [project]?"

---

## Step 1: Identify Project
**Action:** Confirm which project

**Message to the user:**
```
📋 To-Do / Punch List — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_todo_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_todo_project_1` |
| 🏗️ Project Beta | `primary` | `bt_todo_project_2` |
| 🏗️ Project Beta | `primary` | `bt_todo_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_todo_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_todo_project_4` |
| 🏗️ Project Eta | `primary` | `bt_todo_project_5` |
| ❌ Cancel | `danger` | `bt_todo_cancel` |

---

## Step 2: Choose Mode
**Action:** Individual to-do or punch list mode

**Message to the user:**
```
📋 Tasks for [project] — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Create Single To-Do | `success` | `bt_todo_single` |
| 📋 Start Punch List | `primary` | `bt_todo_punchlist` |
| 📊 View Open Tasks | `primary` | `bt_todo_view_open` |
| ⏰ Show Overdue Items | `danger` | `bt_todo_view_overdue` |
| 📈 Punch List Report | `primary` | `bt_todo_report` |
| ❌ Cancel | `danger` | `bt_todo_cancel` |

---

## Step 3A: Create Single To-Do

### Gather Details
**Message to the user:**
```
➕ New To-Do — what needs to be done?
(Type the task title)
```

**After title received:**
```
📝 To-Do: "[title]"

Who should handle it?
```

**Inline buttons (common assignees):**
| Button | Style | callback_data |
|---|---|---|
| 👷 [Sub 1 from job] | `primary` | `bt_todo_assign_[id]` |
| 👷 [Sub 2 from job] | `primary` | `bt_todo_assign_[id]` |
| 👤 {{owner_name}} | `primary` | `bt_todo_assign_kris` |
| 👤 {{team_member}} | `primary` | `bt_todo_assign_niko` |
| 👤 {{team_member}} | `primary` | `bt_todo_assign_arion` |
| ✏️ Other / Multiple | `primary` | `bt_todo_assign_other` |
| ⏭️ Unassigned | `primary` | `bt_todo_assign_none` |

**Then priority and deadline:**
```
📅 Priority and deadline?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔴 High — Due in 3 days | `danger` | `bt_todo_high_3d` |
| 🟡 Medium — Due in 1 week | `primary` | `bt_todo_med_1w` |
| 🟢 Low — Due in 2 weeks | `success` | `bt_todo_low_2w` |
| ✏️ Custom Priority/Date | `primary` | `bt_todo_custom` |
| ⏭️ No Priority / No Date | `primary` | `bt_todo_no_priority` |

**Subtasks/Checklist:**
```
📝 Any subtasks? (type them one per line, or skip)
Example:
- Remove damaged drywall
- Patch and tape
- Prime and paint
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ⏭️ No Subtasks | `primary` | `bt_todo_no_subtasks` |

### Final Review
**Message to the user:**
```
📋 To-Do Ready:

📝 Title: [title]
🏗️ Project: [project]
👤 Assigned to: [name]
🔴 Priority: [High/Med/Low]
📅 Due: [date]
📝 Subtasks: [count or "None"]
  [- subtask 1]
  [- subtask 2]

Create this to-do?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create To-Do | `success` | `bt_todo_create` |
| ✏️ Edit | `primary` | `bt_todo_edit` |
| ❌ Cancel | `danger` | `bt_todo_cancel` |

---

## Step 3B: Punch List Mode (Batch Creation)

### Introduction
**Message to the user:**
```
📋 Punch List Mode — [project]

I'll help you create multiple items. Send me items one at a time or as a list.

For each item, include:
• What needs to be fixed/completed
• Location (e.g., "Unit 3A Kitchen")
• Responsible trade (e.g., "Plumber", "Painter")

Type your first item, or paste a full list.
```

### Batch Input Parsing
Accept input formats:
1. **One at a time:** "Touch up paint in hallway — painter"
2. **Full list:**
```
Kitchen - scratched countertop - countertop sub
Bathroom 2A - toilet wobbles - plumber
Hallway - paint touch up - painter
Living room - outlet cover missing - electrician
Master bath - grout crack at shower - tile sub
```

### Smart Assignment Logic
| Trade Keyword | Suggested Assignee | Suggested Tag |
|---|---|---|
| Plumber, plumbing | Plumbing sub on job | Punchlist |
| Painter, paint, touch up | Paint sub on job | Punchlist |
| Electrician, electrical, outlet | Electrical sub on job | Punchlist |
| Tile, grout | Tile sub on job | Punchlist |
| Drywall, patch | Drywall sub on job | Punchlist |
| Carpenter, trim, door | Carpentry sub on job | Punchlist |
| HVAC, vent, thermostat | HVAC sub on job | Punchlist |
| Countertop | Countertop sub on job | Punchlist |
| General, misc, cleaning | Internal team | Punchlist |

### Present Batch Summary
**Message to the user:**
```
📋 Punch List — [project] — [N] items:

| # | Item | Location | Assigned To | Priority |
|---|------|----------|-------------|----------|
| 1 | [desc] | [location] | [sub/person] | Medium |
| 2 | [desc] | [location] | [sub/person] | Medium |
| 3 | [desc] | [location] | [sub/person] | High |
| ... | ... | ... | ... | ... |

Create all [N] items?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create All | `success` | `bt_punch_create_all` |
| ✏️ Edit Items | `primary` | `bt_punch_edit` |
| ➕ Add More Items | `primary` | `bt_punch_add_more` |
| ❌ Cancel | `danger` | `bt_punch_cancel` |

---

## Step 4: Create via Browser Relay

### Single To-Do — Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/tasks`
3. Snapshot → verify Tasks page loaded (tabs: All tasks | My tasks | Punch list)
4. Click into the inline task creation field
5. Type the task title → press Enter
6. Snapshot → verify task created in list
7. Click the created task to open detail panel → click "Show details"
8. In detail panel:
   - Set **Assignees** (combobox) → select assigned user(s)
   - Set **Due date** (date picker)
   - Set **Tags** → add relevant tags (e.g., "Punchlist", "Inspection")
   - Add **Description** (rich text)
   - Add **Subtasks** → click "Add" for each checklist item
   - Add **Attachments** if any
9. Detail panel auto-saves
10. Snapshot → confirm all fields set correctly

### Punch List Batch — Browser Relay Execution
1. Navigate to `/app/tasks/punch-list` (Punch list tab)
2. For each item in the batch:
   a. Click inline creation field
   b. Type task title → Enter
   c. Open detail panel
   d. Set assignee, due date, tags ("Punchlist"), description
   e. Close detail panel
3. After all items: Snapshot → verify punch list count
4. Report progress: "Created [N]/[total] punch list items"

**Report back:**
```
✅ [N] punch list items created in Buildertrend!

📋 Project: [project]
👷 Assigned to [N] different subs/team members
📅 All due by: [date range]
🏷️ Tagged: Punchlist
📊 Status: Open
```

---

## Step 5: Track Completion

### View Open Tasks
**Browser Relay Execution:**
1. Navigate to `/app/tasks/all` (or `/app/tasks/punch-list` for punchlist)
2. Snapshot → parse task table
3. Extract: Task name, Due date, Assignees, Tags, Status

**Present to the user:**
```
📊 Task Status — [project]:

✅ Completed: [N] / [Total]
⏳ Open: [N]
⏰ Overdue: [N]

| # | Task | Assignee | Due | Status |
|---|------|----------|-----|--------|
| 1 | [name] | [person] | [date] | ✅ Done |
| 2 | [name] | [person] | [date] | ⏳ Open |
| 3 | [name] | [person] | [date] | 🔴 Overdue |

📊 Completion: [X]% complete
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Follow Up on Overdue | `danger` | `bt_todo_followup` |
| ➕ Add New Task | `success` | `bt_todo_single` |
| 📄 Export Report | `primary` | `bt_todo_export` |
| 🔄 Refresh | `primary` | `bt_todo_refresh` |

---

## Step 6: Follow Up on Overdue
**Action:** Identify overdue items and prompt follow-up

**Message to the user:**
```
⏰ Overdue Tasks — [project]:

🔴 "[task name]" — assigned to [person]
   Due: [date] ([N] days overdue)

🔴 "[task name]" — assigned to [person]
   Due: [date] ([N] days overdue)

Send follow-up reminders?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Notify All Overdue Assignees | `success` | `bt_todo_notify_all` |
| 📧 Notify Specific Person | `primary` | `bt_todo_notify_one` |
| 📅 Extend Deadlines | `primary` | `bt_todo_extend` |
| ⏭️ Skip | `primary` | `bt_todo_skip` |

### Follow-up: Add comment to task in BT:
```
This item is past due ([N] days). Please complete ASAP or provide an updated completion date.
```

---

## Step 7: Punch List Report
**Action:** Generate closeout-ready punch list report

**Message to the user:**
```
📈 Punch List Report — [project]:

📊 Summary:
• Total items: [N]
• Completed: [N] ✅
• Outstanding: [N] ⏳
• Overdue: [N] 🔴
• Completion: [X]%

📋 By Trade:
| Trade | Total | Done | Open | Overdue |
|-------|-------|------|------|---------|
| Plumber | 5 | 3 | 2 | 0 |
| Painter | 8 | 5 | 2 | 1 |
| Electrician | 3 | 3 | 0 | 0 |
| Tile | 4 | 1 | 2 | 1 |

📍 By Location:
| Location | Total | Done | Open |
|----------|-------|------|------|
| Kitchen | 6 | 4 | 2 |
| Bathroom A | 4 | 3 | 1 |
| Living Room | 3 | 2 | 1 |

🏁 Ready for closeout? [Yes — all complete / No — [N] items remaining]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Send Report to Team | `primary` | `bt_todo_report_send` |
| 📧 Notify Subs with Open Items | `danger` | `bt_todo_notify_open` |
| ➕ Add More Punch Items | `primary` | `bt_punch_add_more` |
| ✅ Mark Project Closeout | `success` | `bt_todo_closeout` |

---

## Step 8: Post-Action
After to-do/punch list creation:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — track due dates for key items
3. **Link to daily logs** — if task came from site walkthrough
4. **Link to schedule** — if task affects schedule milestone

---

## Link To-Dos to Other Features

### From Daily Log
When a daily log mentions an issue:
```
💡 Daily log mentions "[issue]" — create a to-do to track it?
```

### From Schedule Item
Link a to-do to a schedule item for phase-specific tracking.

### From Change Order
When a CO generates action items, create to-dos for execution tracking.

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save task details for resume |
| Assignee not on job | Ask the user to add them to the job first |
| Tags not loading | Create without tags, add manually later |
| Inline creation fails | Try "New Task" button instead of inline |
| Task auto-save fails | Retry, or note to add details manually |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## Common Tags for To-Dos
| Tag | Use For |
|---|---|
| Punchlist | Closeout deficiency items |
| Client ToDo | Items requiring client action |
| Inspection | Pre-inspection preparations |
| PM Tasks | Project management action items |
| Material Orders | Material ordering tasks |
| Safety Meeting | Safety-related items |
| Clean Up | Cleaning tasks |
| Installation | Installation tasks |
| Pre-Con Checklist | Pre-construction items |

---

## URL Patterns
| Page | URL |
|---|---|
| All Tasks | `/app/tasks/all` |
| My Tasks | `/app/tasks/my-tasks` |
| Punch List | `/app/tasks/punch-list` |
