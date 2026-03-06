# Warranty Claims & Service Management (Agent-Assisted)

## Overview
Manage post-construction warranty claims in Buildertrend — set warranty periods per job, receive and track client claims, assign subs for resolution, schedule service appointments, and generate warranty reports. The warranty phase begins when a job status moves from "Open" to "Warranty."

## Trigger
- the user says "set up warranty for [project]", "new warranty claim", "check warranty status"
- Client submits warranty claim via Client Portal
- Warranty period nearing expiration (automated alert)
- "Show all open claims for [project]"
- Project closeout → transition to warranty phase

---

## Step 1: Navigate to Warranties
**Action:** Open Warranties page

```
browser → navigate to https://buildertrend.net/app/Warranties
browser → snapshot → verify Warranties page loaded
```

**URL:** `/app/Warranties`
**Actions:** Create new Warranty claim, Help, Filter
**Filter Fields:** Search, Status (New/Open), Classifications, Category, Priority, Coordinator, Assigned To, Original Sub/Vendor, Scheduled Date, Added Date, Added By

---

## Step 2: Set Up Warranty Period for a Job

### Change Job Status to Warranty
**Action:** Move completed job from "Open" to "Warranty"

```
browser → navigate to https://buildertrend.net/app/JobPage/{jobId}/1
browser → snapshot → find "Status" dropdown
browser → snapshot → select "Warranty" from dropdown
browser → snapshot → click "Save"
browser → snapshot → verify status updated
```

**Job Statuses:**
| Status | Meaning |
|---|---|
| Pre-Sale | Lead stage, estimating |
| Open | Active construction |
| **Warranty** | Complete, within warranty period |
| Closed | All phases complete |

### Configure Warranty Settings
**Settings URL:** `/app/Settings/WarrantySettings`
- Default warranty duration (e.g., 1 year from completion)
- Warranty claim categories
- Default notifications
- Prefix for warranty items

**Message to the user:**
```
🔧 Warranty period set for [project]:
• Status: Warranty
• Start date: [actual completion date]
• Duration: [X months/years]
• Claims: Now accepting via portal & manual entry
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Looks Good | `success` | `wrty_confirm_setup` |
| 📋 Configure Settings | `primary` | `wrty_settings` |
| 📧 Notify Client | `primary` | `wrty_notify_client` |

---

## Step 3: Create a Warranty Claim

### Manual Claim Creation
**Action:** Click "Create new" → fill claim details

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| Job | Combobox | **Yes** | Current job | Must be in Warranty status |
| Title | Text input | **Yes** | — | Brief description of issue |
| Classification | Combobox | No | — | Type of claim |
| Category | Combobox | No | — | Category grouping |
| Priority | Selector | No | Normal | Low, Normal, High, Urgent |
| Coordinator | Combobox | No | — | Internal user managing claim |
| Description | Rich text | No | — | Detailed issue description |
| Attachments | File upload | No | — | Photos of defect, client correspondence |
| Assigned Sub/Vendor | Combobox | No | — | Sub responsible for resolution |
| Related Items | Selector | No | — | Link to schedule, CO, RFI, etc. |

```
browser → snapshot → click "Create new Warranty" button
browser → snapshot → select Job from combobox
browser → snapshot → fill Title with claim description
browser → snapshot → set Priority level
browser → snapshot → assign Coordinator (internal user)
browser → snapshot → assign Sub/Vendor for resolution
browser → snapshot → add Description and Attachments
browser → snapshot → click "Save"
browser → snapshot → verify claim created
```

### Client Portal Claims
- Clients can submit claims if **Change Order Requests** permission includes warranty
- Job Details → Clients tab → check warranty submission permission
- Claims auto-appear in Warranties dashboard with "New" status

**Message to the user:**
```
🔧 New Warranty Claim Created:
• Job: [project]
• Title: [claim title]
• Priority: [level]
• Assigned to: [sub/vendor or unassigned]
• Status: New
• Claim #: [number]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📅 Schedule Service | `success` | `wrty_schedule_{claimId}` |
| 👷 Assign Sub | `primary` | `wrty_assign_{claimId}` |
| 📸 Add Photos | `primary` | `wrty_photos_{claimId}` |
| 💬 Add Comment | `primary` | `wrty_comment_{claimId}` |

---

## Step 4: Manage Claim Status

### Status Workflow
```
New → In Review → Scheduled → In Progress → Resolved
                                            → Denied
```

**Status Transitions:**
| From | To | Action |
|---|---|---|
| New | In Review | Coordinator reviews claim |
| In Review | Scheduled | Service appointment set |
| Scheduled | In Progress | Sub begins work |
| In Progress | Resolved | Work complete, client satisfied |
| In Review | Denied | Claim not covered by warranty |

**To update status:**
```
browser → snapshot → click on claim row
browser → snapshot → find Status dropdown/field
browser → snapshot → select new status
browser → snapshot → add notes explaining status change
browser → snapshot → click "Save"
browser → snapshot → verify status updated
```

---

## Step 5: Schedule Service Appointment
**Action:** Set appointment date/time with assigned sub/vendor

```
browser → snapshot → open warranty claim
browser → snapshot → find scheduling section
browser → snapshot → set appointment date and time
browser → snapshot → click "Save & Submit"
browser → snapshot → verify appointment set
```

**Sub/Vendor receives:**
- Email notification with appointment details
- Can Accept or Reschedule from Sub Portal
- Mobile: More → Project Management → Warranty

**Message to the user:**
```
📅 Service Appointment Set:
• Claim: [title]
• Sub/Vendor: [name]
• Date: [date] at [time]
• Status: Scheduled
• Sub notification: Sent ✅
```

---

## Step 6: Attach Documentation
**Action:** Add photos, documents, and notes to claims

```
browser → snapshot → open warranty claim
browser → snapshot → click "Attachments" or file upload area
browser → snapshot → upload photos of defect
browser → snapshot → add comments with resolution notes
browser → snapshot → verify files attached
```

**Best Practice:** Always attach:
- 📸 Photos of the defect (before)
- 📸 Photos of the repair (after)
- 📄 Sub's repair report
- 💬 Client communication thread

---

## Step 7: Resolve/Close a Claim
**Action:** Mark claim as resolved after service complete

```
browser → snapshot → open warranty claim
browser → snapshot → update Status to "Resolved"
browser → snapshot → add resolution notes
browser → snapshot → attach completion photos
browser → snapshot → click "Save"
browser → snapshot → verify resolved
```

**Message to the user:**
```
✅ Warranty Claim Resolved:
• Claim: [title]
• Job: [project]
• Resolved by: [sub/vendor]
• Resolution: [notes]
• Duration: [days from filing to resolution]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Close Claim | `success` | `wrty_close_{claimId}` |
| 📧 Notify Client | `primary` | `wrty_notify_{claimId}` |
| 💰 Create Bill (if cost) | `primary` | `wrty_bill_{claimId}` |

---

## Step 8: Warranty Expiration & Closeout
**Action:** Monitor warranty periods approaching expiration

**Expiration Tracking:**
- Filter warranties by job + added date range
- Compare to warranty period duration
- Alert the user 30 days before expiration

**Close Warranty Period:**
```
browser → navigate to https://buildertrend.net/app/JobPage/{jobId}/1
browser → snapshot → verify all claims resolved
browser → snapshot → change Status from "Warranty" to "Closed"
browser → snapshot → click "Save"
```

**Message to the user:**
```
⚠️ Warranty Period Expiring Soon:
• Job: [project]
• Warranty started: [date]
• Expires: [date] ([X] days remaining)
• Open claims: [count]
• Resolved claims: [count]

Close warranty period?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Close Warranty | `success` | `wrty_close_period` |
| 📋 View Open Claims | `primary` | `wrty_open_claims` |
| ⏰ Extend 30 Days | `primary` | `wrty_extend` |
| ⏭️ Later | `danger` | `wrty_later` |

---

## Step 9: Generate Warranty Report
**Action:** Pull warranty data across jobs for reporting

**Report data points:**
| Metric | Source |
|---|---|
| Total claims filed | Warranty count per job |
| Claims by status | Filter by New/In Review/Scheduled/Resolved/Denied |
| Average resolution time | Added date → resolved date |
| Claims by sub/vendor | Group by assigned sub |
| Claims by category | Group by classification/category |
| Cost of warranty work | Bills linked to warranty claims |

```
browser → snapshot → apply filter: Date range + Status
browser → snapshot → read table data
browser → snapshot → export if needed
```

**Message to the user:**
```
📊 Warranty Report — [Project/All Jobs]:
| Metric | Value |
|---|---|
| Total claims | [X] |
| Open | [Y] |
| Resolved | [Z] |
| Denied | [W] |
| Avg resolution | [X] days |
| Warranty cost | $[amount] |
```

---

## Sub/Vendor Warranty Experience
From the Sub Portal:
1. View claims with Priority and Scheduling Info
2. Accept or Reschedule appointments
3. Set appointment → Save & Submit
4. Add Comments and RFIs
5. Mobile: More → Project Management → Warranty

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Job not in Warranty status | Must change job status first (Open → Warranty) |
| No sub assigned to claim | Ask the user who should handle the claim |
| Sub declined service | Notify the user, suggest alternate sub |
| Claim outside warranty period | Flag to the user — may need to deny or handle as goodwill |
| Client submitted duplicate | Compare with existing claims, suggest merge |

---

## Company-Specific Notes
- Warranty settings: `/app/Settings/WarrantySettings`
- Standard company warranty period: Confirm with the user (typically 1 year)
- All warranty claims linked to project closeout documentation
- Photos filed to Google Drive under project's `Other Documents` folder
- Update Apple Reminders when warranty period starts/ends
