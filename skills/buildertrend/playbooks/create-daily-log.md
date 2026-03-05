# Create Daily Log (Agent-Assisted)

## Overview

> **UI Reference:** See `bt-ui-patterns.md` for combobox dropdown, modal, grid, and navigation patterns used in this playbook.
The agent helps the user create a Daily Log in Buildertrend — documenting daily job site progress, issues, materials delivered, and weather conditions. The agent can auto-detect the project from conversation context, suggest relevant tags, and prompt for photos/attachments.

## Trigger
- the user says "daily log for [project]" or "log today's work"
- the user sends a site photo and says "add to daily log"
- End-of-day prompt (if scheduled via heartbeat)
- the user says "what happened on site today?"

---

## Step 1: Identify Project
**Action:** Determine the project — auto-detect from recent context or ask

**Auto-detect logic:**
1. Check if the user mentioned a project name in the last few messages
2. Check if there's an active schedule item for today on any project
3. Check most recently discussed project in today's memory
4. If confident → suggest; otherwise ask

**Message to the user:**
```
📝 Creating a Daily Log — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_log_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_log_project_1` |
| 🏗️ Project Beta | `primary` | `bt_log_project_2` |
| 🏗️ Project Beta | `primary` | `bt_log_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_log_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_log_project_4` |
| 🏗️ Project Eta | `primary` | `bt_log_project_5` |
| ❌ Cancel | `danger` | `bt_log_cancel` |

If auto-detected:
```
📝 Daily Log for [project name] — today, [date]?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Yes, [project] | `success` | `bt_log_confirm` |
| 🔄 Different project | `primary` | `bt_log_change_project` |
| 📅 Different date | `primary` | `bt_log_change_date` |

---

## Step 2: Collect Log Content
**Action:** Ask for the three core sections of a daily log

**Message to the user:**
```
📝 Daily Log — [project] — [date]
🌤️ Weather: [auto-filled by BT based on job zip code]

What happened today? Fill in what applies:

**Progress:**
(What work was completed today?)

**Issues:**
(Any problems, delays, safety concerns?)

**Materials Delivered:**
(What arrived on site?)

You can type all at once, or I'll ask one at a time.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✏️ I'll type it all | `primary` | `bt_log_freeform` |
| 🗣️ Ask me one at a time | `primary` | `bt_log_guided` |
| 📸 Add photos first | `primary` | `bt_log_photos` |
| 📋 Copy from yesterday | `primary` | `bt_log_copy_prev` |

### Guided Mode (one at a time):

**Step 2a — Progress:**
```
🔨 What work was completed today?
(e.g., "Framing 3rd floor 80% complete, electrician started rough-in")
```

**Step 2b — Issues:**
```
⚠️ Any issues or delays?
(e.g., "Plumber no-show, rain delay until 11am")
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ No issues today | `success` | `bt_log_no_issues` |
| ✏️ Type issues | `primary` | `bt_log_type_issues` |

**Step 2c — Materials:**
```
📦 Materials delivered today?
(e.g., "2 pallets drywall, 50 sheets plywood from HD")
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ No deliveries | `success` | `bt_log_no_deliveries` |
| ✏️ Type deliveries | `primary` | `bt_log_type_deliveries` |

---

## Step 3: Photos & Attachments
**Action:** Ask about photos and files

**Message to the user:**
```
📸 Add photos or attachments?
(Send photos here and I'll include them, or skip)
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📸 I'll send photos | `primary` | `bt_log_send_photos` |
| 📎 Attach from Drive | `primary` | `bt_log_drive_attach` |
| ⏭️ No attachments | `primary` | `bt_log_no_attach` |

**If photos sent:** Collect all photos until the user says "done" or hits a button:

**Inline buttons (after photos received):**
| Button | Style | callback_data |
|---|---|---|
| ✅ Done — that's all photos | `success` | `bt_log_photos_done` |
| 📸 More photos coming | `primary` | `bt_log_photos_more` |

---

## Step 4: Tags & Visibility
**Action:** Suggest tags based on log content and set sharing

### Tag Suggestion Logic
| Content Keywords | Suggested Tags |
|---|---|
| rain, weather, snow, wind | Weather Delay |
| delivery, delivered, arrived | Delivery |
| inspect, inspection, DOB | Inspection |
| client, owner, walk | Client Conversation |
| safety, incident, accident, OSHA | Safety Inspection |
| demo, demolition | Demolition |
| concrete, pour | Concrete |
| meeting, huddle | Meeting Minutes |
| clean, cleanup | Clean Up |
| punch, punchlist | Punchlist |
| issue, problem, delay | Site Issues |

**Message to the user:**
```
🏷️ Suggested tags: [tag1], [tag2]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Use suggested tags | `success` | `bt_log_tags_accept` |
| ➕ Add more tags | `primary` | `bt_log_tags_more` |
| ⏭️ No tags | `primary` | `bt_log_no_tags` |

### Sharing defaults:
- **Internal Users:** ✅ Always checked
- **Subs/Vendors:** Only if subs were mentioned in progress
- **Client:** Only if the user explicitly requests

---

## Step 5: Sub Tagging
**Action:** Suggest notifying subs who were on site today

**Smart detection:** Parse the log text for sub/vendor names or trades that match subs assigned to this job.

**Message to the user:**
```
👷 Notify these subs about today's log?
(Based on work described — they're assigned to this project)
```

**Inline buttons (one per detected sub):**
| Button | Style | callback_data |
|---|---|---|
| ☑️ [Sub name 1 — Electrician] | `primary` | `bt_log_notify_sub_1` |
| ☑️ [Sub name 2 — Plumber] | `primary` | `bt_log_notify_sub_2` |
| ✅ Notify All Listed | `success` | `bt_log_notify_all` |
| ⏭️ Don't notify subs | `primary` | `bt_log_no_notify` |

---

## Step 6: Final Review & Approval
**Action:** Present the complete daily log for approval

**Message to the user:**
```
📝 Daily Log Ready:

🏗️ Project: [project name]
📅 Date: [date]
🌤️ Weather: [auto from BT — e.g., "Partly Cloudy, 42°F, Wind 8 mph"]
🏷️ Tags: [tags]
👁️ Shared with: Internal Users [+ Subs] [+ Client]
👷 Notify: [user list]

📋 Notes:
─────────────────
**Progress:**
[progress text]

**Issues:**
[issues text or "None"]

**Materials Delivered:**
[materials text or "None"]
─────────────────

📸 Attachments: [count] photos/files

Publish this log?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Publish | `success` | `bt_log_publish` |
| ✏️ Edit Notes | `primary` | `bt_log_edit_notes` |
| 📸 Add More Photos | `primary` | `bt_log_add_photos` |
| 🏷️ Change Tags | `primary` | `bt_log_change_tags` |
| ❌ Cancel | `danger` | `bt_log_cancel` |

---

## Step 7: Create Daily Log via Browser Relay
**Action:** Execute in Buildertrend

### Browser Relay Execution
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/DailyLogs`
3. Click "Create new Daily Log" button (+ Daily Log)
4. In the dialog/modal:
   - Verify **Job** is correct
   - Verify **Date** is correct (default: today)
   - Set **Title** (max 50 chars — e.g., "Feb 19 — Framing & Electrical")
   - Set **Tags** if applicable (combobox multi-select)
   - **Sharing:** Check appropriate boxes (Internal Users default checked)
   - **Notify Users:** Toggle notification checkboxes for selected users
   - **Attachments:** Upload photos/files if provided
   - **Notes:** Enter the formatted notes (Progress / Issues / Materials)
   - **Weather:** Verify "Include Weather Conditions" is checked (default: checked)
5. Click **Publish**
6. Snapshot → confirm log was published

**⚠️ BT Note:** The Notes field uses rich text. The default template pre-fills "Progress:\nIssues:\nMaterials Delivered:" — The agent should fill in these sections.

**Report back:**
```
✅ Daily Log published in Buildertrend!

📝 Log: [title]
🏗️ Project: [project]
📅 Date: [date]
🌤️ Weather: [conditions]
📸 Photos: [count]
👷 Notified: [users]
🔗 View: [BT URL if available]
```

---

## Step 8: Post-Creation
After daily log is published:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — mark daily log task complete if tracked
3. **Create To-Dos** — if issues were noted, offer to create To-Do items for follow-up
4. **Create RFI** — if an issue needs formal documentation, offer to create an RFI

**Optional follow-up:**
```
📋 Follow-up needed?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create To-Do from issues | `primary` | `bt_log_create_todo` |
| 📨 Create RFI | `primary` | `bt_log_create_rfi` |
| 👍 All good, no follow-up | `success` | `bt_log_done` |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save log content for resume |
| Title exceeds 50 chars | Auto-truncate and notify: "Title shortened to 50 chars" |
| Photo upload fails | Report specific file that failed, continue with remaining |
| Weather data missing | Note in log: "Weather data unavailable — update manually" |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |
| Duplicate log for same date | Warn: "A daily log already exists for [date] on [project] — create another or edit existing?" |
| Sub not assigned to job | Cannot notify — skip or ask the user to add sub to job first |

---

## Batch Mode
For logging multiple projects in one session (the user visited several sites):

1. Ask: "Log multiple projects today?"
2. If yes: loop through Steps 1-7 for each project
3. Batch context: "Progress on Project A: [text]. Progress on Project B: [text]."
4. Show running summary: "Logged 2/3 projects today"

---

## Daily Log Quick Reference

### Common Tags
| Tag | When to Use |
|---|---|
| Job Progress | Default — any normal work day |
| Weather Delay | Rain, snow, extreme heat stopped work |
| Delivery | Materials arrived on site |
| Inspection | DOB, fire dept, structural inspection |
| Client Conversation | Client visit or call about project |
| Safety Inspection | Safety walkthrough or incident |
| Meeting Minutes | Site meeting, coordination meeting |
| Rainout | Full day lost to weather |
| Site Issues | Problems that need attention |
| Sub Contractor Conversation | Coordination with trades |
| Punchlist | Punchlist walkthrough |
| Clean Up | End-of-day or end-of-phase cleanup |

### Weather Auto-Data (from BT)
| Field | Source |
|---|---|
| Conditions | Auto from zip code |
| High/Low Temp | Auto |
| Wind Speed | Auto |
| Humidity | Auto |
| Precipitation | Auto |

### Sharing Matrix
| Audience | Can See | Use When |
|---|---|---|
| Internal Users | All internal team | Always (default) |
| Subs/Vendors | Subs assigned to job | Work coordination, multi-trade days |
| Client | Project client | Progress updates, milestone days |
| Private | Only creator | Personal notes, sensitive issues |

### Title Best Practices (max 50 chars)
| Format | Example |
|---|---|
| Date — Main Activity | "Feb 19 — Framing 3rd floor" |
| Trade Focus | "Electrical rough-in started" |
| Milestone | "Inspection passed — ready for drywall" |
| Issue Flag | "⚠️ Plumber delay — reschedule" |
