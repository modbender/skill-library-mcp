# Manage RFIs — Create & Track Requests for Information (Agent-Assisted)

## Overview
When {{company_name}} needs to formally ask a question to an architect, engineer, client, or sub — or track an open question on a project — the agent guides the user through creating an RFI in Buildertrend, assigning it to the right party, setting a deadline, and following up until it's answered. RFIs maintain a documented trail of project questions and responses.

## Trigger
- the user says "create RFI for [project]" or "I need to ask the architect about [topic]"
- A question arises during daily log, schedule review, or CO discussion
- BT feature "Create RFI" is triggered from a Schedule Item, Daily Log, CO, PO, or Comment
- the user asks "what RFIs are open on [project]?"
- Follow-up on overdue RFIs (heartbeat/scheduled check)

---

## Step 1: Identify Project
**Action:** Confirm which project the RFI is for

**Message to the user:**
```
❓ Creating an RFI — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_rfi_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_rfi_project_1` |
| 🏗️ Project Beta | `primary` | `bt_rfi_project_2` |
| 🏗️ Project Beta | `primary` | `bt_rfi_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_rfi_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_rfi_project_4` |
| 🏗️ Project Eta | `primary` | `bt_rfi_project_5` |
| ❌ Cancel | `danger` | `bt_rfi_cancel` |

---

## Step 2: Choose Action
**Action:** Create new or review existing RFIs

**Message to the user:**
```
❓ RFIs for [project] — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Create New RFI | `success` | `bt_rfi_action_new` |
| 📋 List Open RFIs | `primary` | `bt_rfi_action_list_open` |
| ⏰ Show Overdue RFIs | `danger` | `bt_rfi_action_overdue` |
| 📊 All RFIs Summary | `primary` | `bt_rfi_action_all` |
| ❌ Cancel | `danger` | `bt_rfi_cancel` |

---

## Step 3: Create New RFI — Gather Details
**Action:** Collect the RFI question, recipient, and deadline

### 3A: Who is the RFI directed to?
**Message to the user:**
```
❓ New RFI — who should answer this?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏛️ Architect | `primary` | `bt_rfi_to_architect` |
| 🔧 Engineer | `primary` | `bt_rfi_to_engineer` |
| 👤 Client | `primary` | `bt_rfi_to_client` |
| 👷 Subcontractor | `primary` | `bt_rfi_to_sub` |
| 🏢 Internal Team | `primary` | `bt_rfi_to_internal` |
| ✏️ Other / Multiple | `primary` | `bt_rfi_to_other` |

**If Sub selected:** Show list of subs assigned to this job (from BT) as inline buttons.

### 3B: Question Details
**Message to the user:**
```
❓ What's the question?

Just type it out — I'll format it into an RFI. Include:
• The specific question
• Any relevant plan sheet / drawing reference
• Background / context
```

### 3C: Title & Priority
**After receiving the question, suggest a title:**
```
📝 Suggested RFI title: "[Short summary of question]"

Priority?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔴 High | `danger` | `bt_rfi_priority_high` |
| 🟡 Medium | `primary` | `bt_rfi_priority_medium` |
| 🟢 Low | `success` | `bt_rfi_priority_low` |

### 3D: Deadline
**Message to the user:**
```
📅 When do you need an answer?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ⚡ 3 Days | `primary` | `bt_rfi_deadline_3d` |
| 📅 1 Week | `primary` | `bt_rfi_deadline_1w` |
| 📅 2 Weeks | `primary` | `bt_rfi_deadline_2w` |
| ✏️ Custom Date | `primary` | `bt_rfi_deadline_custom` |
| ⏭️ No Deadline | `primary` | `bt_rfi_deadline_none` |

### 3E: Attachments
**Message to the user:**
```
📎 Any attachments? (plans, photos, sketches)
Send them now or skip.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📎 Upload Attachment | `primary` | `bt_rfi_attach` |
| ⏭️ No Attachments | `primary` | `bt_rfi_no_attach` |

---

## Step 4: Final Approval
**Action:** Present complete RFI summary

**Message to the user:**
```
❓ RFI Ready to Submit:

🏗️ Project: [project name]
📋 Title: [title]
👤 Directed to: [recipient name / role]
🔴 Priority: [High / Medium / Low]
📅 Deadline: [date]
📎 Attachments: [count or "None"]

📝 Question:
[formatted question text]

Submit this RFI?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Submit RFI | `success` | `bt_rfi_submit` |
| ✏️ Edit Details | `primary` | `bt_rfi_edit` |
| ❌ Cancel | `danger` | `bt_rfi_cancel` |

---

## Step 5: Create RFI via Browser Relay
**Action:** Execute in Buildertrend

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/RFIs`
3. Snapshot → verify RFIs page loaded
4. Click **"Create new RFI"** button (or quick-add from another feature)
5. In the RFI form:
   - Set **Title** (text input)
   - Set **Description / Question** (rich text editor — CKEditor)
   - Set **Assigned To** (combobox) → select the recipient user/sub/client
   - Set **Due Date** (date picker) if specified
   - Set **Priority** if field available
   - Add **Attachments** if any (upload or link from BT files)
   - Set **Related Items** (link to schedule item, CO, PO if applicable)
6. Click **Save** or **Send**
7. Snapshot → confirm RFI created with correct details

**Report back:**
```
✅ RFI submitted in Buildertrend!

❓ RFI #[number]: [title]
🏗️ Project: [project]
👤 Assigned to: [recipient]
📅 Deadline: [date]
🔴 Priority: [priority]
📧 Notification sent to [recipient]
📊 Status: Open
```

---

## Step 6: Post-Creation
After RFI is created:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — add reminder for RFI deadline date
   - Title: "RFI #[num] — [title] — due [date]"
   - List: Company - [project list]
3. **Link to related items** — if RFI stems from a schedule item, CO, or daily log

---

## List Open RFIs
**Action:** Pull all open RFIs for a project

### Browser Relay Execution
1. Navigate to `/app/RFIs`
2. Ensure correct job selected
3. Snapshot → parse RFI list
4. Filter: Status = Open

**Present to the user:**
```
📋 Open RFIs — [project]:

| # | RFI | Directed To | Created | Deadline | Status |
|---|-----|-------------|---------|----------|--------|
| 1 | #[num] [title] | [recipient] | [date] | [date] | 🟡 Open |
| 2 | #[num] [title] | [recipient] | [date] | [date] | 🔴 Overdue |
| 3 | #[num] [title] | [recipient] | [date] | [date] | 🟡 Open |

📊 Total: [N] open, [N] overdue
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Follow Up on Overdue | `danger` | `bt_rfi_followup_overdue` |
| ➕ Create New RFI | `success` | `bt_rfi_action_new` |
| 📊 View Answered RFIs | `primary` | `bt_rfi_action_answered` |
| 🔄 Refresh | `primary` | `bt_rfi_refresh` |

---

## Overdue RFI Follow-Up
**Action:** Automatically identify and follow up on overdue RFIs

### Logic:
1. Navigate to `/app/RFIs` → filter by job
2. Identify RFIs where deadline < today AND status = Open
3. Present overdue list

**Message to the user:**
```
⏰ Overdue RFIs — [project]:

🔴 RFI #[num]: "[title]"
   → Directed to: [recipient]
   → Deadline was: [date] ([N] days ago)
   → No response received

Want me to send a follow-up?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Send Follow-Up Comment | `success` | `bt_rfi_followup_send` |
| 📅 Extend Deadline | `primary` | `bt_rfi_extend_deadline` |
| ⏭️ Skip for Now | `primary` | `bt_rfi_followup_skip` |

### Follow-Up Comment:
Navigate to the RFI detail → add Comment:
```
Following up on this RFI — response was due [date]. Please advise at your earliest convenience. This item is holding up [related scope if known].
```

---

## RFI to Change Order Link
When an RFI response requires scope/cost changes:

**Message to the user:**
```
💡 RFI #[num] response may require a Change Order:

📝 Answer: "[summary of response]"
💰 Estimated impact: [describe if known]

Create a Change Order from this RFI?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📝 Create Change Order | `success` | `bt_rfi_to_co` |
| 📋 Note It — No CO Needed | `primary` | `bt_rfi_note_only` |
| ⏭️ Defer Decision | `primary` | `bt_rfi_defer` |

If "Create Change Order": Follow `create-change-order.md` playbook with RFI linked as Related Item.

---

## RFI to Schedule Link
When an RFI affects the schedule:

1. Navigate to RFI detail → Related Items
2. Link to affected Schedule Item(s)
3. If schedule delay expected: Suggest updating schedule item dates

---

## Batch Mode: All RFIs Across Projects
When the user asks "what RFIs are open across all projects?":

1. Navigate to `/app/RFIs` (global view)
2. Snapshot → parse all open RFIs across all jobs
3. Group by project

**Present to the user:**
```
📊 Open RFIs — All Projects:

🏗️ [Project 1]: [N] open ([N] overdue)
  • RFI #[num]: [title] — due [date]
  • RFI #[num]: [title] — ⚠️ OVERDUE [date]

🏗️ [Project 2]: [N] open ([N] overdue)
  • RFI #[num]: [title] — due [date]

📊 Total: [N] open across [N] projects, [N] overdue
```

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save RFI details for resume |
| Recipient not in BT | Ask the user to add the contact first (Users → Subs/Vendors or Job → Clients) |
| Recipient not on this job | Ask the user to add them to the job first |
| Attachment upload fails | Save RFI without attachment, note to attach manually |
| Duplicate RFI detected | Warn: "Similar RFI already exists: #[num] — [title]. Create anyway?" |
| RFI form not available | Check if RFI feature is enabled for this job/role |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## RFI Status Lifecycle

| Status | Meaning | Next Action |
|---|---|---|
| Open | Submitted, awaiting response | Monitor deadline |
| Answered | Response received | Review answer, close or follow up |
| Closed | Resolved, documented | Archive — may link to CO/schedule |
| Overdue | Past deadline, no answer | Follow up, escalate |

---

## Quick Reference

### Common RFI Categories
| Category | Typical Recipient | Example |
|---|---|---|
| Design clarification | Architect | "Confirm ceiling height at corridor junction per plan A-201" |
| Structural question | Engineer | "Verify beam size at grid line B-3 per S-102" |
| Material substitution | Architect | "Can we use [product B] in lieu of specified [product A]?" |
| Field condition | Engineer | "Existing condition differs from plans — advise on proceed" |
| Client decision | Client/Owner | "Confirm preference for [option A] vs [option B]" |
| Code/permit issue | Architect/Expediter | "DOB requires additional egress — confirm revised layout" |
| Coordination | Subcontractor | "Confirm MEP routing at [location] conflicts with framing" |

### URL Patterns
| Page | URL |
|---|---|
| RFI List (global) | `/app/RFIs` |
| RFI Settings | `/app/Settings/RFISettings` |
