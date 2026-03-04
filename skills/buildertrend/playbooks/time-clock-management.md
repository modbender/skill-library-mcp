# Time Clock & Labor Tracking (Agent-Assisted)

## Overview
Manage employee time tracking in Buildertrend — clock in/out, review shifts, approve timesheets, assign labor cost codes, and export for payroll. Time entries feed directly into Job Costing Budget as labor costs and can sync to QuickBooks Online or Gusto.

## Trigger
- the user says "clock in [employee]", "check time entries", "approve timesheets"
- End-of-week timesheet approval cycle
- Payroll processing window (bi-weekly or per Gusto schedule)
- "How many hours on [project] this week?"
- bookkeeper agent requests labor cost data for QBO reconciliation

---

## Step 1: Navigate to Time Clock
**Action:** Open Time Clock Reports page

```
browser → navigate to https://buildertrend.net/app/TimeClock/Reports
browser → snapshot → verify Time Clock page loaded
```

**URL:** `/app/TimeClock/Reports`
**Tabs:** Reports | Shifts Map
**Key elements:** "Record shift" button, "Clock in" button, filters panel, "Clocked In Users" count

**Present to the user:**
```
⏱️ Time Clock — Current Status:
• Clocked in now: [X] users
• Your totals: [hours this period]
• Viewing: [date range]
```

---

## Step 2: Clock In/Out an Employee

### Clock In
**Action:** Click "Clock in" button → fill shift details

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| Employee | Combobox | **Yes** | Current user | Select internal user |
| Job | Combobox | **Yes** | Current selected job | Assign to project |
| Cost Code | Combobox | No | User's default labor code | Maps to `00 - TIME TRACKING` codes |
| Notes | Text | No | Empty | Shift notes |
| GPS Location | Auto | Auto | Device location | Captured automatically on mobile |

```
browser → snapshot → click "Clock in" button
browser → snapshot → select Employee from combobox
browser → snapshot → select Job from combobox
browser → snapshot → select Cost Code (suggest from TIME TRACKING codes)
browser → snapshot → click "Clock In" / "Save"
browser → snapshot → verify confirmation
```

### Clock Out
```
browser → snapshot → find clocked-in user row
browser → snapshot → click "Clock Out" action
browser → snapshot → verify shift completed with total hours
```

**Message to the user:**
```
✅ [Employee] clocked [in/out]
• Job: [project name]
• Cost Code: [XX.XX] [name]
• Time: [start] → [end if out]
• Total: [hours if out]
```

---

## Step 3: Record a Manual Shift
**Action:** Click "Record shift" → fill shift details for missed clock-ins

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| Employee | Combobox | **Yes** | — | Select internal user |
| Job | Combobox | **Yes** | — | Assign to project |
| Cost Code | Combobox | No | Default labor code | TIME TRACKING codes: 00.10, 00.20 |
| Date | Date picker | **Yes** | Today | Shift date |
| Clock In Time | Time picker | **Yes** | — | Start time |
| Clock Out Time | Time picker | **Yes** | — | End time |
| Break Duration | Time input | No | 0 | Break minutes to deduct |
| Tags | Multi-select | No | — | e.g., "Forgot to Clock In", "Amended Time" |
| Notes | Text | No | — | Reason for manual entry |

**Tags Reference (Time Clock):**
| Tag | Use Case |
|---|---|
| Left Early | Employee left before end of shift |
| Overtime | OT shift |
| PTO | Paid time off |
| Approved | Pre-approved shift |
| Amended Time | Corrected after the fact |
| Extra Work Day | Weekend/holiday |
| Forgot to Clock In | Missed digital clock-in |
| Mileage | Travel tracking |
| Shift Edit | Modified by admin |
| Pickup/Delivery | Material runs |
| Errand | Non-jobsite work |
| Change Order Labor | CO-related labor |

```
browser → snapshot → click "Record shift"
browser → snapshot → fill Employee, Job, Cost Code, Date, Times
browser → snapshot → add Break if applicable
browser → snapshot → add Tags (e.g., "Forgot to Clock In")
browser → snapshot → click "Save"
browser → snapshot → verify shift recorded
```

---

## Step 4: View & Filter Time Entries
**Action:** Use filters to view time by employee, job, or date range

**Filter Fields:**
| Filter | Options | Use |
|---|---|---|
| User | All internal users | Per-employee view |
| Tags | Clock-in tags | Filter by type |
| Date | Date range picker | Default: Past 14 days |
| Shift Status Type | Active, Completed | Current vs past |
| Cost Codes | All TIME TRACKING codes | Filter by labor code |
| Approval Status | Pending, Approved, Rejected | Timesheet status |
| Sent To Accounting | Yes/No | QBO sync status |
| Out of Bounds Status | In/Out | Geofence violations |
| Invoiced To Client | Yes/No | Billed to client |

**Message to the user (Weekly Summary):**
```
📊 Time Clock Summary — Week of [date]:

| Employee | Mon | Tue | Wed | Thu | Fri | Total | OT |
|---|---|---|---|---|---|---|---|
| [Name] | 8h | 8h | 8h | 7.5h | 8h | 39.5h | 0h |
| [Name] | 8h | 9h | 8h | 8h | 9h | 42h | 2h |

Total labor: [X] hours across [Y] jobs
Pending approval: [Z] shifts
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Approve All Pending | `success` | `tc_approve_all` |
| 👁️ View by Job | `primary` | `tc_view_by_job` |
| 👁️ View by Employee | `primary` | `tc_view_by_employee` |
| 📤 Export for Payroll | `primary` | `tc_export_payroll` |
| ⏭️ Skip | `danger` | `tc_skip` |

---

## Step 5: Approve Timesheets
**Action:** Review and approve pending shifts

### Individual Approval
```
browser → snapshot → click on pending shift row
browser → snapshot → review shift details (times, job, cost code, GPS)
browser → snapshot → click "Approve" button
browser → snapshot → verify status changed to "Approved"
```

### Bulk Approval (Mass Actions)
```
browser → snapshot → check boxes on multiple shifts
browser → snapshot → click mass action "Approve"
browser → snapshot → verify all selected shifts approved
```

**Message to the user:**
```
✅ Timesheet Approval Complete:
• Approved: [X] shifts
• Total hours: [Y]
• Jobs covered: [list]
• Status: Ready for payroll export
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Send to QuickBooks | `success` | `tc_send_qbo` |
| 📤 Export CSV | `primary` | `tc_export_csv` |
| 🔍 Review One More | `primary` | `tc_review_more` |

---

## Step 6: Export for Payroll / Send to QBO
**Action:** Push approved time entries to accounting

### Send to QuickBooks Online
```
browser → snapshot → select approved shifts (checked boxes)
browser → snapshot → click mass action "Send to QuickBooks"
browser → snapshot → verify QB sync status updated
```

**Data pushed to QBO:** Employee, Cost Code → P&S, Dates/Times, Job/Project
**⚠️ Note:** QBO does NOT auto-calculate overtime pay rates. Default hourly rate assumed. OT requires manual adjustment in QBO or Gusto.

### Gusto Integration (if configured)
**Settings URL:** `/app/Settings/PayrollSettings`
- Time entries push to Gusto for payroll processing
- Gusto handles overtime calculation and tax withholding
- Setup: Connect Gusto account → map employees → enable auto-push

**Message to the user:**
```
📤 Time entries sent to [QBO/Gusto]:
• Shifts: [X]
• Hours: [Y] regular + [Z] OT
• Jobs: [list]
• Period: [date range]
```

---

## Step 7: Time → Job Costing Budget Flow
**How time entries affect the budget:**

| Time Entry Status | Budget Column | Impact |
|---|---|---|
| Unapproved | Committed Costs | Pending labor cost |
| Approved | Actual Costs | Confirmed labor expense |
| Sent to QBO | Actual Costs + QB Synced | Reflected in both systems |

**Enable Time Clock in Budget:**
- Company Settings → Bills/POs/Budget → ✅ "Include Time Clock Labor in Job Costing Budget on new jobs"
- Per job: Job Details → Advanced Settings → enable

**To check labor costs by job:**
```
browser → navigate to https://buildertrend.net/app/JobCostingBudget
browser → snapshot → filter by Related Items → Time Clock
browser → snapshot → read labor cost totals per cost code
```

---

## Geofencing & GPS
- **Mobile clock-in** captures GPS coordinates automatically
- **Shifts Map tab** shows where employees clocked in/out on a map
- **Out of Bounds** filter identifies clock-ins outside the job site radius
- Geofence radius configured per job in Job Details

**To check geofencing violations:**
```
browser → snapshot → click "Shifts map" tab
browser → snapshot → review map pins for out-of-bounds entries
```

---

## Break Tracking
- **Auto-deduct:** Company Settings → Time Clock → set automatic break deduction
- **Manual breaks:** Employee records break during shift
- Break time deducted from total shift hours
- **Settings URL:** `/app/Settings/TimeClockSettings`

---

## Overtime Calculation
- BT tracks total hours per employee per week
- Hours over 40 flagged with "Overtime" tag
- OT rate calculation happens in payroll system (Gusto/QBO), NOT in BT
- Use filter: Tags → "Overtime" to review all OT shifts

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Employee not found | Check Internal Users list, verify active status |
| Cost code not in TIME TRACKING | Use `00.10 Time Tracking Cost code` or `00.20 Driver` |
| GPS location missing | Mobile-only feature — desktop shifts won't have GPS |
| Shift overlaps existing entry | BT prevents overlapping shifts — check for conflicts |
| QBO push failed | Check accounting settings, verify employee linked in QB |
| Gusto not connected | Direct to Settings → Payroll → Connect Gusto |

---

## Cost Code Quick Reference (Time Clock)

| Code | Name | Use |
|---|---|---|
| 00.10 | Time Tracking Cost code | General labor tracking |
| 00.20 | Driver | Driving/delivery time |
| 01.02 | General Carpentry Laborer | Carpentry labor (BILLABLE) |
| Any billable code | Marked as Time Clock Labor | Assign specific trade labor |

**Note:** Any cost code can be enabled for Time Clock use in Company Settings → Cost Codes → mark as "Time Clock Labor Code."

---

## Company-Specific Configuration
- **4 internal users:** Administrative Assistant, {{team_member}}, {{owner_name}}, {{team_member}}
- **Time Zone:** Eastern Standard Time (GMT-5)
- **Settings URL:** `/app/Settings/TimeClockSettings`
- **Payroll Integration:** Gusto available at `/app/Settings/PayrollSettings`
- **Active jobs for time tracking:** All 6 open jobs in BT
