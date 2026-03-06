# Manage Lead Opportunities (Agent-Assisted)

## Overview

> **UI Reference:** See `bt-ui-patterns.md` for combobox dropdown, modal, grid, and navigation patterns used in this playbook.
The agent manages {{company_name}}'s sales pipeline in Buildertrend's Lead Opportunities module — viewing the pipeline, creating new leads, tracking stages, adding activities, uploading files, setting reminders, and providing lead scoring/priority suggestions. All actions use the Browser Relay against `/app/leads/opportunities`.

## Trigger
- the user says "show me the pipeline", "leads", "new lead", or "lead status"
- the user says "add a lead for [address/contact]"
- the user says "pipeline summary" or "lead report"
- Heartbeat check detects stale leads (no activity in 14+ days)
- A referral comes in via email or chat

---

## Step 1: Identify Action
**Action:** Determine what the user wants to do with leads

**Message to the user:**
```
📊 Lead Opportunities — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 View Pipeline | `primary` | `bt_lead_view` |
| ➕ New Lead | `success` | `bt_lead_new` |
| 🔍 Find a Lead | `primary` | `bt_lead_find` |
| 📈 Pipeline Summary | `primary` | `bt_lead_summary` |
| ❌ Cancel | `danger` | `bt_lead_cancel` |

---

## Step 2A: View Pipeline
**Action:** Navigate to Leads and extract the full pipeline

### Browser Relay — Read Pipeline
1. Navigate to `https://buildertrend.net/app/leads/opportunities`
2. Snapshot → read the leads table
3. Extract per lead:
   - **Title** (project name/address)
   - **Client Contact** (name, phone, email)
   - **Lead Status** (Open, Sold, Lost, On Hold)
   - **Age** (days since creation)
   - **Confidence %**
   - **Estimated Revenue** (min–max)
   - **Last Contacted** date
   - **Salesperson** (the user or team members)
   - **Source** (Referral, Previous Client, Contact Form, Architect, etc.)
   - **Next Activity** (if scheduled)
   - **Proposal Status**

**Present to the user:**
```
📊 Company Lead Pipeline — [count] Active Leads

| # | Lead | Revenue | Confidence | Age | Last Contact | Source |
|---|------|---------|-----------|-----|-------------|--------|
| 1 | Project Alpha | $250K-$350K | 85% | Xd | [date] | Prev Client |
| 2 | 1416 Jefferson | $500K-$1.1M | 77% | Xd | [date] | Prev Client |
| 3 | 23-29 Astoria | $4.5M-$5.5M | 75% | Xd | [date] | Contact Form |
| ... |

💰 Total Pipeline: $[min]–$[max]
🔥 Weighted Value: $[sum of revenue × confidence]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔎 View Lead Details | `primary` | `bt_lead_detail` |
| ➕ Add Activity | `primary` | `bt_lead_add_activity` |
| 📝 Update Status | `primary` | `bt_lead_update_status` |
| 📈 Scoring Analysis | `primary` | `bt_lead_scoring` |
| ✅ Done | `success` | `bt_lead_done` |

---

## Step 2B: Create New Lead
**Action:** Gather lead information, then create in Buildertrend

**Message to the user:**
```
➕ New Lead — tell me about it:

I'll need:
• Project name/address
• Contact name, email, phone
• Project type (reno, new construction, fit-out, etc.)
• Estimated value range
• Source (referral, website, previous client, architect, etc.)
• Any notes

Or just give me whatever you have and I'll fill in the rest.
```

**On response, present summary:**
```
📋 New Lead Summary:

📌 Title: [address or project name]
👤 Contact: [name] — [email] — [phone]
🏗️ Type: [project type]
💰 Est. Revenue: $[min]–$[max]
📊 Confidence: [suggested %]
👥 Salesperson: [the user / team members]
📍 Source: [source]
📅 Projected Sales Date: [if provided]
📝 Notes: [notes]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Create Lead | `success` | `bt_lead_create` |
| ✏️ Edit Details | `primary` | `bt_lead_edit` |
| ❌ Cancel | `danger` | `bt_lead_cancel` |

### Browser Relay — Create Lead
1. Navigate to `https://buildertrend.net/app/leads/opportunities`
2. Click **"+ Lead Opportunity"** button
3. In the lead form:
   - Click **"+ New Contact"** (or **"+ Existing Contact"** if already in BT)
   - Fill contact fields: **First Name**, **Last Name**, **Email**, **Phone**, **Company**, **Address**
   - Click **Save** on contact
   - Set **Title** (project name/address)
   - Set **Estimated Revenue Min** and **Max**
   - Set **Confidence %** (slider or input)
   - Set **Salesperson** (combobox — {{owner_name}} and/or {{team_member}})
   - Set **Source** (combobox — Referred, Previous Client, Contact Form, Architect, Sunrise Lead, etc.)
   - Set **Project Type** (combobox)
   - Set **Projected Sales Date** (date picker)
   - Add **Notes** (text area)
   - Add **Tags** if applicable (Hot Lead, Cold Lead, Repeat Client, etc.)
4. Click **Save**
5. Snapshot → confirm lead created

**Report back:**
```
✅ Lead created in Buildertrend!

📌 [Title]
👤 [Contact Name]
💰 $[min]–$[max] | Confidence: [X]%
📊 Pipeline total now: $[updated total]
```

---

## Step 2C: Find a Lead
**Action:** Search for a specific lead

**Message to the user:**
```
🔍 Which lead are you looking for?
```

**Inline buttons (current leads):**
| Button | Style | callback_data |
|---|---|---|
| 109 Gates Ave — Water Damage | `primary` | `bt_lead_sel_1` |
| 1416 Jefferson — Townhouse | `primary` | `bt_lead_sel_2` |
| 175 Broadway — Conversion | `primary` | `bt_lead_sel_3` |
| 23-29 Astoria Blvd — Ground up | `primary` | `bt_lead_sel_4` |
| Project Alpha | `primary` | `bt_lead_sel_5` |
| 474 Irving Avenue | `primary` | `bt_lead_sel_6` |
| 495 Broadway — Interior Fit Out | `primary` | `bt_lead_sel_7` |
| 555 Macon — Violations | `primary` | `bt_lead_sel_8` |
| 🔎 Search by name | `primary` | `bt_lead_search` |

**On selection, navigate to lead detail:**

### Browser Relay — Read Lead Detail
1. Navigate to `/app/leads/opportunities/Lead/{leadId}`
2. Snapshot → extract all lead fields
3. Read **General** tab: contact info, revenue, confidence, dates, notes, files
4. Read **Activities** tab: past/upcoming calls, meetings, site visits

**Present to the user:**
```
📋 Lead Detail: [Title]

👤 Contact: [name] | [email] | [phone]
💰 Revenue: $[min]–$[max]
📊 Confidence: [X]%
👥 Salesperson: [names]
📍 Source: [source]
📅 Age: [X] days | Created: [date]
📅 Last Contacted: [date]
📅 Projected Sales Date: [date]
🏗️ Project Type: [type]
📎 Files: [count]
📝 Notes: [notes excerpt]

📌 Activities: [count total]
🔜 Next: [next activity if any]
📆 Last: [last activity + date]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Add Activity | `primary` | `bt_lead_add_activity` |
| 📝 Update Status | `primary` | `bt_lead_update_status` |
| 📎 Upload File | `primary` | `bt_lead_upload` |
| ⏰ Set Follow-up | `primary` | `bt_lead_followup` |
| 🏗️ Convert to Job | `success` | `bt_lead_convert` |
| ❌ Close | `danger` | `bt_lead_close` |

---

## Step 3: Add Activity to Lead
**Action:** Log a call, meeting, site visit, or other interaction

**Message to the user:**
```
📝 Add activity to [Lead Title]:
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📞 Phone Call | `primary` | `bt_lead_act_call` |
| 🤝 Meeting | `primary` | `bt_lead_act_meeting` |
| 🏗️ Site Visit | `primary` | `bt_lead_act_site` |
| 📧 Email Sent | `primary` | `bt_lead_act_email` |
| 📋 Proposal Sent | `primary` | `bt_lead_act_proposal` |
| 📝 Other | `primary` | `bt_lead_act_other` |

**After type selected:**
```
📝 [Activity Type] — What happened?
(Summary of the interaction, key takeaways, next steps)
```

### Browser Relay — Add Activity
1. Navigate to `/app/leads/opportunities/Lead/{leadId}/LeadActivity/0/{leadId}/1`
2. Click **"+ Activity"** or **"New Activity"** button
3. Fill:
   - **Type** (select activity type)
   - **Date** (default: today)
   - **Description** / **Notes** (the user's summary)
   - **Follow-up date** (if applicable)
4. Click **Save**
5. Snapshot → confirm activity added

**Report back:**
```
✅ Activity logged for [Lead Title]:
📞 [Type] — [date]
📝 [summary]
⏰ Follow-up: [date or "none set"]
```

---

## Step 4: Update Lead Status
**Action:** Move lead through pipeline stages

**Message to the user:**
```
📊 Update status for [Lead Title]:
Current status: [current status]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🆕 Open (Active) | `primary` | `bt_lead_status_open` |
| 📋 Proposal Sent | `primary` | `bt_lead_status_proposal` |
| 🤝 Negotiating | `primary` | `bt_lead_status_negotiating` |
| ✅ Won / Sold | `success` | `bt_lead_status_won` |
| ❌ Lost | `danger` | `bt_lead_status_lost` |
| ⏸️ On Hold | `primary` | `bt_lead_status_hold` |

### Browser Relay — Update Status
1. Navigate to `/app/leads/opportunities/Lead/{leadId}`
2. Find **Lead Status** field (combobox/dropdown)
3. Change to selected status
4. If **Won**: Set **Sold Date** to today
5. If **Lost**: Add note about why (ask the user for reason)
6. Click **Save**
7. Snapshot → confirm status updated

**If Won:**
```
🎉 Lead marked as WON! Ready to convert to a job?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Convert to Job Now | `success` | `bt_lead_convert` |
| ⏭️ Not yet | `primary` | `bt_lead_convert_later` |

**If Lost — ask for reason:**
```
❌ Why was this lead lost?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💰 Price too high | `primary` | `bt_lead_lost_price` |
| 👤 Went with competitor | `primary` | `bt_lead_lost_competitor` |
| ⏳ Client postponed | `primary` | `bt_lead_lost_postponed` |
| 🚫 Project cancelled | `primary` | `bt_lead_lost_cancelled` |
| 📝 Other reason | `primary` | `bt_lead_lost_other` |

---

## Step 5: Upload Files / Photos to Lead
**Action:** Attach documents, photos, or proposals

### Browser Relay — Upload File
1. Navigate to `/app/leads/opportunities/Lead/{leadId}`
2. Go to **General** tab → scroll to files section
3. Click **"Add"** (attach) or **"Create New Doc"**
4. Upload file(s) — supports photos, PDFs, documents
5. Snapshot → confirm files attached

**Note:** File attachments carry over when lead converts to job.

---

## Step 6: Set Follow-up Reminder
**Action:** Create a reminder for follow-up

**Message to the user:**
```
⏰ When should I remind you about [Lead Title]?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📅 Tomorrow | `primary` | `bt_lead_remind_1d` |
| 📅 3 Days | `primary` | `bt_lead_remind_3d` |
| 📅 1 Week | `primary` | `bt_lead_remind_1w` |
| 📅 2 Weeks | `primary` | `bt_lead_remind_2w` |
| 📅 1 Month | `primary` | `bt_lead_remind_1m` |
| 📅 Custom Date | `primary` | `bt_lead_remind_custom` |

**Actions:**
1. Add to **Apple Reminders** (`Company - Admin` list): "Follow up on lead: [Title] — [Contact]"
2. If BT supports activity follow-up date: set it in the lead's next activity
3. Confirm:

```
✅ Reminder set for [date]:
📌 Follow up on [Lead Title] — [Contact Name]
```

---

## Lead Scoring / Priority Logic

### Score Calculation
Each lead gets a **priority score** (0–100) based on:

| Factor | Weight | Scoring |
|---|---|---|
| **Revenue** | 30% | >$1M = 30, $500K-$1M = 25, $250K-$500K = 20, $100K-$250K = 15, <$100K = 10 |
| **Confidence** | 25% | Direct from BT confidence % × 0.25 |
| **Age (freshness)** | 15% | <7d = 15, 7-14d = 12, 14-30d = 8, 30-60d = 5, >60d = 2 |
| **Source quality** | 15% | Prev Client = 15, Referral = 13, Architect = 12, Contact Form = 8, Other = 5 |
| **Last contact recency** | 15% | <3d = 15, 3-7d = 12, 7-14d = 8, 14-30d = 4, >30d = 1 |

### Priority Tiers
| Score | Priority | Action |
|---|---|---|
| 80–100 | 🔴 **Hot** | Follow up within 24 hours |
| 60–79 | 🟠 **Warm** | Follow up within 3 days |
| 40–59 | 🟡 **Active** | Follow up weekly |
| 20–39 | 🔵 **Cool** | Follow up bi-weekly |
| 0–19 | ⚪ **Cold** | Monthly check-in or close |

### Smart Alerts
During pipeline view, flag:
- 🚨 Leads with **no activity in 14+ days** and confidence >50%
- 🚨 Leads with **projected sales date in the past**
- 🚨 High-value leads (>$500K) with **no proposal sent**
- ✅ Leads ready to **convert to job** (confidence >75%, proposal approved)

---

## Batch Mode: Pipeline Summary
When the user says "pipeline summary" or "lead report":

### Browser Relay — Read Full Pipeline
1. Navigate to `https://buildertrend.net/app/leads/opportunities`
2. Snapshot → extract ALL leads with full field data
3. Calculate aggregates

**Present to the user:**
```
📊 Company Pipeline Summary — [date]

📌 Total Leads: [count]

By Stage:
| Stage | Count | Revenue Range | Weighted |
|-------|-------|---------------|----------|
| 🆕 Open | [n] | $[min]–$[max] | $[weighted] |
| 📋 Proposal Sent | [n] | $[min]–$[max] | $[weighted] |
| 🤝 Negotiating | [n] | $[min]–$[max] | $[weighted] |
| ✅ Won (this quarter) | [n] | $[actual] | — |
| ❌ Lost (this quarter) | [n] | $[lost] | — |

💰 Total Pipeline: $[min]–$[max]
🎯 Weighted Pipeline: $[weighted total]
📅 Avg Age: [X] days
📊 Win Rate (90d): [X]%

🔥 Top Priorities:
1. [Lead] — $[revenue] — [score] — [action needed]
2. [Lead] — $[revenue] — [score] — [action needed]
3. [Lead] — $[revenue] — [score] — [action needed]

⚠️ Needs Attention:
- [Lead]: No contact in [X] days
- [Lead]: Projected sales date passed
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📊 View by Source | `primary` | `bt_lead_sum_source` |
| 📊 View by Salesperson | `primary` | `bt_lead_sum_salesperson` |
| 📧 Email Report to the user | `primary` | `bt_lead_sum_email` |
| ✅ Done | `success` | `bt_lead_sum_done` |

### By Source Breakdown:
```
📊 Pipeline by Source:
| Source | Count | Revenue | Win Rate |
|--------|-------|---------|----------|
| Previous Client | [n] | $[range] | [X]% |
| Referral | [n] | $[range] | [X]% |
| Architect | [n] | $[range] | [X]% |
| Contact Form | [n] | $[range] | [X]% |
```

### By Salesperson Breakdown:
```
📊 Pipeline by Salesperson:
| Salesperson | Leads | Revenue | Avg Confidence |
|-------------|-------|---------|---------------|
| the user | [n] | $[range] | [X]% |
| {{team_member}} | [n] | $[range] | [X]% |
| Both | [n] | $[range] | [X]% |
```

---

## Lead Opportunity Tags (BT Built-in)
| Tag | When to Use |
|---|---|
| Available Lot | Land/lot purchase opportunities |
| Real Estate | Property acquisition leads |
| Site Visited | Site visit completed |
| Hot Lead | High priority, time-sensitive |
| Cold Lead | Low activity, back-burner |
| Repeat Client | Previous company client returning |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save lead data for resume |
| Contact already exists | Present existing contact and ask: "Use existing or create new?" |
| Duplicate lead title | Warn the user, suggest appending unique identifier |
| Revenue fields blank | Suggest range based on project type / company historical data |
| Lead not found | Verify spelling, try searching in BT |
| Browser relay disconnected | Stop, save all details, ask the user to re-enable |
| Activity form not loading | Wait 3 seconds, retry; if persistent, report |

---

## URL Quick Reference

| Page | URL |
|---|---|
| Lead Opportunities (List) | `/app/leads/opportunities` |
| Lead Activities | `/app/leads/activities` |
| Lead Proposals | `/app/leads/proposals` |
| Lead Activity Calendar | `/app/leads/calendar` |
| Lead Map | `/app/leads/map` |
| Lead Detail | `/app/leads/opportunities/Lead/{leadId}` |
| Lead Contact | `/app/leads/opportunities/Contact/{contactId}/false` |
| Lead Activity | `/app/leads/opportunities/Lead/{leadId}/LeadActivity/0/{leadId}/1` |
| New Job from Template | `/app/leads/opportunities/QuickAction/JobFromTemplate/0/0/0/-1` |

---

## Sales Reports Available

| Report | URL | Use For |
|---|---|---|
| Lead Activities by Salesperson | `/Reporting/ReportDetails.aspx?reportType=5&reportFilter=106` | Activity tracking |
| Lead Count by Salesperson | `/Reporting/ReportDetails.aspx?reportType=6&reportFilter=104` | Pipeline distribution |
| Lead Status by Source | `/Reporting/ReportDetails.aspx?reportType=7&reportFilter=108` | Source effectiveness |
